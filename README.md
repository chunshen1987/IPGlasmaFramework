# IPGlasmaFramework
This repository contains driver scripts to run simulations with IP-Glasma and other associated code packages.

The individual code package that are included in this framework are as follows,

[IP-Glasma](https://github.com/schenke/ipglasma)

[subnucleondiffraction](https://github.com/hejajama/subnucleondiffraction)

## Choosing `mcintpoints`

`diffraction_dict['mcintpoints']` is the number of Monte Carlo points subnucleondiffraction uses for each integral. It is used by both modes:
- `analyzeDiffraction`: the amplitude as a function of t, with one integral per value in `tlist`.
- `computeTotalCrossSection`: one integral per (b, θ) grid point, so `nbperp × ntheta` integrals per Wilson-line file.

The run time is proportional to `mcintpoints`, and the total cross section mode dominates it.

Note: before subnucleondiffraction commit `0eb59bc` (`roch/devel`), the value was ignored, and every run used 1e5 points.

### Accuracy

Largest relative deviation from a 1e7-point reference (the integration is deterministic, Sobol points):

| Case | 1e5 | 3e5 | 1e6 | 2e6 |
|---|---|---|---|---|
| p, x = 0.01, amplitude, t = 0 | 5.3% | 1.6% | 0.5% | 0.3% |
| p, x = 0.01, amplitude, 0.01 ≤ t ≤ 0.5 | 1.8% | 0.5% | 0.2% | 0.04% |
| p, JIMWLK to x = 3.6e-6, amplitude, 0 ≤ t ≤ 0.5 | 1.7% | 0.4% | 0.2% | 0.2% |
| Pb, JIMWLK to x = 1.45e-5, amplitude, t ≤ 0.005 | 4.4% | 1.2% | 0.3% | 0.05% |
| Pb, JIMWLK to x = 1.45e-5, amplitude, t = 0.02 and 0.1 (around the first diffractive minimum) | 21% | 2.7% | 1.4% | 0.5% |
| p (both), total cross section, F(b, θ) | 0.2% | 0.06% | 0.04% | 0.02% |
| Pb, total cross section, F(b, θ) | 0.3% | 0.1% | 0.03% | 0.04% |

How the numbers were obtained:
- One Wilson line per case, 720² lattice: L = 5.12 fm for p and 18 fm for Pb, with the IP-Glasma settings of `parameters_dict_user_IPGlasmaJIMWLK_pp.py` / `_PbPb.py`.
- Boosted Gaussian J/ψ wave function, Q² = 0.
- Total cross section grid points at b ≤ 20 GeV⁻¹ (p) and b ≤ 60 GeV⁻¹ (Pb), θ = 0 and π.
- Code versions: IP-Glasma `f793db6`, subnucleondiffraction `6439bc8`.

### Cost

Measured single-core time per integral on a 720² lattice:

| `mcintpoints` | per t value (amplitude) | per (b, θ) point (total cross section) |
|---|---|---|
| 3e5 | 0.1 s | 0.09 s |
| 1e6 | 0.34 s | 0.26 s |
| 2e6 | 0.64 s | 0.5 s |

An event of the shipped dictionaries has 10 Wilson-line files: 5 values of x for each of the 2 nuclei. That gives, on a single core:
- **pp** (13 t values, 40 × 32 grid points): about 1 min for the amplitudes and 55 min for the total cross section at 1e6 points. At 2e6 points it is about 1 h 50 min.
- **PbPb** (total cross section only, 120 × 32 grid points): about 1 h at 3e5 points, and about 5 h at 2e6 points.

The total cross section is parallelized with OpenMP over the grid points, using the job's `-n_th` threads.

### Settings of the shipped dictionaries

- `parameters_dict_user_IPGlasmaJIMWLK_pp.py`: 1e6. The amplitudes are within about 0.2%, the total cross section within 0.04%.
- `parameters_dict_user_IPGlasmaJIMWLK_PbPb.py`: 3e5. Only the total cross section is computed (`analyzeDiffraction: 0`), within about 0.1%. When the Pb amplitude is computed, use at least 2e6 points: its diffractive minima need them.
- `config/arXiv_2507.14087/`: 1e5, the setting of the published results.
