# Four stackable towers, one pump

Open `four_tower_unit.blend`. **01 Four-tower unit** shows the full assembly. **02 Shared manifold** removes the deck, tower bodies and front wall so you can see the plumbing. Teal parts are the supply circuit. Amber handles identify four balancing points.

Four copies of [the stackable tower](../concept-01/README.md) sit on a common reservoir. One submersible pump feeds a central header, which splits into four branches. Each branch has an adjustment valve and goes up a tower's internal riser. Each tower drains by gravity through its deck opening into the same tank.

| Concept input | Working value |
| --- | --- |
| Towers | 4 in a square, 470 mm centre-to-centre |
| Planting sites | 12 per tower, 48 total |
| Shared reservoir | 880 × 880 mm outside. Deck at 324 mm above the base |
| Operating water levels | 100–220 mm above the base |
| Header and branch bores for the calculation | 28 mm and 14 mm respectively |
| Nominal lift at the lowest and highest water levels | 1.456 m and 1.336 m respectively, from the reservoir surface to the riser outlet |

The modeled tank holds about 152 L at the high mark before displacement by the pump and pipes. This is a footprint study; choose the actual operating volume and support together.

The header and fittings are simplified assembly geometry. The valve handles mark intended functions, and the hatch shows a proposed service point. Confirm access to each valve and pump, support for the four towers, canopy clearance, usable tank volume and drain-back allowance before building.

## First hydraulic calculation

Start with the total flow as the sum of four target tower flows. For four equal targets, total flow is four times the flow per tower. Calculate head loss in the common supply at total flow and in each branch at its own flow. Use the highest required path head at the low water level to check a candidate pump curve. The four lifts are parallel, so use the lift to one tower. Confirm branch balance and pocket wetting in a plain-water test. No pump has been selected.

## Rebuild in Blender

```powershell
blender --background --threads 8 --python-exit-code 1 --python build_unit.py
```

Run from this directory. The script reuses the saved Option A geometry, so the deck top must match that model's 324 mm tower base. See `unit_dimensions.json` for the layout inputs. Export a separately checked fluid volume before using the geometry for CFD.

## Credits

The stackable tower carries the [credits from the single-tower concept](../concept-01/README.md). [Chris Loh's four-tower build](https://clohofficial.com/diy-hydroponics-aeroponics-garden-tower-build-part-2-4-tower-build/) is a reference for scaling to multiple towers. The common tank, deck, and manifold here are new concept geometry.
