import os as _os
import pathlib as _pl
import pyg4ometry.geant4 as _g4
import pyg4ometry.gdml as _gd
import pyg4ometry.convert as _convert
import pyg4ometry.fluka as _fluka
import pyg4ometry.visualisation as _vi
import numpy as _np
import filecmp as _fc
import g4edgetestdata as _g4td


def Test(vis=False, interactive=False, fluka=True, outputPath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    # registry
    reg = _g4.Registry()

    # defines
    wx = _gd.Constant("wx", "100", reg, True)
    wy = _gd.Constant("wy", "100", reg, True)
    wz = _gd.Constant("wz", "100", reg, True)

    tx1 = _gd.Constant("tx1", "5", reg, True)
    tx2 = _gd.Constant("tx2", "5", reg, True)
    tx3 = _gd.Constant("tx3", "10", reg, True)
    tx4 = _gd.Constant("tx4", "10", reg, True)

    ty1 = _gd.Constant("ty1", "5", reg, True)
    ty2 = _gd.Constant("ty2", "7.5", reg, True)

    tz = _gd.Constant("tz", "10.0", reg, True)

    ttheta = _gd.Constant("ttheta", "0.6", reg, True)
    tphi = _gd.Constant("tphi", "0.0", reg, True)
    talp1 = _gd.Constant("talp1", "0.0", reg, True)
    talp2 = _gd.Constant("talp2", "0.0", reg, True)

    # materials
    wm = _g4.nist_material_2geant4Material("G4_Galactic")
    tm = _g4.nist_material_2geant4Material("G4_Fe")

    # solids
    ws = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")
    ts = _g4.solid.Trap(
        "ts", tz, ttheta, tphi, ty1, tx1, tx2, talp1, ty2, tx3, tx4, talp2, reg, "mm"
    )

    # structure
    wl = _g4.LogicalVolume(ws, wm, "wl", reg)
    tl = _g4.LogicalVolume(ts, tm, "tl", reg)
    tp = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], tl, "t_pv1", wl, reg)

    # set world volume
    reg.setWorld(wl.name)

    # test extent of physical volume
    extentBB = wl.extent(includeBoundingSolid=True)

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write(outputPath / "T007_geant4Trap2Fluka.gdml")

    # fluka conversion
    if fluka:
        freg = _convert.geant4Reg2FlukaReg(reg)
        w = _fluka.Writer()
        w.addDetector(freg)
        w.write(outputPath / "T007_geant4Trap2Fluka.inp")

    # flair output file
    f = _fluka.Flair("T007_geant4Trap2Fluka.inp", extentBB)
    f.write(outputPath / "T007_geant4Trap2Fluka.flair")

    if vis:
        v = _vi.VtkViewer()
        v.addLogicalVolume(wl)
        v.addAxes(_vi.axesFromExtents(extentBB)[0])
        v.view(interactive=interactive)

    g4td = _g4td.G4EdgeTestData()
    testDataPath = g4td["convert/T007_geant4Trap2Fluka.inp"]
    assert _fc.cmp(testDataPath, outputPath / "T007_geant4Trap2Fluka.inp")

    return {"greg": reg, "freg": freg}


if __name__ == "__main__":
    Test()
