import os as _os
import numpy as _np
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import filecmp as _fc
import g4edgetestdata as _g4td


def Test(vis=False, interactive=False, fluka=True, outputPath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "10000", reg, True)
    wy = _gd.Constant("wy", "10000", reg, True)
    wz = _gd.Constant("wz", "10000", reg, True)

    polygon = [
        [0, 0],
        [0, 800],
        [1000, 1000],
        [1000, 666],
        [333, 666],
        [333, 333],
        [1000, 333],
        [1000, 0],
    ]
    slices = [[-2000, [-500, -500], 1], [2000, [-500, -500], 1]]

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    xm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    xs = _g4.solid.ExtrudedSolid("xs", polygon, slices, reg, lunit="mm")

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    xl = _g4.LogicalVolume(xs, xm, "xl", reg)

    xp1 = _g4.PhysicalVolume([0, 0, 0], [-1000, -1000, 0], xl, "xp1", wl, reg, scale=[1, 1, 1])
    xp2 = _g4.PhysicalVolume([0, 0, 0.25], [1000, -1000, 0], xl, "xp2", wl, reg, scale=[1, -1, 1])
    # xp3 = _g4.PhysicalVolume(
    #    [0, 0, 0],
    #    [-1000,  1000, 0], xl, "xp3", wl, reg, scale=[1, -1, 1])
    # xp4 = _g4.PhysicalVolume(
    #    [0, 0, 0],
    #    [ 1000, 1000, 0], xl, "xp4", wl, reg, scale=[-1, -1, 1])

    # set world volume
    reg.setWorld(wl.name)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T202_extrudedReflection.gdml")

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    # fluka conversion
    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputPath / "T202_extrudedReflection.inp")

        # flair output file
        f = _fluka.Flair("T202_extrudedReflection.inp", extentBB)
        f.write(outputPath / "T202_extrudedReflection.flair")

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)
    extent = wl.extent(includeBoundingSolid=False)

    # visualisation
    v = None
    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(reg.getWorldVolume())
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    g4td = _g4td.G4EdgeTestData()
    testDataPath = g4td["convert/T202_extrudedReflection.inp"]
    assert _fc.cmp(testDataPath, outputPath / "T202_extrudedReflection.inp")

    return {"greg": reg, "freg": freg}


if __name__ == "__main__":
    Test()
