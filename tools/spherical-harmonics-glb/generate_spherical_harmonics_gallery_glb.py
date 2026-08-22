#!/usr/bin/env python3
"""Create a floating, ink-rendered spherical-harmonics gallery as one GLB scene.

The included camera frames the scene in a wide, illustration-like composition.
Each object uses faint and soft ink for its signs, with selected surface edges
forming a sparse grid that deforms with the spherical-harmonic geometry.
"""

from __future__ import print_function

import argparse
import json
import math
import re
import struct

from generate_spherical_harmonics_glb import (GRID_LOG_FADE_MAXIMUM, GRID_LOG_FADE_MINIMUM,
                                              GRID_NORMAL_OFFSET, GRID_OPACITY_STEPS,
                                              GRID_SPECULAR_POWER, INK_FAINT, INK_OUTLINE, INK_SOFT,
                                              build_surface, grid_material, ink_material, padded)


# (degree, order, position, scale, Euler rotation in degrees)
GALLERY_MODES = [
    # The three large top anchors and the deliberately cropped corner forms.
    (0, 0, (-9.25, 4.15, -0.8), 5.80, (0, 0, 0)),
    (0, 0, (-4.65, 2.85, 0.3), 5.20, (0, 0, 0)),
    (1, 0, (-2.45, 4.05, -0.4), 1.75, (25, 10, 0)),
    (2, 1, (-2.55, 3.05, -0.2), 2.70, (-12, 30, 12)),
    (2, -1, (-0.55, 3.40, 0.4), 2.75, (25, -20, 22)),
    (1, 1, (2.50, 3.50, -0.5), 3.20, (-18, 25, -20)),
    (2, 0, (4.60, 2.85, -0.1), 2.80, (5, 30, 25)),
    (0, 0, (9.20, 4.10, 0.2), 6.10, (0, 0, 0)),
    # Asymmetric middle clusters: objects overlap diagonally, not in rows.
    (3, 3, (-7.10, 0.70, 0.9), 2.85, (20, -18, 18)),
    (2, -2, (-5.75, 1.05, -0.4), 1.45, (15, 30, -25)),
    (3, -1, (-4.20, -0.05, 0.2), 2.20, (-8, 25, 25)),
    (3, 2, (-0.15, 1.60, 1.0), 2.05, (-12, 25, 0)),
    (2, 2, (0.30, 0.15, -0.3), 2.05, (25, -25, 35)),
    (1, -1, (2.00, -0.05, 0.4), 3.45, (15, -35, -20)),
    (2, 0, (3.45, 0.85, -0.4), 3.50, (-20, 12, 30)),
    (3, -2, (4.50, 0.00, 0.6), 2.05, (12, -30, -12)),
    (3, -3, (6.20, 0.20, 0.7), 2.75, (20, 10, -25)),
    # Lower-left is one dominant four-petal form; the rest taper to the right.
    (2, 2, (-4.75, -2.15, 0.5), 3.80, (15, 24, -8)),
    (3, 1, (-4.10, -2.25, -0.2), 2.95, (-8, 22, 18)),
    (3, -2, (-1.65, -1.65, 0.8), 2.15, (16, -22, -10)),
    (1, 0, (0.25, -2.45, 0.3), 2.45, (12, -15, 20)),
    (2, -2, (1.95, -2.25, -0.4), 2.40, (20, 25, -15)),
    (3, 2, (3.95, -1.70, 0.4), 2.45, (-12, 25, 20)),
    (2, 1, (5.60, -2.85, -0.2), 2.20, (15, -30, 8)),
    (3, -1, (6.20, -3.00, 0.2), 3.25, (-12, 30, 12)),
]

# Curated 16-object cover composition. Matrices are column-major glTF transforms.
COVER_LAYOUT_MODES = [
    (0, 0, [5.2, 0, 0, 0, 0, 5.2, 0, 0, 0, 0, 5.2, 0, 4.7918, 2.8267, 9.1949, 1]),
    (2, 1, [1.0128, -0.1911, -2.4955, 0, -0.9303, 2.4705, -0.5668, 0, 2.3235, 1.0725, 0.8608, 0, 0.6231, -2.9528, 6.9161, 1]),
    (2, -1, [-0.4824, 1.2564, 2.3982, 0, 1.4432, 2.1803, -0.8520, 0, -2.2906, 1.1091, -1.0418, 0, -2.1977, 3.4149, 7.3247, 1]),
    (2, 0, [0.7403, 1.2747, 2.3806, 0, 0.2688, 2.4214, -1.3801, 0, -2.6870, 0.5934, 0.5178, 0, 1.3696, 2.7926, 8.3669, 1]),
    (3, 3, [2.2493, -1.2203, 1.2547, 0, 1.6090, 0.6376, -2.2643, 0, 0.6888, 2.4954, 1.1921, 0, -2.3950, -0.8742, 10.5566, 1]),
    (2, -2, [-0.2775, 0.8700, -1.1263, 0, -1.4232, -0.1627, 0.2250, 0, 0.0086, 1.1485, 0.8851, 0, -4.8233, 0.2346, 4.7365, 1]),
    (3, -1, [-1.5953, 1.4833, -0.3078, 0, -0.7184, -1.1343, -1.7428, 0, -1.3337, -1.1632, 1.3069, 0, 0.6379, 0.5308, 10.6592, 1]),
    (3, 2, [-0.7766, 1.6974, -0.8474, 0, -1.7344, -1.0063, -0.4262, 0, -0.7689, 0.5555, 1.8173, 0, -0.9388, 1.3953, 8.3484, 1]),
    (1, -1, [2.6556, -1.6210, 1.4907, 0, 0.9666, 2.9563, 1.4928, 0, -1.9788, -0.7314, 2.7298, 0, -6.8472, 2.7203, 0.7959, 1]),
    (2, 0, [2.8036, 1.9508, -0.7644, 0, -0.5515, -0.5448, -3.4131, 0, -2.0213, 2.8544, -0.1291, 0, -2.4939, -1.4185, 0.6615, 1]),
    (3, -2, [1.0773, -0.6254, 1.6282, 0, 0.0156, 1.9171, 0.7260, 0, -1.7441, -0.3691, 1.0122, 0, -4.3473, 1.1413, 8.9435, 1]),
    (3, -3, [2.4545, 0.4000, -1.1739, 0, 1.1445, 0.2716, 2.4857, 0, 0.4775, -2.7072, 0.0759, 0, 3.4622, -1.6373, 9.6027, 1]),
    (2, 2, [3.4377, -0.1147, -1.6153, 0, 0.4831, 3.6905, 0.7662, 0, 1.5456, -0.8985, 3.3532, 0, -2.3722, -6.7211, -4.2608, 1]),
    (1, 0, [0.5943, 0.6958, -2.2727, 0, 0.3244, 2.2970, 0.7880, 0, 2.3546, -0.4920, 0.4650, 0, -3.0560, 2.2095, 10.5087, 1]),
    (3, 2, [2.0865, 0.6173, -1.1259, 0, -0.7594, 2.3256, -0.1323, 0, 1.0354, 0.4617, 2.1719, 0, 3.3845, 0.5536, 9.8824, 1]),
    (2, 1, [-1.8678, -1.1494, 0.1736, 0, -1.0380, 1.7970, 0.7302, 0, -0.5233, 0.5381, -2.0680, 0, 1.7242, -0.9044, 8.6048, 1]),
]
COVER_LAYOUT_CAMERA = {"camera": {"name": "Cover camera", "type": "perspective", "perspective": {"aspectRatio": 16.0 / 9.0, "yfov": math.pi / 3.0, "zfar": 1000.0, "znear": 0.1}}, "node": {"name": "Cover camera", "matrix": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, -0.1179333, 0.1926496, 14.3926162, 1], "extras": {"layoutEditorCamera": True, "layoutEditorTarget": [-0.1179333, 0.1926496, 0]}}}


def euler_quaternion(rotation):
    """Convert intrinsic XYZ Euler angles in degrees to a glTF quaternion."""
    x, y, z = [math.radians(angle) / 2.0 for angle in rotation]
    cx, cy, cz = math.cos(x), math.cos(y), math.cos(z)
    sx, sy, sz = math.sin(x), math.sin(y), math.sin(z)
    return (sx * cy * cz + cx * sy * sz,
            cx * sy * cz - sx * cy * sz,
            cx * cy * sz + sx * sy * cz,
            cx * cy * cz - sx * sy * sz)


def add_buffer_part(binary, part):
    offset = len(binary)
    return binary + padded(part), offset


def glb_document(source_path):
    """Read the JSON document from a glTF 2.0 binary file."""
    with open(source_path, "rb") as source_file:
        data = source_file.read()
    magic, version, _ = struct.unpack("<4sII", data[:12])
    if magic != b"glTF" or version != 2:
        raise ValueError("camera source must be a glTF 2.0 binary (.glb) file")
    json_length, chunk_type = struct.unpack("<I4s", data[12:20])
    if chunk_type != b"JSON":
        raise ValueError("camera source does not begin with a JSON glTF chunk")
    return json.loads(data[20:20 + json_length])


def camera_setup_from_glb(source_path):
    """Copy camera definitions and camera-node poses from an existing GLB."""
    document = glb_document(source_path)
    source_cameras = document.get("cameras", [])
    camera_nodes = [node for node in document.get("nodes", []) if "camera" in node]
    if not camera_nodes:
        raise ValueError("camera source contains no camera nodes")

    used_cameras, remap = [], {}
    copied_nodes = []
    for node in camera_nodes:
        source_index = node["camera"]
        if source_index not in remap:
            remap[source_index] = len(used_cameras)
            used_cameras.append(source_cameras[source_index])
        copied = {key: value for key, value in node.items()
                  if key in ("name", "matrix", "translation", "rotation", "scale", "extras")}
        copied["camera"] = remap[source_index]
        copied_nodes.append(copied)
    return used_cameras, copied_nodes


def mesh_transforms_from_glb(source_path):
    """Extract mesh-node transforms in scene order from an existing GLB."""
    transforms = []
    for node in glb_document(source_path).get("nodes", []):
        if "mesh" not in node:
            continue
        transforms.append({key: node[key] for key in ("matrix", "translation", "rotation", "scale")
                           if key in node})
    return transforms


def layout_camera_position_from_glb(source_path):
    """Return the saved layout-editor camera position from an existing GLB."""
    for node in glb_document(source_path).get("nodes", []):
        if node.get("extras", {}).get("layoutEditorCamera") is not True:
            continue
        if "matrix" in node:
            return tuple(node["matrix"][12:15])
        if "translation" in node:
            return tuple(node["translation"])
    raise ValueError("camera source contains no saved layout-editor camera")


def cover_layout_from_glb(source_path):
    """Extract a saved cover layout's object matrices and perspective camera."""
    document = glb_document(source_path)
    modes = []
    for node in document.get("nodes", []):
        label = node.get("extras", {}).get("name", "")
        match = re.match(r"Real spherical harmonic l=(-?\d+), m=(-?\d+)$", label)
        if match and "matrix" in node:
            modes.append((int(match.group(1)), int(match.group(2)), node["matrix"]))
    if not modes:
        raise ValueError("cover layout source contains no logical spherical-harmonic object matrices")

    for node in document.get("nodes", []):
        if node.get("extras", {}).get("layoutEditorCamera") is not True:
            continue
        camera = document.get("cameras", [])[node["camera"]]
        copied_node = {key: node[key] for key in ("name", "matrix", "translation", "rotation", "scale", "extras")
                       if key in node}
        return modes, {"camera": camera, "node": copied_node}
    raise ValueError("cover layout source contains no saved layout-editor camera")


def write_gallery_glb(output_path, theta_steps, phi_steps, grid_offset=GRID_NORMAL_OFFSET,
                      camera_from=None, transforms_from=None, modes=None, camera_setup=None):
    """Build and write a GLB containing all gallery objects and mesh-edge grids."""
    modes = list(GALLERY_MODES if modes is None else modes)
    binary = b""
    buffer_views, accessors, meshes, materials, images, textures, nodes = [], [], [], [], [], [], []
    transforms = None
    camera_position = None
    if camera_from and transforms_from:
        camera_position = layout_camera_position_from_glb(camera_from)
        transforms = mesh_transforms_from_glb(transforms_from)
        if len(transforms) != len(modes) or any("matrix" not in transform for transform in transforms):
            raise ValueError("specular grid baking requires a matrix for every mesh node")
    elif modes and len(modes[0]) == 3 and camera_setup:
        transforms = [{"matrix": mode[2]} for mode in modes]
        camera_position = camera_setup["node"].get("matrix", [])[12:15]

    grid_specular_contexts = None
    if transforms:
        grid_specular_contexts = [{
            "matrix": transform["matrix"],
            "camera_position": camera_position,
            "light_position": (-4.0, 7.0, 12.0),
            "power": GRID_SPECULAR_POWER,
            "log_minimum": GRID_LOG_FADE_MINIMUM,
            "log_maximum": GRID_LOG_FADE_MAXIMUM,
        } for transform in transforms]

    for number, mode in enumerate(modes):
        degree, order = mode[:2]
        (positions, normals, grid_positions, positive_indices, negative_indices,
         grid_index_groups) = build_surface(
            degree, order, theta_steps, phi_steps, grid_offset=grid_offset,
            grid_specular_context=(grid_specular_contexts[number] if grid_specular_contexts else None)
        )
        grid_items = sorted(grid_index_groups.items())
        vertex_count = len(positions) // 3
        chunks = [
            (struct.pack("<%sf" % len(positions), *positions), 34962),
            (struct.pack("<%sf" % len(normals), *normals), 34962),
            (struct.pack("<%sf" % len(grid_positions), *grid_positions), 34962),
            (struct.pack("<%sI" % len(positive_indices), *positive_indices), 34963),
            (struct.pack("<%sI" % len(negative_indices), *negative_indices), 34963),
        ] + [(struct.pack("<%sI" % len(indices), *indices), 34963)
             for _, indices in grid_items]
        view_indices = []
        for chunk, target in chunks:
            binary, offset = add_buffer_part(binary, chunk)
            view = {"buffer": 0, "byteOffset": offset, "byteLength": len(chunk)}
            if target is not None:
                view["target"] = target
            view_indices.append(len(buffer_views))
            buffer_views.append(view)

        accessor_base = len(accessors)
        xs, ys, zs = positions[0::3], positions[1::3], positions[2::3]
        accessors.extend([
            {"bufferView": view_indices[0], "componentType": 5126, "count": vertex_count,
             "type": "VEC3", "min": [min(xs), min(ys), min(zs)],
             "max": [max(xs), max(ys), max(zs)]},
            {"bufferView": view_indices[1], "componentType": 5126, "count": vertex_count, "type": "VEC3"},
            {"bufferView": view_indices[2], "componentType": 5126, "count": vertex_count, "type": "VEC3"},
            {"bufferView": view_indices[3], "componentType": 5125, "count": len(positive_indices), "type": "SCALAR"},
            {"bufferView": view_indices[4], "componentType": 5125, "count": len(negative_indices), "type": "SCALAR"},
        ] + [
            {"bufferView": view_indices[5 + index], "componentType": 5125,
             "count": len(indices), "type": "SCALAR"}
            for index, (_, indices) in enumerate(grid_items)
        ])
        material_index = len(materials)
        materials.extend([
            ink_material("Y_{0}^{1}: positive faint ink".format(degree, order), INK_FAINT),
            ink_material("Y_{0}^{1}: negative soft ink".format(degree, order), INK_SOFT),
        ])
        mesh_index = len(meshes)
        label = "Real spherical harmonic l={0}, m={1}".format(degree, order)
        meshes.append({"name": label, "primitives": [
            {"attributes": {"POSITION": accessor_base, "NORMAL": accessor_base + 1},
             "indices": accessor_base + 3, "material": material_index},
            {"attributes": {"POSITION": accessor_base, "NORMAL": accessor_base + 1},
             "indices": accessor_base + 4, "material": material_index + 1},
        ]})
        for index, ((tone, level), _) in enumerate(grid_items):
            opacity = level / float(GRID_OPACITY_STEPS - 1)
            color = INK_OUTLINE if tone == "dark" else INK_SOFT
            materials.append(grid_material(
                "Y_{0}^{1}: {2} mesh grid opacity {3:.2f}".format(
                    degree, order, tone, opacity), color, opacity
            ))
            meshes[-1]["primitives"].append({
                "attributes": {"POSITION": accessor_base + 2, "NORMAL": accessor_base + 1},
                "indices": accessor_base + 5 + index,
                "material": len(materials) - 1, "mode": 1,
            })
        if len(mode) == 3:
            nodes.append({"name": label, "mesh": mesh_index, "matrix": list(mode[2])})
        else:
            _, _, translation, scale, rotation = mode
            nodes.append({"name": label, "mesh": mesh_index, "translation": list(translation),
                          "rotation": list(euler_quaternion(rotation)), "scale": [scale, scale, scale]})

    if transforms_from:
        saved_transforms = mesh_transforms_from_glb(transforms_from)
        object_nodes = [node for node in nodes if "mesh" in node]
        if len(saved_transforms) != len(object_nodes):
            raise ValueError("transform source must contain {0} mesh nodes, found {1}".format(
                len(object_nodes), len(saved_transforms)))
        for node, saved_transform in zip(object_nodes, saved_transforms):
            for key in ("matrix", "translation", "rotation", "scale"):
                node.pop(key, None)
            node.update(saved_transform)

    # Preserve an editor camera pose when requested; otherwise include the
    # generator's default wide camera.
    camera_node = len(nodes)
    if camera_setup:
        cameras = [camera_setup["camera"]]
        camera_node_data = dict(camera_setup["node"])
        camera_node_data["camera"] = 0
        nodes.append(camera_node_data)
    elif camera_from:
        cameras, camera_nodes = camera_setup_from_glb(camera_from)
        nodes.extend(camera_nodes)
    else:
        cameras = [{"name": "Gallery camera", "type": "orthographic",
                    "orthographic": {"xmag": 8.3, "ymag": 4.7, "znear": 0.1, "zfar": 100.0}}]
        nodes.append({"name": "Gallery camera", "camera": 0, "translation": [0, 0, 24]})
    document = {
        "asset": {"version": "2.0", "generator": "generate_spherical_harmonics_gallery_glb.py"},
        "scene": 0,
        "scenes": [{"name": "Floating spherical-harmonics gallery", "nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "cameras": cameras,
        "meshes": meshes,
        "materials": materials,
        "extensionsUsed": ["KHR_materials_unlit"],
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": buffer_views,
        "accessors": accessors,
        "extras": {"cameraNode": camera_node,
                   "colorMeaning": "Faint ink (#e8e4d8): positive; soft ink (#55503f): negative and positive-lobe grid; outline ink (#14130f): negative-lobe grid.",
                   "grid": "Every second selected latitude and longitude mesh edge, not a texture.",
                   "gridNormalOffset": grid_offset},
    }
    json_bytes = json.dumps(document, separators=(",", ":")).encode("utf-8")
    json_bytes += b" " * ((4 - len(json_bytes) % 4) % 4)
    glb = (struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(json_bytes) + 8 + len(binary)) +
           struct.pack("<I4s", len(json_bytes), b"JSON") + json_bytes +
           struct.pack("<I4s", len(binary), b"BIN\x00") + binary)
    with open(output_path, "wb") as output_file:
        output_file.write(glb)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", default="spherical_harmonics_gallery.glb",
                        help="output GLB path (default: spherical_harmonics_gallery.glb)")
    parser.add_argument("--theta-steps", type=int, default=72,
                        help="latitude subdivisions per object (default: 72)")
    parser.add_argument("--phi-steps", type=int, default=144,
                        help="longitude subdivisions per object (default: 144)")
    parser.add_argument("--grid-offset", type=float, default=GRID_NORMAL_OFFSET,
                        help="normal offset for mesh-edge grid vertices (default: %(default)s)")
    parser.add_argument("--camera-from", help="copy camera definitions and poses from an existing GLB")
    parser.add_argument("--transforms-from", help="copy mesh-node transforms from an existing GLB")
    parser.add_argument("--mode-index", type=int, action="append", dest="mode_indices",
                        help="include one zero-based gallery mode; repeat to keep a selected subset")
    parser.add_argument("--cover-layout-from",
                        help="copy logical transforms and the perspective camera from a saved cover GLB")
    parser.add_argument("--cover-layout", action="store_true",
                        help="generate the built-in 16-object cover composition")
    args = parser.parse_args()
    if args.theta_steps < 2 or args.phi_steps < 3:
        parser.error("--theta-steps must be >= 2 and --phi-steps must be >= 3")
    if args.grid_offset < 0.0:
        parser.error("--grid-offset must be non-negative")
    if (args.cover_layout or args.cover_layout_from) and (args.camera_from or args.transforms_from or args.mode_indices):
        parser.error("cover layout options cannot be combined with camera, transform, or mode-index options")
    if args.cover_layout and args.cover_layout_from:
        parser.error("--cover-layout and --cover-layout-from are mutually exclusive")
    if args.mode_indices and any(index < 0 or index >= len(GALLERY_MODES) for index in args.mode_indices):
        parser.error("--mode-index must be between 0 and {0}".format(len(GALLERY_MODES) - 1))
    camera_setup = None
    if args.cover_layout:
        modes, camera_setup = COVER_LAYOUT_MODES, COVER_LAYOUT_CAMERA
    elif args.cover_layout_from:
        modes, camera_setup = cover_layout_from_glb(args.cover_layout_from)
    else:
        modes = [GALLERY_MODES[index] for index in args.mode_indices] if args.mode_indices else GALLERY_MODES
    write_gallery_glb(args.output, args.theta_steps, args.phi_steps, args.grid_offset,
                      args.camera_from, args.transforms_from, modes, camera_setup)
    print("Wrote {0} with {1} ink-rendered spherical-harmonic objects.".format(
        args.output, len(modes)))


if __name__ == "__main__":
    main()
