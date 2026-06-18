# Análisis de datos — Arsenal FC | Jornada 26 (Brentford 1-1 Arsenal)

Informe de análisis de datos sobre el Arsenal FC en la Premier League 2025/2026,
a partir de datos de eventos en formato Opta (JSON). Incluye un proceso **ETL en
Python** y un informe visual en **Power BI** que analiza tanto al equipo como un
partido concreto.

## Objetivo

El informe se estructura en dos planos:

**A) Análisis del equipo (Arsenal)**
- Análisis individual de la plantilla (estadísticas características por jugador).
- Modelo de juego basado en indicadores de estilo.
- Representación del sistema (formación 4-2-3-1).

**B) Análisis del partido — Brentford vs Arsenal (J26, 1-1)**

| Bloque | Partido | Resultado |
|---|---|---|
| Prepartido Arsenal | Arsenal vs Sunderland (J25) | 3-0 |
| Prepartido rival | Newcastle vs Brentford (J25) | 2-3 |
| Postpartido (foco) | Brentford vs Arsenal (J26) | 1-1 |

## Estructura del repositorio

```
proyecto_arsenal/
├── ETL_Arsenal_J26.ipynb        # Cuaderno con la ETL paso a paso (partidos)
├── scripts/
│   ├── etl_partidos.py          # ETL de métricas de equipo (3 partidos)
│   └── etl_equipo.py            # ETL del equipo: plantilla, modelo y formación
├── data/
│   ├── seasonstats_arsenal.csv  # Stats de temporada por jugador (entrada)
│   ├── raw/                     # JSON originales de los 3 partidos (entrada)
│   └── processed/               # Salidas para Power BI (CSV + imagen del campo)
├── requirements.txt
└── README.md
```

## Tablas generadas (salida para Power BI)

- `metricas_equipo.csv` — métricas por equipo de los 3 partidos.
- `plantilla_arsenal.csv` — análisis individual de jugadores.
- `modelo_juego_arsenal.csv` — indicadores del estilo de juego.
- `once_inicial_arsenal.csv` — once titular con coordenadas (4-2-3-1).
- `campo_futbol.png` — imagen de campo para el diagrama de formación.

## Proceso ETL

1. **Extract**: lectura de los partidos (Opta JSON) y del CSV de temporada.
2. **Transform**: cálculo de métricas de equipo, perfiles de jugador, indicadores
   de estilo y extracción de la formación. Corrige el doble registro de
   faltas/córners de Opta.
3. **Load**: exportación a CSV (y PNG) en `data/processed/` para Power BI.

## Cómo ejecutar

```bash
pip install -r requirements.txt
python scripts/etl_partidos.py
python scripts/etl_equipo.py
```

O abrir `ETL_Arsenal_J26.ipynb` en Jupyter y ejecutar las celdas en orden.

## Herramientas

Python · pandas · matplotlib · Jupyter · Power BI · Git/GitHub
