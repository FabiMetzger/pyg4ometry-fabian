import pathlib as _pl

import pyg4ometry.convert as convert
import pyg4ometry.visualisation as vi
from pyg4ometry.fluka import ZCC, XYP, Region, Zone, FlukaRegistry, Transform, Writer


def Test(vis=False, interactive=False, outputPath=None):
    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    freg = FlukaRegistry()

    zcc = ZCC("ZCC_BODY", 5, 5, 5, transform=Transform(expansion=2.0), flukaregistry=freg)

    xyp_hi = XYP("XYP1_BODY", 20, flukaregistry=freg)
    xyp_lo = XYP("XYP2_BODY", 0, flukaregistry=freg)

    z = Zone()

    z.addIntersection(zcc)
    z.addIntersection(xyp_hi)
    z.addSubtraction(xyp_lo)

    region = Region("REG_INF")
    region.addZone(z)

    freg.addRegion(region)
    freg.assignma("COPPER", region)

    greg = convert.fluka2Geant4(freg)

    w = Writer()
    w.addDetector(freg)
    w.write(outputPath / "T412_ZCC_expansion.inp")

    v = None
    if vis:
        v = vi.VtkViewer()
        v.addAxes(length=20)
        v.addLogicalVolume(greg.getWorldVolume())
        v.view(interactive=interactive)

    return {
        "testStatus": True,
        "logicalVolume": greg.getWorldVolume(),
        "vtkViewer": v,
        "flukaRegistry": freg,
        "geant4Registry": greg,
    }


if __name__ == "__main__":
    Test(True, True)
