# Hydroponic Agriculture

A home hydroponic tower project: learn, calculate, model, test, and build.

Public repository: https://github.com/SuwajAryal/hydroponic-agriculture

The remote was created empty; project files remain local until the first end-of-day push.

Status: project scaffold. No dimensions, pump, watering interval, or flow rate has been validated. The reference video has not been reviewed frame by frame.

## Working approach

- Work locally. Commit useful milestones locally; push to a public GitHub repository only at the end of the working day when requested. No automatic push or scheduled job.
- Use Python for hydraulics, reservoir balance, operating schedules, and later geometry generation.
- Learn Blender for the 3D model and presentation. Use OpenFOAM for engineering flow analysis.
- Validate predictions against a plain-water prototype before adding plants.

## Start here

1. Read `docs/WORKFLOW.md` for milestones and acceptance checks.
2. Read `docs/TOOLS.md` for Blender, FreeCAD, Unreal, and CFD choices.
3. Read `docs/WATER_LOOP.md` for circulation and fresh-water management.
4. Replace unknowns in `configs/tower.json` with measured values.
5. Run `python -m hydroponics configs/tower.json` to inspect the current inputs. Python 3.11+; no external packages needed for this scaffold.

This first command reports inputs only. It does not calculate flow, simulate water, control a pump, or certify a design.

## Layout

- `hydroponics/`: Python entry point; future calculation modules.
- `configs/`: shared design inputs with units in field names; null means unknown.
- `docs/`: workflow, decisions, and operating concept.
- `models/blender/`: future Blender scenes and geometry scripts.
- `cfd/openfoam/`: future reproducible cases and solver notes.
- `data/measurements/`: measured data and experiment records.
- `results/`: generated results, ignored by Git.

Reference: https://www.youtube.com/watch?v=arNVaP5XNEg
