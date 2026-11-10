# Option B: One-piece tower with an external feed

This is a second Blender concept for the same 1.2 m tower body, 150 mm bore, 12 planting pockets, and reservoir. Keeping these dimensions fixed makes it easier to compare the shell and feed layout.

The teal pipe goes from the pump through the reservoir lid, rises alongside the tower and enters the top distributor through its cover. The water returns through the open tower as in Option A. The tower wall is a continuous tube with separate sockets. The external pipe leaves the center free for cleaning and root inspection. It needs support and adds length and bends, which belong in the pump calculation.

| | Option A | Option B |
| --- | --- | --- |
| Tower shell | Four stackable sections | One continuous tube |
| Supply | Straight pipe inside | Accessible pipe outside with a top return bend |
| Outlet elevation | 1.556 m above the base | Same outlet elevation. Pipe crest is 1.610 m, so also check priming on startup. |
| Likely trade-off | Easier to change height and take apart. More shell joints. | Fewer shell joints and easier access to supply. Longer pipe, more bends and external supports. |

Both concepts have assumed dimensions and the same untested distributor. The render shows layout only. Pipe supports, seals and joints still need detailing. For a fair comparison, calculate the pump duty for both routes at the same flows, then test wetting with plain water.

## Open and regenerate

Open `tower_concept.blend`. Use the scene menu to switch between **01 Complete tower** and **02 Cutaway**. To regenerate B from the same script as A, run this from the Option B folder:

```powershell
blender --background --python-exit-code 1 --python ../concept-01/build_tower.py -- concept_dimensions.json
```

The same references and credits apply as for [Option A](../concept-01/README.md). This variant reuses the original project geometry and introduces its own continuous shell and external pipe.
