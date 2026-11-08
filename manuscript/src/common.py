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
X = json.load(open(os.path.join(ROOT, "results", "results_ext.json"), encoding="utf-8"))
DOIS = json.load(open(os.path.join(HERE, "dois.json"), encoding="utf-8"))
GITHUB = "https://github.com/sandlerleon/tamprc-pipeline-crawler-mc"
VERSION = "1.0.0"
TITLE = "Coupled Condensation–Melting Heat Transfer and Thermal Design Limits of a Steam-Assisted Pipeline Cleaning Crawler: A Probabilistic Modeling Study"


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


import re

FIGNUM = {"arch": 1, "path": 2, "bench": 3, "fan": 4, "sweep": 5, "melt": 6, "film": 7, "dyn": 8, "sobol": 9, "cov": 10, "dia": 11, "env": 12, "pt": 13, "pareto": 14, "surge": 15, "bypass": 16, "steam": 17}
TABNUM = {"envelope": 1, "inputs": 2, "bench": 3, "hmod": 4, "film": 5, "cov": 6, "dia": 7, "pt": 8, "design": 9, "surge": 10, "steam": 11, "reqs": 12, "ice": 13}
_TOK = re.compile(r"@([FT]):(\w+)@")


def _sub(x):
    """replace the symbolic figure and table numbers (@F:key@, @T:key@) in a block"""
    if isinstance(x, str):
        return _TOK.sub(lambda m: str({"F": FIGNUM, "T": TABNUM}[m.group(1)][m.group(2)]), x)
    if isinstance(x, tuple):
        return tuple(_sub(i) for i in x)
    if isinstance(x, list):
        return [_sub(i) for i in x]
    return x


B = []      # manuscript blocks
BS = []     # supplementary blocks


def add(b):
    B.append(_sub(b))


def adds(b):
    BS.append(_sub(b))


# ---- frequently used records
A_ATM, A_VAC = V["A_atmospheric"], V["A_evacuated"]
BB = V["B"]
CP, CR, CL = V["C_passive"], V["C_regen"], V["C_relief"]
F = R["film"]
HM = X["hmodels"]["models"]; DY = X["dynfilm"]; BSF = X["bench_stefan"]; BCD = X["bench_conduction"]; SOB = X["sobol"]; CORR = X["corr"]["rows"]; DES = X["design"]; ENVL = X["envelope"]; PT = X["ptcompat"]; UNC = X["uncapped"]; CVD = X["coverage_dyn"]; ICE = X["ice"]
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
