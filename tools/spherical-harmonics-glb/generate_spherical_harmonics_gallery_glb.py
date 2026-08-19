#!/usr/bin/env python3
"""Create a floating spherical-harmonics gallery as one textured GLB scene.

The included camera frames the scene in a wide, illustration-like composition.
Each object has its own embedded sign texture: blue means positive and yellow
means negative for the real spherical-harmonic basis function.
"""

from __future__ import print_function

import argparse
import json
import math
import struct

from generate_spherical_harmonics_glb import build_surface, padded


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


def write_gallery_glb(output_path, theta_steps, phi_steps):
    """Build and write a GLB containing all gallery objects and textures."""
    binary = b""
    buffer_views, accessors, meshes, materials, images, textures, nodes = [], [], [], [], [], [], []

    for number, (degree, order, translation, scale, rotation) in enumerate(GALLERY_MODES):
        positions, normals, uvs, indices, texture_png = build_surface(
            degree, order, theta_steps, phi_steps
        )
        vertex_count = len(positions) // 3
        chunks = [
            (struct.pack("<%sf" % len(positions), *positions), 34962),
            (struct.pack("<%sf" % len(normals), *normals), 34962),
            (struct.pack("<%sf" % len(uvs), *uvs), 34962),
            (struct.pack("<%sI" % len(indices), *indices), 34963),
            (texture_png, None),
        ]
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
            {"bufferView": view_indices[2], "componentType": 5126, "count": vertex_count, "type": "VEC2"},
            {"bufferView": view_indices[3], "componentType": 5125, "count": len(indices), "type": "SCALAR"},
        ])
        material_index = len(materials)
        texture_index = len(textures)
        materials.append({"name": "Y_{0}^{1}: blue positive, yellow negative".format(degree, order),
                          "pbrMetallicRoughness": {"baseColorTexture": {"index": texture_index},
                                                   "metallicFactor": 0.0, "roughnessFactor": 0.55}})
        images.append({"bufferView": view_indices[4], "mimeType": "image/png",
                       "name": "Y_{0}^{1}_signs.png".format(degree, order)})
        textures.append({"sampler": 0, "source": number})
        mesh_index = len(meshes)
        label = "Real spherical harmonic l={0}, m={1}".format(degree, order)
        meshes.append({"name": label, "primitives": [{"attributes": {
            "POSITION": accessor_base, "NORMAL": accessor_base + 1, "TEXCOORD_0": accessor_base + 2},
            "indices": accessor_base + 3, "material": material_index}]})
        nodes.append({"name": label, "mesh": mesh_index, "translation": list(translation),
                      "rotation": list(euler_quaternion(rotation)), "scale": [scale, scale, scale]})

    # A camera lets GLB viewers immediately show the intended wide composition.
    camera_node = len(nodes)
    nodes.append({"name": "Gallery camera", "camera": 0, "translation": [0, 0, 24]})
    document = {
        "asset": {"version": "2.0", "generator": "generate_spherical_harmonics_gallery_glb.py"},
        "scene": 0,
        "scenes": [{"name": "Floating spherical-harmonics gallery", "nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "cameras": [{"name": "Gallery camera", "type": "orthographic",
                     "orthographic": {"xmag": 8.3, "ymag": 4.7, "znear": 0.1, "zfar": 100.0}}],
        "meshes": meshes,
        "materials": materials,
        "samplers": [{"magFilter": 9728, "minFilter": 9728, "wrapS": 10497, "wrapT": 33071}],
        "images": images,
        "textures": textures,
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": buffer_views,
        "accessors": accessors,
        "extras": {"cameraNode": camera_node, "colorMeaning": "Blue: positive; yellow: negative."},
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
    args = parser.parse_args()
    if args.theta_steps < 2 or args.phi_steps < 3:
        parser.error("--theta-steps must be >= 2 and --phi-steps must be >= 3")
    write_gallery_glb(args.output, args.theta_steps, args.phi_steps)
    print("Wrote {0} with {1} textured spherical-harmonic objects.".format(
        args.output, len(GALLERY_MODES)))


if __name__ == "__main__":
    main()
