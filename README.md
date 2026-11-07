# Thermal shielding, melt kinetics and surge control of a steam-assisted pipeline cleaning crawler

Leon Sandler, Independent Researcher — sandler.leon@gmail.com — ORCID 0009-0007-4584-808X

Code, data and manuscript for a Monte Carlo study of a steam-assisted, motorized pipeline cleaning crawler (TAMPRC), prepared for **Applied Thermal Engineering** (Elsevier).
Manuscript: `manuscript/TAMPRC_ATE_Manuscript.{docx,pdf}`, supplementary information `manuscript/TAMPRC_Supplementary_Information.{docx,pdf}`, cover letter `manuscript/TAMPRC_Cover_Letter.{docx,pdf}`.
Archived on Zenodo: paper 10.5281/zenodo.24045596, code 10.5281/zenodo.24045600 (version 1.0.0; all versions: 10.5281/zenodo.24045595 / 10.5281/zenodo.24045599).

**All input distributions are assumed concept-stage values, not measurements. The model is verified numerically, not validated physically. The results rank the measurements that would matter; they are not a predicted performance.**

## What the study does

1. **Original suite (`tamprc_mc.py`, unchanged).** Transient 1-D conduction through an aluminium / silica-aerogel / titanium hull coupled to a lumped battery pack in saturated steam; Nusselt film condensation, melt time and cleaned range; a blockage-release transient (passive pig, crawler with braking, crawler with bypass relief); a deposit-maintenance lattice checked against its exact solution.
2. **Extension (`tamprc_v2.py`).** Five mechanisms, each of which can be switched off (all off = original model draw for draw): a retained melt film (series conduction resistance; `s = 0` is the original instant-removal assumption), pipe length and logistics (deployments, active time against total intervention time), nominal pipe size 4–16 in and pipe temperature 0–55 °C, an orifice bypass that vents the upstream gas pocket (instead of a multiplicative force reduction), and a steam budget that includes heating the pipe wall.
3. **Main findings (under the assumed inputs).** With 40 mm of aerogel the pack stays ≤ 55 °C for 45 min in 98.9 % of draws in a 25 °C pipe, but only 84 % at 35 °C and 22 % at 45 °C, and the hull does not fit pipes below 8 in; the median range per deployment is 138 m with instant melt removal, 27 m with a 0.2 mm retained film and 2 m with none removed (a film of 18 µm already brings the median below 100 m); no 45 min deployment reaches 300 m; heating the pipe wall adds 1.8 times the melting steam; a bypass that is closed at the stall cannot arrest the first surge peak.

## Reproduce

```
pip install -r requirements.txt
python tamprc_mc.py --all        # original suite -> tamprc_out/ (identical to results/v1_results.json)
python tamprc_v2.py --all        # extension -> results/results.json and figures/ (about 8 min)
python tests/test_all.py         # 27 automated checks
python manuscript/src/build_manuscript.py     # manuscript and supplementary information (.docx)
python manuscript/src/build_cover_letter.py   # cover letter (.docx)
```

Seeds are fixed (`SEED = 20260601`); every number in the manuscript is read from `results/*.json`.

## Layout

| Path | Content |
|---|---|
| `tamprc_mc.py` | original single-file suite (unchanged; sha256 checked by the tests) |
| `tamprc_v2.py` | extension: retained film, coverage, diameter, temperature, orifice bypass, steam budget |
| `results/` | `v1_results.json` (original suite), `results.json` (extension) |
| `figures/` | figures of the manuscript |
| `tests/test_all.py` | automated checks |
| `manuscript/` | builders (`src/`), manuscript, supplementary information, cover letter |

## Note on the source of the problem

The operating envelope (pipes of 4–16 in and up to 1 km, no fixed pigging facilities, access through a connection aligned with the flow) is taken from a public scouting challenge ("Innovative Pipeline Cleaning Solutions", Wazoku / InnoCentive, read 7 November 2026). This repository is independent research and is not affiliated with, endorsed by or a submission to that challenge's seeker.

## License

MIT for the code, CC-BY-4.0 for the manuscript. See `LICENSE`.
