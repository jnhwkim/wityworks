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


# Near-white warm ink keeps the positive sign and surface grid airy on paper.
INK_FAINT = (0xE8, 0xE4, 0xD8, 0xFF)
INK_SOFT = (0x55, 0x50, 0x3F, 0xFF)
INK_OUTLINE = (0x14, 0x13, 0x0F, 0xFF)
GRID_EDGE_STEP = 2
# Approximate the editor's key light. Grid edges whose normal is strongly
# aligned with this direction fade through discrete opacity levels, preventing
# highlights from filling with competing line detail.
GRID_KEY_LIGHT = (-4.0 / 13.0, 7.0 / 13.0, 12.0 / 13.0)
GRID_FADE_START = -0.80
GRID_FADE_END = 0.95
GRID_OPACITY_STEPS = 16
GRID_SPECULAR_POWER = 28.0
GRID_LOG_FADE_MINIMUM = -10.0
GRID_LOG_FADE_MAXIMUM = 0.0
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


def transform_point(matrix, point):
    """Transform a point by a glTF column-major matrix."""
    return tuple(sum(matrix[column * 4 + row] * point[column] for column in range(3)) +
                 matrix[12 + row] for row in range(3))


def transform_direction(matrix, direction):
    """Transform a direction by the linear part of a glTF matrix."""
    return unit_normal(tuple(sum(matrix[column * 4 + row] * direction[column]
                                 for column in range(3)) for row in range(3)))


def padded(binary):
    return binary + b"\x00" * ((4 - len(binary) % 4) % 4)


def write_glb(output_path, positions, normals, grid_positions, positive_indices,
              negative_indices, grid_index_groups, name):
    """Write a lit GLB with signed surfaces and selected mesh-edge lines."""
    position_bytes = struct.pack("<%sf" % len(positions), *positions)
    normal_bytes = struct.pack("<%sf" % len(normals), *normals)
    grid_position_bytes = struct.pack("<%sf" % len(grid_positions), *grid_positions)
    positive_index_bytes = struct.pack("<%sI" % len(positive_indices), *positive_indices)
    negative_index_bytes = struct.pack("<%sI" % len(negative_indices), *negative_indices)
    grid_items = sorted(grid_index_groups.items())
    grid_index_bytes = [struct.pack("<%sI" % len(indices), *indices)
                        for _, indices in grid_items]
    parts = [position_bytes, normal_bytes, grid_position_bytes, positive_index_bytes,
             negative_index_bytes] + grid_index_bytes
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
        ]}],
        "materials": [
            ink_material("Positive ink (faint)", INK_FAINT),
            ink_material("Negative ink (soft)", INK_SOFT),
        ],
        "extensionsUsed": ["KHR_materials_unlit"],
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": offsets[0], "byteLength": len(position_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": offsets[1], "byteLength": len(normal_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": offsets[2], "byteLength": len(grid_position_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": offsets[3], "byteLength": len(positive_index_bytes), "target": 34963},
            {"buffer": 0, "byteOffset": offsets[4], "byteLength": len(negative_index_bytes), "target": 34963},
        ] + [
            {"buffer": 0, "byteOffset": offsets[5 + index], "byteLength": len(part), "target": 34963}
            for index, part in enumerate(grid_index_bytes)
        ],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": vertex_count,
             "type": "VEC3", "min": [min(xs), min(ys), min(zs)],
             "max": [max(xs), max(ys), max(zs)]},
            {"bufferView": 1, "componentType": 5126, "count": vertex_count, "type": "VEC3"},
            {"bufferView": 2, "componentType": 5126, "count": vertex_count, "type": "VEC3"},
            {"bufferView": 3, "componentType": 5125, "count": len(positive_indices), "type": "SCALAR"},
            {"bufferView": 4, "componentType": 5125, "count": len(negative_indices), "type": "SCALAR"},
        ] + [
            {"bufferView": 5 + index, "componentType": 5125, "count": len(indices), "type": "SCALAR"}
            for index, (_, indices) in enumerate(grid_items)
        ],
    }
    for index, ((tone, level), _) in enumerate(grid_items):
        opacity = level / float(GRID_OPACITY_STEPS - 1)
        color = INK_OUTLINE if tone == "dark" else INK_SOFT
        document["materials"].append(grid_material(
            "{0} grid, opacity {1:.2f}".format(tone, opacity), color, opacity
        ))
        document["meshes"][0]["primitives"].append({
            "attributes": {"POSITION": 2, "NORMAL": 1}, "indices": 5 + index,
            "material": 2 + index, "mode": 1,
        })
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


def grid_material(name, rgba, opacity=1.0):
    """Return a constant-color line material so grid edges are not light-dependent."""
    return {
        "name": name,
        "pbrMetallicRoughness": {
            "baseColorFactor": [component / 255.0 for component in rgba[:3]] + [opacity]
        },
        "extensions": {"KHR_materials_unlit": {}},
        "alphaMode": "BLEND" if opacity < 1.0 else "OPAQUE",
    }


def build_surface(degree, order, theta_steps, phi_steps, grid_step=GRID_EDGE_STEP,
                  grid_offset=GRID_NORMAL_OFFSET, grid_opacity_thresholds=None,
                  return_grid_alignments=False, grid_specular_context=None):
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
    grid_edges = []
    def add_grid_edge(first, second):
        grid_edges.append((first, second))

    for row in range(grid_step, theta_steps, grid_step):
        for column in range(phi_steps):
            start = row * row_width + column
            add_grid_edge(start, start + 1)
    for column in range(0, phi_steps, grid_step):
        for row in range(1, theta_steps - 1):
            start = row * row_width + column
            add_grid_edge(start, start + row_width)

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
    edge_samples = []
    for first, second in grid_edges:
        average_normal = unit_normal(tuple(
            normals[first * 3 + axis] + normals[second * 3 + axis] for axis in range(3)
        ))
        light_alignment = sum(average_normal[axis] * GRID_KEY_LIGHT[axis] for axis in range(3))
        edge_samples.append((first, second, light_alignment))

    grid_index_groups = {}
    for first, second, light_alignment in edge_samples:
        if grid_specular_context is not None:
            matrix = grid_specular_context["matrix"]
            first_position = transform_point(matrix, vertices[first])
            second_position = transform_point(matrix, vertices[second])
            world_position = tuple((first_position[axis] + second_position[axis]) * 0.5
                                   for axis in range(3))
            average_normal = unit_normal(tuple(
                normals[first * 3 + axis] + normals[second * 3 + axis] for axis in range(3)
            ))
            world_normal = transform_direction(matrix, average_normal)
            light_direction = unit_normal(tuple(
                grid_specular_context["light_position"][axis] - world_position[axis]
                for axis in range(3)
            ))
            view_direction = unit_normal(tuple(
                grid_specular_context["camera_position"][axis] - world_position[axis]
                for axis in range(3)
            ))
            half_vector = unit_normal(tuple(light_direction[axis] + view_direction[axis]
                                             for axis in range(3)))
            specular = (max(sum(world_normal[axis] * half_vector[axis] for axis in range(3)), 0.0) **
                        grid_specular_context["power"] *
                        max(sum(world_normal[axis] * light_direction[axis] for axis in range(3)), 0.0))
            log_specular = math.log10(max(specular, 1.0e-6))
            visibility = 1.0 - max(0.0, min(1.0, (log_specular -
                grid_specular_context["log_minimum"]) /
                (grid_specular_context["log_maximum"] - grid_specular_context["log_minimum"])))
            level = int(round(visibility * (GRID_OPACITY_STEPS - 1)))
        elif grid_opacity_thresholds is None:
            fade = max(0.0, min(1.0, (light_alignment - GRID_FADE_START) /
                                 (GRID_FADE_END - GRID_FADE_START)))
            level = int(round((1.0 - fade) * (GRID_OPACITY_STEPS - 1)))
        else:
            # Low light alignment is opaque; high alignment is transparent.
            level = sum(light_alignment < threshold for threshold in grid_opacity_thresholds)
        first_value = values[first // row_width][first % row_width]
        second_value = values[second // row_width][second % row_width]
        tone = "dark" if first_value + second_value < 0.0 else "soft"
        grid_index_groups.setdefault((tone, level), []).extend((first, second))
    positions = [component for vertex in vertices for component in vertex]
    grid_positions = [position + grid_offset * normal for position, normal in zip(positions, normals)]
    result = (positions, normals, grid_positions, positive_indices, negative_indices, grid_index_groups)
    return result + ([alignment for _, _, alignment in edge_samples],) if return_grid_alignments else result


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
