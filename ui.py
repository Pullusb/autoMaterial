import bpy

def Material_handle_Panel(self, context):
    """options for fast naming and setting materials color"""
    layout = self.layout
    # layout.use_property_split = True
    layout.label(text='Set Color:')
    
    split = layout.split(factor=0.5, align=True)
    split.operator('materials.viewport_color_from_node', text = "Viewport From Node", icon='NLA_PUSHDOWN').from_viewport = False
    split.operator('materials.viewport_color_from_node', text = "Node From Viewport", icon='TRIA_UP_BAR').from_viewport = True
 
    #layout.separator()
    split = layout.split(factor=0.25, align=False)
    split.label(text='Auto Name:')
    split.prop(context.scene, "mat_change_multiple", text='Rename All Slots')
    col = layout.column(align=True)
    row = col.row(align=True)
    row.operator('materials.auto_name_material', text = "Rename From Viewport", icon='RESTRICT_COLOR_ON').viewport = True
    row.operator('materials.auto_name_material', text = "Rename From Nodes", icon='NODETREE').viewport = False
    
    row = col.row()
    row.operator('materials.convert_clip_color_to_name', text = "Replace Clipboard Color By Name", icon='COLOR')

def GP_Material_handle_Panel(self, context):
    layout = self.layout
    layout.use_property_split = True
    # split = layout.split(factor=0.5, align=False)
    split = layout.split(factor=0.25, align=False)
    split.label(text='Auto Name:')
    split.prop(context.scene, "mat_change_multiple", text='Rename All Slots')
    layout.operator('materials.auto_name_material', text = "Rename From Color", icon='RESTRICT_COLOR_ON').viewport = True

def register():
    bpy.types.MATERIAL_PT_viewport.append(Material_handle_Panel)
    bpy.types.MATERIAL_PT_gpencil_options.append(GP_Material_handle_Panel)
 
def unregister():
    bpy.types.MATERIAL_PT_viewport.remove(Material_handle_Panel)
    bpy.types.MATERIAL_PT_gpencil_options.remove(GP_Material_handle_Panel)