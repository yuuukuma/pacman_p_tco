# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Kumagai group.
from pacman_p_tco.make_mongo_data import GetPTypeTcoData

get_data = GetPTypeTcoData(formulas=["Al2O3"])


def test_get_effective_mass():
    actual = get_data.get_effective_mass()
    assert actual == {"Al2O3": (4.152470711508106, 2.1745967142009572)}


def test_get_optical_gap():
    actual = get_data.get_optical_gap()
    assert actual == {"Al2O3": 9.5176}


def test_get_band_gap():
    actual = get_data.get_band_gap()
    expected = \
        {'Al2O3': {'cbm': {'@class': 'BandEdge',
                           '@module': 'vise.analyzer.band_edge_properties',
                           'band_index': 24,
                           'data_source': 'absorption band',
                           'energy': 13.3062,
                           'kpoint_coords': [0.0, 0.0, 0.0],
                           'kpoint_index': 0,
                           'spin': 1,
                           'symbol': None},
                   'cbm_diff': 0.0,
                   'vbm': {'@class': 'BandEdge',
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
