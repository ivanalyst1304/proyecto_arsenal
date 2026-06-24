"""
ETL parte 2 — Análisis del EQUIPO (Arsenal)
============================================
Genera tres tablas para el informe de Power BI:
  1) plantilla_arsenal.csv      -> análisis individual de jugadores
  2) modelo_juego_arsenal.csv   -> indicadores del estilo de juego
  3) once_inicial_arsenal.csv   -> once titular con coordenadas (4-2-3-1)
"""
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
ok = tot("Total Successful Passes ( Excl Crosses & Corners ) ")
ko = tot("Total Unsuccessful Passes ( Excl Crosses & Corners )")
estilo = [
    ("Precisión de pase (%)", round(100 * ok / (ok + ko), 1), "Fiabilidad en la circulación del balón."),
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
# =====================================================================
# 3) ONCE TIPO — jugadores más utilizados (por minutos) en sistema 4-2-3-1
# =====================================================================
# El CSV solo trae posición general (Goalkeeper/Defender/Midfielder/Forward),
# así que: (a) seleccionamos los más usados por minutos en cada línea y
# (b) los colocamos en los huecos del 4-2-3-1 según su rol real conocido.
df["min"] = pd.to_numeric(df["Time Played"], errors="coerce").fillna(0)
activos = df[df["min"] > 0]

def top_min(rol, n):
    return activos[activos["posicion"] == rol].nlargest(n, "min")["nombre"].tolist()

gk = top_min("Goalkeeper", 1)
defensas = top_min("Defender", 4)
medios = top_min("Midfielder", 3)
delanteros = top_min("Forward", 3)

# Colocación en el 4-2-3-1 (x=ancho 0-100, y=profundidad 0-100).
# Asignación por rol real conocido de cada jugador seleccionado.
slots = {
    gk[0]:        (50, 6,  "Portero"),
    defensas[3]:  (15, 24, "Lateral izquierdo"),   # Hincapié
    defensas[0]:  (38, 22, "Central"),             # Gabriel
    defensas[1]:  (62, 22, "Central"),             # Saliba
    defensas[2]:  (85, 24, "Lateral derecho"),     # Timber
    medios[1]:    (38, 44, "Pivote"),              # Zubimendi
    medios[0]:    (62, 44, "Pivote"),              # Rice
    delanteros[2]:(15, 68, "Extremo izquierdo"),   # Trossard
    medios[2]:    (50, 66, "Mediapunta"),          # Eze
    delanteros[1]:(85, 68, "Extremo derecho"),     # Saka
    delanteros[0]:(50, 88, "Delantero"),           # Gyökeres
}
dorsal_map = dict(zip(df["nombre"], df["dorsal"]))
filas = []
for nombre, (x, y, rol) in slots.items():
    filas.append({"dorsal": dorsal_map.get(nombre, 0), "jugador": nombre,
                  "rol": rol, "x": x, "y": y, "minutos": int(activos[activos["nombre"] == nombre]["min"].iloc[0])})
once = pd.DataFrame(filas).sort_values("y")
enteros(once).to_csv(OUT / "once_inicial_arsenal.csv", index=False, sep=";", decimal=",", encoding="utf-8-sig")

print("Generadas 3 tablas en data/processed/:")
print("  - plantilla_arsenal.csv     (", len(pl), "jugadores )")
print("  - modelo_juego_arsenal.csv  (", len(modelo), "indicadores )")
print("  - once_inicial_arsenal.csv  (", len(once), "titulares )")
