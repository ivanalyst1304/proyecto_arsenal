"""
ETL parte 7 — MAPAS DEFENSIVOS (imágenes PNG)
==============================================
Dibuja intercepciones (círculos azules) y despejes (triángulos amarillos)
de un equipo en un partido sobre el campo completo. El equipo defiende
su portería en el lado izquierdo.

Salida: data/processed/mapa_defensivo_<equipo>_<jornada>.png
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)


def campo(ax):
    lc = "white"
    ax.add_patch(Rectangle((0, 0), 100, 100, fill=False, ec=lc, lw=2))
    ax.plot([50, 50], [0, 100], color=lc, lw=2)
    ax.add_patch(Circle((50, 50), 9, fill=False, ec=lc, lw=2))
    ax.add_patch(Rectangle((0, 22), 16, 56, fill=False, ec=lc, lw=2))
    ax.add_patch(Rectangle((84, 22), 16, 56, fill=False, ec=lc, lw=2))


def mapa_defensivo(fichero, equipo, etiqueta, salida):
    d = json.load(open(fichero, encoding="utf-8"))
    ev = d["liveData"]["event"]
    TID = [c["id"] for c in d["matchInfo"]["contestant"] if c["name"] == equipo][0]
    inter = [(e["x"], e["y"]) for e in ev if e["typeId"] == 8 and e["contestantId"] == TID]
    desp = [(e["x"], e["y"]) for e in ev if e["typeId"] == 7 and e["contestantId"] == TID]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_facecolor("#2d6a3e"); fig.patch.set_facecolor("#141414")
    campo(ax)

    if inter:
        ax.scatter([x for x, y in inter], [y for x, y in inter], s=150,
                   color="#3FA7FF", edgecolors="white", linewidths=1, alpha=0.9,
                   marker="o", zorder=3, label=f"Intercepciones ({len(inter)})")
    if desp:
        ax.scatter([x for x, y in desp], [y for x, y in desp], s=170,
                   color="#F2C811", edgecolors="white", linewidths=1, alpha=0.9,
                   marker="^", zorder=3, label=f"Despejes ({len(desp)})")

    ax.set_xlim(-2, 102); ax.set_ylim(-2, 102)
    ax.axis("off")
    ax.set_title(etiqueta, color="white", fontsize=12, pad=12)
    ax.text(50, -1, "El equipo defiende hacia la izquierda \u2190", color="#cfcfcf",
            ha="center", va="top", fontsize=9)
    ax.legend(loc="upper right", fontsize=8, facecolor="#1c1c1c", edgecolor="none", labelcolor="white")
    plt.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.05)
    plt.savefig(salida, dpi=120, facecolor="#141414")
    plt.close()
    print("Generado:", salida.name, f"({len(inter)} interc., {len(desp)} despejes)")


MAPAS = [
    ("prepartido_arsenal_J25_Arsenal_Sunderland.json", "Arsenal", "Mapa defensivo \u00b7 Arsenal vs Sunderland (J25)", "mapa_defensivo_arsenal_J25.png"),
    ("prepartido_brentford_J25_Newcastle_Brentford.json", "Brentford", "Mapa defensivo \u00b7 Brentford en Newcastle (J25)", "mapa_defensivo_brentford_J25.png"),
    ("postpartido_J26_Brentford_Arsenal.json", "Arsenal", "Mapa defensivo \u00b7 Arsenal en Brentford (J26)", "mapa_defensivo_arsenal_J26.png"),
    ("postpartido_J26_Brentford_Arsenal.json", "Brentford", "Mapa defensivo \u00b7 Brentford vs Arsenal (J26)", "mapa_defensivo_brentford_J26.png"),
]

if __name__ == "__main__":
    for fichero, equipo, etiqueta, nombre in MAPAS:
        mapa_defensivo(RAW / fichero, equipo, etiqueta, OUT / nombre)
