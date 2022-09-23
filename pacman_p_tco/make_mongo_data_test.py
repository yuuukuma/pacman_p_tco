# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Kumagai group.
import pytest
from pymatgen.electronic_structure.core import Spin
from vise.analyzer.band_edge_properties import BandEdge
from vise.tests.helpers.assertion import assert_msonable

from pacman_p_tco.make_mongo_data import GetPTypeTcoData, PTypeTcoData

get_data = GetPTypeTcoData(formulas=["Al2O3"])


@pytest.fixture
def p_type_tco_data():
    vbm_band_edge = BandEdge(energy=10.0,
                             spin=Spin.up,
                             band_index=1,
                             kpoint_coords=[0.0, 0.0, 0.0],
                             kpoint_index=1,
                             data_source="band")
    cbm_band_edge = BandEdge(energy=11.0,
                             spin=Spin.up,
                             band_index=2,
                             kpoint_coords=[0.0, 0.0, 0.0],
                             kpoint_index=1,
                             data_source="dos")
    return PTypeTcoData(band_gap=1.0,
                        optical_gap=1.1,
                        ave_p_mass=2.0,
                        ave_n_mass=3.0,
                        min_p_mass=1.9,
                        min_n_mass=2.9,
                        vbm_band_edge=vbm_band_edge,
                        vbm_diff=0.001,
                        cbm_band_edge=cbm_band_edge,
                        cbm_diff=0.001,
                        oxygen_core_potentials=[-10.0, -15.0, -20.0])


def test_p_type_tco_data_msonable(p_type_tco_data):
    assert_msonable(p_type_tco_data)


def test_p_type_tco_vbm_from_oxygen_core_potential(p_type_tco_data):
    actual = p_type_tco_data.vbm_from_oxygen_core_potential
    vbm_energy, ave_oxygen_potential = 10.0, -15.0
    expected = vbm_energy - ave_oxygen_potential
    assert actual == expected


def test_p_type_tco_oxygen_potential_core_potential_diff(p_type_tco_data):
    actual = p_type_tco_data.oxygen_core_potential_diff
    assert actual == 10.0


def test_get_all_data():
    actual = get_data.get_all_data()
    expected = {"Al2O3": {"ave_p_mass": 4.152470711508106,
                          "ave_n_mass": 0.37259405914217364,
                          "min_p_mass": 2.1745967142009572,
                          "min_n_mass": 0.3611766720422496,
                          "optical_gap": 9.5176,
                          "oxygen_core_potentials": [-59.1305]*6,
                          'cbm_band_edge': {
                              '@class': 'BandEdge',
                              '@module': 'vise.analyzer.band_edge_properties',
                              'band_index': 24,
                              'data_source': 'absorption band',
                              'energy': 13.3062,
                              'kpoint_coords': [0.0, 0.0, 0.0],
                              'kpoint_index': 0,
                              'spin': 1,
                              'symbol': None},
                          'cbm_diff': 0.0,
                          'vbm_band_edge': {
                               '@class': 'BandEdge',
                               '@module': 'vise.analyzer.band_edge_properties',
                               'band_index': 23,
                               'data_source': 'absorption band',
                               'energy': 3.9742,
                               'kpoint_coords': [0.0, 0.0, 0.0],
                               'kpoint_index': 0,
                               'spin': 1,
                               'symbol': None},
                          'vbm_diff': 0.001,
                          "band_gap": 9.332}}
    assert actual == expected

