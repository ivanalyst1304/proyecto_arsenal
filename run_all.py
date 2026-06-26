"""
run_all.py — PIPELINE COMPLETO DEL PROYECTO
============================================
Ejecuta todos los scripts ETL en el orden correcto para regenerar, desde los
JSON originales (data/raw/), todos los CSV y PNG que alimentan el informe de
Power BI (data/processed/).

Uso:
    python run_all.py

Requisitos: pip install -r requirements.txt

El orden importa: primero las métricas base (metricas_equipo.csv) y luego los
scripts que las amplían (metricas_extra) o derivan de ellas (comparativas).
"""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SCRIPTS = BASE / "scripts"

# Orden de ejecución del pipeline
PASOS = [
    # 1) Métricas base de equipo y datos de partido
    "etl_partidos.py",          # metricas_equipo.csv (métricas base por equipo)
    "etl_equipo.py",            # plantilla, modelo de juego, once tipo
    "etl_metricas_extra.py",    # añade métricas avanzadas a metricas_equipo (PPDA, etc.)
    # 2) Contexto y portada
    "etl_portada.py",           # KPIs y evolución para la portada
    "etl_contexto.py",          # clasificación, racha, destacados, últimos 5
    "etl_alineaciones.py",      # alineaciones del J26
    # 3) Datos por jugador
    "etl_jugadores_partido.py", # stats por jugador (J25 y J26)
    # 4) Visualizaciones (PNG)
    "etl_red_pases.py",         # redes de pases
    "etl_mapa_tiros.py",        # mapas de tiros
    "etl_mapa_defensivo.py",    # mapas defensivos
    "etl_mapas_calor.py",       # mapas ofensivos y de presión
    # 5) Métricas derivadas y avanzadas
    "etl_comparativas.py",      # comparativas divergentes del postpartido
    "etl_transiciones.py",      # métricas de transición y faltas
]


def main():
    print("=" * 55)
    print("  PIPELINE ETL — Proyecto Arsenal J26")
    print("=" * 55)
    fallos = []
    for i, script in enumerate(PASOS, 1):
        ruta = SCRIPTS / script
        print(f"\n[{i}/{len(PASOS)}] Ejecutando {script} ...")
        if not ruta.exists():
            print(f"  AVISO: no se encontró {script}, se omite.")
            fallos.append(script)
            continue
        res = subprocess.run([sys.executable, str(ruta)], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  OK")
        else:
            print(f"  ERROR en {script}:")
            print(res.stderr[-500:])
            fallos.append(script)

    print("\n" + "=" * 55)
    if fallos:
        print(f"  Pipeline terminado con avisos en: {', '.join(fallos)}")
    else:
        print("  Pipeline completado correctamente. Revisa data/processed/")
    print("=" * 55)


if __name__ == "__main__":
    main()
