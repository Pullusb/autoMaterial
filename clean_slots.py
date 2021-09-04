import bpy, re
import numpy as np

# TODO option : Delete duplication if it isn't assigned at all (a bit hazardous)

attr_exclusion = [
'__doc__',
'__module__',
'__slots__',
'bl_rna',
'rna_type',
'animation_data_clear',
'animation_data_create',
'asset_clear',
'asset_mark',
'copy',
'cycles',
'diffuse_color',
'evaluated_get',
'line_color',
'lineart',
'make_local',
'name',
'name_full',
'node_tree',
'original',
'override_create',
'override_hierarchy_create',
'override_template_create',
'preview',
'preview_ensure',
'texture_paint_images',
'texture_paint_slots',
'update_tag',
'user_clear',
'user_of_id',
'user_remap',
'users',
'is_embedded_data',
'tag',
]
# animation_data

def up_node_tree(node, nlist=[]):
    '''Recursively go up a tree and return a list of each nodes'''
    for input in node.inputs:
        if input.is_linked:
            for link in input.links:
                nlist = up_node_tree(link.from_node, nlist)
    return nlist+[node]

def get_shader_output(m):
    outputs = [n for n in m.node_tree.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output]
    if not outputs:
        return
    return outputs[0]

def mats_similarity_check(a, b, check_settings=True, check_node_tree=True):
    '''Naive check for similarity between two material
    Return True if similar
    '''
    if check_settings:
        for att, b_att in zip(dir(a), dir(b)):
            if att != b_att:
                print(f'! Setting attribute list does not match ! {a.name}:{att} Vs {b.name}:{b_att}')
                return
            if att in attr_exclusion or att.startswith('__'):
                continue
            # print(a_att)
            if getattr(a, att) != getattr(b, att):
                print(f'{att}: {a.name} != {b.name}')
                return

    if check_node_tree and a.use_nodes and b.use_nodes:
        if len(a.node_tree.nodes) != len(b.node_tree.nodes):
            return
        outa = get_shader_output(a)
        outb = get_shader_output(b)
        if not outa or not outb:
            return
        ## just check output connected node_trees have same nodetypes
        for na, nb in zip(up_node_tree(outa), up_node_tree(outb)):
            if na.type != nb.type:
                # print(f'type : {na.type} != {nb.type}')
                return

            for i1, i2 in zip(na.inputs, nb.inputs):
                if i1.is_linked != i2.is_linked:
                    return
                if i1.is_linked:
                    continue
                if not hasattr(i1, 'default_value'): 
                    continue

                ## use isclose since value approximation break similarity checking
                if not np.isclose(i1.default_value, i2.default_value).all():
                    print(f'{a.name} > {na.name} > {i1.name}: {i1.default_value} != {i2.default_value} ({b.name})')
                    return 

    return True

def replace_increment_duplication(targets='ACTIVE', similar_check=False, skip_fake_user=False, force_delete=False):
    """Replace duplication (.001, .002) of a material in object slots by the original material (if any)
    :targets: Select which material slots to scan to affect in ('ACTIVE', 'SELECTED', 'ALL')
    :similar_check: replace material only if settings/node_tree are exactly similar (approximate method, dont check node values)
    :skip_fake_user: skip every material that have a fake user
    :force_delete: True remove the material from blend immediately (usefull to delete fake_user materials).
    """
    
    if targets == 'ACTIVE':
        pool = [bpy.context.object]
    elif targets == 'SELECTED':
        pool = bpy.context.selected_objects
    elif targets == 'ALL':
        pool = bpy.context.scene.objects
    else:
        pool = []
    
    matnum = 0
    todel = []
    for ob in pool:
        if not hasattr(ob, 'material_slots'):
            continue
        for i, ms in enumerate(ob.material_slots):
            mat = ms.material
            if not mat:
                continue
            
            if skip_fake_user and mat.use_fake_user:
                continue

            match = re.search(r'(.*)\.\d{3}$', mat.name)
            if not match:
                continue

            basemat = bpy.data.materials.get(match.group(1))
            if not basemat:
                continue
            
            if similar_check and not mats_similarity_check(basemat, mat):
                continue

            if mat not in todel:
                todel.append(mat)

            ms.material = basemat
            print(f'{ob.name} : slot {i} >> replaced {mat.name}')
            matnum += 1
            mat.use_fake_user = False

    if force_delete:
        for m in reversed(todel):
            bpy.data.materials.remove(m)
    
    return matnum


class AM_OT_replace_mat_duplication(bpy.types.Operator):
    bl_idname = "materials.replace_mat_duplication"
    bl_label = "Replace Material Duplication"
    bl_description = "Delete materials incremental duplications (.001 .002 ...) and replace in slot by material holding original name"
    bl_options = {"REGISTER", "UNDO"} # , "INTERNAL"

    target : bpy.props.EnumProperty(
    name="Target Objects", description="Choose objects targets to check material slots",
    default='ACTIVE',
    items=(
        ('ACTIVE', 'Active', 'Replace incremental duplication in active objects material slots', 0),
        ('SELECTED', 'Selected', 'Replace incremental duplication in selected objects material slots', 1),   
        ('ALL', 'All', 'Replace incremental duplication in all objects material slots', 2),   
        ))

    # use_remove_dup : bpy.props.BoolProperty(name="Remove Duplication", 
    #     description="All duplicated material (with suffix .001, .002 ...) will be replaced by the material with clean name (if found in scene)" ,
    #     default=True)

    skip_different_materials : bpy.props.BoolProperty(name="Skip Different Material", 
        description="Will not affect duplication if settings/node_tree is different",
        default=True)
    
    skip_fake_user : bpy.props.BoolProperty(name="Skip Fake User", 
        description="Duplication with fake user will be untouched, even if they are identical",
        default=False)
    
    force_delete : bpy.props.BoolProperty(name="Direct Delete", 
        description="Replaced duplication will be immediately deleted after being replaced\nThis is usefull to be sure duplication with fake users are not kept in the blend",
        default=False)

    # remove_empty_slots : bpy.props.BoolProperty(name="Remove Empty Slots", 
    #     description="Remove slots that haven't any material attached ", 
    #     default=True)

    @classmethod
    def poll(cls, context):
        return context.object

    def invoke(self, context, event):
        self.ob = context.object
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout

        layout.label(text='Replace incremented clones (.001 .002 ...) by original material' )
        box = layout.box()
        box.prop(self, 'target')
        box.prop(self, 'skip_different_materials')
        box.prop(self, 'skip_fake_user')
        box.prop(self, 'force_delete')

        # box.prop(self, 'use_remove_dup')
        # if self.use_remove_dup:
        #     box.prop(self, 'skip_different_materials')
        # if self.use_remove_dup:
        #     box.prop(self, 'skip_fake_user')
        # if self.use_remove_dup:
        #     box.prop(self, 'force_delete')

        # box = layout.box()
        # box.prop(self, 'remove_empty_slots')

    ## override to affect non-active objects ?
    # def delete_empty_material_slots(self, ob):
    #     for i in range(len(ob.material_slots))[::-1]:
    #         ms = ob.material_slots[i]
    #         mat = ms.material
    #         if not mat:
    #             ob.active_material_index = i
    #             bpy.ops.object.material_slot_remove()

    def execute(self, context):
        ob = context.object
        info = None

        # if not self.use_remove_dup and not self.remove_empty_slots:            
        #     self.report({'ERROR'}, 'At least one operation should be selected')
        #     return {"CANCELLED"}

        # if self.use_remove_dup:
        #     info = self.clean_mats_duplication(ob)

        # if self.remove_empty_slots:
        #     self.delete_empty_material_slots(ob)

        info = replace_increment_duplication(targets=self.target, similar_check=self.skip_different_materials, skip_fake_user=self.skip_fake_user, force_delete=self.force_delete)
        self.report({'INFO'}, f'{info} material slot replaced')
        
        # if info:
        #     self.report({info[0]}, info[1])
        # else:
        #     self.report({'WARNING'}, '')

        return {"FINISHED"}


def material_clean_menu(self, context):
    '''To append to MATERIAL_MT_context_menu'''
    layout = self.layout
    layout.operator("materials.replace_mat_duplication", text='Remove Duplications', icon='NODE_MATERIAL')

classes = (
AM_OT_replace_mat_duplication,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.MATERIAL_MT_context_menu.append(material_clean_menu)

def unregister():
    bpy.types.MATERIAL_MT_context_menu.remove(material_clean_menu)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)