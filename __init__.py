# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "autoMat",
    "description": "Some tools for materials handling",
    "author": "Samuel Bernou",
    "version": (0, 0, 4),
    "blender": (2, 80, 0),
    "location": "Properties > material > Settings",
    "warning": "",
    "wiki_url": "https://github.com/Pullusb/MatNameFromColor",
    "tracker_url": "https://github.com/Pullusb/MatNameFromColor/issues",
    "category": "Material" }
    
import bpy

def report(*args, self=None, mode='INFO'):
    #mode in 'INFO' (default), 'WARNING', 'ERROR'
    text = ' '.join([str(a) for a in args])
    if self:
        self.report({mode}, text)
    else:
        print(text)

"""
def get_colour_name(requested_colour):
    import webcolors
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        min_colours = {}
        for key, name in webcolors.css3_hex_to_names.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - requested_colour[0]) ** 2
            gd = (g_c - requested_colour[1]) ** 2
            bd = (b_c - requested_colour[2]) ** 2
            min_colours[(rd + gd + bd)] = name
        closest_name = min_colours[min(min_colours.keys())]
        #closest_name = closest_colour(requested_colour)
        actual_name = None
    return closest_name
"""
 
 
def convert_color_to_name(color):
    '''get color as a list or tuple and return closest english name'''
    if not isinstance(color, (list,tuple)):
        print(color, 'is not a list/tuple')        
        return
 
    if len(color) == 4:#strip alpha channel
        color = color[:-1]

    #convert to 255
    color = [int(c*255) for c in color]
    print("color", color)#Dbg
    closest_name = get_colour_name(color)
    print("closest_name", closest_name)#Dbg
    return (closest_name)
 
#recursive find color in node_tree
def find_color_up_tree(node):
    #print(node.type)#Dbg
    # ouputs
    if node.outputs.get('Color'):#if has an out (rgb nodes or ramp, etc, take this first)
        #print(node.outputs['Color'].default_value[:])#Dbg
        return node.outputs['Color'].default_value[:]
 
    # inputs
    # try to get colors 
    colsocket = node.inputs.get('Base Color')
    if not colsocket:
        colsocket = node.inputs.get('Color')
 
    if colsocket:
        if colsocket.is_linked:
            #print('has linked color socket')#Dbg
            for link in colsocket.links:
                color = find_color_up_tree(link.from_node)
                if color:
                    return color
        else:
            #print('unlinked input color socket ', colsocket.default_value[:])#Dbg
            return colsocket.default_value[:]
 
    #else search for a color source in links of all socket
    else:
        for input in node.inputs:
            if input.is_linked:
                for link in input.links:
                    color = find_color_up_tree(link.from_node)
                    if color:
                        #print('Color found !', color)
                        return color
 
def get_closest_node_color(mat):
    if not mat.use_nodes:
        print('material is not node based')
        return
    #get output node
    nodes = mat.node_tree.nodes
    out = None
    for n in nodes:
        if n.type == 'OUTPUT_MATERIAL':
            out = n
            break
    if not out:
        return
 
    if not out.inputs['Surface'].is_linked:
        return
 
    #go up in the tree until color found (get the 'last' color found ? or color of first node ?)
    return find_color_up_tree(out)

"""
def get_material_color(mat, viewport=False):
    '''return closest color from nodes (cycle only), or viewport color'''
    if viewport:
        return mat.diffuse_color[:]
    else:
        #later, try to get closest node from output having a color, fallback on viewport color if not any
        return get_closest_node_color(mat)
 
def rename_active_mat(viewport=True, variables={}):
    '''if any rename active material of active objects'''
    self = variables.get('self')
    matlist = material_selection_scope()
    for i, mat in enumerate(matlist):
        # print( mat.name, i+1, '/', len(matlist) )
        #get color from material
        col = get_material_color(mat,viewport)#True get viewport color, False get a connected node color (not optim...).
        #convert to color (use webcolors module)
        colname = convert_color_to_name(col)

        if colname:
            if colname in mat.name:#check if already named
                report('Material "', mat.name, '" already has name:', colname, self=self, mode='WARNING')
            else:
                #check if already exist
                used = 0
                if bpy.data.materials.get(colname):
                    #warning
                    used = 1
                    report('rename, but', colname, 'already existed', self=self)
                mat.name = colname
                report(colname, self=self)
                print(colname, '"from', col, 'on active material')
                if used:
                    report('material name now', mat.name, self=self)
        else:
            report('Error trying to get color name from', col, self=self, mode='ERROR')
"""

def material_selection_scope():
    '''Return a list of all material to change'''
    scene = bpy.context.scene
    if scene.mat_change_multiple:
        matlist=[]
        for ob in bpy.context.selected_objects:
            for slot in ob.material_slots:
                mat = slot.material
                if mat:
                    if mat not in matlist:
                        matlist.append(mat)
        print('material list', matlist)
        return matlist
    else:
        ob = bpy.context.active_object
        if ob:
            mat = ob.active_material
            if mat:
                return [mat]
        else:
            print('no active object')


def match_color_viewport_from_node(variables={}):
    self = variables.get('self')
    for mat in material_selection_scope():
        color = get_closest_node_color(mat)

        if color:
            print("color", color)#Dbg
            #print(convert_color_to_name(color))
            mat.diffuse_color = color[:]#-1
        else:
            report('cant find color in the node tree...', self=self, mode='ERROR')


def set_closest_node_color(mat, color):
    '''Change only fisrt connected node (not recursive)'''
    if not mat.use_nodes:
        print('material is not node based')
        return
    #get output node
    nodes = mat.node_tree.nodes
    out = None
    for n in nodes:
        if n.type == 'OUTPUT_MATERIAL':
            out = n
            break
    if not out:
        return
 
    if not out.inputs['Surface'].is_linked:
        return
    
    node = out.inputs['Surface'].links[0].from_node
    colsocket = node.inputs.get('Base Color')
    if not colsocket:
        colsocket = node.inputs.get('Color')
    if colsocket:
        colsocket.default_value = color
        return node

def match_color_node_from_viewport(variables={}):
    self = variables.get('self')
    matlist = material_selection_scope()
    for i, mat in enumerate(matlist):
        # print( mat.name, i, '/', len(matlist) )
        color = mat.diffuse_color
        if color:
            color = list(color[:-1]) + [1.0]
            print("color", color)#Dbg
            #print(convert_color_to_name(color))
            node = set_closest_node_color(mat,color)
            if not node:
                report('cant find a node to set color in the node tree... (this try only with the first node connected to "Surface")', self=self, mode='ERROR')
                continue
            report('color changed in node', node.name, self=self)
            #return True
                
        
"""
### -- module webcolors downloader
class AM_OT_DL_webcolors_module(bpy.types.Operator):
    bl_idname = "materials.dl_webcolors_module"
    bl_label = "Install webcolors module"
    bl_description = "Install webcolor module in script path"
    bl_options = {"REGISTER"}

    def execute(self, context):
        #auto_download_webcolors_module
        import os
        from pathlib import Path
        from urllib.request import urlretrieve
        module_path = Path(bpy.utils.script_paths(subdir='modules')[-1])
        net_module = 'https://raw.githubusercontent.com/ubernostrum/webcolors/master/webcolors.py'
        module_name = os.path.basename(net_module)
        os.chdir( str(module_path) )
         
        try:
            urlretrieve(net_module, module_name)
        except:
            print('Problem downloading the file')
            report('error trying to download', self=self, mode='ERROR')
            return {"CANCELLED"}
        report('webcolor installed', self=self)
        print('installed in :', module_path)
        return {"FINISHED"}

def dl_popup_panel(self, context):
    layout = self.layout
    layout.label(text="This functionality use module webcolors")
    layout.label(text="(manual installation notes are diplayed in console)")
    layout.label(text="Install automatically ? (restart blender)")
    layout.operator('materials.dl_webcolors_module')

def check_webcolor_module():
    '''return True if modue was found, trigger pop up to download if False'''
    import importlib
    if not importlib.util.find_spec("webcolors"):#test if module exists
 
        print('''\n--- Webcolors install note---
This operator use the module webcolors, to install the module:
STEP 1 - download the module:
Method A: with PIP: using command "pip install webcolors"
the webcolors.py module will be in the site-packages folder ("yourLocalFolder.../Python/Python35/Lib/site-packages")
Method B: directly get the file from github > https://github.com/ubernostrum/webcolors/blob/master/webcolors.py
 
STEP 2 - copy the webcolors.py module in the blender modules folder of your version
located in :''')
 
        from pathlib import Path            
        for p in bpy.utils.script_paths(subdir='modules'):
            print(Path(p))

        #'this pop up call doesnt block execution'
        bpy.context.window_manager.popup_menu(dl_popup_panel, title="webcolors module missing", icon='INFO')
        return False
    return True
### --


class AM_OT_AutoNameMaterial(bpy.types.Operator):
    bl_idname = "materials.auto_name_material"
    bl_label = "Auto name material"
    bl_description = "rename material according to color"
    bl_options = {"REGISTER"}
 
    viewport = bpy.props.BoolProperty()
    @classmethod
    def poll(cls, context):
        return True
 
    def execute(self, context):
        module_ok = check_webcolor_module()
        if not module_ok:
            #report('module webcolors not found ! look in console', self=self, mode='ERROR')
            return {"CANCELLED"}
        rename_active_mat(viewport=self.viewport, variables={'self':self, 'context':context})
        return {"FINISHED"}
"""
 
 
class AM_OT_ViewportColorFromNode(bpy.types.Operator):
    bl_idname = "materials.viewport_color_from_node"
    bl_label = "Material viewport color from node"
    bl_description = "Set the viewport color of active material with color found in node"
    bl_options = {"REGISTER"}
 
    from_viewport: bpy.props.BoolProperty()
    @classmethod
    def poll(cls, context):
        return True
 
    def execute(self, context):
        if self.from_viewport:
            match_color_node_from_viewport(variables={'self':self, 'context':context})
        else:
            match_color_viewport_from_node(variables={'self':self, 'context':context})
        return {"FINISHED"}

"""
class AM_OT_ConvertClipboardColorToName(bpy.types.Operator):
    bl_idname = "materials.convert_color_to_name"
    bl_label = "convert clipboard color to name"
    bl_description = "Convert color in paperclip to name (replace paperclip)"
    bl_options = {"REGISTER"}
 
    def execute(self, context):
        module_ok = check_webcolor_module()
        if not module_ok:
            return {"CANCELLED"}
        clip = context.window_manager.clipboard
        import re#regex check if looks like a list/tuple to ensure safety
        reclip = re.match(r'^(\(|\[)[\d., ]+(\)|\])$', clip)
        if reclip:
            try:
                import ast
                clip = ast.literal_eval(clip)#try to safely eval string
            except:
                report('could not get color name from (must be a color):\n', clip, self=self, mode='ERROR')
                return {"CANCELLED"}
            newclip = convert_color_to_name(clip)
            if newclip:
                report(newclip, self=self)
                context.window_manager.clipboard = newclip
        if not reclip or not newclip:
            report('could not get color name from (must be a color):\n', clip, self=self, mode='ERROR')
            print('exemple of allowed color format : [0.800000, 0.800000, 0.800000, 1.000000] or (0.80, 0.80, 0.80)')
            return {"CANCELLED"}
        return {"FINISHED"}
"""

################## Pannel Integration
 
def MaterialPlus(self, context):
    """option for fast naming and changing materials"""
    layout = self.layout
    #layout.label(text='Naming utils:')
    layout.prop(context.scene, "mat_change_multiple")
    # row = layout.row(align=True)
    # row.operator(AM_OT_AutoNameMaterial.bl_idname, text = "Rename from viewport", icon='RESTRICT_COLOR_ON').viewport = True
    # row.operator(AM_OT_AutoNameMaterial.bl_idname, text = "Rename from nodes", icon='NODETREE').viewport = False
    #row = layout.row(align=False)
    #row.operator(AM_OT_ConvertClipboardColorToName.bl_idname, text = "copied color name to clipboard", icon='COLOR')
    
    #layout.separator()
    #split = layout.split(factor=0.65, align=True)
    #split.operator(AM_OT_ViewportColorFromNode.bl_idname, text = "Set viewport color from node", icon='NLA_PUSHDOWN').from_viewport = False
    #split.operator(AM_OT_ViewportColorFromNode.bl_idname, text = "Color Node", icon='TRIA_UP_BAR').from_viewport = True
    layout.operator(AM_OT_ViewportColorFromNode.bl_idname, text = "Set viewport color from node", icon='NLA_PUSHDOWN').from_viewport = False
    layout.operator(AM_OT_ViewportColorFromNode.bl_idname, text = "Color Node", icon='TRIA_UP_BAR').from_viewport = True
 

class AM_OT_TestOperator(bpy.types.Operator):
    bl_idname = "test.zen_test_ops"
    bl_label = "Print Zen Code"
    bl_description = "Print le zen dans la console (en clair)"
    bl_options = {"REGISTER"}

    def execute(self, context):
        import this
        txt = ''
        for char in this.s: txt += this.d[char] if this.d.get(char) else char
        #from codecs import decode; decode(this.s, 'rot13')
        print('\n%s\n' % txt)
        self.report({'INFO'}, 'Look zen console !')
        return {"FINISHED"}



################## Registration

classes = (
    # AM_OT_DL_webcolors_module,
    # AM_OT_AutoNameMaterial,
    AM_OT_TestOperator,
    AM_OT_ViewportColorFromNode,
    # AM_OT_ConvertClipboardColorToName,
    )

def register():
    bpy.types.Scene.mat_change_multiple = bpy.props.BoolProperty(name="Affect all slots of selection", description="Affect all material slots of all selected objects, else only active slot of active object", default=False)
    for i in classes:
        bpy.utils.register_class(i)
    bpy.types.MATERIAL_PT_viewport.append(MaterialPlus)
 
def unregister():
    bpy.types.MATERIAL_PT_viewport.remove(MaterialPlus)
    for i in classes:
        bpy.utils.unregister_class(i)
    del bpy.types.Scene.mat_change_multiple
 
 
if __name__ == "__main__":
    register()
