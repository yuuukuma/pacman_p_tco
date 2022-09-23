# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Kumagai group.
from pacman_p_tco.make_mongo_data import get_effective_mass


def test_get_effective_mass():
    actual = get_effective_mass(formulas=["MgO"])
    assert actual == {"MgO": (2.097823279476968, 2.097823279476967)}