#!/usr/bin/env python
"""
Extracting stored Geometries from backup_{population,blacklist}.dat
which are genereated by Adriana Supady's "Flexible algorithm
for optimization of molecules", fafoom, to a sdf file.

(c)2015 Philipp Traber
Pylint 1.3.1: Your code has been rated at 10.00/10.
"""
import sys
import os
import errno
import re

# this function is from http://stackoverflow.com/a/10840586
def silentremove(filename):
    """Removes {population,blacklist}.sdf from the folder."""
    try:
        os.remove(filename)
    # this would be "except OSError, e:" before Python 2.6
    except OSError as damn:
        # errno.ENOENT = no such file or directory
        if damn.errno != errno.ENOENT:
            # re-raise exception if a different error occured
            raise

def convert_backup(filename):
    """Converts backup_{population,blacklist}.dat into a sdf-file."""
    filestring = open(filename, 'r').read()
    geometries = re.findall(r"'(.*?)'", filestring, re.DOTALL)

    if "blacklist" in filename:
        sdfname = "blacklist.sdf"
        silentremove(sdfname)
    elif "population" in filename:
        sdfname = "population.sdf"
        silentremove(sdfname)

    with open(sdfname, 'a') as sdffile:
        iszero = 0
        for geometry in geometries:
            if "NEWLINE" in geometry:
                if iszero == 1:
                    line = "\n".join(geometry.split("NEWLINE"))
                    sdffile.write(line+'$$$$\n')
                    iszero = 0
                else:
                    iszero = 1

if __name__ == '__main__':
    convert_backup(sys.argv[1])

