## Changelog

0.3.0

- feat: material cleaner's _similarity check_ is more robust, also check nodes values
- feat: add Gpencil material cleaner in materials submenu (copy of `gp toolbox`'s operator)
    - don't register if gp toolbox addon is active to avoid duplicate

0.2.0

- feat: material incremental clone (duplication) remover
- fix: bad register in Blender 2.93.0

0.1.1

- code: fix bl_infos and typos

0.1.0

- feat: new auto-renaming system based on xkcd color
- feat: better color source check (if tex_image type found, sample center pixel)
- feat: Also works on grease pencil materials
- feat: added addon prefs option to rename only non-named material
- fix:  littles bugs
- code: big refactor

0.0.5

- port from 2.79. Only color transfer options