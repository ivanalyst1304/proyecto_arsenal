"""
ETL parte 11 — MÉTRICAS ADICIONALES (no destructivo)
=====================================================
Añade columnas avanzadas a metricas_equipo.csv SIN modificar las existentes:
  - toques_area_rival   : presencia ofensiva (acciones en el área rival)
  - pases_campo_rival   : dominio territorial (pases con x>50)
  - pases_progresivos   : progresión (pases completados que avanzan >=15 a campo rival)
  - recuperaciones      : balones recuperados (typeId 49)
  - faltas_recibidas    : faltas a favor (typeId 4, outcome 1)
  - ppda                : pases del rival por acción defensiva en presión (más baja = más presión)

Recalcula solo las columnas nuevas a partir de los JSON; respeta todo lo demás.
"""
import json
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
CSV = BASE / "data" / "processed" / "metricas_equipo.csv"

# Mapa: (bloque) -> fichero del partido
FICHERO = {
    "postpartido": "postpartido_J26_Brentford_Arsenal.json",
    "prepartido_arsenal": "prepartido_arsenal_J25_Arsenal_Sunderland.json",
    "prepartido_rival": "prepartido_brentford_J25_Newcastle_Brentford.json",
}


def metricas_extra(fichero, equipo):
    d = json.load(open(RAW / fichero, encoding="utf-8"))
    ev = d["liveData"]["event"]
    cont = {c["id"]: c["name"] for c in d["matchInfo"]["contestant"]}
    TID = [k for k, v in cont.items() if v == equipo][0]
    RID = [k for k in cont if k != TID][0]
    eq = [e for e in ev if e.get("contestantId") == TID]

    toques_area = sum(1 for e in eq if e.get("x", 0) > 83 and 21 < e.get("y", 50) < 79)
    pases_campo_rival = sum(1 for e in eq if e["typeId"] == 1 and e.get("x", 0) > 50)
    recuperaciones = sum(1 for e in eq if e["typeId"] == 49)
    faltas_recibidas = sum(1 for e in eq if e["typeId"] == 4 and e.get("outcome") == 1)

    prog = 0
    for e in eq:
        if e["typeId"] == 1 and e.get("outcome") == 1:
            q = {x["qualifierId"]: x.get("value") for x in e.get("qualifier", [])}
            if 140 in q:
                try:
                    if float(q[140]) - e["x"] >= 15 and float(q[140]) > 50:
                        prog += 1
                except (ValueError, TypeError):
                    pass

    # PPDA: pases del rival en su salida (x<=60) / acciones def. propias en presión (entradas/interc/faltas, x>=40)
    acc_def = sum(1 for e in ev if e.get("contestantId") == TID and e["typeId"] in (4, 8, 12) and e.get("x", 0) >= 40)
    pases_rival = sum(1 for e in ev if e.get("contestantId") == RID and e["typeId"] == 1 and e.get("x", 0) <= 60)
    ppda = round(pases_rival / acc_def, 1) if acc_def else None

    return {"toques_area_rival": toques_area, "pases_campo_rival": pases_campo_rival,
            "pases_progresivos": prog, "recuperaciones": recuperaciones,
            "faltas_recibidas": faltas_recibidas, "ppda": ppda}


def main():
    df = pd.read_csv(CSV, sep=";", decimal=",")
    nuevas = ["toques_area_rival", "pases_campo_rival", "pases_progresivos",
              "recuperaciones", "faltas_recibidas", "ppda"]
    for col in nuevas:
        df[col] = None
    for i, fila in df.iterrows():
        fichero = FICHERO.get(fila["bloque"])
        if not fichero:
            continue
        vals = metricas_extra(fichero, fila["equipo"])
        for col in nuevas:
            df.at[i, col] = vals[col]
    # Asegurar que ppda es numérica (float) para que se exporte con coma decimal, no con punto
    df["ppda"] = pd.to_numeric(df["ppda"], errors="coerce")
    df.to_csv(CSV, index=False, sep=";", decimal=",", encoding="utf-8-sig")
    print("metricas_equipo.csv actualizado con:", ", ".join(nuevas))
    print(df[["bloque", "equipo"] + nuevas].to_string(index=False))


if __name__ == "__main__":
    main()
