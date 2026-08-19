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
angular direction is `|Y_l^m(theta, phi)|`. Its embedded PNG texture is blue
where the value is positive and yellow where it is negative. The GLB also
contains UV coordinates, normals, and a PBR material, so it has no external
texture-file dependency.

The script uses only the Python standard library and is compatible with Python
3.8 or later.

## Floating gallery

`generate_spherical_harmonics_gallery_glb.py` composes 25 different modes into
one wide floating-object scene, based on the accompanying cover-art layout.
Every object has its own embedded texture and the GLB includes an orthographic
camera framing the composition.

```bash
python3 generate_spherical_harmonics_gallery_glb.py -o ../../static/img/blog/spherical-harmonics-cover.glb
```

For a fast composition review before a production render, create the matching
PNG preview with:

```bash
python3 render_spherical_harmonics_gallery.py -o ../../blog/math-stats-notes/spherical_harmonics_gallery_preview.png
```

## Layout editor

`spherical-harmonics-gallery-editor.html` is a small WebGL layout editor. It
loads `../../static/img/blog/spherical-harmonics-cover.glb` by
default, lets you move only the selected object, and exports a new standalone
GLB with the adjusted translations. The cyan render frame shows
the 1440 × 810 (16:9) PNG output area; **렌더 이미지 저장 (PNG)** saves that rendering
without the move gizmo. The arrow keys move X/Y, and `Z` / `X` move the Z axis.
Set the keyboard step from 1 to 100 in the left panel. Serve this directory
(rather than opening the HTML with `file://`) and visit the editor in a browser:

When saving the GLB, the editor also stores the current 60° perspective camera
pose and look target. Reopening that saved file restores the same view. Use
**방금 저장한 GLB 다시 열기** to verify the saved pose without leaving the editor.

The editor starts in **카툰 윤곽선** mode: a WebGL inverted-hull shader draws
`#55503f` outlines around the original blue/yellow sign materials. Choose
**컬러** to disable the shader. The outline is a renderer effect for the editor
and PNG output; GLB saving keeps portable standard materials.

```bash
cd ../..
python3 -m http.server 8000
```

Open `http://localhost:8000/tools/spherical-harmonics-glb/spherical-harmonics-gallery-editor.html`.
