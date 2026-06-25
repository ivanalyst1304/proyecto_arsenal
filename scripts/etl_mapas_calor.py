"""
ETL parte 10 — MAPAS DE CALOR (imágenes PNG)
=============================================
Genera, por equipo y para el partido J26, dos tipos de mapa:
  - calor    : densidad de TODAS las acciones con balón (dónde "vive" el equipo)
  - presion  : densidad de acciones de recuperación (entradas, intercepciones,
               recuperaciones, despejes, duelos) = zonas donde roba el balón

Cada equipo ataca hacia la derecha (coordenadas Opta, ya relativas al equipo).

Salida: data/processed/mapa_<tipo>_<equipo>_J26.png
"""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from scipy.ndimage import gaussian_filter

BASE = Path(__file__).resolve().parent.parent
POST = BASE / "data" / "raw" / "postpartido_J26_Brentford_Arsenal.json"
OUT = BASE / "data" / "processed"

PRESION = {7, 8, 12, 44, 49, 74}  # despeje, interceptación, entrada, duelo, recuperación, falta recibida
CMAP = {"Arsenal": "Reds", "Brentford": "YlOrBr"}


def puntos_ofensivos(eventos, TID):
    """Acciones que generan peligro: pases progresivos (en su destino),
    regates exitosos y tiros (en su ubicación)."""
    pts = []
    for e in eventos:
        if e.get("contestantId") != TID or e.get("x") is None:
            continue
        t = e["typeId"]
        if t in (13, 14, 15, 16):                      # tiros
            pts.append((e["x"], e["y"]))
        elif t == 3 and e.get("outcome") == 1:          # regate exitoso
            pts.append((e["x"], e["y"]))
        elif t == 1 and e.get("outcome") == 1:          # pase progresivo
            q = {x["qualifierId"]: x.get("value") for x in e.get("qualifier", [])}
            if 140 in q and 141 in q:
                try:
                    dx, dy = float(q[140]), float(q[141])
                    if dx - e["x"] >= 15 and dx > 50:   # avanza >=15 y llega a campo rival
                        pts.append((dx, dy))
                except (ValueError, TypeError):
                    pass
    return pts


def campo(ax):
    lc = "white"
    ax.add_patch(Rectangle((0, 0), 100, 100, fill=False, ec=lc, lw=1.5))
    ax.plot([50, 50], [0, 100], color=lc, lw=1.5)
    ax.add_patch(Circle((50, 50), 9, fill=False, ec=lc, lw=1.5))
    ax.add_patch(Rectangle((0, 22), 16, 56, fill=False, ec=lc, lw=1.5))
    ax.add_patch(Rectangle((84, 22), 16, 56, fill=False, ec=lc, lw=1.5))


def heatmap(equipo, tipo, etiqueta):
    d = json.load(open(POST, encoding="utf-8"))
    ev = d["liveData"]["event"]
    cont = {c["id"]: c["name"] for c in d["matchInfo"]["contestant"]}

    pts = []
    if tipo == "ofensivo":
        pts = puntos_ofensivos(ev, [c["id"] for c in d["matchInfo"]["contestant"] if c["name"] == equipo][0])
    else:
        for e in ev:
            if cont.get(e.get("contestantId")) != equipo or e.get("x") is None:
                continue
            if tipo == "presion" and e["typeId"] not in PRESION:
                continue
            pts.append((e["x"], e["y"]))

    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    bins = (24, 16) if tipo in ("presion", "ofensivo") else (30, 20)
    H, _, _ = np.histogram2d(xs, ys, bins=bins, range=[[0, 100], [0, 100]])
    H = gaussian_filter(H, sigma=1.5)

    fig, ax = plt.subplots(figsize=(8, 5.5))
    fig.patch.set_facecolor("#141414")
    ax.imshow(H.T, extent=[0, 100, 0, 100], origin="lower", cmap=CMAP[equipo], alpha=0.92, aspect="auto")
    campo(ax)
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    ax.set_title(f"{etiqueta} · {equipo} ({len(pts)} acc., ataca a la derecha \u2192)",
                 color="white", fontsize=11, pad=10)
    plt.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.03)
    salida = OUT / f"mapa_{tipo}_{equipo.lower()}_J26.png"
    plt.savefig(salida, dpi=120, facecolor="#141414")
    plt.close()
    print("Generado:", salida.name, f"({len(pts)} acciones)")


if __name__ == "__main__":
    for eq in ["Arsenal", "Brentford"]:
        heatmap(eq, "ofensivo", "Zonas de peligro (acciones ofensivas)")
        heatmap(eq, "presion", "Zonas de recuperación")
