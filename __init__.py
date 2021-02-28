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
    "name": "Auto material",
    "description": "Some materials handling tools",
    "author": "Samuel Bernou",
    "version": (0, 1, 0),
    "blender": (2, 91, 0),
    "location": "Properties > Material > Settings",
    "warning": "",
    "wiki_url": "https://github.com/Pullusb/autoMat",
    "tracker_url": "https://github.com/Pullusb/autoMat/issues",
    "category": "Material"}

from . import set_color
from . import auto_rename
from . import ui

import bpy
class AM_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__.split('.')[0] # or with: os.path.splitext(__name__)[0]

    only_unnamed: bpy.props.BoolProperty(
        name='Rename only unnamed materials (when using multiple renaming)',
        description="In 'Rename all slots' mode, rename only unnamed materials (starting with 'Material')",
        default=False)

    def draw(self, context):
            layout = self.layout
            # layout.use_property_split = True
            # flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
            # layout = flow.column()
            layout.label(text='Renaming options:')
            layout.prop(self, "only_unnamed")


def register():
    bpy.utils.register_class(AM_preferences)
    
    auto_rename.register()
    set_color.register()
    ui.register()

def unregister():
    ui.unregister()
    auto_rename.unregister()
    set_color.unregister()

    bpy.utils.unregister_class(AM_preferences)
 
if __name__ == "__main__":
    register()
