"""
ETL parte 2 — Análisis del EQUIPO (Arsenal)
============================================
Genera tres tablas para el informe de Power BI:
  1) plantilla_arsenal.csv      -> análisis individual de jugadores
  2) modelo_juego_arsenal.csv   -> indicadores del estilo de juego
  3) once_inicial_arsenal.csv   -> once titular con coordenadas (4-2-3-1)
"""
import json
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "data" / "raw"
OUT = BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)


def enteros(df):
    """Convierte a entero las columnas numéricas cuyos valores son todos enteros."""
    for c in df.columns:
        if pd.api.types.is_numeric_dtype(df[c]):
            s = df[c].dropna()
            if len(s) > 0 and (s == s.round()).all():
                df[c] = df[c].astype("Int64")
    return df


CSV_PLANTILLA = BASE / "data" / "seasonstats_arsenal.csv"   # CSV original de la temporada
POST = RAW / "postpartido_J26_Brentford_Arsenal.json"

# =====================================================================
# 1) PLANTILLA — análisis individual
# =====================================================================
df = pd.read_csv(CSV_PLANTILLA)
num = lambda c: pd.to_numeric(df[c], errors="coerce")
df["Time Played"] = num("Time Played")
jug = df[df["Time Played"].fillna(0) > 0].copy()

# Columnas clave renombradas a español
mapa = {
    "nombre": "jugador", "posicion": "posicion", "dorsal": "dorsal",
    "Appearances": "partidos", "Time Played": "minutos",
    "Goals": "goles", "Goal Assists": "asistencias",
    "Total Shots": "tiros", "Shots On Target ( inc goals )": "tiros_puerta",
    "Key Passes (Attempt Assists)": "pases_clave", "Total Passes": "pases",
    "Successful Dribbles": "regates", "Total Tackles": "entradas",
    "Interceptions": "intercepciones", "Recoveries": "recuperaciones",
    "Total Big Chances Created": "grandes_ocasiones_creadas",
    "Total Touches In Opposition Box": "toques_area_rival",
    "Progressive Carries": "conducciones_progresivas",
}
pl = pd.DataFrame()
for orig, nuevo in mapa.items():
    pl[nuevo] = jug[orig]
for c in pl.columns[3:]:
    pl[c] = pd.to_numeric(pl[c], errors="coerce").fillna(0)

# Goles + asistencias por 90 minutos (para comparar con justicia)
pl["minutos"] = pl["minutos"].astype(int)
pl["GA_por_90"] = ((pl["goles"] + pl["asistencias"]) / pl["minutos"] * 90).round(2)
pl = pl.sort_values("minutos", ascending=False).reset_index(drop=True)

# Texto descriptivo de los titulares / referentes
perfiles = {
    "V. Gyökeres": "Delantero referencia y máximo goleador. Vive en el área: lidera el equipo en remates y toques en zona de finalización.",
    "B. Saka": "Extremo desequilibrante. Combina gol, asistencia y regate; uno de los grandes generadores de ocasiones del equipo.",
    "D. Rice": "Mediocentro todoterreno. El motor del equipo: enorme volumen de recuperaciones, conducciones progresivas y llegada.",
    "M. Ødegaard": "Cerebro creativo. Capitán y principal asistente; organiza el juego entre líneas con pases clave.",
    "Martín Zubimendi": "Pivote posicional. Ancla defensiva del medio: líder en entradas e intercepciones, da equilibrio.",
    "W. Saliba": "Central de salida. Inmenso volumen de pase y solidez defensiva; inicia el juego desde atrás.",
    "Gabriel Magalhães": "Central dominador. Referencia aérea y defensiva, también muy fiable con balón.",
    "J. Timber": "Lateral moderno. Aporta en ataque (asistencias) y es muy activo defensivamente.",
    "P. Hincapié": "Defensa versátil. Fiable en el uno contra uno y en la recuperación.",
    "L. Trossard": "Atacante polivalente. Eficiente de cara a gol y asistencia desde varias posiciones.",
    "N. Madueke": "Extremo vertical. Gran regateador y con muchos toques en el área rival.",
    "E. Eze": "Mediapunta creativo. Desequilibrio, regate y llegada al área.",
}
pl["perfil"] = pl["jugador"].map(perfiles).fillna("Rotación de la plantilla.")

enteros(pl).to_csv(OUT / "plantilla_arsenal.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")

# =====================================================================
# 2) MODELO DE JUEGO — indicadores de estilo (a partir del CSV de equipo)
# =====================================================================
tot = lambda c: pd.to_numeric(df[c], errors="coerce").fillna(0).sum()
total_pases = tot("Total Passes")
estilo = [
    ("Pases totales (temporada)", int(total_pases), "Volumen de juego asociativo del equipo."),
    ("% pases hacia adelante", round(100*tot("Forward Passes")/total_pases, 1), "Verticalidad: cuánto progresa el balón."),
    ("% pases en campo rival", round(100*tot("Successful Passes Opposition Half")/total_pases, 1), "Dominio de territorio."),
    ("Conducciones progresivas", int(tot("Progressive Carries")), "Progresión con balón controlado."),
    ("Recuperaciones", int(tot("Recoveries")), "Capacidad de robar el balón."),
    ("Grandes ocasiones creadas", int(tot("Total Big Chances Created")), "Generación de ocasiones claras."),
    ("Toques en área rival", int(tot("Total Touches In Opposition Box")), "Presencia ofensiva en zona de gol."),
    ("Regates exitosos", int(tot("Successful Dribbles")), "Juego individual para romper líneas."),
]
modelo = pd.DataFrame(estilo, columns=["indicador", "valor", "descripcion"])
enteros(modelo).to_csv(OUT / "modelo_juego_arsenal.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")

# =====================================================================
# 3) ONCE INICIAL — formación 4-2-3-1 con coordenadas para Power BI
# =====================================================================
d = json.load(open(POST, encoding="utf-8"))
ev = d["liveData"]["event"]
ARS = [c["id"] for c in d["matchInfo"]["contestant"] if c["name"] == "Arsenal"][0]
id2name = dict(zip(df["id"].astype(str).str.strip(), df["nombre"]))
setup = [e for e in ev if e["typeId"] == 34 and e["contestantId"] == ARS][0]
q = {x["qualifierId"]: x.get("value") for x in setup["qualifier"]}
ids = [s.strip() for s in q[30].split(",")]
nums = [s.strip() for s in q[59].split(",")]
pos = [s.strip() for s in q[44].split(",")]
titulares = [(id2name.get(i, i), n) for i, n, p in zip(ids, nums, pos) if p != "5"]

# Coordenadas del 4-2-3-1 (x=ancho 0-100, y=profundidad 0-100)
coords = {
    "1": (50, 6, "Portero"), "12": (85, 24, "Lateral derecho"),
    "3": (62, 22, "Central"), "6": (38, 22, "Central"), "5": (15, 24, "Lateral izquierdo"),
    "36": (38, 44, "Pivote"), "41": (62, 44, "Pivote"),
    "20": (85, 68, "Interior derecho"), "10": (50, 66, "Mediapunta"), "19": (15, 68, "Interior izquierdo"),
    "14": (50, 88, "Delantero"),
}
filas = []
for nombre, dorsal in titulares:
    x, y, rol = coords.get(dorsal, (50, 50, "?"))
    filas.append({"dorsal": int(dorsal), "jugador": nombre, "rol": rol, "x": x, "y": y})
once = pd.DataFrame(filas).sort_values("y")
enteros(once).to_csv(OUT / "once_inicial_arsenal.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")

print("Generadas 3 tablas en data/processed/:")
print("  - plantilla_arsenal.csv     (", len(pl), "jugadores )")
print("  - modelo_juego_arsenal.csv  (", len(modelo), "indicadores )")
print("  - once_inicial_arsenal.csv  (", len(once), "titulares )")
