---
title: Waves on a Sphere, Spherical Harmonics
category: math-stats-notes
categoryLabel: Math & Stats Notes
date: 2026-08-21
readTime: 20 min read
summary: Spherical harmonics are the natural language for directional variation on a sphere. Rooted in Laplace's study of gravitational potentials and central to atomic orbitals, they are like sine and cosine Fourier modes on a line or circle, representing view-dependent color in 3D Gaussian Splatting.
cover: /static/img/blog/spherical-harmonics-cover.png
visibility: public
---

Spherical harmonics are the natural language for directional variation on a sphere. Rooted in Laplace's study of gravitational potentials and central to atomic orbitals, they are like sine and cosine Fourier modes on a line or circle, representing view-dependent color in 3D Gaussian Splatting.

## Table of contents
- [1. Prologue: Why spherical harmonics today?](#1-prologue-why-spherical-harmonics-today)
- [2. Historical background of spherical harmonics](#2-historical-background-of-spherical-harmonics)
- [3. Mathematical definition of spherical harmonics](#3-mathematical-definition-of-spherical-harmonics)
  - [3.1 Laplace equation in spherical coordinates](#31-laplace-equation-in-spherical-coordinates)
  - [3.2 Separation of variables & associated Legendre polynomials](#32-separation-of-variables-amp-associated-legendre-polynomials)
  - [3.3 Key mathematical properties](#33-key-mathematical-properties)
- [4. Modern applications: 3DGS, Ref-NeRF, and IDE](#4-modern-applications-3dgs-ref-nerf-and-ide)
  - [4.1 View-dependent color and radiance in 3D Gaussian Splatting (3DGS)](#41-view-dependent-color-and-radiance-in-3d-gaussian-splatting-3dgs)
  - [4.2 Ref-NeRF and Integrated Directional Encoding (IDE)](#42-ref-nerf-and-integrated-directional-encoding-ide)
- [5. Quantum mechanical correlation: Bohr model & wave mechanics](#5-quantum-mechanical-correlation-bohr-model-amp-wave-mechanics)
  - [5.1 Why spherical harmonics appear in the hydrogen atom](#51-why-spherical-harmonics-appear-in-the-hydrogen-atom)
  - [5.2 Schrödinger equation, orbital structure, and spherical harmonics](#52-schrdinger-equation-orbital-structure-and-spherical-harmonics)
- [6. Epilogue & conclusion](#6-epilogue-amp-conclusion)
- [References](#references)

---

## 1. Prologue: Why spherical harmonics today?

Spherical Harmonics (SH) represent the two-dimensional angular equivalent of the classic 1D Fourier series. While the standard Fourier series decomposes signals on periodic 1D lines or 2D Cartesian grids, Spherical Harmonics act as fundamental vibration modes on the continuous surface of a sphere ($S^2$).

In recent years, Spherical Harmonics have experienced a resurgence in neural 3D, Neural Radiance Fields (NeRF) <a id="ref-mildenhall2020-1" href="#ref-mildenhall2020">[Mildenhall et al., 2020]</a> and 3D Gaussian Splatting (3DGS) <a id="ref-kerbl2023-1" href="#ref-kerbl2023">[Kerbl et al., 2023]</a>. Because real-world objects reflect light non-isotropically based on view direction, SH functions provide a lightweight, closed-form polynomial basis to store and evaluate view-dependent color and high-frequency specular highlights in real time.

---

## 2. Historical background of spherical harmonics

<figure class="post-illustration">
  <img src="../static/img/blog/spherical-harmonics-pioneers.png" alt="Line art illustration of Laplace, Legendre, Thomson, and Tait" loading="lazy">
  <figcaption>Historical figures of Spherical Harmonics: Laplace, Legendre, Kelvin, and Tait.</figcaption>
</figure>

Spherical Harmonics were first introduced in the late 18th century by Pierre-Simon Laplace (1782) and Adrien-Marie Legendre (1785) to analyze gravitational potentials and celestial mechanics without relying on computationally heavy Cartesian series expansions. Throughout the 19th century, the framework expanded to describe physical phenomena like heat conduction, wave propagation, and electrostatics in spherical geometries—giving rise to a fundamental class of mathematical formulations known as **boundary value problems**.

In differential equations and classical physics, boundary value problems refer to differential equations coupled with a set of constraints—known as boundary conditions—that the solution must satisfy at the physical borders of a specified domain. Unlike initial value problems, which evolve a system forward in time from a starting state, a boundary value problem seeks a static or stationary state governed by fixed constraints on the perimeter. In the context of Spherical Harmonics, the underlying domain is typically a continuous spherical surface ($S^2$) or a 3D spherical volume. The boundary conditions mandate that physical properties—such as temperature, electric field, or wave amplitude—remain well-behaved, continuous, and single-valued across the boundary.

To solve these problems in spherical geometry, mathematicians apply the technique of **separation of variables**, decomposing complex 3D boundary constraints into simpler radial and angular differential equations. The spherical harmonics ($Y_l^m$) emerge naturally as the fundamental angular spatial modes that satisfy these spherical boundary conditions. Because any well-behaved continuous function defined on a spherical boundary can be represented as a linear combination of these harmonic modes, spherical harmonics provide an exact analytical framework for constructing full solutions to spatial field equations under spherical constraints.

The term itself was officially introduced by Lord Kelvin (William Thomson) and Peter Guthrie Tait in their landmark 1867 work, *Treatise on Natural Philosophy* <a id="ref-kelvin1867-2" href="#ref-kelvin1867">[Thomson & Tait, 1867]</a>. They coined the name **"spherical harmonics"** to highlight the underlying mathematical property of these functions: they are the restriction of harmonic functions (solutions to Laplace's equation) onto a spherical surface, behaving as the 2D spherical analogs of the trigonometric harmonic oscillations found in 1D Fourier analysis.

---

## 3. Mathematical definition of spherical harmonics

### 3.1 Laplace equation in spherical coordinates
In vector calculus and mathematical physics, **Laplace's equation** ($\nabla^2 f = 0$) governs source-free, static field configurations—such as gravitational potentials in empty space, electrostatic fields outside charges, and steady-state heat distributions. Solutions to Laplace's equation are known as harmonic functions, which possess strong smoothness and the mean-value property—stating that the value of the function at any point equals the average of its values over any sphere centered at that point.

To solve Laplace's equation in spherically symmetric domains, we transform the standard Cartesian Laplacian operator $\nabla^2 = \frac{\partial^2}{\partial x^2} + \frac{\partial^2}{\partial y^2} + \frac{\partial^2}{\partial z^2}$ into spherical coordinates $(r, \theta, \phi)$ using the coordinate transformation $x = r \sin\theta \cos\phi$, $y = r \sin\theta \sin\phi$, and $z = r \cos\theta$. Applying the multivariable chain rule yields the spherical Laplacian:

$$\nabla^2 f = \frac{1}{r^2} \frac{\partial}{\partial r}\left(r^2 \frac{\partial f}{\partial r}\right) + \frac{1}{r^2 \sin\theta} \frac{\partial}{\partial \theta}\left(\sin\theta \frac{\partial f}{\partial \theta}\right) + \frac{1}{r^2 \sin^2\theta} \frac{\partial^2 f}{\partial \phi^2} = 0 \tag{1}$$

Equation (1) naturally decomposes the spatial field into a radial variation scale ($r$) and an angular surface geometry $(\theta, \phi)$ defined on the unit sphere $S^2$.

<figure class="post-illustration post-illustration--compact">
  <img src="../static/img/blog/spherical-harmonics-spherical-coordinates.png" alt="Spherical coordinate system showing the radial distance r, polar angle theta, and azimuthal angle phi on a unit sphere" loading="lazy">
  <figcaption>Spherical coordinates separate radial distance $r$ from the angular coordinates $(\theta, \phi)$ on the unit sphere.</figcaption>
</figure>

### 3.2 Separation of variables & associated Legendre polynomials
To isolate the angular behavior, we apply the technique of **separation of variables**, assuming a factorized solution $f(r, \theta, \phi) = R(r) Y(\theta, \phi)$. Substituting this decomposition into Equation (1) and multiplying by $r^2 / (R Y)$ separates the equation into independent radial and angular Ordinary Differential Equations (ODEs) bound by a separation constant $l(l+1)$:

$$\frac{1}{R} \frac{d}{dr}\left(r^2 \frac{dR}{dr}\right) = -\frac{1}{Y} \left[ \frac{1}{\sin\theta} \frac{\partial}{\partial \theta}\left(\sin\theta \frac{\partial Y}{\partial \theta}\right) + \frac{1}{\sin^2\theta} \frac{\partial^2 Y}{\partial \phi^2} \right] = l(l+1) \tag{2}$$

Further factorizing the angular component $Y(\theta, \phi) = \Theta(\theta) \Phi(\phi)$ with a second separation constant $m^2$ splits the spherical surface into longitudinal ($\Phi$) and latitudinal ($\Theta$) components:

* **Azimuthal equation ($\Phi$)**: $\frac{d^2\Phi}{d\phi^2} + m^2 \Phi = 0 \implies \Phi(\phi) = e^{im\phi}$
* **Associated Legendre equation ($\Theta$)**: Enforcing boundary periodicity and smoothness restricts degree $l \ge 0$ and order $-l \le m \le l$ to integers.

Combining the normalized solutions yields the standard complex Spherical Harmonics $Y_l^m(\theta, \phi)$:

$$Y_l^m(\theta, \phi) = N_l^m P_l^m(\cos\theta) e^{im\phi} \tag{3}$$

* **Normalizing constant ($N_l^m$)**:

$$N_l^m = \sqrt{\frac{(2l+1)}{4\pi} \frac{(l-m)!}{(l+m)!}} \tag{4}$$

* **Associated Legendre polynomials ($P_l^m$)**:
Defined for $m \ge 0$ via Rodrigues' formula using $x = \cos\theta$, incorporating the standard Condon–Shortley phase $(-1)^m$:

$$P_l^m(x) = (-1)^m (1-x^2)^{m/2} \frac{d^m}{dx^m} P_l(x) \quad (m \ge 0) \tag{5}$$

$$P_l(x) = \frac{1}{2^l l!} \frac{d^l}{dx^l} (x^2 - 1)^l \tag{6}$$

For negative order $-l \le m < 0$, $P_l^m(x)$ is defined via $P_l^{-m}(x) = (-1)^m \frac{(l-m)!}{(l+m)!} P_l^m(x)$.

### 3.3 Key mathematical properties

* **Orthonormal basis**: Spherical Harmonics form a complete orthonormal basis over the unit sphere $S^2$, where superscript $*$ denotes the complex conjugate required for complex-valued functions:

$$\int_{0}^{2\pi} \int_{0}^{\pi} Y\_l^m(\theta, \phi) \left( Y\_{l'}^{m'}(\theta, \phi) \right)^* \sin\theta ~ d\theta ~ d\phi = \delta\_{ll'} \delta\_{mm'} \tag{7}$$

* **Rotation equivariance**: Under a 3D rotation $\mathbf{R}$, the original SH coefficients $\mathbf{c}\_{l, m}$ transform linearly within degree $l$ into new coefficients $\mathbf{c}'\_{l, m'}$ using Wigner D-matrices $\mathbf{D}\_{m', m}^{(l)}(\mathbf{R})$:

$$\mathbf{c}'\_{l, m'} = \sum\_{m=-l}^{l} \mathbf{D}^{(l)}\_{m', m}(\mathbf{R}) ~ \mathbf{c}\_{l, m} \tag{8}$$

* **Laplacian eigenvalue & frequency**: Spherical Harmonics are eigenfunctions of the Laplace–Beltrami operator $\Delta\_{S^2}$ on the unit sphere:

$$\Delta\_{S^2} Y\_l^m = -l(l+1) Y\_l^m \tag{9}$$

Degree $l$ relates directly to spatial angular frequency, with an approximate wavelength $\approx \frac{180^\circ}{l}$.

<figure class="post-illustration">
  <img src="../static/img/blog/spherical-harmonics-low-order-modes.png" alt="Comparison of low-order spherical harmonic modes, progressing from a uniform sphere to increasingly structured angular patterns" loading="lazy">
  <figcaption>Visual representations of the first few real spherical harmonics. Light regions represent positive values and dark regions negative values. For each angular direction $(\theta, \phi)$, the surface's radial distance from the origin encodes the magnitude $|Y_l^m(\theta, \phi)|$. Increasing degree $l$ produces increasingly fine angular structure.</figcaption>
</figure>

---

## 4. Modern applications: 3DGS, Ref-NeRF, and IDE

### 4.1 View-dependent color and radiance in 3D Gaussian Splatting (3DGS)
In 3D Gaussian Splatting (3DGS) [<a id="ref-kerbl2023-41" href="#ref-kerbl2023">Kerbl et al., 2023</a>], each 3D Gaussian primitive stores SH coefficients to model view-dependent RGB radiance:

$$\mathbf{c}(\mathbf{v}) = \sum_{l=0}^{l_{\max}} \sum_{m=-l}^{l} \mathbf{c}_{l, m} Y_l^m(\mathbf{v}) \tag{9}$$

For standard real-time rendering, degree $l_{\max} = 3$ is used, corresponding to $(3+1)^2 = 16$ coefficients per color channel (48 parameters per primitive).

### 4.2 Ref-NeRF and Integrated Directional Encoding (IDE)
To account for specular reflections and surface roughness without aliasing artifacts, Ref-NeRF models a distribution of reflected directions with a von Mises–Fisher (vMF) distribution [<a id="ref-verbin2022-42" href="#ref-verbin2022">Verbin et al., 2022</a>]. Here, $\mathbf{\mu}_r \in S^2$ is the unit reflection direction and the mean direction of the distribution, $\mathbf{x} \in S^2$ is a unit direction sampled on the sphere, and $\kappa \ge 0$ is the concentration parameter: lower $\kappa$ represents a broader lobe and thus a rougher surface. The factor $C_3(\kappa)$ normalizes the density over the 3D unit sphere; the subscript $3$ is the ambient dimension because $S^2$ consists of unit vectors in $\mathbb{R}^3$, as specified by the <a href="https://en.wikipedia.org/wiki/Von_Mises%E2%80%93Fisher_distribution#Definition" target="_blank" rel="noopener noreferrer">general vMF definition</a>.

$$f(\mathbf{x}; \mathbf{\mu}_r, \kappa) = C_3(\kappa) \exp(\kappa \mathbf{\mu}_r^T \mathbf{x}) \tag{10}$$

Taking the expectation of SH basis functions over the vMF distribution yields Integrated Directional Encoding (IDE), which closed-form attenuates higher frequencies:

$$\mathbb{E}_{\boldsymbol{\omega} \sim \textnormal{vMF}(\mathbf{\mu}_r, \kappa)} \left[ Y_l^m(\boldsymbol{\omega}) \right] = A_l(\kappa) Y_l^m(\mathbf{\mu}_r) \tag{11}$$

$$A_l(\kappa) \approx \exp\left( -\frac{l(l+1)}{2\kappa} \right) \tag{12}$$

Here, $\boldsymbol{\omega} \in S^2$ is the random unit direction drawn from the vMF distribution, and $A_l(\kappa)$ is the roughness-dependent attenuation factor for SH degree $l$.

**Why does Equation (11) hold? (Proof sketch.)** First rotate the coordinates so that the mean direction $\mathbf{\mu}_r$ becomes the north pole. Write a direction on the sphere using its polar angle $\theta \in [0, \pi]$ and azimuthal angle $\phi \in [0, 2\pi)$. In these coordinates, the vMF density in Equation (10) depends on $\theta$ but not on $\phi$. A spherical harmonic of degree $l$ and order $m$ has azimuthal dependence proportional to $e^{i m \phi}$. Consequently, its integral over $\phi$ is zero whenever $m \ne 0$, because $\int_0^{2\pi} e^{i m \phi}\,d\phi = 0$. This is consistent with the fact that $Y_l^m$ evaluated at the north pole is zero for $m \ne 0$.

For an arbitrary mean direction $\mathbf{\mu}\_r$, rotate the north-pole result back to $\mathbf{\mu}\_r$. Since the density depends only on the angle between $\boldsymbol{\omega}$ and $\mathbf{\mu}\_r$, this averaging operation commutes with every 3D rotation. It therefore preserves each SH degree and applies the same scalar factor $A_l(\kappa)$ to every order $m$ within that degree. More generally, for a directional function $g$ that can be expanded in spherical harmonics as $g(\boldsymbol{\omega}) = \sum\_{l=0}^{\infty}\sum\_{m=-l}^{l} c\_{l,m}Y\_l^m(\boldsymbol{\omega})$, where $c\_{l,m}$ are its SH coefficients, vMF averaging gives

$$\mathbb{E}\_{\boldsymbol{\omega} \sim \textnormal{vMF}(\mathbf{\mu}\_r, \kappa)}[g(\boldsymbol{\omega})] = \sum\_{l=0}^{\infty}\sum_{m=-l}^{l} A\_l(\kappa)c\_{l,m}Y\_l^m(\mathbf{\mu}_r). \tag{13}$$

Thus, no coefficient is transferred to a different degree or order: each coefficient is only attenuated according to its degree. This derivation is an application of the Funk–Hecke theorem; Ref-NeRF gives the full derivation, including the Legendre-polynomial integral for $A_l(\kappa)$, in <a href="https://dorverbin.github.io/refnerf/refnerf.pdf" target="_blank" rel="noopener noreferrer">Appendix A, “Integrated Directional Encoding Proofs”</a>.

<figure class="post-illustration">
  <img src="../static/img/blog/spherical-harmonics-ide-frequency-attenuation.png" alt="Integrated Directional Encoding comparison showing that a broad low-kappa von Mises-Fisher distribution attenuates high-degree spherical harmonic frequencies more strongly" loading="lazy">
  <figcaption>IDE applies a roughness-dependent angular low-pass filter: lower $\kappa$ (rougher surfaces) attenuates higher-degree spherical harmonic frequencies more strongly.</figcaption>
</figure>

---

## 5. Quantum mechanical correlation: Bohr model & wave mechanics

### 5.1 Why spherical harmonics appear in the hydrogen atom
In a hydrogen atom, a negatively charged electron is attracted to a positively charged nucleus. In the simplest model, the strength of this attraction depends only on the distance from the nucleus, not on the direction. Physicists call this distance-dependent energy the Coulomb potential. Because rotating the atom does not change that energy, the quantum description of the electron separates naturally into a radial part, which describes distance, and an angular part, which describes direction. The angular part must be an eigenfunction of the spherical Laplacian, and those eigenfunctions are precisely the spherical harmonics $Y_l^m$. Thus, the degree $l$ and order $m$ of a spherical harmonic label an electron orbital's angular structure and orientation; the next section makes this separation explicit.

<figure class="post-illustration post-illustration--compact">
  <img src="../static/img/blog/spherical-harmonics-bohr.png" alt="Illustration of the Bohr atomic model with electrons on discrete circular orbits around a central nucleus" loading="lazy">
  <figcaption>Bohr’s historical model represents electrons in discrete circular orbits around a nucleus. The atom is deliberately shown excited—an apt prelude to leaving Bohr’s fixed orbits for the richer angular structure of wave mechanics in the following section. ;-)</figcaption>
</figure>

### 5.2 Schrödinger equation, orbital structure, and spherical harmonics
The Schrödinger equation is the basic equation of quantum mechanics: it determines a quantum wavefunction from the energy landscape of a physical system. For hydrogen, this energy landscape is written as $V(r)$, where $r$ is the distance from the nucleus; as Section 5.1 explained, it has no preferred direction. This symmetry lets the three-dimensional spatial-curvature operator, called the Laplacian and written as $\nabla^2$, split into a distance-dependent part and a direction-dependent part:

$$\nabla^2 = \frac{1}{r^2}\frac{\partial}{\partial r}\left(r^2\frac{\partial}{\partial r}\right) + \frac{1}{r^2}\Delta\_{S^2}. \tag{14}$$

The first term describes how the wavefunction changes with distance. The second contains the spherical Laplacian $\Delta\_{S^2}$ from Equation (9), which describes how it changes with direction on a sphere. A spherical harmonic $Y_l^m$ is an eigenfunction of this angular operator: applying the operator changes only its scale, not its angular pattern. This lets the three-dimensional Schrödinger equation separate into one radial equation for each angular mode. A wavefunction with a definite energy can consequently be written as

$$\psi(r, \theta, \phi) = R\_{n,l}(r)Y\_l^m(\theta, \phi). \tag{15}$$

Here, $\psi$ is the spatial wavefunction; $R\_{n,l}$ is its radial part; and $Y\_l^m$ is its angular part. The principal quantum number $n$ is a positive integer that labels the radial energy level, while the nonnegative integer $l$ and integer $m$ label the spherical harmonic, with $0 \le l \le n-1$ and $-l \le m \le l$.

This factorization gives spherical harmonics their physical meaning. The degree $l$ controls the angular complexity and the orbital angular momentum: $l=0,1,2,3$ correspond to the familiar $s,p,d,f$ orbital families. The order $m$ distinguishes the $2l+1$ orientation states within one family. In a perfectly spherically symmetric atom, these states have the same energy; a magnetic field can distinguish them, which is why $m$ is called the magnetic quantum number.

More broadly, this is a useful change of viewpoint: spherical harmonics are not merely convenient functions for drawing orbitals. They are the natural coordinates for any phenomenon with rotational symmetry. The same decomposition that separates a quantum wavefunction into angular modes also organizes lighting on a sphere, directional signals, and neural rendering features into angular frequencies.


## 6. Epilogue & conclusion

Spherical Harmonics illustrate the deep interdisciplinary connection across mathematical physics, quantum mechanics, and modern computer science. Originally developed to calculate celestial gravity in the 18th century, SH functions became foundational to 20th-century quantum physics by defining electron orbital geometries. Today, they power real-time 3D neural rendering engines like 3D Gaussian Splatting [<a id="ref-kerbl2023-6" href="#ref-kerbl2023">Kerbl et al., 2023</a>] and Ref-NeRF [<a id="ref-verbin2022-6" href="#ref-verbin2022">Verbin et al., 2022</a>], solidifying their role as an essential tool for spatial computing.

---
*This article is based on lecture notes from the Neural Graphics module of the Fall 2025 course, "Multimodal Generative AI Theories and Applications," at Seoul National University.*


## References

* <a id="ref-kerbl2023"></a>Bernhard Kerbl, Georgios Kopanas, Thomas Leimkühler, and George Drettakis. 3D Gaussian Splatting for Real-Time Radiance Field Rendering. *ACM Transactions on Graphics (TOG)*, 42(4):1–14, 2023. [<a href="#ref-kerbl2023-1">1</a>, <a href="#ref-kerbl2023-41">4.1</a>, <a href="#ref-kerbl2023-6">6</a>]
* <a id="ref-mildenhall2020"></a>Ben Mildenhall, Pratul P. Srinivasan, Matthew Tancik, Jonathan T. Barron, Ravi Ramamoorthi, and Ren Ng. NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis. In *European Conference on Computer Vision (ECCV)*, pages 405–421. Springer, 2020. [<a href="#ref-mildenhall2020-1">1</a>]
* <a id="ref-verbin2022"></a>Dor Verbin, Peter Hedman, Ben Mildenhall, Todd Zickler, Jonathan T. Barron, and Pratul P. Srinivasan. Ref-NeRF: Structured View-Dependent Appearance for Neural Radiance Fields. In *IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, pages 5491–5500, 2022. [<a href="#ref-verbin2022-42">4.2</a>, <a href="#ref-verbin2022-6">6</a>]
* <a id="ref-kelvin1867"></a>William Thomson (Lord Kelvin) and Peter Guthrie Tait. Treatise on Natural Philosophy, Part I. Clarendon Press, Oxford, 1867. [<a href="#ref-kelvin1867-2">2</a>]
