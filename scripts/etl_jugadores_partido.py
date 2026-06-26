"""
ETL parte 5 — JUGADORES POR PARTIDO (destacados)
=================================================
Para cada equipo en cada partido, calcula estadísticas individuales fiables:
goles, asistencias (pase previo al gol), tiros, pases completados, regates,
entradas, intercepciones y despejes.

Salida (formato europeo): data/processed/jugadores_<equipo>_<jornada>.csv
"""
import json
from collections import defaultdict, Counter
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)


def stats_jugadores(fichero, equipo, salida):
    d = json.load(open(fichero, encoding="utf-8"))
    ev = d["liveData"]["event"]
    TID = [c["id"] for c in d["matchInfo"]["contestant"] if c["name"] == equipo][0]
    evs = sorted(ev, key=lambda e: (e.get("periodId", 0), e.get("timeMin", 0), e.get("timeSec", 0)))

    st = defaultdict(Counter)
    for e in evs:
        if e.get("contestantId") != TID or not e.get("playerName"):
            continue
        j, t, o = e["playerName"], e["typeId"], e.get("outcome")
        if t == 16: st[j]["goles"] += 1
        if t == 1: st[j]["pases"] += 1
        if t == 1 and o == 1: st[j]["pases_completados"] += 1
        if t in (13, 14, 15, 16): st[j]["tiros"] += 1
        if t in (15, 16): st[j]["tiros_a_puerta"] += 1
        if t == 3 and o == 1: st[j]["regates"] += 1
        if t == 12: st[j]["entradas"] += 1
        if t == 8: st[j]["intercepciones"] += 1
        if t == 7: st[j]["despejes"] += 1
        if e.get("x", 0) > 83 and 21 < e.get("y", 50) < 79: st[j]["toques_area_rival"] += 1
        if t == 1 and any(x["qualifierId"] == 210 for x in e.get("qualifier", [])):
            st[j]["pases_clave"] += 1

    # Asistencias: pase completado de un compañero justo antes de cada gol
    for i, e in enumerate(evs):
        if e["typeId"] == 16 and e["contestantId"] == TID:
            for j in range(i - 1, max(i - 6, -1), -1):
                p = evs[j]
                if (p["typeId"] == 1 and p["contestantId"] == TID and p.get("outcome") == 1
                        and p.get("playerName") and p["playerName"] != e["playerName"]):
                    st[p["playerName"]]["asistencias"] += 1
                    break

    cols = ["goles", "asistencias", "tiros", "tiros_a_puerta", "pases_completados",
            "regates", "entradas", "intercepciones", "despejes",
            "pases_clave", "toques_area_rival"]
    filas = [{"jugador": j, **{c: st[j][c] for c in cols}} for j in st]
    df = pd.DataFrame(filas).fillna(0)
    df = df.sort_values(["goles", "asistencias", "tiros"], ascending=False).reset_index(drop=True)
    df.to_csv(salida, index=False, sep=";", decimal=",", encoding="utf-8-sig")
    print("Generado:", salida.name, f"({len(df)} jugadores)")


PARTIDOS = [
    ("prepartido_arsenal_J25_Arsenal_Sunderland.json", "Arsenal", "jugadores_arsenal_J25.csv"),
    ("prepartido_brentford_J25_Newcastle_Brentford.json", "Brentford", "jugadores_brentford_J25.csv"),
    ("postpartido_J26_Brentford_Arsenal.json", "Arsenal", "jugadores_arsenal_J26.csv"),
    ("postpartido_J26_Brentford_Arsenal.json", "Brentford", "jugadores_brentford_J26.csv"),
]

if __name__ == "__main__":
    for fichero, equipo, nombre in PARTIDOS:
        stats_jugadores(RAW / fichero, equipo, OUT / nombre)
