# Análisis de datos — Arsenal FC | Premier League 2025/2026

Informe de análisis de datos sobre el Arsenal FC a partir de datos de eventos en
formato Opta (JSON). Incluye un proceso **ETL en Python** y un informe visual en
**Power BI** que analiza tanto al equipo como un partido de referencia.

## Objetivo

**A) Análisis del equipo (Arsenal)**
- Resumen de temporada y evolución de puntos.
- Análisis individual de la plantilla.
- Modelo de juego y sistema (4-2-3-1).

**B) Análisis del partido — Brentford vs Arsenal (J26, 1-1)**

| Bloque | Partido | Resultado |
|---|---|---|
| Prepartido Arsenal | Arsenal vs Sunderland (J25) | 3-0 |
| Prepartido rival | Newcastle vs Brentford (J25) | 2-3 |
| Postpartido (foco) | Brentford vs Arsenal (J26) | 1-1 |

## Estructura del repositorio

```
proyecto_arsenal/
├── ETL_Arsenal_J26.ipynb          # Cuaderno con la ETL paso a paso (partidos)
├── scripts/
│   ├── etl_partidos.py            # Métricas de equipo de los 3 partidos
│   ├── etl_equipo.py              # Plantilla, modelo de juego y formación
│   └── etl_portada.py             # Resumen de temporada y puntos por jornada
├── data/
│   ├── seasonstats_arsenal.csv    # Stats de temporada por jugador (entrada)
│   ├── source/
│   │   └── matches.json           # Todos los partidos de la liga (entrada)
│   ├── raw/                       # JSON de los 3 partidos (entrada)
│   └── processed/                 # Salidas para Power BI (CSV, tema e imagen)
├── requirements.txt
└── README.md
```

## Salidas para Power BI (data/processed/)

- `metricas_equipo.csv` — métricas por equipo de los 3 partidos.
- `plantilla_arsenal.csv` — análisis individual de jugadores.
- `modelo_juego_arsenal.csv` — indicadores del estilo de juego.
- `once_inicial_arsenal.csv` — once titular con coordenadas (4-2-3-1).
- `resumen_temporada_arsenal.csv` — posición, puntos, V/E/D, goles.
- `puntos_por_jornada.csv` — evolución de puntos del Arsenal.
- `campo_futbol.png` — imagen de campo para el diagrama de formación.
- `tema_arsenal.json` — tema oscuro de Power BI (paleta Arsenal).

Nota: los CSV se generan en formato europeo (separador `;`, decimal `,`) para
Power BI configurado en español.

## Cómo ejecutar

```bash
pip install -r requirements.txt
python scripts/etl_partidos.py
python scripts/etl_equipo.py
python scripts/etl_portada.py
```

## Herramientas

Python · pandas · matplotlib · Jupyter · Power BI · Git/GitHub
