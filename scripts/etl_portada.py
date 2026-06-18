"""
ETL parte 3 — Datos de PORTADA (Arsenal)
=========================================
A partir de 'matches.json' (todos los partidos de la liga) calcula:
  1) resumen_temporada_arsenal.csv  -> posición, puntos, V/E/D, goles...
  2) puntos_por_jornada.csv         -> evolución de puntos del Arsenal

Entrada esperada: data/source/matches.json
Salida (formato europeo ; , ): data/processed/
"""
import json
from pathlib import Path
from collections import defaultdict
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "data" / "source" / "matches.json"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

EQUIPO = "Arsenal"   # nombre corto del equipo objetivo


def cargar_partidos():
    d = json.load(open(SRC, encoding="utf-8"))
    jugados = []
    for m in d["match"]:
        ft = m.get("liveData", {}).get("matchDetails", {}).get("scores", {})
        ft = ft.get("ft") if ft else None
        if not ft:               # partido aún no jugado -> se ignora
            continue
        cs = m["matchInfo"]["contestant"]
        home = next(c for c in cs if c["position"] == "home")
        away = next(c for c in cs if c["position"] == "away")
        jugados.append({
            "week": int(m["matchInfo"]["week"]),
            "home": home["name"], "away": away["name"],
            "gh": ft["home"], "ga": ft["away"],
        })
    return jugados


def tabla_liga(jugados):
    """Calcula puntos de todos los equipos para sacar la posición."""
    pts = defaultdict(int)
    for p in jugados:
        if p["gh"] > p["ga"]:
            pts[p["home"]] += 3
        elif p["gh"] < p["ga"]:
            pts[p["away"]] += 3
        else:
            pts[p["home"]] += 1
            pts[p["away"]] += 1
    orden = sorted(pts.items(), key=lambda x: x[1], reverse=True)
    posiciones = {eq: i + 1 for i, (eq, _) in enumerate(orden)}
    return posiciones


def main():
    jugados = cargar_partidos()

    # Partidos del Arsenal, ordenados por jornada
    filas = []
    for p in jugados:
        if EQUIPO not in (p["home"], p["away"]):
            continue
        local = EQUIPO in p["home"]
        gf, gc = (p["gh"], p["ga"]) if local else (p["ga"], p["gh"])
        rival = p["away"] if local else p["home"]
        res = "V" if gf > gc else ("E" if gf == gc else "D")
        filas.append({
            "jornada": p["week"], "rival": rival,
            "sede": "Casa" if local else "Fuera",
            "gf": gf, "gc": gc, "resultado": res,
            "puntos": 3 if res == "V" else (1 if res == "E" else 0),
        })
    df = pd.DataFrame(filas).sort_values("jornada").reset_index(drop=True)
    df["puntos_acumulados"] = df["puntos"].cumsum()
    df.to_csv(OUT / "puntos_por_jornada.csv", index=False,
              sep=";", decimal=",", encoding="utf-8-sig")

    # Resumen de temporada
    pos = tabla_liga(jugados)
    resumen = {
        "posicion": pos.get(EQUIPO + " FC", pos.get(EQUIPO)),
        "puntos": int(df["puntos"].sum()),
        "jugados": len(df),
        "ganados": int((df.resultado == "V").sum()),
        "empatados": int((df.resultado == "E").sum()),
        "perdidos": int((df.resultado == "D").sum()),
        "goles_favor": int(df["gf"].sum()),
        "goles_contra": int(df["gc"].sum()),
        "pct_victorias": round(100 * (df.resultado == "V").sum() / len(df), 1),
    }
    pd.DataFrame([resumen]).to_csv(OUT / "resumen_temporada_arsenal.csv",
                                   index=False, sep=";", decimal=",",
                                   encoding="utf-8-sig")
    print("Generado puntos_por_jornada.csv y resumen_temporada_arsenal.csv")
    print("Resumen:", resumen)


if __name__ == "__main__":
    main()
