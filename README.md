# Análisis de datos — Arsenal FC | Jornada 26 (Brentford 1-1 Arsenal)

Proyecto de análisis de un partido de la Premier League 2025/2026 a partir de
datos de eventos en formato Opta (JSON), con un proceso **ETL en Python** y
visualización final en **Power BI**.

## Objetivo

Analizar el partido **Brentford vs Arsenal (Jornada 26, 1-1)** mediante tres bloques:

| Bloque | Partido | Resultado |
|---|---|---|
| Prepartido Arsenal | Arsenal vs Sunderland (J25) | 3-0 |
| Prepartido rival | Newcastle vs Brentford (J25) | 2-3 |
| Postpartido (foco) | Brentford vs Arsenal (J26) | 1-1 |

## Estructura del repositorio

```
proyecto_arsenal/
├── ETL_Arsenal_J26.ipynb     # Cuaderno con la ETL paso a paso
├── scripts/
│   └── etl_partidos.py       # Script de la ETL (versión automatizable)
├── data/
│   ├── raw/                  # JSON originales (entrada)
│   └── processed/            # CSV generado (salida para Power BI)
├── requirements.txt          # Librerías necesarias
└── README.md
```

## Proceso ETL

1. **Extract**: lectura de los 3 partidos en formato Opta/Stats Perform (JSON).
2. **Transform**: cálculo de métricas por equipo (posesión, tiros, tiros a puerta,
   pases y precisión, regates, duelos aéreos, entradas, intercepciones, despejes,
   faltas, córners y tarjetas). Corrige el doble registro de faltas/córners de Opta.
3. **Load**: exportación a `data/processed/metricas_equipo.csv` para Power BI.

## Cómo ejecutar

```bash
pip install -r requirements.txt
python scripts/etl_partidos.py
```

O abrir `ETL_Arsenal_J26.ipynb` en Jupyter y ejecutar las celdas en orden.

## Herramientas

Python · pandas · Jupyter · Power BI · Git/GitHub
