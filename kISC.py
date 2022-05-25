#!/usr/bin/env python

import sys
import argparse
import numpy as np


def getinput(args):
    """parse the input"""
    parser = argparse.ArgumentParser(
        description=("Calculation of Intersystem Crossing Rates, k_ISC")
    )
    parser.add_argument(
        "--singlet-energies",
        "-s",
        nargs="*",
        type=float,
        help=("Singlet energies in atomic units."),
    )
    parser.add_argument(
        "--triplet-energies",
        "-t",
        nargs="*",
        type=float,
        help=("Triplet energies in atomic units."),
    )
    parser.add_argument(
        "--spin-orbit-couplings",
        "-soc",
        nargs="*",
        type=float,
        help=("spin-orbit couplings in inverse centimeters."),
    )
    parser.add_argument(
        "--gamma",
        "-g",
        default=1000.0,
        type=float,
        help=("Half life in inverse centimeters ... default 1000 cm^-1"),
    )

    return parser.parse_args(args)


def kISC(singlets, triplets, socs, gamma):
    # constants based on 2018 CODATA adjustments
    # https://physics.nist.gov/cuu/pdf/factors_2018.pdf
    # https://physics.nist.gov/cgi-bin/cuu/Value?c
    planck_constant = 6.62607015 * 10**-34  # Joules Seconds
    joule_per_electronvolts = 1.602176634 * 10**-19  # Joules / Electronvolts
    speed_of_light_in_vacuum = 299792458  # Meters / Seconds
    electronvolts_per_hartree = 27.211386245988  # eV / Eh
    nanometer_per_meter = 10**9
    nanometer_per_centimeter = 10**7

    electronvolts_per_nanometer = (
        nanometer_per_meter
        * planck_constant
        * speed_of_light_in_vacuum
        / joule_per_electronvolts
    )

    # hbar in s cm**-^
    hbar = (
        planck_constant
        / (2 * np.pi)
        * nanometer_per_centimeter
        / joule_per_electronvolts
        / electronvolts_per_nanometer
    )

    # E_kl in cm**-^1 converted from Eh as input
    ekl = (
        get_ekl_matrix(singlets, triplets)
        * electronvolts_per_hartree
        * nanometer_per_centimeter
        / electronvolts_per_nanometer
    )

    socs = get_soc_matrix(ekl, socs)

    # intersystem crossing rates in s**-1 according to equation (53)
    # from 10.1021/acs.jpca.1c06165
    kisc = 2 / hbar * socs**2 * gamma / (ekl**2 + gamma**2)

    with np.printoptions(precision=2):
        print("\nSOCs Rows=Singlets Columns=Triplets")
        print(kisc)


def get_ekl_matrix(singlets, triplets):
    n = len(singlets)
    sing_mat = np.reshape(singlets, (1, n))
    trip_mat = np.tile(triplets, (n, 1))
    return sing_mat.T - trip_mat


def get_soc_matrix(ekl, socs):
    socs = np.array(socs)
    matrix = socs.reshape(ekl.shape)

    print(matrix)

    return matrix


def main():
    args = getinput(sys.argv[1:])

    print(args.singlet_energies)
    print(args.triplet_energies)

    kISC(
        args.singlet_energies,
        args.triplet_energies,
        args.spin_orbit_couplings,
        args.gamma,
    )


if __name__ == "__main__":
    main()
