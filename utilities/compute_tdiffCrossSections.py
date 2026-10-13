#!/usr/bin/env python3

import numpy as np
from sys import argv, exit
from os import path, makedirs
import h5py
import re
import matplotlib.pyplot as plt
import os
import sys

# =========================
# User settings
# =========================
PLOT_FLAG = True
IMPULSE_APPROX_FLAG = False # Only analyze the t=0 data if True; otherwise analyze all t values

# Robust outlier rejection (recommended if occasional events blow up)
# The filter is computed separately for each x-bin so it adapts across parameter sets.
OUTLIER_FILTER_FLAG = True
# Method: robust z-score using median/MAD on log10(event_scale)
OUTLIER_METHOD = "mad_log"
# Typical safe range: 6-10. Smaller removes more events.
OUTLIER_ZMAX = 7.0
# If fewer events than this remain, skip this x-bin (avoid nonsense statistics)
MIN_EVENTS_AFTER_FILTER = 50

HBARC = 0.197327053  # GeV fm


def _ensure_2d_events(arr: np.ndarray) -> np.ndarray:
    """Ensure array has shape (nev, nt)."""
    arr = np.asarray(arr)
    if arr.ndim == 1:
        return arr.reshape(arr.shape[0], 1)
    return arr


def _robust_mad_log_filter(event_scale: np.ndarray, zmax: float) -> np.ndarray:
    """Return boolean mask of events to keep.

    event_scale: 1D array, one non-negative scale per event (e.g. max |F|^2 over t).
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

# Dataset names written by the framework: Amp_Q2_<Q2>_<event>_<file>_x_<x>
AMP_NAME = re.compile(r"^Amp_Q2_([^_]+)_.*_x_([^_]+)$")

if len(argv) < 2 or len(argv) > 3:
    print("Usage: compute_tdiffCrossSections.py <input_file> [optional_additional_file]")
    exit(1)

input_file = argv[1]
extra_file = argv[2] if len(argv) == 3 else None

# =========================
# Output directory
# =========================
if PLOT_FLAG:
    plot_dir = "plots_differential"
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
name_matches = [AMP_NAME.match(name) for name in event_data.keys()]
name_matches = [m for m in name_matches if m]
Q2List = sorted({m.group(1) for m in name_matches}, key=float)
xList = sorted({m.group(2) for m in name_matches}, key=float, reverse=True)

# =========================
# Storage
# =========================
sigma_coh_T = []
sigma_coh_T_err = []
sigma_incoh_T = []
sigma_incoh_T_err = []

sigma_coh_L = []
sigma_coh_L_err = []
sigma_incoh_L = []
sigma_incoh_L_err = []

# Dictionary to hold t-differential results for each (Q2, x)
x_i_results = {}

for Q2 in Q2List:

    # =========================
    # Plot setup
    # =========================
    if PLOT_FLAG:
        # Two rows:
        # 0: |F_T|^2 vs t
        # 1: |F_L|^2 vs t
        fig, axs = plt.subplots(2, len(xList), figsize=(5 * len(xList), 6))
        if len(xList) == 1:
            # Ensure consistent 2D indexing axs[row, col]
            axs = np.array(axs).reshape(2, 1)

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
        t_arr = None

        # -------------------------
        # Read data
        # -------------------------
        for event_name in event_list:
            event_group = events.get(event_name)

            for fileName in event_group.keys():
                m = AMP_NAME.match(fileName)
                if not m or m.group(1) != Q2 or m.group(2) != x_i:
                    continue

                # rows: t, Re F_T, Im F_T, Re F_L, Im F_L (a file with one t
                # value is read as a single row)
                data = np.atleast_2d(np.nan_to_num(event_group.get(fileName)))
                if data.shape[1] < 5:
                    continue

                if not IMPULSE_APPROX_FLAG:
                    F_T_real.append(data[:, 1])
                    F_T_imag.append(data[:, 2])
                    F_L_real.append(data[:, 3])
                    F_L_imag.append(data[:, 4])

                    if t_arr is None:
                        t_arr = data[:, 0]
                else:
                    # the row with the smallest |t|
                    row = data[np.argmin(np.abs(data[:, 0]))]
                    F_T_real.append(row[1])
                    F_T_imag.append(row[2])
                    F_L_real.append(row[3])
                    F_L_imag.append(row[4])

                    if t_arr is None:
                        t_arr = np.array([row[0]])

        if len(F_T_real) == 0:
            print(f"No valid data found for Q2={Q2}, x={x_i}. Skipping.")
            continue

        F_T_real = _ensure_2d_events(np.array(F_T_real))
        F_T_imag = _ensure_2d_events(np.array(F_T_imag))
        F_L_real = _ensure_2d_events(np.array(F_L_real))
        F_L_imag = _ensure_2d_events(np.array(F_L_imag))

        nev_raw = F_T_real.shape[0]

        # -------------------------
        # Robust outlier filtering (per x-bin)
        # -------------------------
        keep_mask = np.ones(nev_raw, dtype=bool)
        if OUTLIER_FILTER_FLAG and OUTLIER_METHOD == "mad_log":
            # One scale per event: max over t of total |F|^2 (T + L)
            # Using log10 makes the cut stable even when scales span many decades.
            total_abs2 = (
                (F_T_real**2 + F_T_imag**2) + (F_L_real**2 + F_L_imag**2)
            )
            event_scale = np.nanmax(total_abs2, axis=1)
            keep_mask = _robust_mad_log_filter(event_scale, zmax=OUTLIER_ZMAX)

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

        F_T_real = F_T_real[keep_mask]
        F_T_imag = F_T_imag[keep_mask]
        F_L_real = F_L_real[keep_mask]
        F_L_imag = F_L_imag[keep_mask]

        nev = F_T_real.shape[0]
        print(f"Q2={Q2}, x={x_i}: number of events used: {nev}")

        # -------------------------
        # Plot the F vs t for each event (after filtering)
        # -------------------------
        if PLOT_FLAG:
            for i in range(nev):
                FT_sq = F_T_real[i]**2 + F_T_imag[i]**2
                FL_sq = F_L_real[i]**2 + F_L_imag[i]**2
                if not IMPULSE_APPROX_FLAG:
                    axs[0, k].plot(t_arr, FT_sq, alpha=0.2, linestyle='-', marker=None)
                    axs[1, k].plot(t_arr, FL_sq, alpha=0.2, linestyle='-', marker=None)
                else:
                    axs[0, k].plot(t_arr, FT_sq, alpha=0.2, marker='o')
                    axs[1, k].plot(t_arr, FL_sq, alpha=0.2, marker='o')

            axs[0, k].set_title(f"x = {x_i}")
            axs[0, k].set_xlabel("t [GeV^2]")
            axs[0, k].set_ylabel(r"$|F_T|^2$")
            axs[1, k].set_xlabel("t [GeV^2]")
            axs[1, k].set_ylabel(r"$|F_L|^2$")
            axs[0, k].set_xscale("log")
            axs[1, k].set_xscale("log")

        # =========================
        # Prefactor
        # =========================
        prefactor = 1e7 * HBARC**2 / (16.0 * np.pi)

        # =========================
        # Coherent and incoherent cross sections (T and L), differential in t
        # =========================
        # Transverse component statistics
        F_T_real_mean = np.mean(F_T_real, axis=0)
        F_T_imag_mean = np.mean(F_T_imag, axis=0)
        F_T_real_std = np.std(F_T_real, axis=0)
        F_T_imag_std = np.std(F_T_imag, axis=0)
        F_T_real_sq_mean = np.mean(F_T_real**2.0, axis=0)
        F_T_imag_sq_mean = np.mean(F_T_imag**2.0, axis=0)
        F_T_real_sq_std = np.std(F_T_real**2.0, axis=0)
        F_T_imag_sq_std = np.std(F_T_imag**2.0, axis=0)

        # Longitudinal component statistics
        F_L_real_mean = np.mean(F_L_real, axis=0)
        F_L_imag_mean = np.mean(F_L_imag, axis=0)
        F_L_real_std = np.std(F_L_real, axis=0)
        F_L_imag_std = np.std(F_L_imag, axis=0)
        F_L_real_sq_mean = np.mean(F_L_real**2.0, axis=0)
        F_L_imag_sq_mean = np.mean(F_L_imag**2.0, axis=0)
        F_L_real_sq_std = np.std(F_L_real**2.0, axis=0)
        F_L_imag_sq_std = np.std(F_L_imag**2.0, axis=0)

        # Coherent cross sections sigma_coh ~ |<F>|^2
        coherent_T = (F_T_real_mean**2.0 + F_T_imag_mean**2.0) * prefactor
        coherent_L = (F_L_real_mean**2.0 + F_L_imag_mean**2.0) * prefactor

        coherent_T_err = (
            2.0
            * (np.abs(F_T_real_mean) * F_T_real_std + np.abs(F_T_imag_mean) * F_T_imag_std)
            * prefactor
            / np.sqrt(nev)
        )
        coherent_L_err = (
            2.0
            * (np.abs(F_L_real_mean) * F_L_real_std + np.abs(F_L_imag_mean) * F_L_imag_std)
            * prefactor
            / np.sqrt(nev)
        )

        # Incoherent cross sections sigma_incoh ~ <|F|^2> - |<F>|^2
        incoherent_T = (
            F_T_real_sq_mean
            + F_T_imag_sq_mean
            - F_T_real_mean**2.0
            - F_T_imag_mean**2.0
        ) * prefactor
        incoherent_L = (
            F_L_real_sq_mean
            + F_L_imag_sq_mean
            - F_L_real_mean**2.0
            - F_L_imag_mean**2.0
        ) * prefactor

        incoherent_T_err = (
            (
                F_T_real_sq_std
                + F_T_imag_sq_std
                + 2.0
                * (np.abs(F_T_real_mean) * F_T_real_std + np.abs(F_T_imag_mean) * F_T_imag_std)
            )
            * prefactor
            / np.sqrt(nev)
        )
        incoherent_L_err = (
            (
                F_L_real_sq_std
                + F_L_imag_sq_std
                + 2.0
                * (np.abs(F_L_real_mean) * F_L_real_std + np.abs(F_L_imag_mean) * F_L_imag_std)
            )
            * prefactor
            / np.sqrt(nev)
        )

        # Store t-differential results for this (Q2, x_i)
        x_i_results[(Q2, x_i)] = {
            "Q2": float(Q2),
            "x": float(x_i),
            "t": np.asarray(t_arr),
            "coh_T": coherent_T,
            "coh_T_err": coherent_T_err,
            "incoh_T": incoherent_T,
            "incoh_T_err": incoherent_T_err,
            "coh_L": coherent_L,
            "coh_L_err": coherent_L_err,
            "incoh_L": incoherent_L,
            "incoh_L_err": incoherent_L_err,
        }


    if PLOT_FLAG:
        plt.tight_layout()
        q2_tag = f"_Q2_{Q2}" if len(Q2List) > 1 else ""
        outfile = path.join(
            plot_dir, f"tdiff_cross_sections_{argv[1].split('_')[-1].split('.')[0]}{q2_tag}.png"
        )
        plt.savefig(outfile)
        plt.close(fig)

# =========================
# Finalize
# =========================
hf1.close()
if hf2:
    hf2.close()

# Write t-differential cross sections to a file
source_dir = path.dirname(path.abspath(argv[1]))
output_file = path.join(source_dir, "tdiff_cross_sections.dat")

with open(output_file, "w") as f:
    f.write(
        "# x  t[GeV^2]  coh_T[nb/GeV^2]  err_coh_T[nb/GeV^2]  incoh_T[nb/GeV^2]  err_incoh_T[nb/GeV^2]  "
        "coh_L[nb/GeV^2]  err_coh_L[nb/GeV^2]  incoh_L[nb/GeV^2]  err_incoh_L[nb/GeV^2]  Q2[GeV^2]\n"
    )
    for key in [(Q2, x_i) for Q2 in Q2List for x_i in xList]:
        if key not in x_i_results:
            continue
        results = x_i_results[key]
        x_val = results["x"]
        t_arr = results["t"]
        # Ensure we always have 1D arrays, also in impulse-approx (single-t) case
        coh_T = np.atleast_1d(results["coh_T"])
        coh_T_err = np.atleast_1d(results["coh_T_err"])
        incoh_T = np.atleast_1d(results["incoh_T"])
        incoh_T_err = np.atleast_1d(results["incoh_T_err"])
        coh_L = np.atleast_1d(results["coh_L"])
        coh_L_err = np.atleast_1d(results["coh_L_err"])
        incoh_L = np.atleast_1d(results["incoh_L"])
        incoh_L_err = np.atleast_1d(results["incoh_L_err"])

        for i in range(len(t_arr)):
            f.write(
                f"{x_val:.6e} {t_arr[i]:.6e} "
                f"{coh_T[i]:.6e} {coh_T_err[i]:.6e} "
                f"{incoh_T[i]:.6e} {incoh_T_err[i]:.6e} "
                f"{coh_L[i]:.6e} {coh_L_err[i]:.6e} "
                f"{incoh_L[i]:.6e} {incoh_L_err[i]:.6e} "
                f"{results['Q2']:.6e}\n"
            )