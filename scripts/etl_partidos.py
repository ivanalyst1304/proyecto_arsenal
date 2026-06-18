"""
ETL - Análisis Arsenal (Jornada 26: Brentford 1-1 Arsenal)
==========================================================
Lee los 3 partidos en formato Opta/Stats Perform (JSON) y genera tablas
limpias (CSV) listas para Power BI.

Bloques:
  - postpartido        -> J26 Brentford vs Arsenal
  - prepartido_arsenal -> J25 Arsenal vs Sunderland
  - prepartido_rival   -> J25 Newcastle vs Brentford

Autor: (tu nombre)
"""

import json
from pathlib import Path
import pandas as pd

# --- Rutas (relativas al proyecto) -----------------------------------------
BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# Mapeo de cada bloque a su archivo
FICHEROS = {
    "postpartido":        RAW / "postpartido_J26_Brentford_Arsenal.json",
    "prepartido_arsenal": RAW / "prepartido_arsenal_J25_Arsenal_Sunderland.json",
    "prepartido_rival":   RAW / "prepartido_brentford_J25_Newcastle_Brentford.json",
}

# --- Diccionario de tipos de evento Opta (los que usamos) -------------------
TIPOS_TIRO = {13, 14, 15, 16}      # 13 fuera, 14 palo, 15 parado, 16 GOL
TIROS_PUERTA = {15, 16}            # a puerta = parado + gol

def cargar(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def quals(evento):
    """Devuelve los qualifiers de un evento como dict {id: valor}."""
    return {q["qualifierId"]: q.get("value") for q in evento.get("qualifier", [])}

def metricas_equipo(eventos, team_id):
    """Calcula las métricas de un equipo a partir de su lista de eventos."""
    ev = [e for e in eventos if e.get("contestantId") == team_id]

    pases = [e for e in ev if e["typeId"] == 1]
    pases_ok = [e for e in pases if e.get("outcome") == 1]
    tiros = [e for e in ev if e["typeId"] in TIPOS_TIRO]
    tiros_p = [e for e in ev if e["typeId"] in TIROS_PUERTA]
    aereos = [e for e in ev if e["typeId"] == 44]
    aereos_ok = [e for e in aereos if e.get("outcome") == 1]
    regates = [e for e in ev if e["typeId"] == 3]
    regates_ok = [e for e in regates if e.get("outcome") == 1]

    # Tarjetas: qualifier 31 = amarilla, 32/33 = roja
    tarjetas = [e for e in ev if e["typeId"] == 17]
    amarillas = sum(1 for t in tarjetas if 31 in quals(t))
    rojas = sum(1 for t in tarjetas if 32 in quals(t) or 33 in quals(t))

    return {
        "pases": len(pases),
        "pases_completados": len(pases_ok),
        "precision_pase_pct": round(100 * len(pases_ok) / len(pases), 1) if pases else 0,
        "tiros_totales": len(tiros),
        "tiros_a_puerta": len(tiros_p),
        "goles": sum(1 for e in ev if e["typeId"] == 16),
        "entradas": sum(1 for e in ev if e["typeId"] == 12),
        "intercepciones": sum(1 for e in ev if e["typeId"] == 8),
        "despejes": sum(1 for e in ev if e["typeId"] == 7),
        # En Opta la falta se registra 2 veces (comete=outcome 0, recibe=outcome 1)
        "faltas_cometidas": sum(1 for e in ev if e["typeId"] == 4 and e.get("outcome") == 0),
        # El córner se registra 2 veces (a favor=outcome 1, en contra=outcome 0)
        "corners": sum(1 for e in ev if e["typeId"] == 6 and e.get("outcome") == 1),
        "duelos_aereos": len(aereos),
        "duelos_aereos_ganados": len(aereos_ok),
        "regates": len(regates),
        "regates_exitosos": len(regates_ok),
        "amarillas": amarillas,
        "rojas": rojas,
    }

def procesar(bloque, path):
    d = cargar(path)
    mi = d["matchInfo"]
    md = d["liveData"]["matchDetails"]
    eventos = d["liveData"]["event"]

    equipos = {c["position"]: c for c in mi["contestant"]}
    home, away = equipos["home"], equipos["away"]
    ft = md["scores"]["ft"]

    filas = []
    for lado, equipo in [("home", home), ("away", away)]:
        m = metricas_equipo(eventos, equipo["id"])
        # posesión por volumen de pases (se completa después con el total)
        m["_pases_brutos"] = m["pases"]
        filas.append({
            "bloque": bloque,
            "jornada": mi["week"],
            "fecha": mi["date"][:10],
            "partido": mi["description"],
            "equipo": equipo["name"],
            "lado": "local" if lado == "home" else "visitante",
            "goles_marcador": ft[lado],
            **m,
        })

    # Posesión % (cuota de pases sobre el total del partido)
    total_pases = sum(f["_pases_brutos"] for f in filas)
    for f in filas:
        f["posesion_pct"] = round(100 * f["_pases_brutos"] / total_pases, 1) if total_pases else 0
        del f["_pases_brutos"]
    return filas

def main():
    todas = []
    for bloque, path in FICHEROS.items():
        print(f"Procesando {bloque}: {path.name}")
        todas.extend(procesar(bloque, path))

    df = pd.DataFrame(todas)
    # Orden de columnas legible
    cols = ["bloque", "jornada", "fecha", "partido", "equipo", "lado",
            "goles_marcador", "posesion_pct", "tiros_totales", "tiros_a_puerta",
            "pases", "pases_completados", "precision_pase_pct",
            "regates", "regates_exitosos", "duelos_aereos", "duelos_aereos_ganados",
            "entradas", "intercepciones", "despejes", "faltas_cometidas",
            "corners", "amarillas", "rojas"]
    df = df[cols]

    salida = OUT / "metricas_equipo.csv"
    # Formato europeo (separador ; y decimal ,) para Power BI en español
    df.to_csv(salida, index=False, sep=";", decimal=",", encoding="utf-8-sig")
    print(f"\nGuardado: {salida}")
    return df

if __name__ == "__main__":
    df = main()
    pd.set_option("display.max_columns", None, "display.width", 200)
    print("\n=== RESULTADO ===")
    print(df.to_string(index=False))
