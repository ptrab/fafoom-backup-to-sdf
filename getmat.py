#!/usr/bin/env python3
""" script to extract the SOCMEs from an ORCA 5.0 output file """

import sys
import argparse as ap
import numpy as np
import matplotlib.pyplot as plt


def get_input(args):
    """parse the input"""
    parser = ap.ArgumentParser(
        description=("extract the spin-orbit-coupling matrix from orca 4.1")
    )
    parser.add_argument(
        "orca_file", help=("orca 4 output file containing the SOC matrix")
    )
    parser.add_argument(
        "--no-print",
        "-np",
        action="store_true",
        help="does not show the matrix",
    )
    parser.add_argument(
        "--no-save",
        "-ns",
        action="store_true",
        help="does not save the matrix",
    )
    parser.add_argument(
        "--matrix-file",
        "-m",
        default="singlet-triplet-mat.csv",
        help=(
            "output filename of the extracted singlet-triplet-soc matrix. default: singlet-triplet-mat.csv"
        ),
    )
    parser.add_argument(
        "--gamma",
        "-g",
        default=1000,
        type=float,
        help="broadening of lorentz function for k_ISC",
    )

    return parser.parse_args(args)


def get_lines(filename):
    with open(filename, "r") as handle:
        lines = handle.readlines()

    print(f"file {filename} read")
    return lines


def get_number_of_excited_states(raw):
    for line in raw:
        if "Number of roots to be determined" in line:
            sline = line.split()
            print(f"{int(sline[-1])} excited states found")
            return int(sline[-1])


def euc_dist(array):
    return np.sqrt(np.sum(np.power(np.abs(array), 2)))


def get_socme(raw):
    line_counter = 0
    n_exc_found = False
    xyz_found = False
    ms_found = False

    print("searching for SOCME matrix")
    for line in raw:
        if "Number of roots to be determined" in line and n_exc_found == False:
            n_exc_found = True
            sline = line.split()
            n_exc = int(sline[-1])
            sing_trip_xyz = np.zeros((n_exc, n_exc + 1))
            sing_trip_ms = np.zeros((n_exc, n_exc + 1))

        #      --------------------------------------------------------------------------------
        #                      CALCULATED SOCME BETWEEN TRIPLETS AND SINGLETS
        #      --------------------------------------------------------------------------------
        #           Root                          <T|HSO|S>  (Re, Im) cm-1
        #         T      S              Z                    X                     Y           < FIRST OCCURRENCE IS XYZ
        #         T      S           MS= 0                  -1                    +1           < SECOND IS M_S
        #      --------------------------------------------------------------------------------
        #         1      0    (0.00e+00 , 8.41e+00)    (-6.17e+00 , -4.88e+00)    (-6.17e+00 , 4.88e+00)

        if (
            "CALCULATED SOCME BETWEEN TRIPLETS AND SINGLETS" in line
            and n_exc_found == True
            and xyz_found == False
        ):
            print(f"found xyz line of socme in line {line_counter}")
            xyz_line_count = line_counter
            xyz_found = True
            # [1, 0] to [100, 100]
            rows = raw[
                line_counter + 5 : line_counter + n_exc * (n_exc + 1) + 5
            ]
            for row in rows:
                row = row.replace("(", " ").replace(")", " ").replace(",", " ")
                #  1      0    0.00e+00  8.41e+00    -6.17e+00   -4.88e+00    -6.17e+00   4.88e+00
                srow = row.split()
                i, j, r1, i1, r2, i2, r3, i3 = srow
                i, j, r1, i1, r2, i2, r3, i3 = (
                    int(i),
                    int(j),
                    float(r1),
                    float(i1),
                    float(r2),
                    float(i2),
                    float(r3),
                    float(i3),
                )
                socme = np.array(
                    [complex(r1, i1), complex(r2, i2), complex(r3, i3)]
                )
                socme = euc_dist(socme)
                sing_trip_xyz[i - 1, j] = socme

        if (
            "CALCULATED SOCME BETWEEN TRIPLETS AND SINGLETS" in line
            and n_exc_found == True
            and xyz_found == True
            and ms_found == False
            and line_counter > xyz_line_count
        ):
            print(f"found m_s line of socme in line {line_counter}")
            ms_found = True
            # [1, 0] to [100, 100]
            rows = raw[
                line_counter + 5 : line_counter + n_exc * (n_exc + 1) + 5
            ]
            for row in rows:
                row = row.replace("(", " ").replace(")", " ").replace(",", " ")
                #  1      0    0.00e+00  8.41e+00    -6.17e+00   -4.88e+00    -6.17e+00   4.88e+00
                srow = row.split()
                i, j, r1, i1, r2, i2, r3, i3 = srow
                i, j, r1, i1, r2, i2, r3, i3 = (
                    int(i),
                    int(j),
                    float(r1),
                    float(i1),
                    float(r2),
                    float(i2),
                    float(r3),
                    float(i3),
                )
                socme = np.array(
                    [complex(r1, i1), complex(r2, i2), complex(r3, i3)]
                )
                socme = euc_dist(socme)
                sing_trip_ms[i - 1, j] = socme

        line_counter += 1

    return sing_trip_xyz.T, sing_trip_ms.T


# haven't tried this in a while
def get_reduced_socme(raw):
    line_counter = 0
    n_exc_found = False
    sing_trip_found = False
    trip_trip_found = False

    for line in raw:
        if "Number of roots to be determined" in line and n_exc_found == False:
            n_exc_found = True
            sline = line.split()
            n_exc = int(sline[-1])
            sing_trip_mat = np.zeros((n_exc, n_exc + 1))
            trip_trip_mat = np.zeros((n_exc, n_exc))

        if (
            "CALCULATED REDUCED SOCME BETWEEN TRIPLETS AND SINGLETS" in line
            and n_exc_found == True
            and sing_trip_found == False
        ):
            sing_trip_found = True
            # [0, 0] bis [n_exc-1, n_exc]
            rows = raw[
                line_counter + 5 : line_counter + n_exc * (n_exc + 1) + 5
            ]
            for row in rows:
                srow = row.split()
                i, j, x, y, z = srow
                i, j, x, y, z = int(i), int(j), float(x), float(y), float(z)
                socme = np.array([x, y, z])
                socme = euc_dist(socme)
                sing_trip_mat[i, j] = socme

        if (
            "CALCULATED REDUCED SOCME BETWEEN TRIPLETS" in line
            and not "SINGLETS" in line
            and n_exc_found == True
            and sing_trip_found == True
            and trip_trip_found == False
        ):
            trip_trip_found == True
            # [0, 0] bis [nexc-1, nexc-1]
            rows = raw[
                line_counter + 5 : line_counter + n_exc * (n_exc + 1) // 2 + 5
            ]
            for row in rows:
                srow = row.split()
                i, j, x, y, z = srow
                i, j, x, y, z = int(i), int(j), float(x), float(y), float(z)
                socme = np.array([x, y, z])
                socme = euc_dist(socme)
                trip_trip_mat[i, j] = socme
            break

        line_counter += 1

    return sing_trip_mat.T, trip_trip_mat.T


def print_mat(mat):
    plt.imshow(mat, interpolation=None, cmap="Greys")
    plt.xticks(np.arange(9, 101, 10), np.arange(10, 101, 10))
    cbar = plt.colorbar()
    plt.show()


def print_3dmat(mat):
    from mpl_toolkits.mplot3d import Axes3D

    fig = plt.figure(figsize=(8, 3))
    ax = fig.add_subplot(111, projection="3d")

    _x = np.arange(100)
    _y = np.arange(101)
    _xx, _yy = np.meshgrid(_x, _y)
    x, y = _xx.ravel(), _yy.ravel()

    top = mat.ravel()
    bottom = np.zeros_like(top)
    width = depth = 1

    ax.bar3d(x, y, bottom, width, depth, top, shade=True)

    plt.show()


def save_mat(mat, filename):
    np.savetxt(filename, mat, delimiter=",", fmt="%.0f")


def get_total_energy(raw):
    # Total Energy       :       -12312.28056663 Eh         -335034.18703 eV
    for line in raw:
        if "Total Energy" in line:
            sline = line.split()
            total_energy = sline[-2]  # in eV
    return total_energy


def get_orca_excited_states(lines):
    s0_energy = float(get_total_energy(lines))  # in eV
    s0_energy_nm = 1239.84 / s0_energy  # in nm
    s0_energy_icm = 10 ** 7 / s0_energy_nm  # in cm**-1
    singlet_states = [[int(0), s0_energy_icm, s0_energy_nm, 0]]
    triplet_states = []

    for i in range(len(lines)):
        if (
            "ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS"
            in lines[i]
        ):
            absorption_start = i + 5
        elif (
            "ABSORPTION SPECTRUM VIA TRANSITION VELOCITY DIPOLE MOMENTS"
            in lines[i]
            or "CD SPECTRUM" in lines[i]
        ):
            absorption_end = i - 2
            break
    #   nr   en / icm  lam / nm   f_osc
    #   20   15147.0    660.2   0.000076214   0.00166   0.03728  -0.01632  -0.00020
    #   21    6525.5   1532.5   spin forbidden (mult=3)
    for line in lines[absorption_start:absorption_end]:
        sline = line.split()
        number = int(sline[0])
        energy = float(sline[1])
        wavelength = float(sline[2])
        if len(sline) == 6:
            print(f"TRIPLET: {sline}")
            oscillator_strength = 0.0
            triplet_states.append(
                [number, s0_energy_icm + energy, wavelength, oscillator_strength]
            )
        elif len(sline) == 8:
            print(f"SINGLET: {sline}")
            oscillator_strength = float(sline[3])
            singlet_states.append(
                [number, s0_energy_icm + energy, wavelength, oscillator_strength]
            )
        else:
            continue

    singlets = np.array(singlet_states)
    triplets = np.array(triplet_states)

    return singlets, triplets


def calc_kISC(singlets, triplets, couplings, gamma):
    # Top to Bottom: Singlets
    # Left to Right: Triplets
    # k_ISC calculated according to (53) and (55) from DOI: 10.1021/acs.jpca.1c06165
    h = 6.62607015 * 10 ** -34  # J s
    print(f"{h:e} s J")
    h = h / (1.602176634 * 10 ** -19)  # eV s
    print(f"{h:e} s eV")
    h = 1239.84 / h # nm^-1 s
    print(f"{h:e} s nm^-1")
    h = 10 ** 7 / h # cm**-1 s
    print(f"{h:e} s cm^-1")
    hbar = h / (2 * np.pi)
    for k in range(len(singlets)):
        print(f"Couplings of S({k:3d}) at {singlets[k,2]:8.1f} nm to:")
        for l in range(len(triplets)):
            Ekl = singlets[k,1] - triplets[l,1]
            kISC = 2 / hbar * couplings[k,l]**2 * gamma / (Ekl**2 + gamma**2)
            print(f"T({l+1:3d}) at {triplets[l,2]:8.1f} nm ... |SOC| = {couplings[k,l]:8.0f} cm^-1 ... Ekl = {Ekl:8.0f} cm^-1... k_ISC = {kISC:6.1e} s^-1")
        print("")


def main():
    args = get_input(sys.argv[1:])

    if args.no_print and args.no_save:
        sys.exit(
            "no save and no print => no matrix … why did you start the program? :D"
        )

    file_data = get_lines(args.orca_file)

    total_energy = get_total_energy(file_data)
    singlets, triplets = get_orca_excited_states(file_data)

    st_xyz_mat, st_ms_mat = get_socme(file_data)

    calc_kISC(singlets, triplets, st_xyz_mat, args.gamma)

    if not args.no_print:
        print_mat(st_ms_mat)

    if not args.no_save:
        save_mat(st_ms_mat, args.matrix_file)
        save_mat(st_xyz_mat, "xyz_matrix.csv")
        with open("xyz_matrix.csv", "a") as handle:
            handle.write("Top to Bottom: Singlets, Left to Right: Triplets")


if __name__ == "__main__":
    main()
