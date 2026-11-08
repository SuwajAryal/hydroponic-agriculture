# Tool decisions

## Recommended starting combination: Python + Blender + OpenFOAM

Python is the source of hydraulic calculations and shared design inputs. Start with the standard library; add numerical and plotting packages when the first calculation needs them.

Blender is the recommended choice between Blender and Unreal for this project: it lets us learn geometry, repeated objects, scripting, cutaways, and animation in the same tool. Its Python API fits the project direction. Blender fluid animation must not be treated as a validated prediction of thin-film wetting, flow distribution or pump performance.

Unreal is worth considering later if an interactive walkthrough, live dashboard or immersive scene becomes a separate goal. It adds a second environment without resolving the current hydraulic questions. Its Water system is oriented toward rendered water and gameplay interaction.

FreeCAD is optional. Its justification is constraint-driven dimensions, editable mechanical features and CAD-oriented fabrication output. Add it if we need accurately fitted parts or workshop drawings that become cumbersome in Blender. We do not need to learn all three tools now. Any CAD-to-CFD handoff still requires geometry and unit checks.

## CFD choices

OpenFOAM is the preferred starting engineering solver: use an appropriate transient air-water VOF formulation, with surface tension and wetting conditions where relevant. Start with a tutorial, then a local distributor/pocket case. Solver names and case syntax depend on the selected distribution/version.

DualSPHysics is a free alternative to investigate for free-surface jets, splashing and large deformation. Its particle resolution and supported physics must be checked carefully for thin films and wall wetting; it is not automatically a simpler replacement for this tower.

FLOW-3D remains an option if a suitable licence becomes available; no purchase is needed for the present workflow.

No solver removes the need to measure flow and root-zone wetting on the prototype. Empty-tower results do not establish performance with mature roots.

## Official references

- Blender modelling and scripting: https://www.blender.org/features/modeling/
- Blender Python introduction: https://docs.blender.org/manual/en/latest/advanced/scripting/introduction.html
- FreeCAD features: https://www.freecad.org/features.php?lang=us
- Unreal Water system: https://dev.epicgames.com/documentation/unreal-engine/water-system-in-unreal-engine
- OpenFOAM air-water tutorial: https://www.openfoam.com/documentation/tutorial-guide/4-multiphase-flow/4.1-breaking-of-a-dam
- DualSPHysics: https://dual.sphysics.org/features/
- DualSPHysics downloads/licensing: https://dual.sphysics.org/downloads/
