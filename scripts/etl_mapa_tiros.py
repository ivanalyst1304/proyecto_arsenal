"""
ETL parte 6 — MAPAS DE TIROS (imágenes PNG)
============================================
Dibuja los tiros de un equipo en un partido sobre la media cancha de ataque:
verde = gol, amarillo = a puerta, gris = fuera. Tamaño mayor para los goles.

Salida: data/processed/mapa_tiros_<equipo>_<jornada>.png
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

COLOR = {16: "#1DBF73", 15: "#F2C811", 14: "#F2C811", 13: "#888888"}  # gol / a puerta / palo / fuera


def media_cancha(ax):
    lc = "white"
    # Mostramos de x=50 (medio campo) a x=100 (portería rival, a la derecha)
    ax.add_patch(Rectangle((50, 0), 50, 100, fill=False, ec=lc, lw=2))
    ax.add_patch(Rectangle((84, 22), 16, 56, fill=False, ec=lc, lw=2))   # área grande
    ax.add_patch(Rectangle((94, 37), 6, 26, fill=False, ec=lc, lw=2))    # área pequeña
    ax.add_patch(Arc((88, 50), 18, 18, angle=0, theta1=300, theta2=60, color=lc, lw=2))
    ax.plot([100, 100], [44, 56], color=lc, lw=4)  # portería


def mapa_tiros(fichero, equipo, etiqueta, salida):
    d = json.load(open(fichero, encoding="utf-8"))
    ev = d["liveData"]["event"]
    TID = [c["id"] for c in d["matchInfo"]["contestant"] if c["name"] == equipo][0]
    tiros = [e for e in ev if e["typeId"] in (13, 14, 15, 16) and e["contestantId"] == TID]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_facecolor("#2d6a3e"); fig.patch.set_facecolor("#141414")
    media_cancha(ax)

    for t in tiros:
        c = COLOR.get(t["typeId"], "#888888")
        es_gol = t["typeId"] == 16
        ax.scatter(t["x"], t["y"], s=320 if es_gol else 160, color=c,
                   edgecolors="white", linewidths=1.4 if es_gol else 1,
                   alpha=0.9, zorder=3)

    goles = sum(1 for t in tiros if t["typeId"] == 16)
    ap = sum(1 for t in tiros if t["typeId"] in (15, 16))
    sub = f"{len(tiros)} tiros · {ap} a puerta · {goles} goles · ataque a la derecha →"

    ax.set_xlim(49, 101); ax.set_ylim(-2, 102)
    ax.axis("off")
    ax.set_title(etiqueta, color="white", fontsize=12, pad=12)
    ax.text(75, -1, sub, color="#cfcfcf", ha="center", va="top", fontsize=9)
    # leyenda
    ax.scatter([], [], c="#1DBF73", s=120, edgecolors="white", label="Gol")
    ax.scatter([], [], c="#F2C811", s=120, edgecolors="white", label="A puerta")
    ax.scatter([], [], c="#888888", s=120, edgecolors="white", label="Fuera")
    ax.legend(loc="upper left", fontsize=8, facecolor="#1c1c1c", edgecolor="none", labelcolor="white")
    plt.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.06)
    plt.savefig(salida, dpi=120, facecolor="#141414")
    plt.close()
    print("Generado:", salida.name, f"({len(tiros)} tiros, {goles} goles)")


MAPAS = [
    ("prepartido_arsenal_J25_Arsenal_Sunderland.json", "Arsenal", "Mapa de tiros · Arsenal vs Sunderland (J25)", "mapa_tiros_arsenal_J25.png"),
    ("prepartido_brentford_J25_Newcastle_Brentford.json", "Brentford", "Mapa de tiros · Brentford en Newcastle (J25)", "mapa_tiros_brentford_J25.png"),
    ("postpartido_J26_Brentford_Arsenal.json", "Arsenal", "Mapa de tiros · Arsenal en Brentford (J26)", "mapa_tiros_arsenal_J26.png"),
    ("postpartido_J26_Brentford_Arsenal.json", "Brentford", "Mapa de tiros · Brentford vs Arsenal (J26)", "mapa_tiros_brentford_J26.png"),
]

if __name__ == "__main__":
    for fichero, equipo, etiqueta, nombre in MAPAS:
        mapa_tiros(RAW / fichero, equipo, etiqueta, OUT / nombre)
