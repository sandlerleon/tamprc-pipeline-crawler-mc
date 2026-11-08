# Coupled condensation–melting heat transfer and thermal design limits of a steam-assisted pipeline cleaning crawler

Leon Sandler, Independent Researcher — sandler.leon@gmail.com — ORCID 0009-0007-4584-808X

Code, data and manuscript for a probabilistic modeling study of a steam-assisted, motorized pipeline cleaning crawler (TAMPRC), prepared for **Applied Thermal Engineering** (Elsevier).
Manuscript: `manuscript/TAMPRC_ATE_Manuscript.{docx,pdf}`, supplementary information `manuscript/TAMPRC_Supplementary_Information.{docx,pdf}`, cover letter `manuscript/TAMPRC_Cover_Letter.{docx,pdf}`.
Archived on Zenodo: paper 10.5281/zenodo.24045596, code 10.5281/zenodo.24045600 (version 1.0.0; all versions: 10.5281/zenodo.24045595 / 10.5281/zenodo.24045599).

**All input distributions are assumed concept-stage values, not measurements. The numerical solutions are verified and the melt formulas are benchmarked against independent solutions, but the coupled model is not validated against experiment (none was identified). The success percentages are model probabilities under the assumed distributions, not field reliabilities.**

## What the study does

1. **Original suite (`tamprc_mc.py`, unchanged).** Transient 1-D conduction through an aluminium / silica-aerogel / titanium hull into a lumped battery pack in saturated steam; Nusselt film condensation, melt time and cleaned range; a blockage-release transient; a deposit-maintenance lattice checked against its exact solution.
2. **Extension (`tamprc_v2.py`).** Switchable mechanisms (all off = original model draw for draw): retained melt film (series resistance), pipe length and logistics, pipe size 4–16 in and temperature, an orifice bypass that vents the upstream gas pocket, a steam budget including heating the pipe wall.
3. **Revision studies (`tamprc_v3.py`).** Benchmarks (enthalpy-method Stefan solver against the exact Neumann solution and the melt formulas; conduction solver against an independent BDF integration); Nusselt, Chato and non-condensable condensation representations; a **dynamic retained film** (melt production against gravity drainage) and the dimensionless film resistance Π_f = h s / k_l; global Sobol sensitivity and correlated inputs; a constrained design search with Pareto set; feasible envelope against pipe size and temperature; steam pressure against flange ratings (IAPWS-IF97) and a revised operating envelope.
4. **Main findings (under the assumed inputs).** Heat flux through a retained film is q0/(1 + Π_f); a 100 m range needs Π_f below about 0.3. The median range per 45 min deployment is 138 m if the melt leaves at once, about 18 m with the dynamic film (0.35 mm) and 2 m if none drains. Pack probability 98.9 % at 25 °C, 22 % at 45 °C; hull does not fit below 8 in; no 45 min deployment reaches 300 m at the 0.10 m/s set-point (a cap, not a thermal limit); steam at 198 °C exceeds a Class 150 rating (limit about 195 °C) at a cost of about 3 % of the range; a bypass closed at the stall cannot arrest the first surge peak. A 1 km line needs a median of 57 deployments with the dynamic film (8 if the melt leaves at once); the revised steam envelope (192 °C, truncated at the Class 150 limit) respects the pressure limit in every sampled draw; steam shear and wall orientation move the range by tens of percent, not by an order of magnitude (sensitivity runs).

## Reproduce

```
pip install -r requirements.txt
python tamprc_mc.py --all        # original suite -> tamprc_out/ (identical to results/v1_results.json)
python tamprc_v2.py --all        # extension -> results/results.json (about 8 min)
python tamprc_v3.py --all        # revision studies -> results/results_ext.json and figures/ (about 5 min)
python tests/test_all.py         # 62 automated checks
python manuscript/src/build_manuscript.py     # manuscript and supplementary information (.docx)
python manuscript/src/build_cover_letter.py   # cover letter (.docx)
```

Seeds are fixed (`SEED = 20260601`); every number in the manuscript is read from `results/*.json`.

## Layout

| Path | Content |
|---|---|
| `tamprc_mc.py` | original single-file suite (unchanged; sha256 checked by the tests) |
| `tamprc_v2.py` | extension: retained film, coverage, diameter, temperature, orifice bypass, steam budget |
| `tamprc_v3.py` | revision: benchmarks, condensation models, dynamic film, Sobol, correlation, design search, envelope, pressure–temperature |
| `results/` | `v1_results.json`, `results.json`, `results_ext.json` |
| `figures/` | figures of the manuscript |
| `tests/test_all.py` | automated checks |
| `manuscript/` | builders (`src/`), manuscript, supplementary information, cover letter |

## Note on the source of the problem

The operating envelope (pipes of 4–16 in and up to 1 km, no fixed pigging facilities, access through a connection aligned with the flow) is taken from a public scouting challenge ("Innovative Pipeline Cleaning Solutions", Wazoku / InnoCentive, read 7 November 2026). This repository is independent research and is not affiliated with, endorsed by or a submission to that challenge's seeker.

## License

MIT for the code, CC-BY-4.0 for the manuscript. See `LICENSE`.
