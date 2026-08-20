#!/usr/bin/env python3
"""Export an ink-rendered real spherical-harmonic surface as a self-contained GLB.

The surface radius is ``abs(Y_l^m(theta, phi))``.  Its two signs use a light
and dark ink, while selected latitude and longitude mesh edges form a grid
that follows the stretched harmonic surface.

Examples:
    python3 generate_spherical_harmonics_glb.py 3 2
    python3 generate_spherical_harmonics_glb.py 4 -3 -o sh_4_neg3.glb
"""

from __future__ import print_function

import argparse
import json
import math
import struct
import zlib


INK_FAINT = (0x8D, 0x87, 0x6E, 0xFF)
INK_SOFT = (0x55, 0x50, 0x3F, 0xFF)
# Grid vertices are deliberately separate from the surface vertices and moved
# outward along their normals. Raise this only if a viewer still z-fights.
GRID_NORMAL_OFFSET = 0.004
EPSILON = 1.0e-10


def associated_legendre(degree, order, x):
    """Return P_degree^order(x), including the Condon--Shortley phase."""
    if order < 0 or order > degree:
        raise ValueError("order must satisfy 0 <= order <= degree")

    # Numerical roundoff can take cos(theta) just beyond the valid interval.
    x = max(-1.0, min(1.0, x))
    p_mm = 1.0
    if order:
        root = math.sqrt(max(0.0, 1.0 - x * x))
        factor = 1.0
        for _ in range(order):
            p_mm *= -factor * root
            factor += 2.0
    if degree == order:
        return p_mm

    p_mmp1 = x * (2 * order + 1) * p_mm
    if degree == order + 1:
        return p_mmp1

    previous, current = p_mm, p_mmp1
    for ell in range(order + 2, degree + 1):
        following = ((2 * ell - 1) * x * current -
                     (ell + order - 1) * previous) / float(ell - order)
        previous, current = current, following
    return current


def real_spherical_harmonic(degree, order, theta, phi):
    """Evaluate the orthonormal, real-valued Y_degree^order(theta, phi).

    ``theta`` is the polar angle and ``phi`` is the azimuth.  Positive orders
    use cosine terms; negative orders use sine terms.  This is a real basis,
    so the resulting signed scalar can directly drive both radius and colour.
    """
    absolute_order = abs(order)
    normalization = math.sqrt(
        (2.0 * degree + 1.0) / (4.0 * math.pi) *
        math.factorial(degree - absolute_order) /
        float(math.factorial(degree + absolute_order))
    )
    value = normalization * associated_legendre(
        degree, absolute_order, math.cos(theta)
    )
    if order > 0:
        return math.sqrt(2.0) * value * math.cos(order * phi)
    if order < 0:
        return math.sqrt(2.0) * value * math.sin(absolute_order * phi)
    return value


def png_rgba(width, height, pixels):
    """Encode RGBA bytes as a minimal lossless PNG using only the stdlib."""
    scanlines = bytearray()
    row_size = width * 4
    for row in range(height):
        scanlines.append(0)  # PNG filter: None
        start = row * row_size
        scanlines.extend(pixels[start:start + row_size])

    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data +
                struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))

    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(bytes(scanlines), 9)) +
            chunk(b"IEND", b""))


def unit_normal(position):
    length = math.sqrt(sum(component * component for component in position))
    if length < EPSILON:
        return (0.0, 0.0, 1.0)
    return tuple(component / length for component in position)


def padded(binary):
    return binary + b"\x00" * ((4 - len(binary) % 4) % 4)


def write_glb(output_path, positions, normals, grid_positions, positive_indices,
              negative_indices, grid_indices, name):
    """Write a lit GLB with signed surfaces and selected mesh-edge lines."""
    position_bytes = struct.pack("<%sf" % len(positions), *positions)
    normal_bytes = struct.pack("<%sf" % len(normals), *normals)
    grid_position_bytes = struct.pack("<%sf" % len(grid_positions), *grid_positions)
    positive_index_bytes = struct.pack("<%sI" % len(positive_indices), *positive_indices)
    negative_index_bytes = struct.pack("<%sI" % len(negative_indices), *negative_indices)
    grid_index_bytes = struct.pack("<%sI" % len(grid_indices), *grid_indices)
    parts = [position_bytes, normal_bytes, grid_position_bytes, positive_index_bytes,
             negative_index_bytes, grid_index_bytes]
    offsets, binary = [], b""
    for part in parts:
        offsets.append(len(binary))
        binary += padded(part)

    vertex_count = len(positions) // 3
    xs = positions[0::3]
    ys = positions[1::3]
    zs = positions[2::3]
    document = {
        "asset": {"version": "2.0", "generator": "generate_spherical_harmonics_glb.py"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": name}],
        "meshes": [{"name": name, "primitives": [
            {"attributes": {"POSITION": 0, "NORMAL": 1}, "indices": 3, "material": 0},
            {"attributes": {"POSITION": 0, "NORMAL": 1}, "indices": 4, "material": 1},
            {"attributes": {"POSITION": 2}, "indices": 5, "material": 2, "mode": 1},
        ]}],
        "materials": [
            ink_material("Positive ink (faint)", INK_FAINT),
            ink_material("Negative ink (soft)", INK_SOFT),
            grid_material("Surface grid (faint ink)", INK_FAINT),
        ],
        "extensionsUsed": ["KHR_materials_unlit"],
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": offsets[0], "byteLength": len(position_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": offsets[1], "byteLength": len(normal_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": offsets[2], "byteLength": len(grid_position_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": offsets[3], "byteLength": len(positive_index_bytes), "target": 34963},
            {"buffer": 0, "byteOffset": offsets[4], "byteLength": len(negative_index_bytes), "target": 34963},
            {"buffer": 0, "byteOffset": offsets[5], "byteLength": len(grid_index_bytes), "target": 34963}
        ],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": vertex_count,
             "type": "VEC3", "min": [min(xs), min(ys), min(zs)],
             "max": [max(xs), max(ys), max(zs)]},
            {"bufferView": 1, "componentType": 5126, "count": vertex_count, "type": "VEC3"},
            {"bufferView": 2, "componentType": 5126, "count": vertex_count, "type": "VEC3"},
            {"bufferView": 3, "componentType": 5125, "count": len(positive_indices), "type": "SCALAR"},
            {"bufferView": 4, "componentType": 5125, "count": len(negative_indices), "type": "SCALAR"},
            {"bufferView": 5, "componentType": 5125, "count": len(grid_indices), "type": "SCALAR"},
        ],
    }
    json_bytes = json.dumps(document, separators=(",", ":")).encode("utf-8")
    json_bytes += b" " * ((4 - len(json_bytes) % 4) % 4)
    glb = (struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(json_bytes) + 8 + len(binary)) +
           struct.pack("<I4s", len(json_bytes), b"JSON") + json_bytes +
           struct.pack("<I4s", len(binary), b"BIN\x00") + binary)
    with open(output_path, "wb") as output_file:
        output_file.write(glb)


def ink_material(name, rgba):
    """Return a non-metallic ink material that responds to scene lighting."""
    return {
        "name": name,
        "pbrMetallicRoughness": {
            "baseColorFactor": [component / 255.0 for component in rgba],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.55,
        },
    }


def grid_material(name, rgba):
    """Return a constant-color line material so grid edges are not light-dependent."""
    return {
        "name": name,
        "pbrMetallicRoughness": {"baseColorFactor": [component / 255.0 for component in rgba]},
        "extensions": {"KHR_materials_unlit": {}},
    }


def build_surface(degree, order, theta_steps, phi_steps, grid_step=8,
                  grid_offset=GRID_NORMAL_OFFSET):
    """Build surface triangles plus sparse grid edges from the same mesh."""
    vertices = []
    values = []
    for row in range(theta_steps + 1):
        theta = math.pi * row / float(theta_steps)
        row_values = []
        for column in range(phi_steps + 1):
            phi = 2.0 * math.pi * column / float(phi_steps)
            value = real_spherical_harmonic(degree, order, theta, phi)
            row_values.append(value)
            radius = abs(value)
            position = (radius * math.sin(theta) * math.cos(phi),
                        radius * math.sin(theta) * math.sin(phi),
                        radius * math.cos(theta))
            vertices.append(position)
        values.append(row_values)

    positive_indices, negative_indices, all_indices = [], [], []
    row_width = phi_steps + 1
    for row in range(theta_steps):
        for column in range(phi_steps):
            top_left = row * row_width + column
            bottom_left = top_left + row_width
            triangles = ((top_left, bottom_left, top_left + 1),
                         (top_left + 1, bottom_left, bottom_left + 1))
            for triangle in triangles:
                all_indices.extend(triangle)
                # One material per face keeps the two ink tones crisp.
                average = sum(values[index // row_width][index % row_width] for index in triangle) / 3.0
                (positive_indices if average >= 0.0 else negative_indices).extend(triangle)

    # These are actual surface mesh edges, not a projected or texture grid.
    # Offset from poles avoids a visually dense star where all longitude edges meet.
    grid_indices = []
    for row in range(grid_step, theta_steps, grid_step):
        for column in range(phi_steps):
            start = row * row_width + column
            grid_indices.extend((start, start + 1))
    for column in range(0, phi_steps, grid_step):
        for row in range(1, theta_steps - 1):
            start = row * row_width + column
            grid_indices.extend((start, start + row_width))

    # Area-weighted vertex normals make the PBR material follow the actual
    # harmonic surface rather than merely pointing away from the origin.
    normal_sums = [[0.0, 0.0, 0.0] for _ in vertices]
    for start in range(0, len(all_indices), 3):
        first, second, third = (vertices[all_indices[start + offset]] for offset in range(3))
        edge_one = tuple(second[i] - first[i] for i in range(3))
        edge_two = tuple(third[i] - first[i] for i in range(3))
        face_normal = (edge_one[1] * edge_two[2] - edge_one[2] * edge_two[1],
                       edge_one[2] * edge_two[0] - edge_one[0] * edge_two[2],
                       edge_one[0] * edge_two[1] - edge_one[1] * edge_two[0])
        for vertex_index in (all_indices[start], all_indices[start + 1], all_indices[start + 2]):
            for axis in range(3):
                normal_sums[vertex_index][axis] += face_normal[axis]
    normals = [component for normal in normal_sums for component in unit_normal(normal)]
    positions = [component for vertex in vertices for component in vertex]
    grid_positions = [position + grid_offset * normal for position, normal in zip(positions, normals)]
    return positions, normals, grid_positions, positive_indices, negative_indices, grid_indices


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("degree", type=int, help="non-negative degree l")
    parser.add_argument("order", type=int, help="order m, with -l <= m <= l")
    parser.add_argument("-o", "--output", help="output GLB path (default: spherical_harmonic_l{l}_m{m}.glb)")
    parser.add_argument("--theta-steps", type=int, default=192, help="latitude subdivisions (default: 192)")
    parser.add_argument("--phi-steps", type=int, default=384, help="longitude subdivisions (default: 384)")
    parser.add_argument("--grid-offset", type=float, default=GRID_NORMAL_OFFSET,
                        help="normal offset for mesh-edge grid vertices (default: %(default)s)")
    args = parser.parse_args()
    if args.degree < 0 or abs(args.order) > args.degree:
        parser.error("degree must be >= 0 and order must satisfy -degree <= order <= degree")
    if args.theta_steps < 2 or args.phi_steps < 3:
        parser.error("--theta-steps must be >= 2 and --phi-steps must be >= 3")
    if args.grid_offset < 0.0:
        parser.error("--grid-offset must be non-negative")

    output = args.output or "spherical_harmonic_l{0}_m{1}.glb".format(args.degree, args.order)
    surface = build_surface(args.degree, args.order, args.theta_steps, args.phi_steps,
                            grid_offset=args.grid_offset)
    write_glb(output, *surface, name="Real spherical harmonic l={0}, m={1}".format(args.degree, args.order))
    print("Wrote {0} (l={1}, m={2}; faint ink=positive, soft ink=negative)".format(
        output, args.degree, args.order))


if __name__ == "__main__":
    main()
