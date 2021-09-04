import bpy
import addon_utils

class AMT_OT_clean_gp_material_stack(bpy.types.Operator):
    bl_idname = "materials.clean_gp_material_stack"
    bl_label = "Clean GPencil Material Stack"
    bl_description = "Clean materials duplication in active GP object stack"
    bl_options = {"REGISTER", "UNDO"}

    use_clean_mats : bpy.props.BoolProperty(name="Remove Duplication", 
        description="All duplicated material (with suffix .001, .002 ...) will be replaced by the material with clean name (if found in scene)" ,
        default=True)

    skip_different_materials : bpy.props.BoolProperty(name="Skip Different Material", 
        description="Will not touch duplication if color settings are different (and show infos about skipped materials)",
        default=True)

    use_fuses_mats : bpy.props.BoolProperty(name="Fuse Materials Slots", 
        description="Fuse materials slots when multiple uses same materials",
        default=True)
    
    remove_empty_slots : bpy.props.BoolProperty(name="Remove Empty Slots", 
        description="Remove slots that haven't any material attached ", 
        default=True)

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'GPENCIL'

    def invoke(self, context, event):
        self.ob = context.object
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        box.prop(self, 'use_clean_mats')
        if self.use_clean_mats:
            box.prop(self, 'skip_different_materials')

        box = layout.box()
        box.prop(self, 'use_fuses_mats')
        box = layout.box()
        box.prop(self, 'remove_empty_slots')
        

    def different_gp_mat(self, mata, matb):
        a = mata.grease_pencil
        b = matb.grease_pencil
        if a.color[:] != b.color[:]:
            return f'! {self.ob.name}: {mata.name} and {matb.name} stroke color is different'
        if a.fill_color[:] != b.fill_color[:]:
            return f'! {self.ob.name}: {mata.name} and {matb.name} fill_color color is different'
        if a.show_stroke != b.show_stroke:
            return f'! {self.ob.name}: {mata.name} and {matb.name} stroke has different state'
        if a.show_fill != b.show_fill:
            return f'! {self.ob.name}: {mata.name} and {matb.name} fill has different state'

    ## Clean dups
    def clean_mats_duplication(self, ob):
        import re
        diff_ct = 0
        todel = []
        if ob.type != 'GPENCIL':
            return
        if not hasattr(ob, 'material_slots'):
            return
        for i, ms in enumerate(ob.material_slots):
            mat = ms.material
            if not mat:
                continue
            match = re.search(r'(.*)\.\d{3}$', mat.name)
            if not match:
                continue
            basemat = bpy.data.materials.get(match.group(1))
            if not basemat:
                continue
            diff = self.different_gp_mat(mat, basemat)
            if diff:
                print(diff)
                diff_ct += 1
                if self.skip_different_materials:
                    continue

            if mat not in todel:
                todel.append(mat)
            ms.material = basemat
            print(f'{ob.name} : slot {i} >> replaced {mat.name}')
            mat.use_fake_user = False

        if diff_ct:
            return('INFO', f'{diff_ct} mat skipped >> same name but different color settings!')

    ## fuse
    def fuse_object_mats(self, ob):
        for i in range(len(ob.material_slots))[::-1]:
            ms = ob.material_slots[i]
            mat = ms.material
            
            # update mat list
            mlist = [ms.material for ms in ob.material_slots if ms.material]
            if mlist.count(mat) > 1:
                # get first material in list
                new_mat_id = mlist.index(mat)
                
                # iterate in all strokes and replace with new_mat_id
                for l in ob.data.layers:
                    for f in l.frames:
                        for s in f.strokes:
                            if s.material_index == i:
                                s.material_index = new_mat_id

                # delete slot (or add to the remove_slot list
                ob.active_material_index = i
                bpy.ops.object.material_slot_remove()

    def delete_empty_material_slots(self, ob):
        for i in range(len(ob.material_slots))[::-1]:
            ms = ob.material_slots[i]
            mat = ms.material
            if not mat:
                ob.active_material_index = i
                bpy.ops.object.material_slot_remove()

    def execute(self, context):
        ob = context.object
        info = None

        if not self.use_clean_mats and not self.use_fuses_mats and not self.remove_empty_slots:            
            self.report({'ERROR'}, 'At least one operation should be selected')
            return {"CANCELLED"}

        if self.use_clean_mats:
            info = self.clean_mats_duplication(ob)
        if self.use_fuses_mats:
            self.fuse_object_mats(ob)
        if self.remove_empty_slots:
            self.delete_empty_material_slots(ob)
        
        if info:
            self.report({info[0]}, info[1])

        return {"FINISHED"}


def material_gp_clean_menu(self, context):
    '''To append to GPENCIL_MT_material_context_menu'''
    layout = self.layout
    layout.operator("materials.clean_gp_material_stack", text='Clean Material Slots', icon='NODE_MATERIAL')

# avoid unregister error if Gp toolbox was unregistered before
registered = True

def register():
    global registered
    # Don't register if gp toolbox is loaded (same ops)
    if not any(addon_utils.check('gp_toolbox')):
        bpy.utils.register_class(AMT_OT_clean_gp_material_stack)
        bpy.types.GPENCIL_MT_material_context_menu.append(material_gp_clean_menu)
    else:
        registered = False

def unregister():
    if not registered:
        return
    if not any(addon_utils.check('gp_toolbox')):
        bpy.types.GPENCIL_MT_material_context_menu.remove(material_gp_clean_menu)
        bpy.utils.unregister_class(AMT_OT_clean_gp_material_stack)