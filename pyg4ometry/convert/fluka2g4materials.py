import pandas as pd
import os.path

from pyg4ometry.geant4 import MaterialPredefined, MaterialSingleElement
from pyg4ometry.fluka.material import BuiltIn, Element, Compound

# http://www.fluka.org/content/manuals/online/5.2.html
# See also fluka/material.py
FLUKA_BUILTIN_TO_G4_MATERIAL_MAP = {
    # Elements
    "BLCKHOLE": "G4_Galactic",
    "VACUUM": "G4_Galactic",
    "HYDROGEN": "G4_H",
    "HELIUM": "G4_He",
    "BERYLLIU": "G4_Be",
    "CARBON": "G4_B",
    "NITROGEN": "G4_N",
    "OXYGEN": "G4_O",
    "MAGNESIU": "G4_Mg",
    "ALUMINUM": "G4_Al",
    "IRON": "G4_Fe",
    "COPPER": "G4_Cu",
    "SILVER": "G4_Ag",
    "SILICON": "G4_Si",
    "GOLD": "G4_Au",
    "MERCURY": "G4_Hg",
    "LEAD": "G4_Pb",
    "TANTALUM": "G4_Ta",
    "SODIUM": "G4_Na",
    "ARGON": "G4_Ar",
    "CALCIUM": "G4_Ca",
    "TIN": "G4_Sn",
    "TUNGSTEN": "G4_W",
    "TITANIUM": "G4_Ti",
    "NICKEL": "G4_Ni",
    # Compounds
    "WATER": "G4_WATER",
    "POLYSTYR": "G4_POLYSTYRENE",
    "PLASCINT": "G4_PLASTIC_SC_VINYLTOLUENE",
    "PMMA": "G4_PLEXIGLASS",
    "BONECOMP": "G4_BONE_COMPACT_ICRU",
    "BONECORT": "G4_BONE_CORTICAL_ICRP", # This has slightly different density?
    "MUSCLESK": "G4_MUSCLE_SKELETAL_ICRP", # So does this..
    "MUSCLEST": "G4_MUSCLE_STRIATED_ICRU",
    "ADTISSUE": "G4_ADIPOSE_TISSUE_ICRP", # and this
    "KAPTON": "G4_KAPTON",
    "POLYETHY": "G4_POLYETHYLENE",
    "AIR": "G4_AIR"
}


def addFlukaMaterialsToG4Registry(freg, greg):
    """Convert the materials defined in a FlukaRegistry, and populate
    the provided geant4 registry with said materials."""

    mnl = _MassNumberLookup()

    fluka = freg.materialDict

    for name, material in fluka.iteritems():
        if isinstance(material, BuiltIn):
            MaterialPredefined(FLUKA_BUILTIN_TO_G4_MATERIAL_MAP[name],
                               registry=greg)
        elif isinstance(material, Element):
            name = material.name
            atomicNumber = material.atomicNumber
            density = material.density
            massNumber = material.massNumber
            if massNumber is None:
                massNumber = mnl.getMassNumberFromAtomicNumber(atomicNumber)
            MaterialSingleElement(name, atomicNumber, massNumber,
                                  density, registry=greg)
        elif isinstance(material, Compound):
            pass

    return greg

class _MassNumberLookup(object):
    THISDIR = os.path.dirname(os.path.abspath(__file__))
    def __init__(self):
        self.table = pd.read_csv(
            os.path.join(self.THISDIR, "periodic-table.csv"))

    def getMassNumberFromAtomicNumber(self, z):
        t = self.table
        result = t["AtomicMass"][t["AtomicNumber"] == z].values
        if not result:
            raise FLUKAError(
                "Unable to determine mass number for Z = {}".format(z))

        return int(round(result))

            
