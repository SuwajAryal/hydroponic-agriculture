# Four towers with a top recirculation loop

Open `four_tower_top_loop.blend`. **01 Four-tower top loop** shows the whole unit and **02 Top loop close-up** shows the four connections from above.

One pump lifts nutrient solution through a rear riser into a closed square supply header. The header connects all four tower tops, with one balancing valve and one downward feed into each distributor. Water falls inside each tower and drains by gravity back to the shared reservoir. The bottom manifold and four internal supply risers from the earlier concept are replaced by the top loop.

| Concept assumption | Value |
| --- | --- |
| Towers and pockets | Four 1.2 m stackable bodies, 12 pockets per tower |
| Tower centres | 470 mm apart |
| Top header centreline | 1.690 m above tank base |
| Riser outlet in each distributor | 1.556 m above tank base |
| Nominal static lift to each outlet | 1.336–1.456 m at the high and low water levels |
| Nominal lift to the top loop centreline at low water | 1.590 m. Startup must also allow for losses and trapped air. |

The top pipe connects the water supply. A frame or other supports still need to carry the pipe and secure the towers. In the hydraulic model, treat the top header as a looped network. Flow can reach a tower from either direction, and equal flows still need checking at the four drops. For pump selection, use the sum of the tower flows and account for losses through the riser, header, valves and outlets. Run a water test for priming, balance and drain-back. The visible fittings are simplified and have no assigned loss coefficients yet.

## Rebuild

Run from this directory with Blender 4.2 or later:

```powershell
blender --background --threads 8 --python-exit-code 1 --python build_top_loop.py
```

This starts from the [previous four-tower assembly](../four-tower-unit/README.md), which retains the source credits. The square loop, single riser, and top entry into the distributors are new concept geometry.
