"""
ETL parte 13 — MÉTRICAS DE TRANSICIÓN
======================================
Calcula, por equipo y partido, indicadores de transición ofensiva tras robo:
  - tiempo_transicion_seg  : segundos medios desde la recuperación hasta llegar
                             a campo rival (x>66)
  - transiciones_rapidas   : nº de transiciones que llegaron en < 6 segundos
  - altura_recuperacion    : x media donde se recupera el balón
  - pase_adelante_pct      : % de primeros pases tras recuperar que van hacia adelante

Todo se calcula a partir de coordenadas y marcas temporales de los eventos
(elaboración propia, no viene precalculado en los datos Opta).

Salida: data/processed/transiciones.csv  (formato europeo)
"""
import json
from pathlib import Path
from statistics import mean
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"

RECUP = {7, 8, 12, 49}  # despeje, interceptación, entrada, recuperación

PARTIDOS = [
    ("postpartido_J26_Brentford_Arsenal.json", "postpartido", "J26"),
    ("prepartido_arsenal_J25_Arsenal_Sunderland.json", "prepartido_arsenal", "J25"),
    ("prepartido_brentford_J25_Newcastle_Brentford.json", "prepartido_rival", "J25"),
]


def transiciones_equipo(ev, TID):
    evs = sorted(ev, key=lambda e: (e.get("periodId", 0), e.get("timeMin", 0), e.get("timeSec", 0)))
    trans = []
    for i, e in enumerate(evs):
        if e.get("contestantId") == TID and e["typeId"] in RECUP and e.get("x") is not None:
            x0 = e["x"]
            t0 = e.get("timeMin", 0) * 60 + e.get("timeSec", 0)
            for j in range(i + 1, min(i + 12, len(evs))):
                n = evs[j]
                if n.get("contestantId") != TID:
                    if n["typeId"] in (1, 3, 8, 12, 49):
                        break
                    continue
                if n.get("x", 0) > 66:
                    t1 = n.get("timeMin", 0) * 60 + n.get("timeSec", 0)
                    if 0 <= t1 - t0 <= 30:
                        trans.append({"dur": t1 - t0, "x0": x0})
                    break

    # primer pase tras recuperar hacia adelante
    adel = tot = 0
    for i, e in enumerate(evs):
        if e.get("contestantId") == TID and e["typeId"] in RECUP:
            for j in range(i + 1, min(i + 3, len(evs))):
                n = evs[j]
                if n.get("contestantId") == TID and n["typeId"] == 1 and n.get("x") is not None:
                    tot += 1
                    q = {x["qualifierId"]: x.get("value") for x in n.get("qualifier", [])}
                    if 140 in q:
                        try:
                            if float(q[140]) > n["x"]:
                                adel += 1
                        except (ValueError, TypeError):
                            pass
                    break

    return {
        "tiempo_transicion_seg": round(mean(t["dur"] for t in trans), 1) if trans else None,
        "transiciones_rapidas": sum(1 for t in trans if t["dur"] < 6),
        "altura_recuperacion": round(mean(t["x0"] for t in trans), 1) if trans else None,
        "pase_adelante_pct": round(100 * adel / tot, 1) if tot else None,
    }


def main():
    filas = []
    for fichero, bloque, jornada in PARTIDOS:
        d = json.load(open(RAW / fichero, encoding="utf-8"))
        ev = d["liveData"]["event"]
        for c in d["matchInfo"]["contestant"]:
            vals = transiciones_equipo(ev, c["id"])
            filas.append({"bloque": bloque, "jornada": jornada, "equipo": c["name"], **vals})
    df = pd.DataFrame(filas)
    df.to_csv(OUT / "transiciones.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")
    print("Generado: transiciones.csv")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
