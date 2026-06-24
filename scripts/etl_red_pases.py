"""
ETL parte 4 — REDES DE PASES (imágenes PNG)
============================================
Genera la red de pases de un equipo en un partido:
  - Nodos: jugadores titulares en su posición media (tamaño = nº de toques).
  - Aristas: nº de pases entre cada par de jugadores (grosor = volumen).
El receptor de cada pase se infiere del siguiente evento del mismo equipo.

Salida: data/processed/red_pases_<equipo>_<jornada>.png
"""
import json
from collections import defaultdict, Counter
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle, Circle

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# Mapa id->apellido para etiquetas legibles
import pandas as pd
_df = pd.read_csv(BASE / "data" / "seasonstats_arsenal.csv")
ID2NAME = dict(zip(_df["id"].astype(str).str.strip(), _df["nombre"]))


def red_pases(fichero, equipo, etiqueta, salida):
    d = json.load(open(fichero, encoding="utf-8"))
    ev = d["liveData"]["event"]
    TID = [c["id"] for c in d["matchInfo"]["contestant"] if c["name"] == equipo][0]

    setup = [e for e in ev if e["typeId"] == 34 and e["contestantId"] == TID][0]
    q = {x["qualifierId"]: x.get("value") for x in setup["qualifier"]}
    ids = [s.strip() for s in q[30].split(",")]
    pos = [s.strip() for s in q[44].split(",")]
    titulares = set(i for i, p in zip(ids, pos) if p != "5")

    ev = sorted(ev, key=lambda e: (e.get("periodId", 0), e.get("timeMin", 0), e.get("timeSec", 0)))

    px, py, toques = defaultdict(list), defaultdict(list), Counter()
    for e in ev:
        if e["contestantId"] == TID and e.get("playerId") in titulares and e.get("x") is not None:
            px[e["playerName"]].append(e["x"])
            py[e["playerName"]].append(e["y"])
            toques[e["playerName"]] += 1

    con = Counter()
    for i, e in enumerate(ev[:-1]):
        if e["typeId"] == 1 and e["contestantId"] == TID and e.get("outcome") == 1 and e.get("playerId") in titulares:
            for nxt in ev[i + 1:i + 4]:
                if (nxt["contestantId"] == TID and nxt.get("playerId") in titulares
                        and nxt.get("playerName") and nxt["playerName"] != e["playerName"]):
                    con[tuple(sorted([e["playerName"], nxt["playerName"]]))] += 1
                    break

    posm = {j: (sum(px[j]) / len(px[j]), sum(py[j]) / len(py[j])) for j in px}

    # --- Dibujo del campo (horizontal, ataque hacia la derecha) ---
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_facecolor("#2d6a3e"); fig.patch.set_facecolor("#141414")
    lc = "white"
    ax.add_patch(Rectangle((0, 0), 100, 100, fill=False, ec=lc, lw=2))
    ax.plot([50, 50], [0, 100], color=lc, lw=2)
    ax.add_patch(Circle((50, 50), 9, fill=False, ec=lc, lw=2))
    ax.add_patch(Rectangle((0, 22), 16, 56, fill=False, ec=lc, lw=2))
    ax.add_patch(Rectangle((84, 22), 16, 56, fill=False, ec=lc, lw=2))

    maxc = max(con.values()) if con else 1
    for (a, b), n in con.items():
        if n < 4 or a not in posm or b not in posm:
            continue
        x1, y1 = posm[a]; x2, y2 = posm[b]
        ax.plot([x1, x2], [y1, y2], color="#F2C811", lw=1 + 5 * n / maxc, alpha=0.55, zorder=1)

    maxt = max(toques.values()) if toques else 1
    for j, (x, y) in posm.items():
        frac = toques[j] / maxt
        r = 600 + 1500 * frac
        ax.scatter(x, y, s=r, color="#EF0107", edgecolors="white", linewidths=1.5, zorder=2)
        # etiqueta debajo del nodo, con contorno oscuro para legibilidad
        offset = 5 + 4 * frac
        ax.text(x, y - offset, j.split()[-1], color="white", ha="center", va="top",
                fontsize=9, zorder=4,
                path_effects=[pe.withStroke(linewidth=2.5, foreground="#141414")])

    ax.set_xlim(-2, 102); ax.set_ylim(-2, 102)
    ax.axis("off")
    ax.set_title(etiqueta, color="white", fontsize=12, pad=10)
    plt.subplots_adjust(left=0.02, right=0.98, top=0.93, bottom=0.02)
    plt.savefig(salida, dpi=120, facecolor="#141414")
    plt.close()
    print("Generada:", salida.name)


REDES = [
    ("prepartido_arsenal_J25_Arsenal_Sunderland.json", "Arsenal", "Red de pases · Arsenal vs Sunderland (J25)", "red_pases_arsenal_J25.png"),
    ("prepartido_brentford_J25_Newcastle_Brentford.json", "Brentford", "Red de pases · Brentford en Newcastle (J25)", "red_pases_brentford_J25.png"),
    ("postpartido_J26_Brentford_Arsenal.json", "Arsenal", "Red de pases · Arsenal en Brentford (J26)", "red_pases_arsenal_J26.png"),
    ("postpartido_J26_Brentford_Arsenal.json", "Brentford", "Red de pases · Brentford vs Arsenal (J26)", "red_pases_brentford_J26.png"),
]

if __name__ == "__main__":
    for fichero, equipo, etiqueta, nombre in REDES:
        red_pases(RAW / fichero, equipo, etiqueta, OUT / nombre)
