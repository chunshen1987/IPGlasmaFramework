#!/usr/bin/env python3

import numpy as np
from sys import argv, exit
from os import path
import h5py
from scipy.integrate import simpson
import matplotlib.pyplot as plt
import os
import sys

# =========================
# User settings
# =========================
PLOT_FLAG = True
PRINT_FLAG = True

HBARC = 0.197327053  # GeV fm

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
ampList = list(event_data.keys())
xList = sorted({x.split("_")[-1] for x in ampList}, key=float, reverse=True)

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
            if not fileName.startswith("AmpF_"):
                continue
            if x_i not in fileName:
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

    # Infer the 2D (b, theta) grid from the flattened arrays
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

    nev = F_T_real.shape[0]
    print(f"x={x_i}: Number of events after filtering: {nev}")

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

            F_T_abs2_int_theta = simpson(F_T_abs2, x=theta_vals, axis=1)  # shape (nb,)
            F_L_abs2_int_theta = simpson(F_L_abs2, x=theta_vals, axis=1)  # shape (nb,)

            # Integrate over b to get b-integrated profiles vs θ
            F_T_abs2_int_b = simpson(F_T_abs2, x=b_vals, axis=0)  # shape (ntheta,)
            F_L_abs2_int_b = simpson(F_L_abs2, x=b_vals, axis=0)  # shape (ntheta,)

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
    number_JK = 5000
    delete_n = int(0.2 * nev)

    if delete_n == 0:
        sys.exit("Not enough events for jackknife.")

    sigma_coh_T_samples = []
    sigma_incoh_T_samples = []
    sigma_coh_L_samples = []
    sigma_incoh_L_samples = []

    # -------------------------
    # Jackknife resampling
    # -------------------------
    for _ in range(number_JK):
        idx = np.random.choice(nev, nev - delete_n, replace=False)

        # Transverse component: coherent part |<F_T>|^2
        F_T_real_mean = np.mean(F_T_real[idx], axis=0).reshape(nb, ntheta)
        F_T_imag_mean = np.mean(F_T_imag[idx], axis=0).reshape(nb, ntheta)
        F_T_mean_sq = F_T_real_mean**2 + F_T_imag_mean**2

        F_T_mean_sq_int_over_theta = simpson(F_T_mean_sq, x=theta_vals, axis=1)  # shape (nb,)
        sigma_coh_T_val = prefactor_coh * simpson(F_T_mean_sq_int_over_theta * b_vals, x=b_vals)
        sigma_coh_T_samples.append(sigma_coh_T_val)

        # Transverse component: incoherent part <|F_T|^2> - |<F_T>|^2
        F_T_abs2_mean = np.mean(F_T_real[idx]**2 + F_T_imag[idx]**2, axis=0).reshape(nb, ntheta)
        F_T_var = F_T_abs2_mean - F_T_mean_sq
        F_T_var_int_over_theta = simpson(F_T_var, x=theta_vals, axis=1)
        sigma_incoh_T_val = prefactor_incoh * simpson(F_T_var_int_over_theta * b_vals, x=b_vals)
        sigma_incoh_T_samples.append(sigma_incoh_T_val)

        # Longitudinal component: coherent part |<F_L>|^2
        F_L_real_mean = np.mean(F_L_real[idx], axis=0).reshape(nb, ntheta)
        F_L_imag_mean = np.mean(F_L_imag[idx], axis=0).reshape(nb, ntheta)
        F_L_mean_sq = F_L_real_mean**2 + F_L_imag_mean**2

        F_L_mean_sq_int_over_theta = simpson(F_L_mean_sq, x=theta_vals, axis=1)  # shape (nb,)
        sigma_coh_L_val = prefactor_coh * simpson(F_L_mean_sq_int_over_theta * b_vals, x=b_vals)
        sigma_coh_L_samples.append(sigma_coh_L_val)

        # Longitudinal component: incoherent part <|F_L|^2> - |<F_L>|^2
        F_L_abs2_mean = np.mean(F_L_real[idx]**2 + F_L_imag[idx]**2, axis=0).reshape(nb, ntheta)
        F_L_var = F_L_abs2_mean - F_L_mean_sq
        F_L_var_int_over_theta = simpson(F_L_var, x=theta_vals, axis=1)
        sigma_incoh_L_val = prefactor_incoh * simpson(F_L_var_int_over_theta * b_vals, x=b_vals)
        sigma_incoh_L_samples.append(sigma_incoh_L_val)

    sigma_coh_T_samples = np.array(sigma_coh_T_samples)
    sigma_incoh_T_samples = np.array(sigma_incoh_T_samples)
    sigma_coh_L_samples = np.array(sigma_coh_L_samples)
    sigma_incoh_L_samples = np.array(sigma_incoh_L_samples)

    # =========================
    # Means and errors
    # =========================
    def jk_err(samples):
        return np.sqrt((nev - delete_n) / nev * np.var(samples))

    sigma_coh_T.append(np.mean(sigma_coh_T_samples))
    sigma_coh_T_err.append(jk_err(sigma_coh_T_samples))
    sigma_incoh_T.append(np.mean(sigma_incoh_T_samples))
    sigma_incoh_T_err.append(jk_err(sigma_incoh_T_samples))

    sigma_coh_L.append(np.mean(sigma_coh_L_samples))
    sigma_coh_L_err.append(jk_err(sigma_coh_L_samples))
    sigma_incoh_L.append(np.mean(sigma_incoh_L_samples))
    sigma_incoh_L_err.append(jk_err(sigma_incoh_L_samples))

# =========================
# Finalize
# =========================
hf1.close()
if hf2:
    hf2.close()

if PLOT_FLAG:
    plt.tight_layout()
    outfile = path.join(
        plot_dir, f"total_cross_sections_{argv[1].split('_')[-1].split('.')[0]}.png"
    )
    plt.savefig(outfile)

# =========================
# Write output file
# =========================
source_dir = path.dirname(path.abspath(argv[1]))
output_file = path.join(source_dir, "total_cross_sections.dat")

with open(output_file, "w") as of:
    of.write("# x  coh_T[nb]  err_coh_T[nb]  incoh_T[nb]  err_incoh_T[nb]  coh_L[nb]  err_coh_L[nb]  incoh_L[nb]  err_incoh_L[nb] \n")
    for i, x in enumerate(xList):
        of.write(
            f"{float(x):.6e} "
            f"{sigma_coh_T[i]:.6e} {sigma_coh_T_err[i]:.6e} "
            f"{sigma_incoh_T[i]:.6e} {sigma_incoh_T_err[i]:.6e} "
            f"{sigma_coh_L[i]:.6e} {sigma_coh_L_err[i]:.6e} "
            f"{sigma_incoh_L[i]:.6e} {sigma_incoh_L_err[i]:.6e}\n"
        )

if PRINT_FLAG:
    for i, x in enumerate(xList):
        print(
            f"x={x}: "
            f"sigma_coh_T={sigma_coh_T[i]:.4e}±{sigma_coh_T_err[i]:.4e}, "
            f"sigma_incoh_T={sigma_incoh_T[i]:.4e}±{sigma_incoh_T_err[i]:.4e}, "
            f"sigma_coh_L={sigma_coh_L[i]:.4e}±{sigma_coh_L_err[i]:.4e}, "
            f"sigma_incoh_L={sigma_incoh_L[i]:.4e}±{sigma_incoh_L_err[i]:.4e}"
        )
