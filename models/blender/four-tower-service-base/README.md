# Four-tower service base

Open `four_tower_service_base.blend`. **01 Four towers with service base** shows the assembled unit. **02 Top loop close-up** retains the existing top piping. **03 Base and gravity returns** removes the deck and tank lid/front wall to show how the base works.

The deck and towers sit on a separate support frame. The opaque reservoir sits in a floor-supported guide tray and can slide out through the front. The supply line has a disconnect between the tank and rear riser. There is a separate top-up cap, and the deck's centre hatch gives access to the two open return collectors.

Four short funnels catch the water below the tower openings. The two collectors each drain a pair of towers, falling about 15 mm from either end toward the middle. Their spouts end 8 mm above the reservoir lid openings in this layout. With the reservoir removed, release the collector cradles and lower the collectors for removal through the front. Before removing the reservoir, stop the pump, allow the system to drain back, disconnect the pump line and power lead, and drain enough water for handling.

| Concept assumption | Working value |
| --- | --- |
| Tower spacing and deck height | 470 mm centres, deck top 324 mm above floor, as before |
| Tank outside dimensions | 580 × 460 × 200 mm |
| Low and high operating marks | About 21 and 35 L before pump displacement |
| Available volume above the high mark | About 13 L to the tank rim, before displacement |
| Collector outlets | Two 44 mm concept bores, with open channels upstream |
| Nominal static lift from the new low mark to a tower outlet | 1.446 m, using the unchanged 1.556 m outlet elevation |

The former concept held about 152 L at its high mark. A smaller tank is easier to access and reduces the water stored in the unit. It does not change the four towers' flow requirement. Test the actual shutdown drain-back against the available freeboard, check pump minimum submergence and monitor solution temperature and level before settling on a tank. Check the return capacity with all four towers flowing and with partial root blockage. The frame and deck are geometric placeholders and still need support and stability checks.

## Rebuild in Blender

```powershell
blender --background --threads 8 --python-exit-code 1 --python build_service_base.py
```

Run from this directory. The script starts with the [top-loop assembly](../four-tower-top-loop/README.md) and keeps its tower and upper pipe geometry. For the gravity return and accessible reservoir design, see [Oklahoma State University Extension's vertical tower guide](https://extension.okstate.edu/fact-sheets/building-a-vertical-hydroponic-tower). The frame, reservoir and collectors in this revision are original concept geometry.
