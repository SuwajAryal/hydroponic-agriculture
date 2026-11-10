"""Replace the full-width tank with a removable service reservoir and gravity collectors."""
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
source = Path(args[0]).resolve() if args else ROOT.parent / "four-tower-top-loop" / "four_tower_top_loop.blend"
spec = json.loads((ROOT / "service_base_dimensions.json").read_text(encoding="utf-8"))
tank = spec["tank"]
drain = spec["return_system"]
feed = spec["supply"]
spacing = spec["tower_spacing_m"] / 2
deck = spec["deck_bottom_m"]
half_x, half_y = tank["outside_x_m"] / 2, tank["outside_y_m"] / 2
floor = tank["bottom_m"] + tank["floor_m"]
lid = tank["rim_m"]

bpy.ops.wm.open_mainfile(filepath=str(source))
full = bpy.data.scenes["01 Four-tower top loop"]
bpy.context.window.scene = full
full.name = "01 Four towers with service base"
teal = bpy.data.materials["Pressurized feed | teal"]
green = bpy.data.materials["Shared reservoir | forest"]
sage = bpy.data.materials["Deck and inspection hatch | sage"]
amber = bpy.data.materials["Branch balancing handles | amber"]


def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = mat.diffuse_color
    shader.inputs["Roughness"].default_value = 0.42
    return mat


steel = material("Frame | slate", (0.085, 0.12, 0.125))
return_mat = material("Gravity return | pale blue", (0.19, 0.49, 0.57))
level_mat = material("Reservoir level marks", (0.06, 0.37, 0.65))


def group(scene, name):
    collection = bpy.data.collections.new(name)
    scene.collection.children.link(collection)
    return collection


def put(obj, collection, name, mat=None):
    obj.name = name
    for previous in list(obj.users_collection):
        previous.objects.unlink(obj)
    collection.objects.link(obj)
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def box(collection, name, center, dims, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    put(obj, collection, name, mat)
    if bevel:
        mod = obj.modifiers.new("Soft edges", "BEVEL")
        mod.width, mod.segments = bevel, 3
    return obj


def cylinder(collection, name, a, b, radius, mat=None, sides=48):
    a, b = Vector(a), Vector(b)
    direction = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides, radius=radius,
                                      depth=direction.length, location=(a + b)/2)
    obj = bpy.context.object
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return put(obj, collection, name, mat)


def bore(obj, cutter):
    mod = obj.modifiers.new("Opening", "BOOLEAN")
    mod.operation, mod.solver, mod.object = "DIFFERENCE", "EXACT", cutter
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def mesh_object(collection, name, vertices, faces, mat):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    mesh.materials.append(mat)
    return obj


def ring_profile(collection, name, x, y, profile):
    steps = 96
    size = len(profile)
    points, faces = [], []
    for i in range(steps):
        a = i * math.tau / steps
        points.extend((x + r*math.cos(a), y + r*math.sin(a), z) for r, z in profile)
    for i in range(steps):
        n = (i+1) % steps
        for j in range(size):
            k = (j+1) % size
            faces.append((i*size+j, n*size+j, n*size+k, i*size+k))
    return mesh_object(collection, name, points, faces, return_mat)


def frame_parts():
    parts = group(full, "06 Support frame and slide tray")
    c, w = spec["frame"]["leg_centers_m"], spec["frame"]["member_size_m"]
    for x in (-c, c):
        for y in (-c, c):
            box(parts, f"Frame leg {x:g}, {y:g}", (x, y, deck/2), (w, w, deck), steel, 0.003)
    for x in (-c, c):
        box(parts, "Frame side rail", (x, 0, deck-w/2), (w, 2*c, w), steel, 0.003)
    for y in (-c, -0.127, 0.127, c):
        box(parts, "Deck cross rail", (0, y, deck-w/2), (2*c, w, w), steel, 0.003)
    box(parts, "Floor-supported slide tray", (0, -0.025, tank["bottom_m"]/2),
        (0.65, 0.57, tank["bottom_m"]), steel, 0.004)
    for x in (-half_x-0.012, half_x+0.012):
        box(parts, "Tray guide", (x, 0, tank["bottom_m"]+0.008), (0.016, 0.50, 0.016), steel, 0.002)
    return parts


def reservoir():
    parts = group(full, "07 Removable opaque reservoir")
    bottom, wall = tank["bottom_m"], tank["wall_m"]
    height = lid-floor
    box(parts, "Tank floor", (0, 0, (bottom+floor)/2), (2*half_x, 2*half_y, floor-bottom), green)
    for side in (-1, 1):
        box(parts, "Tank side", (side*(half_x-wall/2), 0, floor+height/2),
            (wall, 2*half_y, height), green, 0.0015)
        label = "Tank front" if side < 0 else "Tank rear"
        box(parts, label, (0, side*(half_y-wall/2), floor+height/2),
            (2*(half_x-wall), wall, height), green, 0.0015)
    for z, label in ((tank["low_mark_m"], "Low"), (tank["high_mark_m"], "High")):
        box(parts, label+" water level", (0, half_y-wall-0.002, z),
            (2*(half_x-wall), 0.003, 0.0025), level_mat)
    cover = box(parts, "Opaque lift-off tank lid", (0, 0, lid+0.003),
                (2*half_x+0.006, 2*half_y+0.006, 0.006), sage)
    for x in (-spacing, spacing):
        cutter = cylinder(parts, "Temporary return port", (x, 0, lid-0.01),
                          (x, 0, lid+0.016), 0.025)
        bore(cover, cutter)
    for name, y, radius in (("Supply port", feed["lid_feed_y_m"], 0.018),
                            ("Top-up opening", -0.14, 0.032)):
        cutter = cylinder(parts, "Temporary "+name, (0, y, lid-0.01), (0, y, lid+0.016), radius)
        bore(cover, cutter)
    cylinder(parts, "Removable top-up cap", (0, -0.14, lid+0.006), (0, -0.14, lid+0.014), 0.037, sage)
    for x in (-0.058, 0.058):
        box(parts, "Handle mount", (x, -half_y-0.010, 0.135), (0.016, 0.026, 0.018), steel, 0.003)
    box(parts, "Front pull handle", (0, -half_y-0.024, 0.135), (0.132, 0.016, 0.018), amber, 0.004)
    return parts


def collector(parts, x, label):
    lo, hi = drain["center_floor_m"], drain["end_floor_m"]
    end, width = drain["collector_half_length_m"], drain["collector_width_m"]
    w, wall = width/2, 0.004
    height = 0.030
    stations = [(-end, hi), (-0.023, lo), (0.023, lo), (end, hi)]
    vertices, faces = [], []
    for y, z in stations:
        profile = [(-w, z-wall), (w, z-wall), (w, z+height), (w-wall, z+height),
                   (w-wall, z), (-w+wall, z), (-w+wall, z+height), (-w, z+height)]
        vertices.extend((x+dx, y, h) for dx, h in profile)
    size = len(profile)
    for i in range(len(stations)-1):
        for j in range(size):
            k = (j+1) % size
            faces.append((i*size+j, (i+1)*size+j, (i+1)*size+k, i*size+k))
    faces.extend((tuple(reversed(range(size))), tuple(range(3*size, 4*size))))
    body = mesh_object(parts, label+" | sloped open collector", vertices, faces, return_mat)
    r = drain["spout_inside_diameter_m"]/2
    tool = cylinder(parts, "Temporary collector drain", (x, 0, lo-0.012), (x, 0, lo+0.013), r)
    bore(body, tool)
    for side in (-1, 1):
        box(parts, label+" | collector end stop", (x, side*(end-wall/2), hi+height/2),
            (width-2*wall, wall, height), return_mat)
    z = drain["spout_bottom_m"]
    ring_profile(parts, label+" | open return spout", x, 0,
                 [(r, z), (r+0.003, z), (r+0.003, lo), (r, lo)])
    for y in (-0.127, 0.127):
        underside = lo + (hi-lo) * (abs(y)-0.023) / (end-0.023) - wall
        rail_bottom = deck - spec["frame"]["member_size_m"]
        box(parts, label+" | lift-out collector cradle", (x, y, underside-0.002),
            (width+0.022, 0.013, 0.004), steel, 0.001)
        for side in (-1, 1):
            box(parts, label+" | cradle hanger", (x+side*(w+0.005), y, (rail_bottom+underside)/2),
                (0.006, 0.013, rail_bottom-underside), steel, 0.001)


def gravity_parts():
    parts = group(full, "08 Sloped gravity returns")
    for x, label in ((-spacing, "Left pair"), (spacing, "Right pair")):
        collector(parts, x, label)
        for y in (-spacing, spacing):
            ring_profile(parts, label+" | reducer funnel", x, y,
                         [(0.021, 0.270), (0.024, 0.270), (0.079, deck), (0.076, deck)])
    return parts


def pump_parts():
    parts = full.collection.children["02 Single pump and riser"]
    pump = parts.objects["P1 | shared pump envelope"]
    for obj in list(parts.objects):
        if obj != pump:
            bpy.data.objects.remove(obj, do_unlink=True)
    pump.location.y = feed["lid_feed_y_m"]
    pump.location.z = floor + pump.dimensions.z/2
    pump_top = pump.location.z + pump.dimensions.z/2
    y, riser_y = feed["lid_feed_y_m"], feed["rear_riser_y_m"]
    z = feed["disconnect_height_m"]
    cylinder(parts, "Pump outlet through lid", (0, y, pump_top), (0, y, z), 0.013, teal)
    cylinder(parts, "Removable pump lead", (0, y, z), (0, riser_y, z), 0.017, teal)
    cylinder(parts, "Quick disconnect union", (0, y+0.036, z), (0, y+0.072, z), 0.023, amber, 32)
    cylinder(parts, "Single rear riser", (0, riser_y, z), (0, riser_y, feed["top_header_centerline_m"]),
             0.017, teal)
    cylinder(parts, "Rear elbow housing", (0, riser_y, z-0.017), (0, riser_y, z+0.019),
             0.020, teal)
    return parts


def aim(obj, point):
    obj.rotation_euler = (Vector(point)-obj.location).to_track_quat("-Z", "Y").to_euler()


def detail_view(frame, reservoir_parts, returns, supply):
    scene = bpy.data.scenes.new("03 Base and gravity returns")
    bpy.context.window.scene = scene
    scene.unit_settings.system = "METRIC"
    cut = group(scene, "Service view | deck, lid and tank front removed")
    for obj in frame.objects:
        if not obj.name.startswith(("Deck cross rail", "Frame side rail")) and not (
            obj.name.startswith("Frame leg") and obj.location.y < 0
        ):
            cut.objects.link(obj)
    for obj in reservoir_parts.objects:
        if not obj.name.startswith(("Opaque", "Tank front", "Front pull", "Handle mount", "Removable top-up")):
            cut.objects.link(obj)
    scene.collection.children.link(returns)
    for obj in supply.objects:
        if not obj.name.startswith("Single rear riser"):
            cut.objects.link(obj)
    cylinder(cut, "Rear riser | cropped for detail",
             (0, feed["rear_riser_y_m"], feed["disconnect_height_m"]),
             (0, feed["rear_riser_y_m"], deck+0.044), 0.017, teal)
    studio = group(scene, "Base render studio")
    for obj in full.collection.children["05 Render studio"].objects:
        if obj.type == "LIGHT" or obj.name == "Studio floor":
            studio.objects.link(obj)
    camera = bpy.data.objects.new("Base camera", bpy.data.cameras.new("Base camera"))
    studio.objects.link(camera)
    camera.location = (1.30, -1.9, 1.42)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 1.21
    aim(camera, (0, 0, 0.15))
    scene.camera = camera
    studio.hide_viewport = True
    scene.world = full.world
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1060, 770
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    return scene


old = full.collection.children["01 Shared reservoir and deck"]
for obj in list(old.objects):
    if obj.name.startswith("Reservoir"):
        bpy.data.objects.remove(obj, do_unlink=True)
old.name = "01 Deck and cleanout hatch"
frame = frame_parts()
tank_parts = reservoir()
returns = gravity_parts()
supply = pump_parts()
base_view = detail_view(frame, tank_parts, returns, supply)
bpy.context.window.scene = full
full["Reservoir layout"] = "Front-removable reservoir below independent deck frame"
full["Return layout"] = "Four funnels feed two sloped, open collectors"
bpy.ops.object.select_all(action="DESELECT")
bpy.data.orphans_purge(do_recursive=True)
notes = bpy.data.texts.new("Service base design notes")
notes.write((ROOT / "README.md").read_text(encoding="utf-8"))
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "four_tower_service_base.blend"))
for scene, filename in ((full, "four_tower_service_base.png"), (base_view, "base_return_detail.png")):
    bpy.context.window.scene = scene
    scene.render.filepath = str(ROOT / filename)
    bpy.ops.render.render(write_still=True)
