# Hydroponic tower concept 01

A metric Blender study of one home tower. Open `tower_concept.blend` and use the scene menu to switch between **01 Complete tower** and **02 Cutaway**. The cutaway removes the front of the shell and some pockets to reveal the internals. The two blue marks inside the reservoir show the assumed water levels measured from the outside bottom.

| Part | Working dimensions |
| --- | --- |
| Tower | Four 300 mm sections, 1,200 mm body height, 150 mm bore, 158 mm outside diameter |
| Planting pockets | 12 total, three per section, alternating 60° rotation between sections |
| Reservoir | 310 mm base, 350 mm rim, 320 mm rim height |
| Reservoir operating levels | 100 and 220 mm above the outside bottom, before allowing for pump and pipe displacement |
| Supply | 14 mm bore, 18 mm outside diameter. Pump represented by a placeholder. |
| Distributor | Eight 4 mm holes at 51 mm pitch radius. Hole sizes and wetting still need testing. |

The assumed riser outlet is 1.556 m above the reservoir base. This gives a nominal static lift of 1.336 m at the high level and 1.456 m at the low level. Use the outlet height as the discharge datum for the first supply calculation, then account for pipe, fitting and outlet losses separately. The distributor feeds the inside of the tower. The tower is open at the base to let water return through the lid into the same reservoir.

These are design assumptions, not measurements from the video. This is an assembly study with simplified parts and separate overlapping interfaces. Before CFD, build and check a dedicated fluid volume. Before fabrication, measure the real parts and check joint fit, reservoir capacity and drain-back, pump duty, distributor wetting, and stability.

## References and credits

| Reference | How it informed the model |
| --- | --- |
| [Chris Loh, DIY Hydroponics Garden Tower Build](https://www.youtube.com/watch?v=arNVaP5XNEg) | Original project reference for the single vertical tower. The video is linked as a reference. |
| [MootSeeker, HydroponicTower](https://github.com/MootSeeker/HydroponicTower), [MIT license](https://github.com/MootSeeker/HydroponicTower/blob/main/LICENSE) | Stackable sections and removable net pots. |
| [László Dániel, ModularHydroponicTowerGarden](https://github.com/laszlodaniel/ModularHydroponicTowerGarden), [GPL-3.0 source](https://github.com/laszlodaniel/ModularHydroponicTowerGarden/blob/master/LICENSE) | Modular assembly and a pump feeding the top of the tower. |
| [Hardeep Singh and Bruce Dunn, Oklahoma State University Extension](https://extension.okstate.edu/fact-sheets/building-a-vertical-hydroponic-tower) | Staggered pockets, top distribution and the gravity return through the lid. |

The model and generator are original geometry and code. No upstream mesh, STL, image, video, or controller code is included.

## Change the model

Edit `concept_dimensions.json` for a new concept, then run the generator from Blender 4.2 or later:

```powershell
blender --background --python-exit-code 1 --python build_tower.py
```

Run this from the model directory. It rewrites the Blender file and both preview images. Save hand edits under a different filename first. The shared project configuration still records measured design inputs separately.

Compare this with [Option B](../concept-02/README.md) in the [side-by-side renders](../concept-02/tower_options.png).
