# Análisis de datos — Arsenal FC | Jornada 26 (Brentford 1-1 Arsenal)

Informe de scouting de un partido de la Premier League 2025/2026 construido a
partir de datos de eventos en formato **Opta / Stats Perform (JSON)**, con un
proceso **ETL en Python** y un informe final de **scouting en Power BI**.

El proyecto cubre la cadena completa: extracción de los eventos del partido,
cálculo de métricas (incluidas varias **avanzadas de elaboración propia**),
generación de visualizaciones (redes de pases, mapas de tiros, mapas defensivos
y mapas de calor) y exportación a CSV/PNG en **formato europeo** para Power BI.

## Objetivo

Analizar el partido **Brentford 1-1 Arsenal (Jornada 26)** en tres bloques, con
foco en el scouting del rival y el rendimiento del Arsenal:

| Bloque              | Partido                       | Resultado |
| ------------------- | ----------------------------- | --------- |
| Prepartido Arsenal  | Arsenal vs Sunderland (J25)   | 3-0       |
| Prepartido rival    | Newcastle vs Brentford (J25)  | 2-3       |
| Postpartido (foco)  | Brentford vs Arsenal (J26)    | 1-1       |

## Estructura del repositorio

```
proyecto_arsenal/
├── run_all.py                 # Script maestro: ejecuta todo el pipeline ETL en orden
├── ETL_Arsenal_J26.ipynb      # Cuaderno con la exploración inicial de los datos
├── scripts/                   # Scripts ETL (un módulo por tipo de salida)
│   ├── etl_partidos.py        # Métricas base por equipo -> metricas_equipo.csv
│   ├── etl_equipo.py          # Plantilla, modelo de juego y once tipo del Arsenal
│   ├── etl_metricas_extra.py  # Añade métricas avanzadas (PPDA, toques área, etc.)
│   ├── etl_portada.py         # KPIs y evolución de puntos para la portada
│   ├── etl_contexto.py        # Clasificación, racha, destacados y últimos 5
│   ├── etl_alineaciones.py    # Alineaciones del J26
│   ├── etl_jugadores_partido.py # Estadísticas por jugador (J25 y J26)
│   ├── etl_red_pases.py       # Redes de pases (PNG)
│   ├── etl_mapa_tiros.py      # Mapas de tiros (PNG)
│   ├── etl_mapa_defensivo.py  # Mapas defensivos (PNG)
│   ├── etl_mapas_calor.py     # Mapas ofensivos y de presión (PNG)
│   ├── etl_comparativas.py    # Comparativas divergentes del postpartido
│   └── etl_transiciones.py    # Métricas de transición y faltas tras pérdida
├── data/
│   ├── raw/                   # JSON originales de los 3 partidos (entrada)
│   ├── source/                # Datos auxiliares (clasificación, temporada)
│   └── processed/             # CSV y PNG generados (salida para Power BI)
├── requirements.txt           # Librerías necesarias
└── README.md
```

## Proceso ETL

1. **Extract** — Lectura de los 3 partidos en formato Opta/Stats Perform (JSON),
   con sus bloques `matchInfo` (equipos, jornada, fecha) y `liveData` (eventos).

2. **Transform** — Cálculo de métricas a partir de los eventos y sus coordenadas:
   - **Métricas de equipo**: posesión, tiros, tiros a puerta, pases y precisión,
     pases en campo rival, pases progresivos, toques en área rival, regates,
     duelos aéreos, entradas, intercepciones, despejes, recuperaciones, faltas,
     córners y tarjetas. Se corrige el doble registro de faltas/córners de Opta.
   - **Métricas por jugador**: goles, asistencias, tiros, pases completados,
     pases clave, regates, toques en área rival y acciones defensivas.
   - **Métricas avanzadas (elaboración propia)**: PPDA (intensidad de presión),
     tiempo de transición tras recuperación, transiciones rápidas, altura de
     recuperación, % de primer pase hacia adelante, altura de las faltas y % de
     faltas cometidas tras pérdida.
   - **Visualizaciones**: redes de pases, mapas de tiros, mapas defensivos y
     mapas de calor (ofensivos y de presión), exportadas como PNG.

3. **Load** — Exportación a `data/processed/` en **formato europeo** (separador
   `;`, decimal `,`, codificación `utf-8-sig`) para que Power BI en español
   interprete correctamente los números.

## Cómo ejecutar

Instalar dependencias y lanzar el pipeline completo:

```bash
pip install -r requirements.txt
python run_all.py
```

Esto regenera todos los CSV y PNG en `data/processed/`. También se puede
ejecutar cada script por separado, por ejemplo:

```bash
python scripts/etl_transiciones.py
```

## Notas metodológicas

Algunas métricas **no vienen precalculadas** en los datos Opta, sino que son de
elaboración propia con umbrales definidos en el proyecto:

- **PPDA**: pases del rival en su zona de salida dividido entre las acciones
  defensivas propias (entradas, intercepciones, faltas) en campo rival. Más baja
  = presión más intensa.
- **Pase progresivo**: pase completado que avanza al menos 15 unidades y termina
  en campo rival.
- **Transición**: se considera que un equipo transita cuando, tras recuperar el
  balón, llega a campo rival (x > 66) en 30 segundos o menos. "Rápida" = < 6 s.
- **Falta tras pérdida**: falta cometida en los 15 segundos posteriores a perder
  el balón (indicador de falta táctica para cortar transiciones).

Los datos de cada partido reflejan ese encuentro concreto (muestra de un
partido), por lo que se interpretan como tendencias, no como valores absolutos.

## Herramientas

Python · pandas · matplotlib · scipy · Jupyter · Power BI · Git/GitHub
