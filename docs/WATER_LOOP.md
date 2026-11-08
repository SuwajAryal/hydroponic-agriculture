# Water-loop concept

Working interpretation following the initial discussion; operating details remain to be confirmed.

## One nutrient-water recirculation loop

Reservoir -> small pump -> supply pipe -> top distributor -> planting sites -> gravity return -> same reservoir.

The pump raises water to the top. Gravity returns it; a separate motor is not needed for the return if the layout drains freely. Root-zone circulation and reservoir mixing are different functions: mixing only inside the reservoir does not water the tower.

## Fresh water and nutrients

Fresh water is needed to replenish losses from evaporation, plant uptake, sampling and any leaks or discharge. It is not required as a fresh supply on every circulation pass. At first, top up manually to a marked level, mix, and measure EC/pH before correcting nutrients for the chosen crop. EC indicates overall dissolved ions; it does not identify each nutrient or prove nutrient balance.

Do not blindly add full-strength nutrient solution at every top-up. Record additions and plan solution replacement/cleaning based on water quality, crop needs and observations.

For later automation, use reservoir-level limits, a maximum fill duration/volume, and an independent overflow path. A scheduled check can initiate a top-up decision; time alone does not establish how much water is missing. Low level should inhibit the circulation pump to avoid running dry. No hardware control is implemented in this project scaffold.

## Scheduled circulation

Whether the tower runs continuously or intermittently remains open. Roots must remain adequately moist and aerated. Off-time depends on the crop, medium, root development and environment; establish it by observation and testing rather than copying an arbitrary timer setting.

Water balance for the later Python model:

change in stored volume = fresh-water additions - plant uptake - evaporation - leaks - intentional discharge.

Recirculated flow is internal to the whole system and cancels in its overall mass balance. Startup and shutdown redistribute water between reservoir, tower and pipes, so reservoir level must also account for hold-up and drain-back.

References:
- https://extension.okstate.edu/fact-sheets/hydroponics
- https://extension.okstate.edu/fact-sheets/electrical-conductivity-and-ph-guide-for-hydroponics
- https://extension.umn.edu/garden-and-home/yard-and-garden/gardening-in-minnesota/small-scale-hydroponics
