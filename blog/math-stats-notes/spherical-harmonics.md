---
title: Waves on a Sphere: Waves on a Sphere, Spherical Harmonics
category: math-stats-notes
categoryLabel: Math & Stats Notes
date: 2026-08-17
readTime: 15 min read
summary: History, mathematical definition, and applications of spherical harmonics from quantum mechanics to neural 3D.
visibility: public
---

## Table of contents
- [1. Prologue: Why spherical harmonics today?](#1-prologue-why-spherical-harmonics-today)
- [2. Historical background of spherical harmonics](#2-historical-background-of-spherical-harmonics)
- [3. Rigorous mathematical definition of spherical harmonics](#3-rigorous-mathematical-definition-of-spherical-harmonics)
  - [3.1 Laplace equation in spherical coordinates](#31-laplace-equation-in-spherical-coordinates)
  - [3.2 Separation of variables & associated Legendre polynomials](#32-separation-of-variables--associated-legendre-polynomials)
  - [3.3 Key mathematical properties](#33-key-mathematical-properties)
- [4. Modern applications: 3DGS, Ref-NeRF, and IDE](#4-modern-applications-in-3d-vision--ai-3dgs-ref-nerf-and-ide)
  - [4.1 View-dependent color and radiance in 3D Gaussian Splatting (3DGS)](#41-view-dependent-color-and-radiance-in-3d-gaussian-splatting-3dgs)
  - [4.2 Ref-NeRF and Integrated Directional Encoding (IDE)](#42-ref-nerf-and-integrated-directional-encoding-ide)
- [5. Quantum mechanical correlation: Bohr model & wave mechanics](#5-quantum-mechanical-correlation-bohr-model-amp-wave-mechanics)
  - [5.1 From Bohr's model to Schrödinger's wave function](#51-from-bohr39s-model-to-schrdinger39s-wave-function)
  - [5.2 Hydrogen atom solution & quantum numbers](#52-hydrogen-atom-solution--quantum-numbers)
- [6. Epilogue & conclusion](#6-epilogue--conclusion)
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

## 3. Rigorous mathematical definition of spherical harmonics

### 3.1 Laplace equation in spherical coordinates
In vector calculus and mathematical physics, **Laplace's equation** ($\nabla^2 f = 0$) governs source-free, static field configurations—such as gravitational potentials in empty space, electrostatic fields outside charges, and steady-state heat distributions. Solutions to Laplace's equation are known as harmonic functions, which possess strong smoothness and the mean-value property—stating that the value of the function at any point equals the average of its values over any sphere centered at that point.

To solve Laplace's equation in spherically symmetric domains, we transform the standard Cartesian Laplacian operator $\nabla^2 = \frac{\partial^2}{\partial x^2} + \frac{\partial^2}{\partial y^2} + \frac{\partial^2}{\partial z^2}$ into spherical coordinates $(r, \theta, \phi)$ using the coordinate transformation $x = r \sin\theta \cos\phi$, $y = r \sin\theta \sin\phi$, and $z = r \cos\theta$. Applying the multivariable chain rule yields the spherical Laplacian:

$$\nabla^2 f = \frac{1}{r^2} \frac{\partial}{\partial r}\left(r^2 \frac{\partial f}{\partial r}\right) + \frac{1}{r^2 \sin\theta} \frac{\partial}{\partial \theta}\left(\sin\theta \frac{\partial f}{\partial \theta}\right) + \frac{1}{r^2 \sin^2\theta} \frac{\partial^2 f}{\partial \phi^2} = 0 \tag{1}$$

Equation (1) naturally decomposes the spatial field into a radial variation scale ($r$) and an angular surface geometry $(\theta, \phi)$ defined on the unit sphere $S^2$.

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

$$\int_{0}^{2\pi} \int_{0}^{\pi} Y\_l^m(\theta, \phi) \left( Y\_{l'}^{m'}(\theta, \phi) \right)^* \sin\theta \, d\theta \, d\phi = \delta\_{ll'} \delta\_{mm'} \tag{7}$$

* **Rotation equivariance**: Under a 3D rotation $\mathbf{R}$, the original SH coefficients $\mathbf{c}\_{l, m}$ transform linearly within degree $l$ into new coefficients $\mathbf{c}'\_{l, m'}$ using Wigner D-matrices $\mathbf{D}\_{m', m}^{(l)}(\mathbf{R})$:

$$\mathbf{c}'\_{l, m'} = \sum\_{m=-l}^{l} \mathbf{D}^{(l)}\_{m', m}(\mathbf{R}) \, \mathbf{c}\_{l, m} \tag{8}$$

* **Laplacian eigenvalue & frequency**: Spherical Harmonics are eigenfunctions of the Laplace–Beltrami operator $\Delta\_{S^2}$ on the unit sphere:

$$\Delta\_{S^2} Y\_l^m = -l(l+1) Y\_l^m \tag{9}$$

Degree $l$ relates directly to spatial angular frequency, with an approximate wavelength $\approx \frac{180^\circ}{l}$.


---

## 4. Modern applications: 3DGS, Ref-NeRF, and IDE

### 4.1 View-dependent color and radiance in 3D Gaussian Splatting (3DGS)
In 3D Gaussian Splatting (3DGS) [<a id="ref-kerbl2023-41" href="#ref-kerbl2023">Kerbl et al., 2023</a>], each 3D Gaussian primitive stores SH coefficients to model view-dependent RGB radiance:

$$\mathbf{c}(\mathbf{v}) = \sum_{l=0}^{l_{\max}} \sum_{m=-l}^{l} \mathbf{c}_{l, m} Y_l^m(\mathbf{v}) \tag{9}$$

For standard real-time rendering, degree $l_{\max} = 3$ is used, corresponding to $(3+1)^2 = 16$ coefficients per color channel (48 parameters per primitive).

### 4.2 Ref-NeRF and Integrated Directional Encoding (IDE)
To account for specular reflections and surface roughness without aliasing artifacts, viewing distributions can be modeled as a von Mises–Fisher (vMF) distribution with concentration parameter $\kappa$ (where $\kappa \propto \frac{1}{\textnormal{roughness}}$) in Ref-NeRF [<a id="ref-verbin2022-42" href="#ref-verbin2022">Verbin et al., 2022</a>]:

$$f(\mathbf{x}; \mathbf{\mu}_r, \kappa) = C_d(\kappa) \exp(\kappa \mathbf{\mu}_r^T \mathbf{x}) \tag{10}$$

Taking the expectation of SH basis functions over the vMF distribution yields Integrated Directional Encoding (IDE), which closed-form attenuates higher frequencies:

$$\mathbb{E}_{\mathbf{\mu} \sim \textnormal{vMF}(\mathbf{\mu}_r, \kappa)} \left[ Y_l^m(\mathbf{\mu}) \right] = A_l(\kappa) Y_l^m(\mathbf{\mu}_r) \tag{11}$$

$$A_l(\kappa) \approx \exp\left( -\frac{l(l+1)}{2\kappa} \right) \tag{12}$$

---

## 5. Quantum mechanical correlation: Bohr model & wave mechanics

### 5.1 From Bohr's model to Schrödinger's wave function
* **Bohr model limitations**: Niels Bohr's classical model constrained electrons to flat, 2D circular orbits with quantized orbital angular momentum ($L = n\hbar$). However, it failed to account for intrinsic electron spin, multi-electron interactions, spectral line Zeeman splitting, and non-planar 3D probability distributions.
* **Schrödinger paradigm shift**: Quantum mechanics replaced discrete planar orbits with 3D spatial wavefunctions $\psi(r, \theta, \phi)$, representing probability density clouds over 3D space.

### 5.2 Hydrogen atom solution & quantum numbers
For a hydrogenic atom subject to a spherically symmetric Coulomb potential $V(r)$, the 3D Schrödinger equation simplifies via separation of variables:

$$\psi(r, \theta, \phi) = R\_{n, l}(r) Y\_l^m(\theta, \phi) \tag{13}$$

where $\psi(r, \theta, \phi)$ denotes the full spatial wavefunction, $R\_{n, l}(r)$ is the radial wavefunction governed by the principal quantum number $n$ ($n \in \mathbb{N}^+$) and azimuthal quantum number $l$, and $Y\_l^m(\theta, \phi)$ represents the Spherical Harmonics capturing the angular dependence.

* **Azimuthal quantum number ($l$)**: Determines total orbital angular momentum and the angular shape of subshells ($s, p, d, f$ orbitals corresponding to $l = 0, 1, 2, 3$, restricted by $0 \le l \le n-1$).
* **Magnetic quantum number ($m$)**: Determines the spatial orientation of the orbital in 3D space, taking integer values $-l \le m \le l$.


## 6. Epilogue & conclusion

Spherical Harmonics illustrate the deep interdisciplinary connection across mathematical physics, quantum mechanics, and modern computer science. Originally developed to calculate celestial gravity in the 18th century, SH functions became foundational to 20th-century quantum physics by defining electron orbital geometries. Today, they power real-time 3D neural rendering engines like 3D Gaussian Splatting [<a id="ref-kerbl2023-6" href="#ref-kerbl2023">Kerbl et al., 2023</a>] and Ref-NeRF [<a id="ref-verbin2022-6" href="#ref-verbin2022">Verbin et al., 2022</a>], solidifying their role as an essential tool for spatial computing.

---
*This article is a lecture note from the Neural Graphics module of the Fall 2025 course "Multimodal Generative AI Theories and Applications" at Seoul National University.*


## References

* <a id="ref-kerbl2023"></a>Bernhard Kerbl, Georgios Kopanas, Thomas Leimkühler, and George Drettakis. 3D Gaussian Splatting for Real-Time Radiance Field Rendering. *ACM Transactions on Graphics (TOG)*, 42(4):1–14, 2023. [<a href="#ref-kerbl2023-1">1</a>, <a href="#ref-kerbl2023-41">4.1</a>, <a href="#ref-kerbl2023-6">6</a>]
* <a id="ref-mildenhall2020"></a>Ben Mildenhall, Pratul P. Srinivasan, Matthew Tancik, Jonathan T. Barron, Ravi Ramamoorthi, and Ren Ng. NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis. In *European Conference on Computer Vision (ECCV)*, pages 405–421. Springer, 2020. [<a href="#ref-mildenhall2020-1">1</a>]
* <a id="ref-verbin2022"></a>Dor Verbin, Peter Hedman, Ben Mildenhall, Todd Zickler, Jonathan T. Barron, and Pratul P. Srinivasan. Ref-NeRF: Structured View-Dependent Appearance for Neural Radiance Fields. In *IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, pages 5481–5490, 2022. [<a href="#ref-verbin2022-42">4.2</a>, <a href="#ref-verbin2022-6">6</a>]
* <a id="ref-kelvin1867"></a>William Thomson (Lord Kelvin) and Peter Guthrie Tait. Treatise on Natural Philosophy, Part I. Clarendon Press, Oxford, 1867. [<a href="#ref-kelvin1867-2">2</a>]
