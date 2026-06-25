"""
ETL parte 9 — ALINEACIONES DEL PARTIDO (J26)
=============================================
Extrae el once inicial real de cada equipo en el partido analizado (J26) y lo
coloca en su sistema (ambos jugaron 4-2-3-1). El dataset solo da el rol general
(GK/def/mid/fwd), así que la posición concreta de cada hueco se asigna por el
rol real conocido de cada jugador.

Salida: data/processed/alineacion_<equipo>_J26.csv  (dorsal, jugador, rol, x, y)
"""
import json
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
POST = BASE / "data" / "raw" / "postpartido_J26_Brentford_Arsenal.json"
OUT = BASE / "data" / "processed"

ars = pd.read_csv(BASE / "data" / "seasonstats_arsenal.csv")
bre = pd.read_csv(BASE / "data" / "seasonstats_brentford.csv")
ID2NAME = {**dict(zip(ars["id"].astype(str).str.strip(), ars["nombre"])),
           **dict(zip(bre["id"].astype(str).str.strip(), bre["nombre"]))}

# Coordenadas del 4-2-3-1 por dorsal (x=ancho 0-100, y=profundidad 0-100)
COORDS = {
    "Arsenal": {
        "1": (50, 6, "Portero"), "5": (15, 24, "Lateral izquierdo"),
        "6": (38, 22, "Central"), "3": (62, 22, "Central"), "12": (85, 24, "Lateral derecho"),
        "36": (38, 44, "Pivote"), "41": (62, 44, "Pivote"),
        "19": (15, 68, "Extremo izquierdo"), "10": (50, 66, "Mediapunta"),
        "20": (85, 68, "Extremo derecho"), "14": (50, 88, "Delantero"),
    },
    "Brentford": {
        "1": (50, 6, "Portero"), "3": (15, 24, "Lateral izquierdo"),
        "4": (38, 22, "Central"), "20": (62, 22, "Central"), "33": (85, 24, "Lateral derecho"),
        "27": (38, 44, "Pivote"), "18": (62, 44, "Pivote"),
        "23": (15, 68, "Extremo izquierdo"), "8": (50, 66, "Mediapunta"),
        "19": (85, 68, "Extremo derecho"), "9": (50, 88, "Delantero"),
    },
}


def alineacion(equipo):
    d = json.load(open(POST, encoding="utf-8"))
    ev = d["liveData"]["event"]
    TID = [c["id"] for c in d["matchInfo"]["contestant"] if c["name"] == equipo][0]
    setup = [e for e in ev if e["typeId"] == 34 and e["contestantId"] == TID][0]
    q = {x["qualifierId"]: x.get("value") for x in setup["qualifier"]}
    ids = [s.strip() for s in q[30].split(",")]
    nums = [s.strip() for s in q[59].split(",")]
    pos = [s.strip() for s in q[44].split(",")]

    filas = []
    for i, n, p in zip(ids, nums, pos):
        if p == "5":
            continue
        x, y, rol = COORDS[equipo].get(n, (50, 50, "?"))
        filas.append({"dorsal": int(n), "jugador": ID2NAME.get(i, i), "rol": rol, "x": x, "y": y})
    df = pd.DataFrame(filas).sort_values("y")
    salida = OUT / f"alineacion_{equipo.lower()}_J26.csv"
    df.to_csv(salida, index=False, sep=";", decimal=",", encoding="utf-8-sig")
    print("Generada:", salida.name)
    print(df.to_string(index=False))
    print()


if __name__ == "__main__":
    for eq in ["Arsenal", "Brentford"]:
        alineacion(eq)
