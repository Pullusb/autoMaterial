import bpy

def report(*args, self=None, mode='INFO'):
    #mode in 'INFO' (default), 'WARNING', 'ERROR'
    text = ' '.join([str(a) for a in args])
    if self:
        self.report({mode}, text)
    else:
        print(text)

def get_addon_prefs():
    import os 
    addon_name = os.path.splitext(__name__)[0]
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[addon_name].preferences
    return (addon_prefs)

### --- Object Color <-> Material Color 

#-# seem like it's needed to be passed to linear in blender for correct result
#-# https://blender.stackexchange.com/questions/158896/how-set-hex-in-rgb-node-python/158902

def srgb_to_linearrgb(c):
    if   c < 0:       return 0
    elif c < 0.04045: return c/12.92
    else:             return ((c+0.055)/1.055)**2.4

def hex_to_rgb(h):
    '''Convert a hexadecimal color value to a 3-tuple of integers
    suitable for use in an ``rgb()`` triplet specifying that color.
    '''

    h=int(h[1:], 16)
    r = (h & 0xff0000) >> 16
    g = (h & 0x00ff00) >> 8
    b = (h & 0x0000ff)
    return tuple([srgb_to_linearrgb(c/0xff) for c in (r,g,b)])


def get_color_name(rgb, color_dict):
    '''Get a rgb[a] (tuple/list) or an hex (str)
    return nearest color name found in passed color database
    '''
    if isinstance(rgb, str): # must be an hexa code
        rgb = rgb if rgb.clip.startswith('#') else '#'+rgb
        rgb = hex_to_rgb(rgb)

    min_colours = {}
    for name, hex in color_dict.items():
        r_c, g_c, b_c = hex_to_rgb(hex)#.strip('#')
        rd = (r_c - rgb[0]) ** 2
        gd = (g_c - rgb[1]) ** 2
        bd = (b_c - rgb[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    closest_name = min_colours[min(min_colours.keys())]

    return closest_name

def load_color_dic(fp):
    import json
    from pathlib import Path
    color_dict = None
    color_db = Path(fp)
    with color_db.open() as fd:
        color_dict = json.load(fd)
    return color_dict



### --- Object Color <-> Material Color 


def get_single_pixel_color_from_image(img):
    '''
    :img: A blender type image
    Sample color of center pixel
    '''

    # do a mean of every color (not so usefull...) ?
    if img.type != 'IMAGE':
        print (f'{img.name}, not an image type >> {img.type}')
        return

    pix_num = len(img.pixels)
    width = img.size[0]
    height = img.size[1]
    
    target = [width//2, height//2] #sample middle pixel
    # target = [0,0] # sample first pixel

    index = ( target[1] * width + target[0] ) * img.channels
    print('index: ', index)
    
    rgb = (img.pixels[index],
    img.pixels[index + 1],
    img.pixels[index + 2], 1.0)
    
    print(rgb)
    return rgb


color_node_exclude =  ('MIX_RGB', 'TEX_GRADIENT', 'BRIGHTCONTRAST', 'CURVE_RGB', 'VALTORGB')


def find_color_up_tree(node):
    '''Recursive find color in node_tree'''
    # print(node.type)#Dbg

    # Ouputs
    if node.outputs.get('Color') and node.type not in color_node_exclude:
        # if has an out (rgb nodes or ramp, etc, take this first)
        if node.type == 'TEX_IMAGE' and node.image and node.image.type == 'IMAGE':
            # if is a texture, sample center pixel color and return
            return get_single_pixel_color_from_image(node.image)
        return node.outputs['Color'].default_value[:]

    # Inputs (Try to get colors)
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
 
    # else search for a color source in links of all other socket
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

"""# old selection scope
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
"""

def material_selection_scope():
    '''Return a list of all material to change'''
    scene = bpy.context.scene
    
    prefs = get_addon_prefs()
    matlist=[]

    # On active and selected objects
    active = bpy.context.object
    pool = [o for o in bpy.context.selected_objects]
    if active and active not in pool:
        pool = [active] + pool

    for ob in pool:
        if scene.mat_change_multiple:
            for slot in ob.material_slots:
                mat = slot.material
                if mat and mat not in matlist:
                    # filter to only affect unnamed material
                    if prefs.only_unnamed and not mat.name.startswith('Material'):
                        continue
                    matlist.append(mat)
        else:
            mat = ob.active_material
            if mat and mat not in matlist:
                matlist.append(mat)

    return matlist


def match_color_viewport_from_node(variables={}):
    self = variables.get('self')
    for mat in material_selection_scope():
        color = get_closest_node_color(mat)

        if color:
            # print("color", color)#Dbg
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
            # print("color", color)#Dbg
            node = set_closest_node_color(mat,color)
            if not node:
                report('cant find a node to set color in the node tree... (this try only with the first node connected to "Surface")', self=self, mode='ERROR')
                continue
            report('color changed in node', node.name, self=self)
            #return True