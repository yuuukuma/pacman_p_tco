# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Kumagai group.
from pathlib import Path
from typing import List

from monty.json import MontyDecoder
from pacman.utils.get_database import get_database
from vise.analyzer.effective_mass import EffectiveMass

parent = Path(__file__).parent
decoder = MontyDecoder()
pd = decoder.process_decoded


def ato_mongo():
    return get_database(config_file=parent / "ato_mongo.json", admin=True)


def local_mongo():
    return get_database(config_file=parent / "local_mongo.json", admin=True)


def get_effective_mass(formulas: List[str] = None):
    result = {}
    for doc in ato_mongo().effective_mass_dd_hybrid.find(
            {"formula": {"$in": formulas}}):
        em: EffectiveMass = pd(doc["effective_mass"])
        ave_p_mass = em.average_mass("p", 10**18)
        min_p_mass = em.minimum_mass("p", 10**18)
        result[doc["formula"]] = (ave_p_mass, min_p_mass)

    return result
