# -*- coding: utf-8 -*-
"""Shared helpers for the manuscript builders: results, number formatting, block lists."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
FIG = os.path.join(ROOT, "figures")
OUT = os.path.join(ROOT, "manuscript")
R = json.load(open(os.path.join(ROOT, "results", "results.json"), encoding="utf-8"))
V = json.load(open(os.path.join(ROOT, "results", "v1_results.json"), encoding="utf-8"))
DOIS = json.load(open(os.path.join(HERE, "dois.json"), encoding="utf-8"))
GITHUB = "https://github.com/sandlerleon/tamprc-pipeline-crawler-mc"
VERSION = "1.0.0"
TITLE = "Thermal Shielding, Melt Kinetics and Surge Control of a Steam-Assisted Pipeline Cleaning Crawler: A Monte Carlo Study and Its Deployment Limits"


def n(x, d=0):
    s = "{:,.{d}f}".format(x, d=d)
    if set(s) <= set("-0.,"):
        return s.lstrip("-")
    return s.replace("-", "−")


def pc(x, d=0):
    """probability (0-1) as a percentage string"""
    return n(100.0 * x, d) + "%"


def ci(lo, hi, d=1):
    return "%s–%s%%" % (n(100 * lo, d), n(100 * hi, d))


B = []      # manuscript blocks
BS = []     # supplementary blocks


def add(b):
    B.append(b)


def adds(b):
    BS.append(b)


# ---- frequently used records
A_ATM, A_VAC = V["A_atmospheric"], V["A_evacuated"]
BB = V["B"]
CP, CR, CL = V["C_passive"], V["C_regen"], V["C_relief"]
F = R["film"]
FR = {round(r["s_mm"], 3): r for r in F["rows"]}
ND = F["nodrain"]
COV = R["coverage"]["rows"]
DIA = {r["nps"]: r for r in R["diameter"]["rows"]}
ENV = {r["T_amb"]: r for r in R["env"]["rows"]}
BY = R["bypass"]
STM = {r["nps"]: r for r in R["steam"]["rows"]}


def fmt(_text, **kw):
    """replace <<key>> tokens (so that % and { } in the text are never interpreted)"""
    for k, v in kw.items():
        _text = _text.replace("<<%s>>" % k, str(v))
    assert "<<" not in _text, _text[_text.index("<<"):_text.index("<<") + 30]
    return _text
