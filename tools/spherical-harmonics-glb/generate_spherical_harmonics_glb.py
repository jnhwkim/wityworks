#!/usr/bin/env python3
"""Export a textured real spherical-harmonic surface as a self-contained GLB.

The surface radius is ``abs(Y_l^m(theta, phi))``.  The embedded texture is
blue where the real harmonic is positive and yellow where it is negative.

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


BLUE = (55, 145, 184, 255)
YELLOW = (245, 188, 62, 255)
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


def write_glb(output_path, positions, normals, uvs, indices, texture_png, name):
    """Write a glTF 2.0 binary file with an embedded texture and PBR material."""
    position_bytes = struct.pack("<%sf" % len(positions), *positions)
    normal_bytes = struct.pack("<%sf" % len(normals), *normals)
    uv_bytes = struct.pack("<%sf" % len(uvs), *uvs)
    index_bytes = struct.pack("<%sI" % len(indices), *indices)
    parts = [position_bytes, normal_bytes, uv_bytes, index_bytes, texture_png]
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
        "meshes": [{"name": name, "primitives": [{
            "attributes": {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2},
            "indices": 3, "material": 0
        }]}],
        "materials": [{"name": "Signed real spherical harmonic", "pbrMetallicRoughness": {
            "baseColorTexture": {"index": 0}, "metallicFactor": 0.0,
            "roughnessFactor": 0.58
        }}],
        "textures": [{"sampler": 0, "source": 0}],
        "samplers": [{"magFilter": 9728, "minFilter": 9728,
                      "wrapS": 10497, "wrapT": 33071}],
        "images": [{"bufferView": 4, "mimeType": "image/png", "name": "sign-colors.png"}],
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": offsets[0], "byteLength": len(position_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": offsets[1], "byteLength": len(normal_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": offsets[2], "byteLength": len(uv_bytes), "target": 34962},
            {"buffer": 0, "byteOffset": offsets[3], "byteLength": len(index_bytes), "target": 34963},
            {"buffer": 0, "byteOffset": offsets[4], "byteLength": len(texture_png)}
        ],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": vertex_count,
             "type": "VEC3", "min": [min(xs), min(ys), min(zs)],
             "max": [max(xs), max(ys), max(zs)]},
            {"bufferView": 1, "componentType": 5126, "count": vertex_count, "type": "VEC3"},
            {"bufferView": 2, "componentType": 5126, "count": vertex_count, "type": "VEC2"},
            {"bufferView": 3, "componentType": 5125, "count": len(indices), "type": "SCALAR"}
        ]
    }
    json_bytes = json.dumps(document, separators=(",", ":")).encode("utf-8")
    json_bytes += b" " * ((4 - len(json_bytes) % 4) % 4)
    glb = (struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(json_bytes) + 8 + len(binary)) +
           struct.pack("<I4s", len(json_bytes), b"JSON") + json_bytes +
           struct.pack("<I4s", len(binary), b"BIN\x00") + binary)
    with open(output_path, "wb") as output_file:
        output_file.write(glb)


def build_surface(degree, order, theta_steps, phi_steps):
    vertices, uvs, texture = [], [], bytearray()
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
            uvs.extend((column / float(phi_steps), 1.0 - row / float(theta_steps)))
        values.append(row_values)

    # Texture rows go north to south, matching the UV coordinates above.
    for row in range(theta_steps + 1):
        for column in range(phi_steps + 1):
            texture.extend(BLUE if values[row][column] >= 0.0 else YELLOW)

    indices = []
    row_width = phi_steps + 1
    for row in range(theta_steps):
        for column in range(phi_steps):
            top_left = row * row_width + column
            bottom_left = top_left + row_width
            indices.extend((top_left, bottom_left, top_left + 1,
                            top_left + 1, bottom_left, bottom_left + 1))

    # Area-weighted vertex normals make the PBR material follow the actual
    # harmonic surface rather than merely pointing away from the origin.
    normal_sums = [[0.0, 0.0, 0.0] for _ in vertices]
    for start in range(0, len(indices), 3):
        first, second, third = (vertices[indices[start + offset]] for offset in range(3))
        edge_one = tuple(second[i] - first[i] for i in range(3))
        edge_two = tuple(third[i] - first[i] for i in range(3))
        face_normal = (edge_one[1] * edge_two[2] - edge_one[2] * edge_two[1],
                       edge_one[2] * edge_two[0] - edge_one[0] * edge_two[2],
                       edge_one[0] * edge_two[1] - edge_one[1] * edge_two[0])
        for vertex_index in (indices[start], indices[start + 1], indices[start + 2]):
            for axis in range(3):
                normal_sums[vertex_index][axis] += face_normal[axis]
    normals = [component for normal in normal_sums for component in unit_normal(normal)]
    positions = [component for vertex in vertices for component in vertex]
    return positions, normals, uvs, indices, png_rgba(phi_steps + 1, theta_steps + 1, texture)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("degree", type=int, help="non-negative degree l")
    parser.add_argument("order", type=int, help="order m, with -l <= m <= l")
    parser.add_argument("-o", "--output", help="output GLB path (default: spherical_harmonic_l{l}_m{m}.glb)")
    parser.add_argument("--theta-steps", type=int, default=192, help="latitude subdivisions (default: 192)")
    parser.add_argument("--phi-steps", type=int, default=384, help="longitude subdivisions (default: 384)")
    args = parser.parse_args()
    if args.degree < 0 or abs(args.order) > args.degree:
        parser.error("degree must be >= 0 and order must satisfy -degree <= order <= degree")
    if args.theta_steps < 2 or args.phi_steps < 3:
        parser.error("--theta-steps must be >= 2 and --phi-steps must be >= 3")

    output = args.output or "spherical_harmonic_l{0}_m{1}.glb".format(args.degree, args.order)
    surface = build_surface(args.degree, args.order, args.theta_steps, args.phi_steps)
    write_glb(output, *surface, name="Real spherical harmonic l={0}, m={1}".format(args.degree, args.order))
    print("Wrote {0} (l={1}, m={2}; blue=positive, yellow=negative)".format(
        output, args.degree, args.order))


if __name__ == "__main__":
    main()
