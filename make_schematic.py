#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schematic of the steam delivery geometry (Fig. 2 of the manuscript): three options by which steam reaches the deposit face.  python make_schematic.py -> figures/Fig2_steam_path.png"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
STEAM, COND, DEP, BODY, WALL, MELT = "#d62728", "#1f77b4", "#e0c9a6", "#9aa5b1", "0.25", "#f2b134"


def pipe(ax, x0=0.0, x1=12.0, y0=0.0, y1=3.0, tdep=0.28, deposit_from=7.4):
    ax.add_patch(Rectangle((x0, y1), x1 - x0, 0.12, color=WALL)); ax.add_patch(Rectangle((x0, y0 - 0.12), x1 - x0, 0.12, color=WALL))
    ax.add_patch(Rectangle((deposit_from, y1 - tdep), x1 - deposit_from, tdep, color=DEP)); ax.add_patch(Rectangle((deposit_from, y0), x1 - deposit_from, tdep, color=DEP))
    ax.add_patch(Rectangle((deposit_from, y1 - tdep), 0.0, 0.0, color=DEP))
    # melt pool at the invert, ahead of the skirt, and a draining film on the crown wall
    ax.add_patch(Polygon([(5.7, y0), (7.4, y0), (7.4, y0 + 0.5), (6.2, y0 + 0.28)], color=MELT, alpha=0.85))
    ax.add_patch(Rectangle((5.7, y1 - 0.06), 1.7, 0.06, color=MELT, alpha=0.9))
    ax.set_xlim(-2.6, x1 + 0.2); ax.set_ylim(y0 - 0.6, y1 + 0.9); ax.axis("off")


def body(ax, y0=0.55, y1=2.45):
    ax.add_patch(Rectangle((1.8, y0), 3.4, y1 - y0, color=BODY, ec="k", lw=0.8))
    ax.add_patch(Rectangle((2.0, y0 + 0.25), 3.0, y1 - y0 - 0.5, color="#f4e3b0", ec="k", lw=0.5))
    ax.text(3.5, 2.0, "pack + electronics\n(aerogel-insulated hull)", ha="center", va="center", fontsize=6.5)
    ax.add_patch(Polygon([(5.2, y0), (5.7, 0.02), (5.7, 0.35), (5.2, y0)], color="k"))
    ax.add_patch(Polygon([(5.2, y1), (5.7, 2.98), (5.7, 2.65), (5.2, y1)], color="k"))
    ax.text(4.9, 3.2, "sealing skirt", ha="center", fontsize=6.5)
    for x in (2.2, 3.1, 4.0, 4.9):
        ax.add_patch(Rectangle((x - 0.35, y0 - 0.22), 0.7, 0.22, color="0.45")); ax.add_patch(Rectangle((x - 0.35, y1), 0.7, 0.22, color="0.45"))


def arrow(ax, p, q, col, lw=1.6, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=9, color=col, lw=lw, ls=ls))


fig, axs = plt.subplots(3, 1, figsize=(7.2, 8.0))
titles = ["(a) Forward lance through the tool (geometry assumed by the model)", "(b) Steam through the pipe behind the tool, through ports in the skirt", "(c) Steam hose (tether) inside the pipe feeding a forward lance"]
for ax, t in zip(axs, titles):
    pipe(ax); body(ax); ax.set_title(t, fontsize=8.5, loc="left")
    ax.text(-2.5, 1.5, "flow-aligned\nconnection\n(launch / recovery)", ha="left", va="center", fontsize=6.5)
    ax.annotate("", xy=(11.6, 1.5), xytext=(9.4, 1.5), arrowprops=dict(arrowstyle="<|-|>", color="0.4", lw=0.8))
    ax.text(10.5, 1.65, "deposit face", ha="center", fontsize=6.5)
    ax.text(10.0, 0.12, "deposit", ha="center", fontsize=6.5); ax.text(6.5, 0.8, "melt pool\n(invert)", ha="center", fontsize=6.2, color="#9a6b00")
    ax.text(7.2, 3.38, "draining melt film", ha="center", fontsize=6.2, color="#9a6b00")
    ax.annotate("", xy=(7.4, 2.15), xytext=(5.7, 2.15), arrowprops=dict(arrowstyle="<|-|>", color="k", lw=0.7)); ax.text(6.55, 1.9, "steam zone $L_z$", ha="center", fontsize=6.2)
# (a) steam tube through the body, exiting ahead of the skirt; supply from the rear through the tether
axs[0].add_patch(Rectangle((-0.1, 1.45), 6.4, 0.1, color=STEAM)); arrow(axs[0], (3.0, 1.5), (6.9, 1.5), STEAM, 2.0)
axs[0].text(0.05, 1.7, "steam supply\nline", fontsize=6.2, color=STEAM)
for y in (1.0, 2.0):
    arrow(axs[0], (7.0, 1.5), (7.35, y), STEAM, 1.1)
arrow(axs[0], (6.6, 1.0), (6.6, 0.55), COND, 1.0); arrow(axs[0], (6.0, 2.85), (6.0, 2.5), COND, 1.0)
axs[0].text(6.0, -0.45, "pipe wall behind the tool stays cold; hull sees steam only in the zone", fontsize=6.2, ha="left")
# (b) steam in the annulus around the body
for y in (0.3, 2.7):
    arrow(axs[1], (0.5, y), (5.15, y), STEAM, 1.6)
axs[1].text(0.05, 1.45, "steam behind\nthe tool heats\nthe pipe wall", fontsize=5.8, color=STEAM)
for y in (0.6, 2.4):
    arrow(axs[1], (5.7, y), (7.2, y + (0.15 if y > 1.5 else -0.15)), STEAM, 1.2)
axs[1].text(3.0, 3.5, "ports in the skirt (bypass annulus)", fontsize=6.2, ha="center", color=STEAM)
axs[1].text(6.0, -0.45, "whole line wall is heated to saturation: +1.8× the melting steam (Section 6.11)", fontsize=6.2, ha="left")
# (c) hose with a lance
axs[2].plot([-0.1, 1.8], [1.5, 1.5], color="k", lw=3.2); axs[2].plot([-0.1, 1.8], [1.5, 1.5], color=STEAM, lw=1.6)
axs[2].add_patch(Rectangle((1.8, 1.45), 4.1, 0.1, color=STEAM)); arrow(axs[2], (3.2, 1.5), (7.0, 1.5), STEAM, 2.0)
axs[2].text(0.05, 1.7, "steam hose\n(tether)", fontsize=6.2, color=STEAM)
axs[2].text(6.0, -0.45, "no wall heating; tether drag and a second line at saturation temperature to the tool", fontsize=6.2, ha="left")
for ax in axs:
    ax.plot([], [], color=STEAM, lw=2, label="steam"); ax.plot([], [], color=MELT, lw=6, label="molten deposit"); ax.plot([], [], color=DEP, lw=6, label="solid deposit")
axs[0].legend(frameon=False, fontsize=6.5, loc="upper right", ncol=3, bbox_to_anchor=(1.0, 1.28))
fig.tight_layout(); fig.savefig(os.path.join(FIG, "Fig2_steam_path.png"), dpi=200)
print("written")
