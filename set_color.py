from . import fn
import bpy
 
class AM_OT_viewport_color_from_node(bpy.types.Operator):
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
            fn.match_color_node_from_viewport(variables={'self':self, 'context':context})
        else:
            fn.match_color_viewport_from_node(variables={'self':self, 'context':context})
        return {"FINISHED"}

def register():
    bpy.utils.register_class(AM_OT_viewport_color_from_node)
 
def unregister():
    bpy.utils.unregister_class(AM_OT_viewport_color_from_node)

