# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Kumagai group.
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np
from monty.json import MontyDecoder, MSONable
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
class PTypeTcoData(MSONable):
    band_gap: float
    optical_gap: float
    ave_p_mass: float
    ave_n_mass: float
    min_p_mass: float
    min_n_mass: float
    vbm_band_edge: BandEdge
    vbm_diff: float
    cbm_band_edge: BandEdge
    cbm_diff: float
    oxygen_core_potentials: List[float]

    @property
    def vbm_from_oxygen_core_potential(self):
        ave_oxygen_potential = float(np.average(self.oxygen_core_potentials))
        return self.vbm_band_edge.energy - ave_oxygen_potential

    @property
    def oxygen_core_potential_diff(self):
        return (max(self.oxygen_core_potentials)
                - min(self.oxygen_core_potentials))


class GetPTypeTcoData:
    def __init__(self, formulas: List[str] = None):
        self.formulas = formulas
        self.ato_mongo = ato_mongo()

    def get_all_data(self):
        result = {}
        effective_masses = self.get_effective_masses()
        optical_gaps = self.get_optical_gaps()
        band_edges = self.get_band_edges()
        oxygen_core_potentials = self.get_oxygen_core_potentials()

        for k, effective_mass in effective_masses.items():
            try:
                result[k] = {**effective_mass,
                             **optical_gaps[k],
                             **oxygen_core_potentials[k],
                             **band_edges[k]}
            except KeyError:
                print(f"{k} does not exist.")
        return result

    def get_effective_masses(self):
        result = {}
        for doc in self.ato_mongo.effective_mass_dd_hybrid.find(
                {"formula": {"$in": self.formulas}}):
            em: EffectiveMass = pd(doc["effective_mass"])
            result[doc["formula"]] = \
                {"ave_p_mass": em.average_mass("p", 10**18),
                 "ave_n_mass": em.average_mass("n", 10**18),
                 "min_p_mass": em.minimum_mass("p", 10**18),
                 "min_n_mass": em.minimum_mass("n", 10**18)}
        return result

    def get_optical_gaps(self):
        result = {}
        for doc in self.ato_mongo.absorption_dd_hybrid.find(
                {"formula": {"$in": self.formulas}},
                {"formula": True, "diele_func": True}):
            diele: DieleFuncData = pd(doc["diele_func"])
            quantities = diele.absorption_coeff[-1]
            opt_gap = min_e_w_target_coeff(diele.energies, quantities, 10**4)
            result[doc["formula"]] = {"optical_gap": opt_gap}
        return result

    def get_band_edges(self):
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
            result[doc["formula"]] = {"vbm_band_edge": vbm.as_dict(),
                                      "cbm_band_edge": cbm.as_dict(),
                                      "vbm_diff": vbm_diff,
                                      "cbm_diff": cbm_diff,
                                      "band_gap": band_gap}
        return result

    def get_oxygen_core_potentials(self):
        result = {}
        for doc in self.ato_mongo.absorption_dd_hybrid.find(
                {"formula": {"$in": self.formulas}},
                {"formula": True, "dirpath": True}):
            path = Path(doc["dirpath"].replace(
                "/storage", "/Users/kumagai/ato"))
            structure = Structure.from_file(path / "CONTCAR-finish")
            outcar = Outcar(path / "OUTCAR-finish")
            o_site_potentials = []
            for site, pot in zip(structure, outcar.electrostatic_potential):
                if str(site.specie) == "O":
                    o_site_potentials.append(pot)
            result[doc["formula"]] = \
                {"oxygen_core_potentials": o_site_potentials}

        return result
