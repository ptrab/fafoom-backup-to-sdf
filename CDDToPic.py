#!/usr/bin/env python
import sys
import os
import glob
import re
import argparse
import platform
from jinja2 import Template


def getinput(args):
    """parse the input"""
    parser = argparse.ArgumentParser(
        description=("Find several cube files and convert them to jpeg.")
    )
    parser.add_argument(
        "--supersampling",
        "-ss",
        default=4,
        type=int,
        help="Supersampling of the resulting image. default 4",
    )
    parser.add_argument(
        "--dpi", "-d", default=600, type=int, help="DPI value, default 600"
    )
    parser.add_argument(
        "--filetype", "-f", default="jpeg", help="default jpeg, png possible"
    )
    parser.add_argument(
        "--background", "-bg", default="none", help="set the background color (default: none)"
    )
    parser.add_argument(
        "--sizefactor",
        "-sf",
        default=2.0,
        type=float,
        help="n times the window size of the session.py, default 2",
    )
    parser.add_argument(
        "--cdd-image-width",
        "-ciw",
        default=3.0,
        type=float,
        help="Preferred image width for CDD, electron, and hole images to be inserted into pyparse.py-generated docx files. (default: 3 cm)"
    )
    parser.add_argument(
        "--mo-image-width",
        "-mow",
        default=2.6,
        type=float,
        help="Preferred image width for MO images to be inserted into pyparse.py-generated docx files. (default: 2.6 cm)"
    )
    parser.add_argument(
        "--image-units",
        "-unit",
        default="centimeters",
        help="Width and height values are assumed to be in pixels unless units are specified as one of the following types: inches, millimeters, centimeters, points (72 points = 1 inch)"
    )
    parser.add_argument(
        "--stephan", "-cu", action="store_true", help="inverts the CDD colors"
    )
    parser.add_argument(
        "-abs", "--abs-cubes", action="store_true", help="changes to isovalues for CDDs to account for abs cubes instead of squared cubes")
    parser.add_argument(
        "-rt", "--raytrace", action="store_true"
    )
    return parser.parse_args(args)


# Find the window size in the session file
def WindowSize(data):
    with open(data) as file:
        for line in file:
            if "windowSize =" in line:
                return re.split("[(),]", line)


# find the session file and all relevant cube files
session = glob.glob("*.py")
# find Multiwfn's Charge density (CDD='electron'-'hole') files
cdds = glob.glob("*CDD*.cub")
orca_cdds = glob.glob("*cisdp*.cube")
# find Multiwfn's electron-files
eles = glob.glob("*electron*.cub")
# find Multiwfn's hole-files
hols = glob.glob("*hole*.cub")
# find all MO cube files
orbs = glob.glob("*orb*.cub")
# find one file for spindensity
spindensity = glob.glob("spind*nsity.cub")
# find transition densities
transdens = glob.glob("transdens*.cub")

# if more than one or no session file ... actually *.py file ... is found
# the script aborts
print(os.getcwd())
if len(session) > 1:
    print("More than one chimera session found. Reduce to one!")
    print(session)
    sys.exit(0)
elif len(session) < 1:
    print("No session file found")
    sys.exit(0)
else:
    session = session[0]
    print("Chimera session file found: " + session)

# get the window size to change it later
WWidth, WHeight = WindowSize(session)[1:3]
WWidth = int(WWidth)
WHeight = int(WHeight)

# parse the arguments
args = getinput(sys.argv[1:])

# define the quality of the resulting images
# color preset is the publication preset that can be set in chimera
ColorPreset = "2"
# cube resolution 1 means 'use every point', 2 would be use every 2nd point
CubeResolution = "1"
# super sampling of the final image
SuperSample = str(args.supersampling)
# pixel density
DPI = str(args.dpi)
# image width for CDD, electron and hole for docx
CDDimagewidth = args.cdd_image_width # cm
# image width for MOs for docx
MOimagewidth = args.mo_image_width # cm
# image units
units = args.image_units
# image type ... could also be png
FileType = str(args.filetype)
# background color
backgroundcolor = str(args.background)
# the isovalue for the MOs
orbLevel = "0.04"
# the isovalue for densities
cddLevel = "0.002"
# the RGB colors for MOs
orbRGB = [["0", ".5", ".6"], [".9", ".7", ".1"]]
# the RGB colors for 'regular' densities
cddRGB = [["0", "0.8", "1"], ["1", "0.2", "0"]]
# the RGB for spin densities
sdRGB = [["0", "0.2", "0.6"], ["0", "0.6", "0.3"]]
# the enlargement for the image size ... window size multiplier
sizeFactor = args.sizefactor

# stephan's colors and a preset to fit GaussView more or less
if args.stephan:
    orbRGB = [["0.0", "0.4", "0.0"], ["1.0", "1.0", "0.0"]]
    cddRGB = [["1.0", "0.0", "0.0"], ["0.0", "0.47451", "1.0"]]
    ColorPreset = "4"

# abs cubes
if args.abs_cubes:
    cddLevel = orbLevel

# template for easy use when creating the output
# if the image should be rendered with PovRay, activate the raytrace part
if args.raytrace:
    template = Template(
        (
            "\nopen {{ name }}"
            "\npreset apply pub {{ preset }}; color byelement"
            "\nvolume #1 level -{{ level }} color {{ minus }}"
            " level {{ level }} color {{ plus }} step {{ cubres }}"
            "\nbackground solid {{ bgcolor }}"
            "\nsetattr M stickScale 0.6 #; unset depthCue"
            "\ncopy file {{ output }} supersample {{ supsam }} "
            "dpi {{ dpi }} width {{ width }} units {{ units }}"
            'raytrace rtwait'
            "\nclose #1"
        )
    )
else:
    template = Template(
          (
              "\nopen {{ name }}"
              "\npreset apply pub {{ preset }}; color byelement"
              "\nvolume #1 level -{{ level }} color {{ minus }}"
              " level {{ level }} color {{ plus }} step {{ cubres }}"
              "\nbackground solid {{ bgcolor }}"
              "\nsetattr M stickScale 0.6 #; unset depthCue"
              "\ncopy file {{ output }} supersample {{ supsam }} "
              "dpi {{ dpi }} width {{ width }} units {{units}}"
              "\nclose #1"
          )
      )

if args.stephan:
    template = Template(
        (
            "\nopen {{ name }}"
            "\npreset apply pub {{ preset }}; color byelement"
            "\nvolume #1 level -{{ level }} color {{ minus }}"
            " level {{ level }} color {{ plus }} step {{ cubres }}"
            "\nbackground solid {{ bgcolor }}"
            "\nsetattr M stickScale 0.6 #; unset depthCue; unset shadows"
            "\ncopy file {{ output }} supersample {{ supsam }} "
            "dpi {{ dpi }} width {{ width }} units {{ units }}"
            "\nclose #1"
        )
    )

# open the session, apply the color preset, set dpi etc for the geometry image and save it
mytext = "open " + session
mytext += "\npreset apply pub " + ColorPreset + "; color byelement"
mytext += "\nbackground solid " + backgroundcolor + "; setattr M stickScale 0.6 #"
if args.stephan:
    mytext += "\nunset depthCue; unset shadows"
mytext += "\ncopy file geometry." + FileType + " supersample " + SuperSample
mytext += " dpi " + DPI + " width " + str(int(sizeFactor * WWidth))
mytext += " height " + str(int(sizeFactor * WHeight))

# for every CDD add the resp. commands to the output
for cdd in cdds:
    mytext += template.render(
        name=cdd,
        preset=ColorPreset,
        level=cddLevel,
        cubres=CubeResolution,
        output=cdd.replace("cub", FileType),
        supsam=SuperSample,
        dpi=DPI,
        bgcolor=backgroundcolor,
        width=str(CDDimagewidth),
        units=units,
        minus=",".join(cddRGB[0]),
        plus=",".join(cddRGB[1]),
    )
# for every ORCA_plot CDD add the resp. commands to the output
for cdd in orca_cdds:
    mytext += template.render(
        name=cdd,
        preset=ColorPreset,
        level=cddLevel,
        cubres=CubeResolution,
        output=cdd.replace("cube", FileType),
        supsam=SuperSample,
        dpi=DPI,
        bgcolor=backgroundcolor,
        width=str(CDDimagewidth),
        units=units,
        minus=",".join(cddRGB[0]),
        plus=",".join(cddRGB[1]),
    )
# same for electron
for ele in eles:
    mytext += template.render(
        name=ele,
        preset=ColorPreset,
        level=cddLevel,
        cubres=CubeResolution,
        output=ele.replace("cub", FileType),
        supsam=SuperSample,
        dpi=DPI,
        bgcolor=backgroundcolor,
        width=str(CDDimagewidt),
        units=units,
        minus=",".join(cddRGB[0]),
        plus=",".join(cddRGB[1]),
    )
# ... for hole
for hol in hols:
    mytext += template.render(
        name=hol,
        preset=ColorPreset,
        level=cddLevel,
        cubres=CubeResolution,
        output=hol.replace("cub", FileType),
        supsam=SuperSample,
        dpi=DPI,
        bgcolor=backgroundcolor,
        width=str(CDDimagewidth),
        units=units,
        minus=",".join(cddRGB[1]),
        plus=",".join(cddRGB[0]),
    )
# ... for MOs
for orb in orbs:
    mytext += template.render(
        name=orb,
        preset=ColorPreset,
        level=orbLevel,
        cubres=CubeResolution,
        output=orb.replace("cub", FileType),
        supsam=SuperSample,
        dpi=DPI,
        bgcolor=backgroundcolor,
        width=str(MOimagewidth),
        units=units,
        minus=",".join(orbRGB[0]),
        plus=",".join(orbRGB[1]),
    )
# ... for spin density
for sd in spindensity:
    mytext += template.render(
        name=sd,
        preset=ColorPreset,
        level=cddLevel,
        cubres=CubeResolution,
        output=sd.replace("cub", FileType),
        supsam=SuperSample,
        dpi=DPI,
        bgcolor=backgroundcolor,
        width=str(int(sizeFactor * WWidth)),
        height=str(int(sizeFactor * WHeight)),
        minus=",".join(sdRGB[0]),
        plus=",".join(sdRGB[1]),
    )
# ... for transition densities
for td in transdens:
    mytext += template.render(
        name=td,
        preset=ColorPreset,
        level=cddLevel,
        cubres=CubeResolution,
        output=td.replace("cub", FileType),
        supsam=SuperSample,
        dpi=DPI,
        bgcolor=backgroundcolor,
        width=str(int(sizeFactor * WWidth)),
        height=str(int(sizeFactor * WHeight)),
        minus=",".join(cddRGB[0]),
        plus=",".join(cddRGB[1]),
    )
# end the input
mytext += "\nstop"

# write the input
with open("input.cmd", "w") as f:
    f.write(mytext)

# execute the input
if platform.system() == "Linux":
    os.system("chimera --bgopacity input.cmd")
    os.remove("input.cmd")
