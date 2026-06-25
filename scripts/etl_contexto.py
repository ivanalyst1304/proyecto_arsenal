"""
ETL parte 8 — CONTEXTO PRE-PARTIDO (situación antes de la J26)
==============================================================
Calcula, con corte en la jornada 25 (lo que se sabía ANTES de la J26):
  - clasificacion_j25.csv        -> tabla de la liga tras J25
  - resumen_j25_<equipo>.csv     -> posición, puntos, V/E/D, goles
  - ultimos5_<equipo>.csv        -> los 5 partidos previos
  - destacados_<equipo>.csv      -> jugadores top (stats de temporada, proxy)
"""
import json
from collections import defaultdict
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "data" / "source" / "matches.json"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

CORTE = 25
EQUIPOS = ["Arsenal", "Brentford"]
SEASONSTATS = {
    "Arsenal": BASE / "data" / "seasonstats_arsenal.csv",
    "Brentford": BASE / "data" / "seasonstats_brentford.csv",
}


def cargar():
    d = json.load(open(SRC, encoding="utf-8"))
    out = []
    for m in d["match"]:
        ft = m.get("liveData", {}).get("matchDetails", {}).get("scores", {})
        ft = ft.get("ft") if ft else None
        if not ft:
            continue
        w = int(m["matchInfo"]["week"])
        if w > CORTE:
            continue
        cs = m["matchInfo"]["contestant"]
        h = next(c for c in cs if c["position"] == "home")
        a = next(c for c in cs if c["position"] == "away")
        out.append({"w": w, "home": h["name"], "away": a["name"], "gh": ft["home"], "ga": ft["away"]})
    return out


def clasificacion(jug):
    P = defaultdict(lambda: {"pts": 0, "pj": 0, "gf": 0, "gc": 0, "v": 0, "e": 0, "d": 0})
    for p in jug:
        for eq, gf, gc in [(p["home"], p["gh"], p["ga"]), (p["away"], p["ga"], p["gh"])]:
            s = P[eq]
            s["pj"] += 1; s["gf"] += gf; s["gc"] += gc
            if gf > gc: s["pts"] += 3; s["v"] += 1
            elif gf == gc: s["pts"] += 1; s["e"] += 1
            else: s["d"] += 1
    orden = sorted(P.items(), key=lambda x: (x[1]["pts"], x[1]["gf"] - x[1]["gc"]), reverse=True)
    filas = []
    for i, (eq, s) in enumerate(orden, 1):
        filas.append({"posicion": i, "equipo": eq, "puntos": s["pts"], "jugados": s["pj"],
                      "ganados": s["v"], "empatados": s["e"], "perdidos": s["d"],
                      "goles_favor": s["gf"], "goles_contra": s["gc"], "dif": s["gf"] - s["gc"]})
    return pd.DataFrame(filas)


def ultimos5(jug, equipo):
    res = []
    for p in jug:
        if equipo not in (p["home"], p["away"]):
            continue
        local = equipo == p["home"]
        gf, gc = (p["gh"], p["ga"]) if local else (p["ga"], p["gh"])
        rival = p["away"] if local else p["home"]
        r = "V" if gf > gc else ("E" if gf == gc else "D")
        res.append({"jornada": p["w"], "rival": rival, "sede": "Casa" if local else "Fuera",
                    "gf": gf, "gc": gc, "resultado": r})
    return pd.DataFrame(sorted(res, key=lambda x: x["jornada"])[-5:])


def destacados(equipo):
    df = pd.read_csv(SEASONSTATS[equipo])
    n = lambda c: pd.to_numeric(df[c], errors="coerce").fillna(0)
    out = pd.DataFrame({
        "jugador": df["nombre"],
        "goles": n("Goals").astype(int),
        "asistencias": n("Goal Assists").astype(int),
        "pases_clave": n("Key Passes (Attempt Assists)").astype(int),
    })
    out["G+A"] = out["goles"] + out["asistencias"]
    return out.sort_values("G+A", ascending=False).head(6)


def main():
    jug = cargar()
    clasificacion(jug).to_csv(OUT / "clasificacion_j25.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")
    tabla = clasificacion(jug).set_index("equipo")
    for eq in EQUIPOS:
        ultimos5(jug, eq).to_csv(OUT / f"ultimos5_{eq.lower()}.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")
        destacados(eq).to_csv(OUT / f"destacados_{eq.lower()}.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")
        fila = tabla.loc[eq]
        resumen = {"posicion": int(fila["posicion"]), "puntos": int(fila["puntos"]),
                   "jugados": int(fila["jugados"]), "ganados": int(fila["ganados"]),
                   "empatados": int(fila["empatados"]), "perdidos": int(fila["perdidos"]),
                   "goles_favor": int(fila["goles_favor"]), "goles_contra": int(fila["goles_contra"])}
        pd.DataFrame([resumen]).to_csv(OUT / f"resumen_j25_{eq.lower()}.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")
    print("Contexto generado para:", ", ".join(EQUIPOS))


if __name__ == "__main__":
    main()
