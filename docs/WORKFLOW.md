# Learning and build workflow

## 0. Establish the project

- [x] Record the Python / Blender / OpenFOAM direction.
- [x] Separate recirculation from water replenishment.
- [x] Create the local Python scaffold.
- [ ] Create and connect an empty public GitHub repository.
- [ ] Publish reviewed files at the end of the working day.

## 1. Record the design basis

Sketch one tower and its reservoir, pump, supply pipe, distributor, planting pockets, and return.
Record tower height and internal diameter; pocket count, spacing and projection; high/low reservoir levels; pipe internal diameter and length; fittings; and distributor openings.
Choose the crop, location and available light. Record pump make/model and an actual flow-head curve when available.
Store measured inputs in configs/tower.json. Label every estimated value as assumed; never present an estimate as a video measurement.
Deliverable: dimensioned sketch and input table, with unresolved inputs listed.

## 2. Build the Python hydraulic model

Learn unit conversion, functions, arrays, CSV, and plotting through the actual project.
Calculate required head versus flow: static lift + Darcy-Weisbach pipe losses + fitting losses + distributor head.
Use an appropriate friction relation for the Reynolds number; flag the transition regime.
Find the pump/system-curve intersection. Repeat for minimum and maximum reservoir levels.
Check sensitivity to pipe diameter, restrictions and partial blockage.
Deliverable: system curves, pump duty point and explicit validity limits; no final pump selection without a real pump curve.

## 3. Learn Blender through the tower

Set units and dimensions, create the reservoir and tower, then make one pocket and repeat it.
Use Python to generate repeatable geometry from the shared input file.
Inspect internals with a cutaway. Keep illustrative water animation labelled separately from computed CFD results.
Before CFD export, verify actual dimensions, watertight fluid boundaries, normals, and mesh resolution.
Deliverable: dimensioned scene and exportable geometry.

## 4. Learn CFD on a small problem

First run and understand a simple air-water tutorial. Record the OpenFOAM distribution and version.
Then model the distributor and a short tower section with representative pockets.
Include gravity, air/water interfaces, surface tension and appropriate wall-wetting assumptions.
Check conservation, mesh and time-step sensitivity, and sensitivity to contact angle.
Measure wetting/capture at planting sites rather than judging an animation alone.
Deliverable: reproducible case and quantified results with uncertainty. Expand the domain only if justified.

## 5. Build a plain-water prototype

Measure delivered flow by collected volume / time and compare with the hydraulic model.
Check each pocket for consistent wetting and record comparable collection measurements where practicable.
Test leaks, splash, drainage, restart, pump shutdown/drain-back, low reservoir level, and partial obstruction.
Check the reservoir has capacity for drain-back and the return accepts full discharge.
Use measured results to revise assumptions; do not claim validation from appearance alone.

## 6. Grow and refine

Introduce a few plants, log reservoir level, EC, pH and temperature, and inspect root development.
Recheck distribution as roots obstruct or redirect water.
Choose any intermittent circulation interval from crop/root-zone observations and tests; no timer interval is prescribed yet.

## End-of-day publishing

Review changed files and confirm there are no credentials, personal records, or large generated caches.
Run the relevant checks, update the learning log, commit locally, and then push the reviewed changes.
No pushes during the session unless the user explicitly changes this rule.
