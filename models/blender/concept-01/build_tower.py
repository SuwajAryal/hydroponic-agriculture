"""Generate a metric tower assembly and a second scene showing its cutaway.

Run with Blender, not system Python. Dimensions are a concept, in metres.
"""
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

DEFAULT_SPEC = Path(__file__).resolve().with_name("concept_dimensions.json")
arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(arguments) > 1:
    raise SystemExit("Pass at most one concept_dimensions.json path after --.")
spec_path = Path(arguments[0]).resolve() if arguments else DEFAULT_SPEC
ROOT = spec_path.parent
SPEC = json.loads(spec_path.read_text(encoding="utf-8"))
TOWER = SPEC["tower"]
TANK = SPEC["reservoir"]
FEED = SPEC["feed"]
DISTRIBUTOR = SPEC["distributor"]
ONE_PIECE = TOWER.get("body_style", "modular") == "one_piece"
EXTERNAL_FEED = FEED.get("route", "internal") == "external"
CUT = (math.radians(15), math.radians(225))
FULL = (0.0, math.tau)
VERTICAL = Vector((0, 0, 1))


def material(name, color, roughness=0.4):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = mat.diffuse_color
    shader.inputs["Roughness"].default_value = roughness
    return mat


def collection(scene, name):
    group = bpy.data.collections.new(name)
    scene.collection.children.link(group)
    return group


def move_to(obj, group):
    for previous in list(obj.users_collection):
        previous.objects.unlink(obj)
    group.objects.link(obj)


def revolve(group, name, profile, mat, sector=FULL):
    """Sweep a closed, nonzero-radius profile around its local Z axis."""
    start, end = sector
    closed = math.isclose(end - start, math.tau)
    steps = 96 if closed else 56
    count = steps if closed else steps + 1
    vertices, faces = [], []
    size = len(profile)
    for i in range(count):
        theta = start + i * (end - start) / steps
        vertices.extend((r * math.cos(theta), r * math.sin(theta), z) for r, z in profile)
    for i in range(steps):
        next_ring = ((i + 1) % count) * size
        for j in range(size):
            k = (j + 1) % size
            faces.append((i * size + j, next_ring + j, next_ring + k, i * size + k))
    if not closed:
        faces.extend((tuple(reversed(range(size))), tuple(range((count - 1) * size, count * size))))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    group.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def ring(group, name, inner, outer, bottom, top, mat, sector=FULL):
    return revolve(group, name, [(inner, bottom), (outer, bottom), (outer, top), (inner, top)], mat, sector)


def cylinder(group, name, radius, depth, center, axis=VERTICAL, mat=None, vertices=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = axis.to_track_quat("Z", "Y").to_euler()
    move_to(obj, group)
    if mat is not None:
        obj.data.materials.append(mat)
    return obj


def box(group, name, center, dimensions, mat, radius=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to(obj, group)
    obj.data.materials.append(mat)
    if radius:
        bevel = obj.modifiers.new("Rounded edges", "BEVEL")
        bevel.width = radius
        bevel.segments = 3
    return obj


def subtract(obj, cutter):
    mod = obj.modifiers.new("Opening", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def place_on_axis(obj, origin, axis):
    obj.location = origin
    obj.rotation_euler = axis.to_track_quat("Z", "Y").to_euler()


def pot(group, label, mouth, axis):
    """An open basket with a lip, tapered ribs and a perforated base."""
    r = TOWER["net_pot_rim_diameter_m"] / 2
    d = TOWER["net_pot_depth_m"]
    lower = r * 0.64
    lip = ring(group, label + " rim", r - 0.003, r + 0.003, -0.007, 0.001, MATS["pot"])
    place_on_axis(lip, mouth, axis)
    base = ring(group, label + " base ring", lower * 0.40, lower, -d, -d + 0.004, MATS["pot"])
    place_on_axis(base, mouth, axis)
    rotation = axis.to_track_quat("Z", "Y")
    for k in range(8):
        angle = k * math.tau / 8
        c, s = math.cos(angle), math.sin(angle)
        top = mouth + rotation @ Vector(((r - 0.002) * c, (r - 0.002) * s, -0.006))
        bottom = mouth + rotation @ Vector((lower * c, lower * s, -d + 0.002))
        cylinder(group, label + f" rib {k+1}", 0.00155, (top - bottom).length, (top + bottom) / 2,
                 (top - bottom).normalized(), MATS["pot"], vertices=8)


def add_reservoir(group, sector):
    low_r = TANK["base_outside_diameter_m"] / 2
    top_r = TANK["rim_outside_diameter_m"] / 2
    wall = TANK["wall_m"]
    depth = TANK["rim_height_m"]
    floor = TANK["floor_m"]
    revolve(group, "Reservoir | tapered shell", [
        (0.0005, 0), (low_r, 0), (top_r, depth), (top_r - wall, depth),
        (low_r + (top_r - low_r) * floor / depth - wall, floor), (0.0005, floor)
    ], MATS["tank"], sector)
    # Cover the tiny inner radius left by the revolve so the base is closed.
    cylinder(group, "Reservoir | floor centre", 0.0006, floor, (0, 0, floor / 2), mat=MATS["tank"])
    lid = ring(group, "Lid | open gravity return", OUTSIDE - 0.003, top_r + 0.004,
               depth - 0.004, BASE, MATS["rim"], sector)
    if EXTERNAL_FEED and sector == FULL:
        offset = FEED["external_offset_m"]
        cutter = cylinder(group, "Temporary lid drill", FEED["riser_outside_diameter_m"] / 2 + 0.001,
                          0.024, (0, -offset, depth), vertices=48)
        subtract(lid, cutter)


def add_water_references(group):
    for name, z, width in (
        ("High water level", TANK["high_water_m"], 0.008),
        ("Low water level", TANK["low_water_m"], 0.004),
    ):
        wall_r = (TANK["base_outside_diameter_m"] / 2
                  + z / TANK["rim_height_m"] * (TANK["rim_outside_diameter_m"] - TANK["base_outside_diameter_m"]) / 2
                  - TANK["wall_m"] - 0.001)
        ring(group, f"{name} | {z * 1000:g} mm datum", wall_r - width, wall_r,
             z - 0.001, z + 0.001, MATS["water"], CUT)


def add_tiers(shells, pots, sector):
    if ONE_PIECE:
        tube = ring(shells, "Tower | continuous tube", INSIDE, OUTSIDE, BASE, TOP, MATS["tube"], sector)
        ring(shells, "Tower | base collar", OUTSIDE - 0.0005, OUTSIDE + 0.004,
             BASE, BASE + 0.013, MATS["rim"], sector)
    for tier in range(TOWER["tier_count"]):
        z = BASE + tier * TOWER["tier_height_m"]
        top = z + TOWER["tier_height_m"]
        if not ONE_PIECE:
            tube = ring(shells, f"Tier {tier+1} | open tube", INSIDE, OUTSIDE, z, top, MATS["tube"], sector)
            ring(shells, f"Tier {tier+1} | joint collar", OUTSIDE - 0.0005, OUTSIDE + 0.004,
                 z, z + 0.013, MATS["rim"], sector)
        for site in range(TOWER["sites_per_tier"]):
            theta = (site * math.tau / TOWER["sites_per_tier"]
                     + (tier % 2) * math.radians(TOWER["stagger_angle_deg"])) % math.tau
            if sector != FULL and not sector[0] + 0.40 <= theta <= sector[1] - 0.40:
                continue
            radial = Vector((math.cos(theta), math.sin(theta), 0))
            tilt = math.radians(TOWER["pocket_tilt_deg"])
            axis = radial * math.cos(tilt) + VERTICAL * math.sin(tilt)
            center = radial * OUTSIDE + Vector((0, 0, (z + top) / 2))
            label = f"T{tier+1} site {site+1}"
            socket = TOWER["socket_bore_m"] / 2
            cutter = cylinder(shells, "Temporary port cutter", socket, 0.115, center, axis, vertices=64)
            subtract(tube, cutter)
            length = TOWER["socket_projection_m"]
            sleeve = ring(pots, label + " socket", socket, socket + 0.004, -0.020, length, MATS["rim"])
            place_on_axis(sleeve, center, axis)
            trim = cylinder(pots, "Temporary bore cutter", INSIDE, top - z, (0, 0, (z + top) / 2),
                            vertices=96)
            subtract(sleeve, trim)
            pot(pots, label + " net pot", center + axis * (length + 0.003), axis)


def curved_pipe(group, name, points, bend, inner, outer):
    """Build a hollow tube with rounded bends in the vertical YZ plane."""
    stations = [(points[0], (points[1] - points[0]).normalized())]
    for i in range(1, len(points) - 1):
        corner = points[i]
        before = (corner - points[i - 1]).normalized()
        after = (points[i + 1] - corner).normalized()
        distance = min(bend, (corner - points[i - 1]).length / 3,
                       (points[i + 1] - corner).length / 3)
        start, end = corner - before * distance, corner + after * distance
        for j in range(13):
            t = j / 12
            u = 1 - t
            center = u * u * start + 2 * u * t * corner + t * t * end
            tangent = (u * (corner - start) + t * (end - corner)).normalized()
            stations.append((center, tangent))
    stations.append((points[-1], (points[-1] - points[-2]).normalized()))

    sides = 48
    vertices, faces = [], []
    transverse = Vector((1, 0, 0))
    for center, tangent in stations:
        normal = tangent.cross(transverse).normalized()
        for radius in (outer, inner):
            for j in range(sides):
                a = j * math.tau / sides
                vertices.append(tuple(center + radius * (math.cos(a) * transverse + math.sin(a) * normal)))
    stride = 2 * sides
    for i in range(len(stations) - 1):
        for j in range(sides):
            k = (j + 1) % sides
            a, b = i * stride, (i + 1) * stride
            faces.append((a + j, a + k, b + k, b + j))
            faces.append((a + sides + j, b + sides + j, b + sides + k, a + sides + k))
    for i in (0, len(stations) - 1):
        a = i * stride
        for j in range(sides):
            k = (j + 1) % sides
            faces.append((a + j, a + sides + j, a + sides + k, a + k))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    group.objects.link(obj)
    obj.data.materials.append(MATS["feed"])
    for poly in mesh.polygons[:-2 * sides]:
        poly.use_smooth = True


def add_feed(group, distributor_group, sector):
    pump_top = FEED["pump_top_m"]
    box(group, "Pump | placeholder envelope", (0, 0, (pump_top + 0.014) / 2),
        (0.070, 0.064, pump_top - 0.014), MATS["pump"], 0.005)
    riser_od = FEED["riser_outside_diameter_m"] / 2
    riser_id = FEED["riser_inside_diameter_m"] / 2
    outlet = TOP + DISTRIBUTOR["outlet_offset_above_tower_m"]
    floor_z = TOP + DISTRIBUTOR["plate_offset_above_tower_m"]
    plate_r = DISTRIBUTOR["plate_outside_diameter_m"] / 2
    if EXTERNAL_FEED:
        y = -FEED["external_offset_m"]
        bottom_turn = FEED["bottom_turn_height_m"]
        crest = floor_z + 0.047 + FEED["crest_above_cover_m"]
        points = [(0, 0, pump_top), (0, 0, bottom_turn), (0, y, bottom_turn),
                  (0, y, crest), (0, 0, crest), (0, 0, outlet)]
        curved_pipe(group, "Riser | external supply with rounded bends", [Vector(p) for p in points],
                    FEED["bend_trim_m"], riser_id, riser_od)
        if sector == FULL:
            plate = cylinder(distributor_group, "Distributor | perforated plate", plate_r, 0.005,
                             (0, 0, floor_z + 0.0025), mat=MATS["rim"], vertices=96)
            # Put the plate in the same global coordinates as the cutaway ring.
            bpy.context.view_layer.objects.active = plate
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
        else:
            plate = ring(distributor_group, "Distributor | perforated plate", 0.00001, plate_r,
                         floor_z, floor_z + 0.005, MATS["rim"], sector)
    else:
        ring(group, "Riser | open-bore tube", riser_id, riser_od, pump_top, outlet, MATS["feed"])
        plate = ring(distributor_group, "Distributor | perforated plate", riser_od + 0.0005, plate_r,
                     floor_z, floor_z + 0.005, MATS["rim"], sector)
    for k in range(DISTRIBUTOR["hole_count"]):
        theta = (k + 0.5) * math.tau / DISTRIBUTOR["hole_count"]
        if sector != FULL and not sector[0] + 0.07 <= theta <= sector[1] - 0.07:
            continue
        r = DISTRIBUTOR["hole_pitch_radius_m"]
        hole = cylinder(distributor_group, "Temporary distributor drill", DISTRIBUTOR["hole_diameter_m"] / 2,
                        0.018, (r * math.cos(theta), r * math.sin(theta), floor_z + 0.0025), vertices=24)
        subtract(plate, hole)
    ring(distributor_group, "Distributor | cup wall", plate_r - 0.004, plate_r,
         TOP - 0.006, floor_z + 0.040, MATS["tube"], sector)
    cover_bore = riser_od + 0.0005 if EXTERNAL_FEED else 0.0005
    ring(distributor_group, "Distributor | removable cover", cover_bore, plate_r + 0.003,
         floor_z + 0.040, floor_z + 0.047, MATS["rim"], sector)


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def presentation(scene, group):
    center = TOP / 2
    box(group, "Studio floor", (0, 0, -0.021), (200, 200, 0.04), MATS["ground"])
    camera_data = bpy.data.cameras.new("Isometric camera")
    camera = bpy.data.objects.new("Isometric camera", camera_data)
    group.objects.link(camera)
    camera.location = (2.3, -4.1, center + 1.45)
    aim(camera, (0, 0, center))
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = TOP * 1.17
    scene.camera = camera
    for name, location, power, size in (
        ("Key", (2, -2, 3), 220, 2.0),
        ("Fill", (-2, -0.5, 1.8), 130, 2.0),
        ("Rim", (0.5, 2, 2.4), 240, 1.7),
    ):
        data = bpy.data.lights.new(name, "AREA")
        data.energy, data.shape, data.size = power, "DISK", size
        light = bpy.data.objects.new(name, data)
        group.objects.link(light)
        light.location = location
        aim(light, (0, 0, center))
    scene.world = bpy.data.worlds.new("Studio world")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.42
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 740, 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    # Show only engineering geometry in the viewport, keep the studio in renders.
    group.hide_viewport = True
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                view = area.spaces.active
                view.region_3d.view_location = (0, 0, center)
                view.region_3d.view_distance = 2.4
                view.region_3d.view_rotation = camera.rotation_euler.to_quaternion()
                view.region_3d.view_perspective = "ORTHO"
                view.shading.color_type = "MATERIAL"
                view.overlay.show_floor = False
                view.overlay.show_axis_x = view.overlay.show_axis_y = False


def make_scene(scene, name, cutaway=False):
    bpy.context.window.scene = scene
    scene.name = name
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene["Design status"] = "Unmeasured concept geometry"
    scene["Body style"] = TOWER.get("body_style", "modular")
    scene["Supply route"] = FEED.get("route", "internal")
    scene["Tower body height (m)"] = TOP - BASE
    scene["Tower inside diameter (m)"] = INSIDE * 2
    scene["Planting sites in complete assembly"] = TOWER["tier_count"] * TOWER["sites_per_tier"]
    sector = CUT if cutaway else FULL
    add_reservoir(collection(scene, "01 Reservoir and lid"), sector)
    add_tiers(collection(scene, "02 Tower sections"), collection(scene, "03 Planting pockets"), sector)
    add_feed(collection(scene, "04 Pump and riser"), collection(scene, "05 Top distributor"), sector)
    if cutaway:
        add_water_references(collection(scene, "06 Reservoir water level markers"))
    presentation(scene, collection(scene, "07 Render studio"))
    bpy.ops.object.select_all(action="DESELECT")


bpy.ops.wm.read_factory_settings(use_empty=True)
BASE = TANK["rim_height_m"] + 0.004
TOP = BASE + TOWER["tier_count"] * TOWER["tier_height_m"]
INSIDE = TOWER["inside_diameter_m"] / 2
OUTSIDE = INSIDE + TOWER["wall_m"]
MATS = {
    "tube": material("Ivory | tower body", (0.78, 0.81, 0.72)),
    "rim": material("Sage | collars and plate", (0.27, 0.44, 0.31)),
    "tank": material("Forest | reservoir", (0.055, 0.15, 0.113)),
    "pot": material("Charcoal | net pots", (0.041, 0.047, 0.043)),
    "pump": material("Graphite | pump", (0.078, 0.097, 0.107)),
    "feed": material("Teal | supply riser", (0.018, 0.37, 0.38)),
    "water": material("Blue | water level marker", (0.055, 0.42, 0.72)),
    "ground": material("Pale sand | backdrop", (0.78, 0.81, 0.75)),
}
full = bpy.context.scene
make_scene(full, "01 Complete tower")
cut = bpy.data.scenes.new("02 Cutaway")
make_scene(cut, "02 Cutaway", cutaway=True)

notes = bpy.data.texts.new("Design notes and credits")
notes.write((ROOT / "README.md").read_text(encoding="utf-8"))
bpy.context.window.scene = full
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "tower_concept.blend"))

for scene, filename in ((full, "tower_assembly.png"), (cut, "tower_cutaway.png")):
    bpy.context.window.scene = scene
    scene.render.filepath = str(ROOT / filename)
    bpy.ops.render.render(write_still=True)
