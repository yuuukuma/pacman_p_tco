# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Kumagai group.
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np
from monty.json import MontyDecoder
from pacman.utils.get_database import get_database
from pymatgen.core import Structure
from pymatgen.io.vasp import Outcar
from vise.analyzer.band_edge_properties import BandEdge, merge_band_edge
from vise.analyzer.dielectric_function import DieleFuncData, \
    min_e_w_target_coeff
from vise.analyzer.effective_mass import EffectiveMass

parent = Path(__file__).parent
decoder = MontyDecoder()
pd = decoder.process_decoded


def ato_mongo():
    return get_database(config_file=parent / "ato_mongo.json", admin=True)


def local_mongo():
    return get_database(config_file=parent / "local_mongo.json", admin=True)


@dataclass
class PTypeTcoData:
    ave_p_mass: float
    min_p_mass: float
    ave_n_mass: float
    min_n_mass: float


class GetPTypeTcoData:
    def __init__(self, formulas: List[str] = None):
        self.formulas = formulas
        self.ato_mongo = ato_mongo()

    def get_effective_mass(self):
        result = {}
        for doc in self.ato_mongo.effective_mass_dd_hybrid.find(
                {"formula": {"$in": self.formulas}}):
            em: EffectiveMass = pd(doc["effective_mass"])
            ave_p_mass = em.average_mass("p", 10**18)
            min_p_mass = em.minimum_mass("p", 10**18)
            result[doc["formula"]] = (ave_p_mass, min_p_mass)

        return result

    def get_optical_gap(self):
        result = {}
        for doc in self.ato_mongo.absorption_dd_hybrid.find(
                {"formula": {"$in": self.formulas}},
                {"formula": True, "diele_func": True}):
            diele: DieleFuncData = pd(doc["diele_func"])
            quantities = diele.absorption_coeff[-1]
            result[doc["formula"]] = min_e_w_target_coeff(diele.energies,
                                                          quantities, 10**4)
        return result

    def get_band_gap(self):
        result = {}
        for doc in self.ato_mongo.absorption_dd_hybrid.find(
                {"formula": {"$in": self.formulas}},
                {"formula": True, "band_edge": True}):

            abs_vbm: BandEdge = pd(doc["band_edge"]["vbm"])
            abs_cbm: BandEdge = pd(doc["band_edge"]["cbm"])
            abs_vbm.data_source = "absorption"
            abs_cbm.data_source = "absorption"

            band_doc = self.ato_mongo.band_dd_hybrid.find_one(
                {"formula": doc["formula"]}, {"band_edge": True})
            band_vbm: BandEdge = pd(band_doc["band_edge"]["vbm"])
            band_cbm: BandEdge = pd(band_doc["band_edge"]["cbm"])

            band_vbm.data_source = "band"
            band_cbm.data_source = "band"

            vbm = merge_band_edge(abs_vbm, band_vbm, "vbm")
            cbm = merge_band_edge(abs_cbm, band_cbm, "cbm")

            vbm_diff = round(abs(abs_vbm.energy - band_vbm.energy), 3)
            cbm_diff = round(abs(abs_cbm.energy - band_cbm.energy), 3)
            band_gap = cbm.energy - vbm.energy
            result[doc["formula"]] = {"vbm": vbm.as_dict(),
                                      "cbm": cbm.as_dict(),
                                      "vbm_diff": vbm_diff,
                                      "cbm_diff": cbm_diff,
                                      "band_gap": band_gap}
        return result

    def get_average_O_core_potential(self):
        result = {}
        for doc in self.ato_mongo.absorption_dd_hybrid.find(
                {"formula": {"$in": self.formulas}},
                {"formula": True, "dirpath": True}):
            path = Path(doc["dirpath"].replace("/storage", "/Users/kumagai/ato"))
            structure = Structure.from_file(path / "CONTCAR-finish")
            outcar = Outcar(path / "OUTCAR-finish")
            o_site_pot = []
            for site, pot in zip(structure, outcar.electrostatic_potential):
                if str(site.specie) == "O":
                    o_site_pot.append(pot)
            result[doc["formula"]] = float(np.average(o_site_pot))

        return result
