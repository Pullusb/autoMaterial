# Auto material

Blender addon - automate stuff to handle materials

**[Download latest](https://github.com/Pullusb/autoMaterial/archive/master.zip)**


<!-- ### [youtube demo]() -->

Want to support me? [Check this page](http://www.samuelbernou.fr/donate)

### Description:

**Set viewport color from nodes** (or the opposite)

![set_color](https://github.com/Pullusb/images_repo/raw/master/AM_set_vp_color_from_node_and_back.gif)

When getting from node, the node tree is reverse climbed until it found a "relevant" color input.  (result can be unexpected)  

> If it stumble upon an image texture it will sample the center pixel color of the image  


**Auto name material from closest color name**  

![auto_rename](https://github.com/Pullusb/images_repo/raw/master/AM_material_auto_renaming.png)


Applied on selected objects. There is an option to apply on all slots instead of active only

> On grease pencil material the fill color is always taken if activated  

*Only unnamed* option (in addon preferences, disabled by default) : Allow to rename only materials that have default names ('Material', 'Material.001'...)


The color name are taken from xkcd database (Licence [CC0](http://creativecommons.org/publicdomain/zero/1.0/)) listed here : https://xkcd.com/color/rgb  
Made for a [color survey by Randall Munroe](https://blog.xkcd.com/2010/05/03/color-survey-results/)

If you want to use another data base, just swap yours with colornames.json in addon folder (formated like `"name" : "hexa code"`)

e.g:

```
{   
    "cloudy blue": "#acc2d9",
    "dark pastel green": "#56ae57"
}
```

---
### Changelog

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