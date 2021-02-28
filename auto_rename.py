from . import fn
import bpy
import os
from pathlib import Path


def get_material_color(mat, viewport=False):
    '''return closest color from nodes (cycle only), or viewport color'''
    if mat.is_grease_pencil:
        if mat.grease_pencil.show_fill:
            return mat.grease_pencil.fill_color[:]
        else:# if not fill get
            return mat.grease_pencil.color[:]

    if viewport:
        return mat.diffuse_color[:]
    else:
        # later, try to get closest node from output having a color, fallback on viewport color
        return fn.get_closest_node_color(mat)


def rename_mat(viewport=True, self=None, color_dic=None, context=None):
    '''If any, rename active material of active objects'''

    matlist = fn.material_selection_scope()
    if not matlist:
        fn.report('No material to rename', self=self, mode='ERROR')

    errors = []
    warnings = []

    ct = 0
    for mat in matlist:
        col = get_material_color(mat, viewport) # get rgb color
        colname = fn.get_color_name(col, color_dic) # get name
        if not colname:
            errors.append(f'Error trying to get color name from {col}')
            continue

        if colname == mat.name:  # check if already named
            warnings.append(f'Material "{mat.name}" already named')
            continue

        # check if already exist
        if bpy.data.materials.get(colname):
            warnings.append(f'"{mat.name}" -> "{colname}" but already existed')

        print(f'"{mat.name}" -> "{colname}"')
        mat.name = colname
        ct += 1

    if warnings:
        fn.report(f"Auto material {len(warnings)} warnings--\n" + '\n'.join(errors), self=self, mode='WARNING')

    if errors:
        fn.report(f"Auto material {len(errors)} errors--\n" + '\n'.join(errors), self=self, mode='ERROR')

    if not warnings and not errors:
        fn.report(f'{ct} Materials renamed', self=self)
    else:
        print(f'{ct} Materials renamed')



class AM_OT_auto_name_material(bpy.types.Operator):
    bl_idname = "materials.auto_name_material"
    bl_label = "Auto name material"
    bl_description = "rename material according to color"
    bl_options = {"REGISTER"}

    viewport: bpy.props.BoolProperty()

    def execute(self, context):
        db = Path(os.path.realpath(__file__)).parent / 'colornames.json'
        color_dic = fn.load_color_dic(db)
        rename_mat(viewport=self.viewport, self=self,
                   color_dic=color_dic, context=context)
        return {"FINISHED"}


class AM_OT_convert_clipboard_color_to_name(bpy.types.Operator):
    bl_idname = "materials.convert_clip_color_to_name"
    bl_label = "convert clipboard color to name"
    bl_description = "Convert color in paperclip to name (replace paperclip)"
    bl_options = {"REGISTER"}

    def execute(self, context):
        clip = context.window_manager.clipboard

        import re  # regex check if looks like a list/tuple/hex to ensure safety
        reclip = re.match(r'^(\(|\[)[\d., ]+(\)|\])$', clip)
        rehex = re.match(r'#?[a-zA-Z0-9]{3,6}', clip)

        if not reclip and not rehex:
            fn.report(f'Could not get color name from clipboard\nFormat exemple : [0.8, 0.8, 0.8, 1.0], (0.80, 0.80, 0.80)',
                      self=self, mode='ERROR')
            return {"CANCELLED"}

        db = Path(os.path.realpath(__file__)).parent / 'colornames.json'
        color_dic = fn.load_color_dic(db)

        if reclip:
            # try to safely eval string to get tuple/list
            try:
                import ast #  string
                clip = ast.literal_eval(clip)
            except:
                fn.report(f'Could not evaluate:\n{clip}',
                          self=self, mode='ERROR')
                return {"CANCELLED"}

        # send rgb as tuple or hex as str
        newclip = fn.get_color_name(clip, color_dic)

        if not newclip:
            fn.report('Could not get color name', self=self, mode='ERROR')
            return {"CANCELLED"}

        fn.report(newclip, self=self)
        context.window_manager.clipboard = newclip

        return {"FINISHED"}


classes = (
    AM_OT_auto_name_material,
    AM_OT_convert_clipboard_color_to_name,
)


def register():
    bpy.types.Scene.mat_change_multiple = bpy.props.BoolProperty(
        name="Affect All Slots", default=True,
        description="Affect all material slots (skip already named materials if option is active in addon prefs)\nelse only active slot", options={'HIDDEN'})

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.mat_change_multiple
