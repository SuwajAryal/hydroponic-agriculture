"""Build a four-tower assembly from the local stackable Blender concept."""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
source = Path(args[0]).resolve() if args else ROOT.parent / "concept-01" / "tower_concept.blend"
spec = json.loads((ROOT / "unit_dimensions.json").read_text(encoding="utf-8"))
tank = spec["reservoir"]
feed = spec["feed"]
spacing = spec["tower_spacing_m"]
centers = [(-spacing/2, -spacing/2), (spacing/2, -spacing/2),
           (-spacing/2, spacing/2), (spacing/2, spacing/2)]
deck = tank["deck_top_m"]
manifold = feed["manifold_centerline_m"]
tower_ids = ("T1", "T2", "T3", "T4")

bpy.ops.wm.open_mainfile(filepath=str(source))
template = bpy.data.scenes["01 Complete tower"]
old_scenes = list(bpy.data.scenes)
groups = {group.name: list(group.objects) for group in template.collection.children}
base_feed = next(obj for obj in groups["04 Pump and riser"] if obj.name.startswith("Riser"))
riser_mesh = base_feed.data.copy()
for vertex in riser_mesh.vertices:
    if vertex.co.z < manifold:
        vertex.co.z = manifold


def mat(name, rgb):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*rgb, 1)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = material.diffuse_color
    bsdf.inputs["Roughness"].default_value = 0.38
    return material


green = mat("Shared reservoir | forest", (0.062, 0.17, 0.125))
sage = mat("Deck and inspection hatch | sage", (0.28, 0.45, 0.33))
teal = mat("Pressurized feed | teal", (0.012, 0.43, 0.44))
orange = mat("Branch balancing handles | amber", (0.81, 0.27, 0.045))
charcoal = mat("Pump envelope | charcoal", (0.065, 0.085, 0.090))
ground = mat("Studio | pale neutral", (0.78, 0.81, 0.75))
waterline = mat("Reservoir levels | blue", (0.05, 0.32, 0.63))


def group(scene, name):
    collection = bpy.data.collections.new(name)
    scene.collection.children.link(collection)
    return collection


def put(obj, collection, name, material=None):
    obj.name = name
    for previous in list(obj.users_collection):
        previous.objects.unlink(obj)
    collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj


def box(collection, name, center, dimensions, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    put(obj, collection, name, material)
    if bevel:
        mod = obj.modifiers.new("Soft edge", "BEVEL")
        mod.width = bevel
        mod.segments = 3
    return obj


def cylinder(collection, name, a, b, radius, material=None, sides=48):
    a, b = Vector(a), Vector(b)
    direction = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides, radius=radius,
                                      depth=direction.length, location=(a + b) / 2)
    obj = bpy.context.object
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return put(obj, collection, name, material)


def bore(obj, cutter):
    mod = obj.modifiers.new("Bore", "BOOLEAN")
    mod.operation, mod.solver, mod.object = "DIFFERENCE", "EXACT", cutter
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def tank_parts(scene, exposed):
    parts = group(scene, "01 Shared reservoir and deck")
    length, width = tank["outside_x_m"], tank["outside_y_m"]
    wall, floor = tank["wall_m"], tank["floor_m"]
    h = tank["rim_height_m"]
    box(parts, "Reservoir floor", (0, 0, floor/2), (length, width, floor), green, 0.003)
    for side in (-1, 1):
        box(parts, f"Reservoir side {side}", (side*(length-wall)/2, 0, (h+floor)/2),
            (wall, width, h-floor), green, 0.003)
        if side == 1 or not exposed:
            box(parts, f"Reservoir end {side}", (0, side*(width-wall)/2, (h+floor)/2),
                (length-2*wall, wall, h-floor), green, 0.003)
    if exposed:
        for z, label in ((tank["low_water_m"], "Low"), (tank["high_water_m"], "High")):
            box(parts, label + " reservoir level marker", (0, width/2-wall-0.001, z),
                (length-2*wall, 0.002, 0.003), waterline)
        return
    thickness = deck - h
    top = box(parts, "Common deck | four gravity returns", (0, 0, h+thickness/2),
              (length+0.016, width+0.016, thickness), sage)
    for tower, (x, y) in zip(tower_ids, centers):
        tool = cylinder(parts, "Temporary return opening " + tower,
                        (x, y, h-0.005), (x, y, deck+0.005), spec["return_opening_diameter_m"]/2,
                        sides=96)
        bore(top, tool)
    hatch_width, hatch_depth = 0.67, 0.27
    tool = box(parts, "Temporary service opening", (0, 0, h+thickness/2),
               (hatch_width, hatch_depth, thickness + 0.010), sage)
    bore(top, tool)
    box(parts, "Removable service hatch", (0, 0, deck+0.004),
        (hatch_width + 0.020, hatch_depth + 0.020, 0.008), green, 0.003)


def plumbing(scene, exposed):
    common = group(scene, "02 Pump and common header")
    shared_outer = feed["header_outside_diameter_m"] / 2
    branch_outer = feed["branch_outside_diameter_m"] / 2
    pump_top = feed["pump_envelope_top_m"]
    box(common, "P1 | shared pump envelope", (0, 0, (pump_top+0.018)/2),
        (0.104, 0.088, pump_top-0.018), charcoal, 0.007)
    cylinder(common, "P1 discharge", (0, 0, pump_top), (0, 0, manifold), shared_outer, teal)
    left, right = -spacing/2, spacing/2
    cylinder(common, "Common header", (left, 0, manifold), (right, 0, manifold), shared_outer, teal)
    for x in (left, right):
        cylinder(common, f"Split tee at x={x:g}", (x, -0.026, manifold), (x, 0.026, manifold),
                 shared_outer + 0.004, teal)
    for tower, (x, y) in zip(tower_ids, centers):
        branch = group(scene, f"03 Branch {tower}")
        cylinder(branch, f"{tower} feed branch", (x, 0, manifold), (x, y, manifold), branch_outer, teal)
        end = deck + 0.045 if exposed else manifold + 0.024
        cylinder(branch, f"{tower} riser connection", (x, y, manifold), (x, y, end), branch_outer, teal)
        valve_y = y * 0.50
        cylinder(branch, f"{tower} balancing valve body", (x, valve_y-0.020, manifold),
                 (x, valve_y+0.020, manifold), 0.017, teal)
        box(branch, f"{tower} valve handle", (x, valve_y, manifold+0.022),
            (0.061, 0.016, 0.010), orange, 0.003)


def tower_copies(scene):
    included = ("02 Tower sections", "03 Planting pockets", "05 Top distributor")
    for tower, (x, y) in zip(tower_ids, centers):
        parts = group(scene, f"04 Tower {tower} | stackable")
        for name in included:
            for original in groups[name]:
                obj = original.copy()
                obj.name = f"{tower} / {original.name}"
                obj.location += Vector((x, y, 0))
                parts.objects.link(obj)
        riser = bpy.data.objects.new(f"{tower} / internal riser", riser_mesh)
        riser.location = (x, y, 0)
        parts.objects.link(riser)


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def presentation(scene, exposed):
    studio = group(scene, "05 Render studio")
    box(studio, "Studio floor", (0, 0, -0.021), (200, 200, 0.04), ground)
    camera = bpy.data.objects.new("Isometric camera", bpy.data.cameras.new("Isometric camera"))
    studio.objects.link(camera)
    target = (0, 0, 0.15 if exposed else 0.78)
    camera.location = (1.6, -2.5, 2.3) if exposed else (4.4, -6.5, 3.5)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 1.52 if exposed else 2.35
    aim(camera, target)
    scene.camera = camera
    for name, pos, power, size in (
        ("Key", (2, -2, 3), 290, 2.8),
        ("Fill", (-2, -0.5, 1.8), 180, 2.5),
        ("Rim", (0.5, 2, 2.4), 260, 2.0),
    ):
        light = bpy.data.lights.new(name, "AREA")
        light.energy, light.shape, light.size = power, "DISK", size
        obj = bpy.data.objects.new(name, light)
        studio.objects.link(obj)
        obj.location = pos
        aim(obj, target)
    scene.world = template.world
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = (1060, 760) if exposed else (1060, 960)
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    studio.hide_viewport = True


def make_scene(name, exposed=False):
    scene = bpy.data.scenes.new(name)
    bpy.context.window.scene = scene
    scene.unit_settings.system = "METRIC"
    scene["Design status"] = "Concept geometry. Pump and pipe sizes are placeholders."
    scene["Tower count"] = 4
    scene["Planting sites"] = 48
    scene["Pumps"] = 1
    tank_parts(scene, exposed)
    plumbing(scene, exposed)
    if not exposed:
        tower_copies(scene)
    presentation(scene, exposed)
    bpy.ops.object.select_all(action="DESELECT")
    return scene


full = make_scene("01 Four-tower unit")
detail = make_scene("02 Shared manifold", exposed=True)
bpy.context.window.scene = full
for scene in old_scenes:
    bpy.data.scenes.remove(scene)
bpy.data.orphans_purge(do_recursive=True)
notes = bpy.data.texts.new("Four-tower notes and credits")
notes.write((ROOT / "README.md").read_text(encoding="utf-8"))
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "VIEW_3D":
            view = area.spaces.active
            view.region_3d.view_location = (0, 0, 0.78)
            view.region_3d.view_distance = 3.0
            view.region_3d.view_rotation = full.camera.rotation_euler.to_quaternion()
            view.region_3d.view_perspective = "ORTHO"
            view.shading.color_type = "MATERIAL"
            view.overlay.show_floor = False
            view.overlay.show_axis_x = view.overlay.show_axis_y = False

bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "four_tower_unit.blend"))
for scene, filename in ((full, "four_tower_unit.png"), (detail, "shared_manifold.png")):
    bpy.context.window.scene = scene
    scene.render.filepath = str(ROOT / filename)
    bpy.ops.render.render(write_still=True)
