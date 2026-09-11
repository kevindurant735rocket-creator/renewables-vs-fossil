"""Generate branded, data-driven share images (hero banner + square social card).

Real numbers are pulled from results.json so the graphics never drift from the analysis.
Run after analysis.py:  python src/build_shareimg.py
"""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = __import__("pathlib").Path(__file__).resolve().parent.parent
R = json.load(open(ROOT / "results.json"))

tg = R["trend_global"]
rs0, rs1 = tg["renew_share"][0], tg["renew_share"][-1]
disp = R["displacement"]
dfossil = disp["delta_fossil_world_TWh"]
pct = disp["pct_displacing"]
wit = R["what_it_takes"]
flat = wit["scenarios"]["flat"]["low_carbon_share_needed_2030"]
mom = wit["momentum_low_carbon_2030"]
fe = R["fe_co2"]["contemporaneous"]["coef"][0] * 100

GREEN, RED, INK, MUT = "#1b6b3a", "#c0492b", "#13201a", "#5d6b63"
DARK = "#0f3d24"


def box(ax, x, y, w, h, fc, ec="none"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.005",
                                fc=fc, ec=ec, transform=ax.transAxes, lw=1.2))


# ---------------------------------------------------------------- hero banner
fig = plt.figure(figsize=(16, 6), dpi=150)
fig.patch.set_facecolor("white")
ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
box(ax, 0.0, 0.52, 1.0, 0.48, DARK)
ax.text(0.04, 0.80, "Did renewables actually displace fossil power?",
        color="white", fontsize=29, fontweight="bold", transform=ax.transAxes)
ax.text(0.04, 0.66, "A reproducible cross-country analysis  ·  187 countries  ·  2000–2022",
        color="#cfe9d8", fontsize=14.5, transform=ax.transAxes)

box(ax, 0.04, 0.10, 0.44, 0.34, "#f3f7f4", "#e4eae6")
ax.text(0.07, 0.37, "Renewable share rose", color=MUT, fontsize=13.5, transform=ax.transAxes)
ax.text(0.07, 0.245, f"{rs0:.1f}%  →  {rs1:.1f}%", color=GREEN, fontsize=33,
        fontweight="bold", transform=ax.transAxes)
ax.text(0.07, 0.14, "of global electricity (2000 → 2022)", color=MUT, fontsize=12.5,
        transform=ax.transAxes)

box(ax, 0.52, 0.10, 0.44, 0.34, "#f3f7f4", "#e4eae6")
ax.text(0.55, 0.37, "Fossil generation", color=MUT, fontsize=13.5, transform=ax.transAxes)
ax.text(0.55, 0.245, f"+{dfossil:,.0f} TWh", color=RED, fontsize=33,
        fontweight="bold", transform=ax.transAxes)
ax.text(0.55, 0.14, "added worldwide over the same period", color=MUT, fontsize=12.5,
        transform=ax.transAxes)

box(ax, 0.04, 0.015, 0.92, 0.07, "#fff5f1", "#f3d9cf")
ax.text(0.5, 0.05, f"Yet only ~{pct:.0f}% of countries cut their fossil generation.  "
        f"Holding fossil flat to 2030 needs a {flat:.1f}% low-carbon share — momentum reaches only {mom:.1f}%.",
        color=RED, fontsize=13, ha="center", va="center", fontweight="bold", transform=ax.transAxes)
fig.savefig(ROOT / "figures" / "hero.png", dpi=150, bbox_inches="tight", facecolor="white")
print("wrote figures/hero.png")

# ---------------------------------------------------------------- square card
fig = plt.figure(figsize=(10.8, 10.8), dpi=150)
fig.patch.set_facecolor("white")
ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
box(ax, 0.0, 0.78, 1.0, 0.22, DARK)
ax.text(0.06, 0.90, "Renewables surged.", color="white", fontsize=33,
        fontweight="bold", transform=ax.transAxes)
ax.text(0.06, 0.835, "Fossil kept rising.", color="#cfe9d8", fontsize=33,
        fontweight="bold", transform=ax.transAxes)

blocks = [
    (GREEN, "Renewable share", f"{rs0:.1f}% → {rs1:.1f}%", "of global electricity (2000→2022)"),
    (RED, "Fossil generation", f"+{dfossil:,.0f} TWh", "added worldwide — more dirty power"),
    (RED, "Only ~%d%% of countries" % round(pct), "cut their fossil generation", "displacement ≠ addition"),
]
y = 0.70
for color, t, big, sub in blocks:
    box(ax, 0.06, y - 0.16, 0.88, 0.17, "#f3f7f4", "#e4eae6")
    ax.text(0.10, y - 0.01, t, color=MUT, fontsize=15, transform=ax.transAxes)
    ax.text(0.10, y - 0.085, big, color=color, fontsize=30, fontweight="bold", transform=ax.transAxes)
    ax.text(0.62, y - 0.05, sub, color=MUT, fontsize=13, transform=ax.transAxes, va="center")
    y -= 0.20

box(ax, 0.06, 0.05, 0.88, 0.13, "#0f3d24", "none")
ax.text(0.10, 0.115, f"Hold fossil flat by 2030 → need ~{flat:.0f}% low-carbon", color="white",
        fontsize=16, fontweight="bold", transform=ax.transAxes)
ax.text(0.10, 0.075, f"(momentum only reaches ~{mom:.0f}%).  Per +1pp renewables: {fe:.2f}% lower CO₂/capita.",
        color="#cfe9d8", fontsize=12.5, transform=ax.transAxes)
fig.savefig(ROOT / "figures" / "social.png", dpi=150, bbox_inches="tight", facecolor="white")
print("wrote figures/social.png")
