"""Add a top supply loop to the four-tower Blender assembly."""
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
source = Path(args[0]).resolve() if args else ROOT.parent / "four-tower-unit" / "four_tower_unit.blend"
spec = json.loads((ROOT / "top_loop_dimensions.json").read_text(encoding="utf-8"))
offset = spec["tower_spacing_m"] / 2
header_z = spec["top_header_centerline_m"]
outlet_z = spec["tower_outlet_m"]
riser_y = spec["riser_y_m"]
header_r = spec["header_outside_diameter_m"] / 2
drop_r = spec["drop_outside_diameter_m"] / 2
corners = [(-offset, -offset), (offset, -offset), (offset, offset), (-offset, offset)]
towers = [("T1", corners[0]), ("T2", corners[1]), ("T3", corners[3]), ("T4", corners[2])]

bpy.ops.wm.open_mainfile(filepath=str(source))
full = bpy.data.scenes["01 Four-tower unit"]
bpy.context.window.scene = full
bpy.data.scenes.remove(bpy.data.scenes["02 Shared manifold"])
full.name = "01 Four-tower top loop"
teal = bpy.data.materials["Pressurized feed | teal"]
amber = bpy.data.materials["Branch balancing handles | amber"]
sage = bpy.data.materials["Sage | collars and plate"]


def group(scene, name):
    collection = bpy.data.collections.new(name)
    scene.collection.children.link(collection)
    return collection


def put(obj, collection, name, material=None):
    obj.name = name
    for previous in list(obj.users_collection):
        previous.objects.unlink(obj)
    collection.objects.link(obj)
    if material is not None:
        obj.data.materials.append(material)
    return obj


def cylinder(collection, name, a, b, radius, material=None, sides=48):
    a, b = Vector(a), Vector(b)
    direction = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides, radius=radius,
                                      depth=direction.length, location=(a + b) / 2)
    obj = bpy.context.object
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return put(obj, collection, name, material)


def fitting(collection, name, pos, radius):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=radius, location=pos)
    obj = put(bpy.context.object, collection, name, teal)
    for poly in obj.data.polygons:
        poly.use_smooth = True


def handle(collection, name, pos):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    obj = bpy.context.object
    obj.dimensions = (0.060, 0.015, 0.010)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    put(obj, collection, name, amber)
    bevel = obj.modifiers.new("Rounded handle", "BEVEL")
    bevel.width, bevel.segments = 0.004, 3


def bore(obj, cutter):
    mod = obj.modifiers.new("Bore", "BOOLEAN")
    mod.operation, mod.solver, mod.object = "DIFFERENCE", "EXACT", cutter
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def prepare_tops():
    """Reuse the tower geometry and adapt its cover and plate for top entry."""
    cover_mesh = None
    plate_mesh = None
    for tower, (x, y) in towers:
        parts = full.collection.children[f"04 Tower {tower} | stackable"]
        bpy.data.objects.remove(parts.objects[f"{tower} / internal riser"], do_unlink=True)
        cover = parts.objects[f"{tower} / Distributor | removable cover"]
        plate = parts.objects[f"{tower} / Distributor | perforated plate"]
        if cover_mesh is None:
            cover_mesh = cover.data.copy()
            for vertex in cover_mesh.vertices:
                radius = math.hypot(vertex.co.x, vertex.co.y)
                if radius < 0.001:
                    scale = (drop_r + 0.0005) / radius
                    vertex.co.x *= scale
                    vertex.co.y *= scale
            cover_mesh.update()
        cover.data = cover_mesh
        if plate_mesh is None:
            z = spec["distributor_plate_base_m"]
            replacement = cylinder(parts, "Temporary top-fed plate", (0, 0, z), (0, 0, z+0.005),
                                   spec["distributor_plate_diameter_m"]/2, sage, sides=96)
            bpy.context.view_layer.objects.active = replacement
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
            for k in range(8):
                angle = (k + 0.5) * math.tau / 8
                dx, dy = 0.051 * math.cos(angle), 0.051 * math.sin(angle)
                cutter = cylinder(parts, "Temporary distributor drill", (dx, dy, z-0.006),
                                  (dx, dy, z+0.011), 0.002, sides=24)
                bore(replacement, cutter)
            plate_mesh = replacement.data
            plate.data = plate_mesh
            bpy.data.objects.remove(replacement, do_unlink=True)
        else:
            plate.data = plate_mesh


def add_supply():
    common = full.collection.children["02 Pump and common header"]
    supply = group(full, "02 Single pump and riser")
    pump = next(obj for obj in common.objects if "pump envelope" in obj.name)
    pump_top = pump.location.z + pump.dimensions.z / 2
    put(pump, supply, "P1 | shared pump envelope")
    for name in [common.name] + [f"03 Branch {tower}" for tower, _ in towers]:
        collection = full.collection.children[name]
        for obj in list(collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(collection)
    base_z = 0.120
    cylinder(supply, "Pump discharge", (0, 0, pump_top), (0, 0, base_z), header_r, teal)
    cylinder(supply, "Run to rear riser", (0, 0, base_z), (0, riser_y, base_z), header_r, teal)
    fitting(supply, "Pump elbow", (0, 0, base_z), header_r * 1.09)
    fitting(supply, "Riser lower elbow", (0, riser_y, base_z), header_r * 1.09)
    cylinder(supply, "Single rear riser", (0, riser_y, base_z), (0, riser_y, header_z), header_r, teal)
    deck = full.collection.children["01 Shared reservoir and deck"].objects["Common deck | four gravity returns"]
    cutter = cylinder(supply, "Temporary riser clearance", (0, riser_y, 0.300),
                      (0, riser_y, 0.345), header_r+0.001)
    bore(deck, cutter)

    loop = group(full, "03 Top recirculation supply loop")
    for i, ((x1, y1), (x2, y2)) in enumerate(zip(corners, corners[1:] + corners[:1]), 1):
        cylinder(loop, f"Loop side {i}", (x1, y1, header_z), (x2, y2, header_z), header_r, teal)
    cylinder(loop, "Feed into rear side of loop", (0, riser_y, header_z), (0, offset, header_z),
             header_r, teal)
    fitting(loop, "Riser top elbow", (0, riser_y, header_z), header_r * 1.09)
    fitting(loop, "Ring feed tee", (0, offset, header_z), header_r * 1.13)
    for tower, (x, y) in towers:
        fitting(loop, tower + " | three-way top fitting", (x, y, header_z), header_r * 1.15)
        cylinder(loop, tower + " | drop into distributor", (x, y, outlet_z), (x, y, header_z), drop_r, teal)
        z = (header_z + 1.575) / 2
        cylinder(loop, tower + " | balancing valve", (x, y, z-0.018), (x, y, z+0.018),
                 drop_r+0.006, teal)
        handle(loop, tower + " | valve handle", (x, y-0.016, z))
    return loop


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def make_detail(loop):
    scene = bpy.data.scenes.new("02 Top loop close-up")
    bpy.context.window.scene = scene
    scene.unit_settings.system = "METRIC"
    parts = group(scene, "Upper tower sections")
    for tower, _ in towers:
        for obj in full.collection.children[f"04 Tower {tower} | stackable"].objects:
            if "Distributor |" in obj.name or " / Tier 4 |" in obj.name or " / T4 site " in obj.name:
                parts.objects.link(obj)
    scene.collection.children.link(loop)
    cylinder(parts, "Rear riser | cropped", (0, riser_y, 1.224),
             (0, riser_y, header_z), header_r, teal)

    studio = group(scene, "Render studio")
    camera = bpy.data.objects.new("Top loop camera", bpy.data.cameras.new("Top loop camera"))
    studio.objects.link(camera)
    camera.location = (1.35, -1.7, 2.9)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 1.18
    aim(camera, (0, 0, 1.47))
    scene.camera = camera
    for obj in full.collection.children["05 Render studio"].objects:
        if obj.type == "LIGHT":
            studio.objects.link(obj)
        elif obj.name == "Studio floor":
            floor = obj.copy()
            floor.location.z = 1.203
            studio.objects.link(floor)
    studio.hide_viewport = True
    scene.world = full.world
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1060, 790
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.object.select_all(action="DESELECT")
    return scene


prepare_tops()
loop = add_supply()
full["Supply layout"] = "One rear riser, one closed top ring, four valved drops"
full["Top loop centerline (m)"] = header_z
full.camera.data.ortho_scale = 2.48
aim(full.camera, (0, 0, 0.83))
detail = make_detail(loop)
bpy.context.window.scene = full
bpy.ops.object.select_all(action="DESELECT")
bpy.data.orphans_purge(do_recursive=True)
notes = bpy.data.texts.new("Top loop design notes")
notes.write((ROOT / "README.md").read_text(encoding="utf-8"))
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "four_tower_top_loop.blend"))

for scene, filename in ((full, "four_tower_top_loop.png"), (detail, "top_loop_detail.png")):
    bpy.context.window.scene = scene
    scene.render.filepath = str(ROOT / filename)
    bpy.ops.render.render(write_still=True)
