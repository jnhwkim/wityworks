#!/usr/bin/env python3
"""Render a fast PNG preview of the floating spherical-harmonics GLB scene.

This compact, dependency-free orthographic renderer uses the same mode list,
camera framing, geometry, mesh-edge grid, and ink colours as the GLB generator. It is meant
for composition review before a final render in Blender or another DCC tool.
"""

from __future__ import print_function

import argparse
import math
from array import array

from generate_spherical_harmonics_glb import INK_FAINT, INK_SOFT, png_rgba, real_spherical_harmonic
from generate_spherical_harmonics_gallery_glb import GALLERY_MODES, euler_quaternion


CAMERA_XMAG = 8.3
CAMERA_YMAG = 4.7
CAMERA_Z = 24.0
BACKGROUND = (250, 249, 246, 255)


def rotate(point, quaternion):
    """Rotate a point by a glTF quaternion."""
    x, y, z, w = quaternion
    px, py, pz = point
    # q * point * conjugate(q), expanded to avoid allocating quaternion pairs.
    ix = w * px + y * pz - z * py
    iy = w * py + z * px - x * pz
    iz = w * pz + x * py - y * px
    iw = -x * px - y * py - z * pz
    return (ix * w + iw * -x + iy * -z - iz * -y,
            iy * w + iw * -y + iz * -x - ix * -z,
            iz * w + iw * -z + ix * -y - iy * -x)


def draw_triangle(pixels, depths, width, height, triangle, rgba):
    """Rasterize one flat-shaded triangle with a depth buffer."""
    (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = triangle
    minimum_x = max(0, int(math.floor(min(x0, x1, x2))))
    maximum_x = min(width - 1, int(math.ceil(max(x0, x1, x2))))
    minimum_y = max(0, int(math.floor(min(y0, y1, y2))))
    maximum_y = min(height - 1, int(math.ceil(max(y0, y1, y2))))
    denominator = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(denominator) < 1.0e-9:
        return
    for y in range(minimum_y, maximum_y + 1):
        for x in range(minimum_x, maximum_x + 1):
            one = ((y1 - y2) * (x - x2) + (x2 - x1) * (y - y2)) / denominator
            two = ((y2 - y0) * (x - x2) + (x0 - x2) * (y - y2)) / denominator
            three = 1.0 - one - two
            if one < 0.0 or two < 0.0 or three < 0.0:
                continue
            index = y * width + x
            depth = one * z0 + two * z1 + three * z2
            if depth >= depths[index]:
                continue
            depths[index] = depth
            pixel_index = index * 4
            pixels[pixel_index:pixel_index + 4] = bytes(rgba)


def projected(point, width, height):
    """Project world coordinates through the gallery's orthographic camera."""
    x, y, z = point
    return ((x + CAMERA_XMAG) / (2.0 * CAMERA_XMAG) * (width - 1),
            (CAMERA_YMAG - y) / (2.0 * CAMERA_YMAG) * (height - 1),
            CAMERA_Z - z)


def draw_line(pixels, depths, width, height, first, second, rgba):
    """Draw a one-pixel mesh edge when it belongs to the visible surface."""
    x0, y0, z0 = first
    x1, y1, z1 = second
    steps = max(1, int(max(abs(x1 - x0), abs(y1 - y0))))
    for step in range(steps + 1):
        fraction = step / float(steps)
        x = int(round(x0 + (x1 - x0) * fraction))
        y = int(round(y0 + (y1 - y0) * fraction))
        if not (0 <= x < width and 0 <= y < height):
            continue
        index = y * width + x
        depth = z0 + (z1 - z0) * fraction
        if depth <= depths[index] + 0.08:
            pixels[index * 4:index * 4 + 4] = bytes(rgba)


def render_mode(pixels, depths, width, height, mode, theta_steps, phi_steps):
    degree, order, translation, scale, rotation = mode
    quaternion = euler_quaternion(rotation)
    vertices, values = [], []
    for row in range(theta_steps + 1):
        theta = math.pi * row / float(theta_steps)
        for column in range(phi_steps + 1):
            phi = 2.0 * math.pi * column / float(phi_steps)
            value = real_spherical_harmonic(degree, order, theta, phi)
            radius = abs(value) * scale
            local = (radius * math.sin(theta) * math.cos(phi),
                     radius * math.sin(theta) * math.sin(phi),
                     radius * math.cos(theta))
            rotated = rotate(local, quaternion)
            vertices.append((rotated[0] + translation[0], rotated[1] + translation[1],
                             rotated[2] + translation[2]))
            values.append(value)

    light = (-0.35, 0.45, 0.82)
    row_width = phi_steps + 1
    for row in range(theta_steps):
        for column in range(phi_steps):
            first = row * row_width + column
            second = first + row_width
            for indices in ((first, second, first + 1), (first + 1, second, second + 1)):
                a, b, c = (vertices[index] for index in indices)
                edge_one = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
                edge_two = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
                normal = (edge_one[1] * edge_two[2] - edge_one[2] * edge_two[1],
                          edge_one[2] * edge_two[0] - edge_one[0] * edge_two[2],
                          edge_one[0] * edge_two[1] - edge_one[1] * edge_two[0])
                normal_length = math.sqrt(sum(component * component for component in normal))
                if normal_length < 1.0e-10 or normal[2] <= 0.0:
                    continue
                base = INK_FAINT if sum(values[index] for index in indices) >= 0.0 else INK_SOFT
                illumination = 0.30 + 0.70 * max(0.0, sum(
                    normal[axis] * light[axis] for axis in range(3)
                ) / normal_length)
                color = tuple(min(255, int(component * illumination)) for component in base[:3]) + (255,)
                draw_triangle(pixels, depths, width, height,
                              tuple(projected(vertices[index], width, height) for index in indices), color)

    grid_step = max(1, int(round(theta_steps / 9.0)))
    for row in range(grid_step, theta_steps, grid_step):
        for column in range(phi_steps):
            start = row * row_width + column
            draw_line(pixels, depths, width, height,
                      projected(vertices[start], width, height),
                      projected(vertices[start + 1], width, height), INK_FAINT)
    for column in range(0, phi_steps, grid_step):
        for row in range(1, theta_steps - 1):
            start = row * row_width + column
            draw_line(pixels, depths, width, height,
                      projected(vertices[start], width, height),
                      projected(vertices[start + row_width], width, height), INK_FAINT)


def render(output_path, width, height, theta_steps, phi_steps):
    pixels = bytearray(BACKGROUND * (width * height))
    depths = array("f", [float("inf")]) * (width * height)
    for mode in GALLERY_MODES:
        render_mode(pixels, depths, width, height, mode, theta_steps, phi_steps)
    with open(output_path, "wb") as output_file:
        output_file.write(png_rgba(width, height, pixels))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", default="spherical_harmonics_gallery_preview.png",
                        help="output PNG path (default: spherical_harmonics_gallery_preview.png)")
    parser.add_argument("--width", type=int, default=1440, help="image width (default: 1440)")
    parser.add_argument("--height", type=int, default=816, help="image height (default: 816)")
    parser.add_argument("--theta-steps", type=int, default=28, help="preview latitude subdivisions (default: 28)")
    parser.add_argument("--phi-steps", type=int, default=56, help="preview longitude subdivisions (default: 56)")
    args = parser.parse_args()
    if args.width < 32 or args.height < 32 or args.theta_steps < 2 or args.phi_steps < 3:
        parser.error("image dimensions must be >= 32; theta steps >= 2; phi steps >= 3")
    render(args.output, args.width, args.height, args.theta_steps, args.phi_steps)
    print("Wrote {0}.".format(args.output))


if __name__ == "__main__":
    main()
