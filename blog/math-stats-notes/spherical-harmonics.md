---
title: Waves on a Sphere: Waves on a Sphere, Spherical Harmonics
category: math-stats-notes
categoryLabel: Math & Stats Notes
date: 2026-08-17
readTime: 15 min read
summary: History, mathematical definition, and applications of spherical harmonics from quantum mechanics to neural 3D.
visibility: public
---

# Table of Contents
- [1. Prologue: Why Spherical Harmonics Today?](#1-prologue-why-spherical-harmonics-today)
- [2. Historical Background of Spherical Harmonics](#2-historical-background-of-spherical-harmonics)
- [3. Rigorous Mathematical Definition of Spherical Harmonics](#3-rigorous-mathematical-definition-of-spherical-harmonics)
  - [3.1 Laplace Equation in Spherical Coordinates](#31-laplace-equation-in-spherical-coordinates)
  - [3.2 Separation of Variables & Associated Legendre Polynomials](#32-separation-of-variables--associated-legendre-polynomials)
  - [3.3 Key Mathematical Properties](#33-key-mathematical-properties)
- [4. Modern Applications in 3D Vision & AI: 3DGS, Ref-NeRF, and IDE](#4-modern-applications-in-3d-vision--ai-3dgs-ref-nerf-and-ide)
  - [4.1 View-Dependent Color and Radiance in 3D Gaussian Splatting (3DGS)](#41-view-dependent-color-and-radiance-in-3d-gaussian-splatting-3dgs)
  - [4.2 Ref-NeRF and Integrated Directional Encoding (IDE)](#42-ref-nerf-and-integrated-directional-encoding-ide)
- [5. Quantum Mechanical Correlation: Bohr Model & Wave Mechanics](#5-quantum-mechanical-correlation-bohr-model--wave-mechanics)
  - [5.1 From Bohr's Model to Schrödinger's Wave Function](#51-from-bohrs-model-to-schrödingers-wave-function)
  - [5.2 Hydrogen Atom Solution & Quantum Numbers](#52-hydrogen-atom-solution--quantum-numbers)
- [6. Epilogue & Conclusion](#6-epilogue--conclusion)
- [References](#references)

---

## 1. Prologue: Why Spherical Harmonics Today?

Spherical Harmonics (SH) represent the two-dimensional angular equivalent of the classic 1D Fourier series. While the standard Fourier series decomposes signals on periodic 1D lines or 2D Cartesian grids, Spherical Harmonics act as fundamental vibration modes on the continuous surface of a sphere ($S^2$).

In recent years, Spherical Harmonics have experienced a resurgence in neural 3D, Neural Radiance Fields (NeRF) <a href="#ref-mildenhall2020">[Mildenhall et al., 2020]</a> and 3D Gaussian Splatting (3DGS) <a href="#ref-kerbl2023">[Kerbl et al., 2023]</a>. Because real-world objects reflect light non-isotropically based on view direction, SH functions provide a lightweight, closed-form polynomial basis to store and evaluate view-dependent color and high-frequency specular highlights in real time.

---

## 2. Historical Background of Spherical Harmonics

* **18th Century Gravitational & Celestial Mechanics**: Developed primarily by Pierre-Simon Laplace (1782) and Adrien-Marie Legendre (1785) to solve gravitational potentials and celestial mechanics without expanding computationally heavy Cartesian series.
* **Heat Conduction & Wave Mechanics**: Formulated via separation of variables to address boundary value problems in spherical domains.
* **Name Origin**: Lord Kelvin (William Thomson) and Peter Guthrie Tait explicitly coined the term "spherical harmonics" in 1867 to emphasize their harmonic relationship on spherical coordinate geometries.

---

## 3. Rigorous Mathematical Definition of Spherical Harmonics

### 3.1 Laplace Equation in Spherical Coordinates
Spherical Harmonics form the angular solution to Laplace's equation $\nabla^2 f = 0$ in spherical coordinates $(r, \theta, \phi)$:

$$\nabla^2 f = \frac{1}{r^2} \frac{\partial}{\partial r}\left(r^2 \frac{\partial f}{\partial r}\right) + \frac{1}{r^2 \sin\theta} \frac{\partial}{\partial \theta}\left(\sin\theta \frac{\partial f}{\partial \theta}\right) + \frac{1}{r^2 \sin^2\theta} \frac{\partial^2 f}{\partial \phi^2} = 0 \tag{1}$$

### 3.2 Separation of Variables & Associated Legendre Polynomials
Assuming $f(r, \theta, \phi) = R(r) Y(\theta, \phi)$ where $Y(\theta, \phi) = \Theta(\theta) \Phi(\phi)$, the angular solution $Y_l^m(\theta, \phi)$ is parameterized by degree $l \ge 0$ and order $-l \le m \le l$:

$$Y_l^m(\theta, \phi) = N_l^m P_l^m(\cos\theta) e^{im\phi} \tag{2}$$

* **Normalizing Constant ($N_l^m$)**:

$$N_l^m = \sqrt{\frac{(2l+1)}{4\pi} \frac{(l-m)!}{(l+m)!}} \tag{3}$$

* **Associated Legendre Polynomials ($P_l^m$)**:
Defined via Rodrigues' formula to satisfy the latitude-dependent component:

$$P_l^m(x) = (-1)^m (1-x^2)^{m/2} \frac{d^m}{dx^m} P_l(x) \tag{4}$$

$$P_l(x) = \frac{1}{2^l l!} \frac{d^l}{dx^l} (x^2 - 1)^l \tag{5}$$

### 3.3 Key Mathematical Properties
* **Orthonormal Basis**: Spherical Harmonics form a complete orthonormal basis over the unit sphere:

$$\int_{0}^{2\pi} \int_{0}^{\pi} Y_l^m(\theta, \phi) \left(Y_{l'}^{m me}(\theta, \phi)\right)^* \sin\theta \, d\theta \, d\phi = \delta_{ll'} \delta_{mm'} \tag{6}$$

* **Rotation Equivariance**: Under a 3D rotation $\mathbf{R}$, new SH coefficients $\mathbf{c}_{l, m'}'$ transform linearly within degree $l$ using Wigner D-matrices $\mathbf{D}_{m'm}^{(l)}(\mathbf{R})$:

$$\mathbf{c}_{l, m'}' = \sum_{m=-l}^{l} \mathbf{D}_{m'm}^{(l)}(\mathbf{R}) \mathbf{c}_{l, m} \tag{7}$$

* **Laplacian Eigenvalue & Frequency**: Spherical Harmonics are eigenfunctions of the Laplace–Beltrami operator $\Delta$ on the unit sphere:

$$\Delta Y_l^m = -l(l+1) Y_l^m \tag{8}$$

Degree $l$ relates directly to spatial angular frequency, with an approximate wavelength of $\textnormal{Wavelength} \approx \frac{180^\circ}{l}$.

---

## 4. Modern Applications in 3D Vision & AI: 3DGS, Ref-NeRF, and IDE

### 4.1 View-Dependent Color and Radiance in 3D Gaussian Splatting (3DGS)
In 3D Gaussian Splatting (3DGS) [<a href="#ref-kerbl2023">Kerbl et al., 2023</a>], each 3D Gaussian primitive stores SH coefficients to model view-dependent RGB radiance:

$$\mathbf{c}(\mathbf{v}) = \sum_{l=0}^{l_{\max}} \sum_{m=-l}^{l} \mathbf{c}_{l, m} Y_l^m(\mathbf{v}) \tag{9}$$

For standard real-time rendering, degree $l_{\max} = 3$ is used, corresponding to $(3+1)^2 = 16$ coefficients per color channel (48 parameters per primitive).

### 4.2 Ref-NeRF and Integrated Directional Encoding (IDE)
To account for specular reflections and surface roughness without aliasing artifacts, viewing distributions can be modeled as a von Mises–Fisher (vMF) distribution with concentration parameter $\kappa$ (where $\kappa \propto \frac{1}{\textnormal{roughness}}$) in Ref-NeRF [<a href="#ref-verbin2022">Verbin et al., 2022</a>]:

$$f(\mathbf{x}; \mathbf{\mu}_r, \kappa) = C_d(\kappa) \exp(\kappa \mathbf{\mu}_r^T \mathbf{x}) \tag{10}$$

Taking the expectation of SH basis functions over the vMF distribution yields Integrated Directional Encoding (IDE), which closed-form attenuates higher frequencies:

$$\mathbb{E}_{\mathbf{\mu} \sim \textnormal{vMF}(\mathbf{\mu}_r, \kappa)} \left[ Y_l^m(\mathbf{\mu}) \right] = A_l(\kappa) Y_l^m(\mathbf{\mu}_r) \tag{11}$$

$$A_l(\kappa) \approx \exp\left( -\frac{l(l+1)}{2\kappa} \right) \tag{12}$$

---

## 5. Quantum Mechanical Correlation: Bohr Model & Wave Mechanics

### 5.1 From Bohr's Model to Schrödinger's Wave Function
* **Bohr Model Limitations**: Niels Bohr's classical model constrained electrons to flat, 2D circular orbits with quantized angular momentum. However, it failed to explain multi-electron atoms, complex spectral line splitting, and non-planar 3D probability distributions.
* **Schrödinger Paradigm Shift**: Quantum mechanics replaced discrete planar orbits with 3D spatial wavefunctions $\psi(r, \theta, \phi)$, representing probability density clouds.

### 5.2 Hydrogen Atom Solution & Quantum Numbers
For a hydrogenic atom subject to a spherically symmetric Coulomb potential $V(r)$, the 3D Schrödinger equation simplifies via separation of variables:

$$\psi(r, \theta, \phi) = R_{n, l}(r) Y_l^m(\theta, \phi) \tag{13}$$

* **Azimuthal Quantum Number ($l$)**: Determines the angular shape of atomic subshells ($s, p, d, f$ orbitals corresponding to $l = 0, 1, 2, 3$).
* **Magnetic Quantum Number ($m$)**: Determines spatial orientation in 3D space, taking integer values $-l \le m \le l$.

---

## 6. Epilogue & Conclusion

Spherical Harmonics illustrate the deep interdisciplinary connection across mathematical physics, quantum mechanics, and modern computer science. Originally developed to calculate celestial gravity in the 18th century, SH functions became foundational to 20th-century quantum physics by defining electron orbital geometries. Today, they power real-time 3D neural rendering engines like 3D Gaussian Splatting [<a href="#ref-kerbl2023">Kerbl et al., 2023</a>] and Ref-NeRF [<a href="#ref-verbin2022">Verbin et al., 2022</a>], solidifying their role as an essential tool for spatial computing.

---

## References

* <a id="ref-kerbl2023"></a>Bernhard Kerbl, Georgios Kopanas, Thomas Leimkühler, and George Drettakis. 3D Gaussian Splatting for Real-Time Radiance Field Rendering. *ACM Transactions on Graphics (TOG)*, 42(4):1–14, 2023.
* <a id="ref-mildenhall2020"></a>Ben Mildenhall, Pratul P. Srinivasan, Matthew Tancik, Jonathan T. Barron, Ravi Ramamoorthi, and Ren Ng. NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis. In *European Conference on Computer Vision (ECCV)*, pages 405–421. Springer, 2020.
* <a id="ref-verbin2022"></a>Dor Verbin, Peter Hedman, Ben Mildenhall, Todd Zickler, Jonathan T. Barron, and Pratul P. Srinivasan. Ref-NeRF: Structured View-Dependent Appearance for Neural Radiance Fields. In *IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)*, pages 5481–5490, 2022.
