#!/usr/bin/env python3

import numpy as np
from sys import argv, exit
from os import path
import h5py
import re
import matplotlib.pyplot as plt
import os
import sys

# =========================
# User settings
# =========================
PLOT_FLAG = False
PRINT_FLAG = False

# Robust outlier rejection (recommended if occasional events blow up)
# The filter is computed separately for each x-bin so it adapts across parameter sets.
OUTLIER_FILTER_FLAG = True
# Method: robust z-score using median/MAD on log10(event_scale)
OUTLIER_METHOD = "mad_log"
# Typical safe range: 6-10. Smaller removes more events.
OUTLIER_ZMAX = 6.0

# Additional outlier filter: use the θ-integrated |F|^2 at the smallest and largest b.
# This catches rare events where the endpoint b-bins blow up (common failure mode in some datasets).
ENDPOINT_OUTLIER_FILTER_FLAG = True
# Typical safe range: 6-10. Set equal to OUTLIER_ZMAX for consistent aggressiveness.
ENDPOINT_OUTLIER_ZMAX = 6.0

# Shape filter: require θ-integrated total |F|^2 at b≈0 to be at least
# B0_END_RATIO_MIN_DECADES order of magnitude larger than at the largest b (helps reject non-physical / unstable events).
B0_END_RATIO_FILTER_FLAG = True
# Number of decades: 1.0 means b0 >= 10 * b_end.
B0_END_RATIO_MIN_DECADES = 2.0
# If fewer events than this remain, skip this x-bin (avoid nonsense statistics)
MIN_EVENTS_AFTER_FILTER = 25

# Jackknife / delete-d resampling controls
# Note: the loop below is a Monte-Carlo approximation to delete-d jackknife
# (random subsets of size nev-delete_n), so runtime scales ~ number_JK.
JK_DELETE_FRACTION = 0.2
# Choose number of random resamples based on available events.
# Typical stable/fast range: 200-800. Larger gives diminishing returns.
JK_SAMPLES_PER_EVENT = 0.5
JK_SAMPLES_MIN = 200
JK_SAMPLES_MAX = 800
# Seed of the random subsets, so the error bars are reproducible
JK_SEED = 1

HBARC = 0.197327053  # GeV fm


def _robust_mad_log_filter(event_scale: np.ndarray, zmax: float) -> np.ndarray:
    """Return boolean mask of events to keep.

    event_scale: 1D array, one non-negative scale per event.
    The filter is performed on log10(event_scale) to handle heavy tails.
    """
    event_scale = np.asarray(event_scale)
    keep = np.isfinite(event_scale) & (event_scale > 0)
    if keep.sum() < 3:
        # Not enough info to robustly filter; keep what is valid.
        return keep

    x = np.log10(event_scale[keep])
    med = np.median(x)
    mad = np.median(np.abs(x - med))

    if mad == 0 or not np.isfinite(mad):
        # Distribution is degenerate; avoid dividing by 0.
        return keep

    # Modified z-score (consistent with normal dist when data are Gaussian)
    z = 0.6745 * (x - med) / mad
    keep_idx = np.zeros_like(keep, dtype=bool)
    keep_idx[np.where(keep)[0]] = np.abs(z) <= zmax
    return keep_idx


def _integrate_theta(values: np.ndarray, axis: int) -> np.ndarray:
    """Integrate over theta on the grid theta_i = i 2 pi / ntheta.

    subnucleondiffraction writes theta in [0, 2 pi) without the end point, and
    the integrand is periodic, so the rectangle rule is the right rule here
    (Simpson's rule on these points would leave out [2 pi - dtheta, 2 pi]).
    """
    return np.sum(values, axis=axis) * 2.0 * np.pi / values.shape[axis]


def _integrate_b(values: np.ndarray, b_vals: np.ndarray, axis: int) -> np.ndarray:
    """Integrate over b on the midpoint grid b_i = (i + 1/2) db."""
    db = (b_vals[-1] - b_vals[0]) / (len(b_vals) - 1) if len(b_vals) > 1 else 2.0 * b_vals[0]
    return np.sum(values, axis=axis) * db


# Dataset names written by the framework: AmpF_Q2_<Q2>_<event>_<file>_x_<x>
AMPF_NAME = re.compile(r"^AmpF_Q2_([^_]+)_.*_x_([^_]+)$")

if len(argv) < 2 or len(argv) > 3:
    print("Usage: compute_totalCrossSections.py <input_file> [optional_additional_file]")
    exit(1)

input_file = argv[1]
extra_file = argv[2] if len(argv) == 3 else None

# =========================
# Output directory
# =========================
if PLOT_FLAG:
    plot_dir = "plots_Integrated"
    os.makedirs(plot_dir, exist_ok=True)

# =========================
# Load HDF5 file
# =========================
hf1 = h5py.File(input_file, "r")
event_list1 = list(hf1.keys())

if len(event_list1) == 0:
    sys.exit("No events found in the file.")

event_list2 = []
hf2 = None
if extra_file and os.path.exists(extra_file):
    hf2 = h5py.File(extra_file, "r")
    event_list2 = list(hf2.keys())
elif extra_file and not os.path.exists(extra_file):
    print(f"File {extra_file} does not exist.")
# Rename events from second file to avoid collisions
event_list2_renamed = [name + "_extra" for name in event_list2]
# Merge event lists
event_list = event_list1 + event_list2_renamed
events = {name: hf1[name] for name in event_list1}
if hf2:
    events.update({new_name: hf2[old_name] for old_name, new_name in zip(event_list2, event_list2_renamed)})


event_data = events[event_list[0]]
name_matches = [AMPF_NAME.match(name) for name in event_data.keys()]
name_matches = [m for m in name_matches if m]
Q2List = sorted({m.group(1) for m in name_matches}, key=float)
xList = sorted({m.group(2) for m in name_matches}, key=float, reverse=True)

# =========================
# Storage
# =========================
Q2_used = []
x_used = []
sigma_coh_T = []
sigma_coh_T_err = []
sigma_incoh_T = []
sigma_incoh_T_err = []

sigma_coh_L = []
sigma_coh_L_err = []
sigma_incoh_L = []
sigma_incoh_L_err = []

for Q2 in Q2List:

    # =========================
    # Plot setup
    # =========================
    if PLOT_FLAG:
        # Four rows:
        # 0: |F_T|^2 (θ-integrated) vs b
        # 1: |F_L|^2 (θ-integrated) vs b
        # 2: |F_T|^2 (b-integrated) vs θ
        # 3: |F_L|^2 (b-integrated) vs θ
        fig, axs = plt.subplots(4, len(xList), figsize=(5 * len(xList), 10))
        if len(xList) == 1:
            # Ensure consistent 2D indexing axs[row, col]
            axs = np.array(axs).reshape(4, 1)

    # =========================
    # Main loop over x
    # =========================
    for k, x_i in enumerate(xList):

        try:
            float(x_i)
        except ValueError:
            continue

        F_T_real = []
        F_T_imag = []
        F_L_real = []
        F_L_imag = []
        b_arr = None
        theta_arr = None

        # -------------------------
        # Read data
        # -------------------------
        for event_name in event_list:
            event_group = events.get(event_name)

            for fileName in event_group.keys():
                m = AMPF_NAME.match(fileName)
                if not m or m.group(1) != Q2 or m.group(2) != x_i:
                    continue
                data = np.nan_to_num(event_group.get(fileName))
                if data.ndim != 2 or data.shape[1] < 6:
                    continue

                F_T_real.append(data[:, 2])
                F_T_imag.append(data[:, 3])
                F_L_real.append(data[:, 4])
                F_L_imag.append(data[:, 5])

                if b_arr is None:
                    b_arr = data[:, 0]
                if theta_arr is None:
                    theta_arr = data[:, 1]

        if len(F_T_real) == 0:
            continue

        F_T_real = np.array(F_T_real)
        F_T_imag = np.array(F_T_imag)
        F_L_real = np.array(F_L_real)
        F_L_imag = np.array(F_L_imag)

        nev_raw = F_T_real.shape[0]

        # Infer the 2D (b, theta) grid from the flattened arrays (use first event as reference)
        b_arr = np.asarray(b_arr)
        theta_arr = np.asarray(theta_arr)
        b_vals = np.unique(b_arr)
        theta_vals = np.unique(theta_arr)
        nb = len(b_vals)
        ntheta = len(theta_vals)

        if nb * ntheta != b_arr.size:
            raise RuntimeError(
                f"Inconsistent grid: nb*ntheta={nb*ntheta} but number of points={b_arr.size}"
            )
        if not np.allclose(theta_vals, np.arange(ntheta) * 2.0 * np.pi / ntheta, atol=1e-4):
            raise RuntimeError("Expected theta_i = i 2 pi / ntheta, the grid of subnucleondiffraction")

        # -------------------------
        # Robust outlier filtering (per x-bin)
        # -------------------------
        keep_mask = np.ones(nev_raw, dtype=bool)
        if OUTLIER_FILTER_FLAG and OUTLIER_METHOD == "mad_log":
            # One scale per event: max over grid of total |F|^2 (T + L)
            # Using log10 makes the cut stable even when scales span many decades.
            total_abs2 = (
                (F_T_real**2 + F_T_imag**2) + (F_L_real**2 + F_L_imag**2)
            )
            event_scale = np.nanmax(total_abs2, axis=1)
            keep_mask = _robust_mad_log_filter(event_scale, zmax=OUTLIER_ZMAX)

        # Precompute θ-integrated total |F|^2 vs b if needed by endpoint/shape filters.
        total_abs2_int_theta = None
        if (ENDPOINT_OUTLIER_FILTER_FLAG and OUTLIER_METHOD == "mad_log") or B0_END_RATIO_FILTER_FLAG:
            total_abs2_2d = (
                (F_T_real**2 + F_T_imag**2) + (F_L_real**2 + F_L_imag**2)
            ).reshape(nev_raw, nb, ntheta)

            # shape (nev_raw, nb)
            total_abs2_int_theta = _integrate_theta(total_abs2_2d, axis=2)

        if ENDPOINT_OUTLIER_FILTER_FLAG and OUTLIER_METHOD == "mad_log":
            # Compute θ-integrated total |F|^2 at b=min and b=max.
            # Filter smallest-b and largest-b endpoints separately and AND-combine them.
            endpoint_scale_minb = total_abs2_int_theta[:, 0]
            endpoint_scale_maxb = total_abs2_int_theta[:, -1]

            endpoint_keep_minb = _robust_mad_log_filter(endpoint_scale_minb, zmax=ENDPOINT_OUTLIER_ZMAX)
            endpoint_keep_maxb = _robust_mad_log_filter(endpoint_scale_maxb, zmax=ENDPOINT_OUTLIER_ZMAX)
            endpoint_keep = endpoint_keep_minb & endpoint_keep_maxb
            keep_mask = keep_mask & endpoint_keep

        if B0_END_RATIO_FILTER_FLAG:
            # b≈0 bin: choose the b value closest to 0.
            b0_idx = int(np.argmin(np.abs(b_vals)))
            b0_val = total_abs2_int_theta[:, b0_idx]
            bend_val = total_abs2_int_theta[:, -1]
            ratio_threshold = 10.0 ** float(B0_END_RATIO_MIN_DECADES)

            finite = np.isfinite(b0_val) & np.isfinite(bend_val)
            nonneg = (b0_val > 0) & (bend_val >= 0)
            # If bend_val == 0, ratio is +inf; treat as passing the ratio cut.
            passes = finite & nonneg & (b0_val >= ratio_threshold * bend_val)
            keep_mask = keep_mask & passes

        # Always drop events that produced NaNs/Infs anywhere
        keep_mask = (
            keep_mask
            & np.all(np.isfinite(F_T_real), axis=1)
            & np.all(np.isfinite(F_T_imag), axis=1)
            & np.all(np.isfinite(F_L_real), axis=1)
            & np.all(np.isfinite(F_L_imag), axis=1)
        )

        if keep_mask.sum() < MIN_EVENTS_AFTER_FILTER:
            print(
                f"Q2={Q2}, x={x_i}: kept {keep_mask.sum()} / {nev_raw} events after filtering (<{MIN_EVENTS_AFTER_FILTER}); skipping."
            )
            continue

        if OUTLIER_FILTER_FLAG and keep_mask.sum() != nev_raw:
            print(
                f"Q2={Q2}, x={x_i}: filtered out {nev_raw - keep_mask.sum()} / {nev_raw} events (method={OUTLIER_METHOD}, zmax={OUTLIER_ZMAX})."
            )

        if ENDPOINT_OUTLIER_FILTER_FLAG and OUTLIER_METHOD == "mad_log":
            removed_minb = np.count_nonzero(~endpoint_keep_minb)
            removed_maxb = np.count_nonzero(~endpoint_keep_maxb)
            removed_either = np.count_nonzero(~endpoint_keep)
            if removed_either:
                print(
                    f"Q2={Q2}, x={x_i}: endpoint filter removed {removed_either} / {nev_raw} events "
                    f"(min-b removed {removed_minb}, max-b removed {removed_maxb}, zmax={ENDPOINT_OUTLIER_ZMAX})."
                )

        if B0_END_RATIO_FILTER_FLAG:
            removed_ratio = np.count_nonzero(~passes)
            if removed_ratio:
                print(
                    f"Q2={Q2}, x={x_i}: b0/end ratio filter removed {removed_ratio} / {nev_raw} events "
                    f"(min decades={B0_END_RATIO_MIN_DECADES})."
                )

        F_T_real = F_T_real[keep_mask]
        F_T_imag = F_T_imag[keep_mask]
        F_L_real = F_L_real[keep_mask]
        F_L_imag = F_L_imag[keep_mask]

        nev = F_T_real.shape[0]
        print(f"Q2={Q2}, x={x_i}: number of events used: {nev}")

        # -------------------------
        # Plot theta-integrated |F|^2 vs b
        # -------------------------
        if PLOT_FLAG:
            for i in range(nev):
                # Reshape to (nb, ntheta) to integrate over theta
                F_T_real_i = F_T_real[i].reshape(nb, ntheta) + 1e-16
                F_T_imag_i = F_T_imag[i].reshape(nb, ntheta) + 1e-16
                F_L_real_i = F_L_real[i].reshape(nb, ntheta) + 1e-16
                F_L_imag_i = F_L_imag[i].reshape(nb, ntheta) + 1e-16

                F_T_abs2 = F_T_real_i**2 + F_T_imag_i**2
                F_L_abs2 = F_L_real_i**2 + F_L_imag_i**2

                F_T_abs2_int_theta = _integrate_theta(F_T_abs2, axis=1)  # shape (nb,)
                F_L_abs2_int_theta = _integrate_theta(F_L_abs2, axis=1)  # shape (nb,)

                # Integrate over b to get b-integrated profiles vs θ
                F_T_abs2_int_b = _integrate_b(F_T_abs2, b_vals, axis=0)  # shape (ntheta,)
                F_L_abs2_int_b = _integrate_b(F_L_abs2, b_vals, axis=0)  # shape (ntheta,)

                # Plot only lines (no markers) for clearer curves
                axs[0, k].plot(b_vals, F_T_abs2_int_theta, alpha=0.2, linestyle='-', marker=None)
                axs[1, k].plot(b_vals, F_L_abs2_int_theta, alpha=0.2, linestyle='-', marker=None)
                axs[2, k].plot(theta_vals, F_T_abs2_int_b, alpha=0.2, linestyle='-', marker=None)
                axs[3, k].plot(theta_vals, F_L_abs2_int_b, alpha=0.2, linestyle='-', marker=None)

            axs[0, k].set_title(f"x = {x_i}")
            axs[0, k].set_xlabel("b [1/GeV]")
            axs[0, k].set_ylabel(r"|F_T|$^2$ (θ-integrated)")
            axs[0, k].set_yscale("log")

            axs[1, k].set_xlabel("b [1/GeV]")
            axs[1, k].set_ylabel(r"|F_L|$^2$ (θ-integrated)")
            axs[1, k].set_yscale("log")

            axs[2, k].set_xlabel(r"θ")
            axs[2, k].set_ylabel(r"|F_T|$^2$ (b-integrated)")
            axs[2, k].set_yscale("log")

            axs[3, k].set_xlabel(r"θ")
            axs[3, k].set_ylabel(r"|F_L|$^2$ (b-integrated)")
            axs[3, k].set_yscale("log")

        # =========================
        # Prefactor
        # =========================
        prefactor_coh = 1e7 * HBARC**2 / (16.0 * np.pi * np.pi)
        prefactor_incoh = 1e7 * HBARC**2 / (16.0 * np.pi * np.pi)

        # =========================
        # Jackknife
        # =========================
        delete_n = int(JK_DELETE_FRACTION * nev)
        number_JK = int(np.clip(JK_SAMPLES_PER_EVENT * nev, JK_SAMPLES_MIN, JK_SAMPLES_MAX))

        if delete_n == 0 or (nev - delete_n) < 2:
            print(f"Q2={Q2}, x={x_i}: not enough events for jackknife (nev={nev}, delete_n={delete_n}); skipping.")
            continue

        rng = np.random.default_rng(JK_SEED)
        sigma_coh_T_samples = []
        sigma_incoh_T_samples = []
        sigma_coh_L_samples = []
        sigma_incoh_L_samples = []

        # -------------------------
        # Jackknife resampling
        # -------------------------
        for _ in range(number_JK):
            idx = rng.choice(nev, nev - delete_n, replace=False)

            # Transverse component: coherent part |<F_T>|^2
            F_T_real_mean = np.mean(F_T_real[idx], axis=0).reshape(nb, ntheta)
            F_T_imag_mean = np.mean(F_T_imag[idx], axis=0).reshape(nb, ntheta)
            F_T_mean_sq = F_T_real_mean**2 + F_T_imag_mean**2

            F_T_mean_sq_int_over_theta = _integrate_theta(F_T_mean_sq, axis=1)  # shape (nb,)
            sigma_coh_T_val = prefactor_coh * _integrate_b(F_T_mean_sq_int_over_theta * b_vals, b_vals, axis=0)
            sigma_coh_T_samples.append(sigma_coh_T_val)

            # Transverse component: incoherent part <|F_T|^2> - |<F_T>|^2
            F_T_abs2_mean = np.mean(F_T_real[idx]**2 + F_T_imag[idx]**2, axis=0).reshape(nb, ntheta)
            F_T_var = F_T_abs2_mean - F_T_mean_sq
            F_T_var_int_over_theta = _integrate_theta(F_T_var, axis=1)
            sigma_incoh_T_val = prefactor_incoh * _integrate_b(F_T_var_int_over_theta * b_vals, b_vals, axis=0)
            sigma_incoh_T_samples.append(sigma_incoh_T_val)

            # Longitudinal component: coherent part |<F_L>|^2
            F_L_real_mean = np.mean(F_L_real[idx], axis=0).reshape(nb, ntheta)
            F_L_imag_mean = np.mean(F_L_imag[idx], axis=0).reshape(nb, ntheta)
            F_L_mean_sq = F_L_real_mean**2 + F_L_imag_mean**2

            F_L_mean_sq_int_over_theta = _integrate_theta(F_L_mean_sq, axis=1)  # shape (nb,)
            sigma_coh_L_val = prefactor_coh * _integrate_b(F_L_mean_sq_int_over_theta * b_vals, b_vals, axis=0)
            sigma_coh_L_samples.append(sigma_coh_L_val)

            # Longitudinal component: incoherent part <|F_L|^2> - |<F_L>|^2
            F_L_abs2_mean = np.mean(F_L_real[idx]**2 + F_L_imag[idx]**2, axis=0).reshape(nb, ntheta)
            F_L_var = F_L_abs2_mean - F_L_mean_sq
            F_L_var_int_over_theta = _integrate_theta(F_L_var, axis=1)
            sigma_incoh_L_val = prefactor_incoh * _integrate_b(F_L_var_int_over_theta * b_vals, b_vals, axis=0)
            sigma_incoh_L_samples.append(sigma_incoh_L_val)

        sigma_coh_T_samples = np.array(sigma_coh_T_samples)
        sigma_incoh_T_samples = np.array(sigma_incoh_T_samples)
        sigma_coh_L_samples = np.array(sigma_coh_L_samples)
        sigma_incoh_L_samples = np.array(sigma_incoh_L_samples)

        # =========================
        # Means and errors
        # =========================
        def jk_err(samples):
            # delete-d jackknife: var = (n - d) / d * (variance of the subset estimates)
            return np.sqrt((nev - delete_n) / delete_n * np.var(samples))

        sigma_coh_T.append(np.mean(sigma_coh_T_samples))
        sigma_coh_T_err.append(jk_err(sigma_coh_T_samples))
        sigma_incoh_T.append(np.mean(sigma_incoh_T_samples))
        sigma_incoh_T_err.append(jk_err(sigma_incoh_T_samples))

        sigma_coh_L.append(np.mean(sigma_coh_L_samples))
        sigma_coh_L_err.append(jk_err(sigma_coh_L_samples))
        sigma_incoh_L.append(np.mean(sigma_incoh_L_samples))
        sigma_incoh_L_err.append(jk_err(sigma_incoh_L_samples))

        Q2_used.append(float(Q2))
        x_used.append(float(x_i))

    if PLOT_FLAG:
        plt.tight_layout()
        q2_tag = f"_Q2_{Q2}" if len(Q2List) > 1 else ""
        outfile = path.join(
            plot_dir, f"total_cross_sections_{argv[1].split('_')[-1].split('.')[0]}{q2_tag}.png"
        )
        plt.savefig(outfile)
        plt.close(fig)

# =========================
# Finalize
# =========================
hf1.close()
if hf2:
    hf2.close()


# =========================
# Write output file
# =========================
source_dir = path.dirname(path.abspath(argv[1]))
output_file = path.join(source_dir, "total_cross_sections.dat")

with open(output_file, "w") as of:
    of.write("# x  coh_T[nb]  err_coh_T[nb]  incoh_T[nb]  err_incoh_T[nb]  coh_L[nb]  err_coh_L[nb]  incoh_L[nb]  err_incoh_L[nb]  Q2[GeV^2]\n")
    for i, x in enumerate(x_used):
        of.write(
            f"{float(x):.6e} "
            f"{sigma_coh_T[i]:.6e} {sigma_coh_T_err[i]:.6e} "
            f"{sigma_incoh_T[i]:.6e} {sigma_incoh_T_err[i]:.6e} "
            f"{sigma_coh_L[i]:.6e} {sigma_coh_L_err[i]:.6e} "
            f"{sigma_incoh_L[i]:.6e} {sigma_incoh_L_err[i]:.6e} "
            f"{Q2_used[i]:.6e}\n"
        )

if PRINT_FLAG:
    for i, x in enumerate(x_used):
        print(
            f"Q2={Q2_used[i]}, x={x}: "
            f"sigma_coh_T={sigma_coh_T[i]:.4e}±{sigma_coh_T_err[i]:.4e}, "
            f"sigma_incoh_T={sigma_incoh_T[i]:.4e}±{sigma_incoh_T_err[i]:.4e}, "
            f"sigma_coh_L={sigma_coh_L[i]:.4e}±{sigma_coh_L_err[i]:.4e}, "
            f"sigma_incoh_L={sigma_incoh_L[i]:.4e}±{sigma_incoh_L_err[i]:.4e}"
        )
