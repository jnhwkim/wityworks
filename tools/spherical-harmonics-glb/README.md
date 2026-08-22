# Spherical-harmonic GLB generator

`generate_spherical_harmonics_glb.py` makes a self-contained glTF binary
(`.glb`) model for any valid degree `l` and order `m`.

```bash
cd tools/spherical-harmonics-glb
python3 generate_spherical_harmonics_glb.py 3 2 -o ../../blog/math-stats-notes/spherical_harmonic_l3_m2.glb
```

Use `-o` to choose an output filename and `--theta-steps` / `--phi-steps` to
adjust mesh density. The generated example is stored at
`../../blog/math-stats-notes/spherical_harmonic_l3_m2.glb`.

The model represents the real spherical-harmonic basis: its radius in each
angular direction is `|Y_l^m(theta, phi)|`. Its positive and negative regions
use lit `#e8e4d8` and `#55503f` ink materials respectively. A latitude/longitude grid is exported from every second selected
mesh edge as `#55503f` `LINES` on positive lobes and `#14130f` `LINES` on
negative lobes, so it follows the stretched surface
rather than a texture and remains visible independently of surface lighting.

The grid gets its own position buffer, displaced by `GRID_NORMAL_OFFSET =
0.004` along each surface normal. This prevents depth fighting against the
surface triangles while preserving occlusion. If a target viewer still hides
the grid, regenerate with a larger `--grid-offset` value; reduce it if the
lines look detached from the surface.

To keep specular highlights clean, grid edges fade linearly through
`GRID_OPACITY_STEPS = 16` opacity levels. The GLB fallback uses a
`log10(specular)` range of `-10` (fully opaque) to `0` (fully transparent).

In the layout editor, grid lines use a view-dependent half-vector shader
instead: their opacity follows the current camera, surface normal, and key
light direction. When `--camera-from` and `--transforms-from` are supplied,
the 16-level GLB fallback bakes the same half-vector approximation at the
saved camera pose in `log10(specular)` space. Its default fade range is `-10`
to `0`.

The script uses only the Python standard library and is compatible with Python
3.8 or later.

## Floating gallery

`generate_spherical_harmonics_gallery_glb.py` composes 25 different modes into
one wide floating-object scene, based on the accompanying cover-art layout.
Every object has the same lit ink materials and mesh-edge grid; the GLB
includes an orthographic camera framing the composition.

```bash
python3 generate_spherical_harmonics_gallery_glb.py -o ../../static/glb/spherical-harmonics-cover.glb
```

To generate the built-in 16-object cover composition and its perspective
camera—without an unused wide orthographic camera—use the canonical
`cover.glb` name:

```bash
python3 generate_spherical_harmonics_gallery_glb.py \
  --cover-layout \
  -o ../../static/glb/spherical-harmonics-cover.glb
```

For example, use `--grid-offset 0.006` to make the grid sit slightly farther
above the surface in a renderer with a less forgiving depth buffer.

To retain a layout-editor camera pose when regenerating the mesh, make a backup
first and pass it explicitly:

```bash
cp ../../static/glb/spherical-harmonics-cover.glb ../../static/glb/spherical-harmonics-cover-backup.glb
python3 generate_spherical_harmonics_gallery_glb.py \
  --camera-from ../../static/glb/spherical-harmonics-cover-backup.glb \
  --transforms-from ../../static/glb/spherical-harmonics-cover-backup.glb \
  -o ../../static/glb/spherical-harmonics-cover.glb
```

For a fast composition review before a production render, create the matching
PNG preview with:

```bash
python3 render_spherical_harmonics_gallery.py -o ../../blog/math-stats-notes/spherical_harmonics_gallery_preview.png
```

## Layout editor

`spherical-harmonics-gallery-editor.html` is a small WebGL layout editor. It
loads `../../static/glb/spherical-harmonics-cover.glb` by
default, lets you move only the selected object, and exports a new standalone
GLB with the adjusted object transforms. The cyan render frame shows
the 1440 × 810 (16:9) PNG output area; **렌더 이미지 저장 (PNG)** saves that rendering
without the move gizmo. The arrow keys move X/Y, and `Z` / `X` move the Z axis.
Set the keyboard step from 1 to 100 in the left panel. Serve this directory
(rather than opening the HTML with `file://`) and visit the editor in a browser:

**현재 상태 GLB 저장** stores the current object transforms, 60° camera pose
and look target, grid fade range, ink colours, render style, and editor light
settings. On reopening, the editor reconstructs its grid shader from that
metadata because standard GLB line primitives cannot carry the view-dependent
grid shader directly. Use **방금 저장한 GLB 다시 열기** to verify the saved state
without leaving the editor.

The editor starts in **잉크 + 얇은 윤곽선** mode: a WebGL inverted-hull shader
draws 1.0px `#14130f` outlines around the ink materials. The grid is drawn
below this outline layer. Choose
**잉크 + 그리드** to disable the extra silhouette. The outline is a renderer
effect for the editor and PNG output; GLB saving keeps portable standard materials.

```bash
cd ../..
python3 -m http.server 8000
```

Open `http://localhost:8000/tools/spherical-harmonics-glb/spherical-harmonics-gallery-editor.html`.
