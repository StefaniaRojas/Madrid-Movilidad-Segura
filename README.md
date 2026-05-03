# Madrid Segura

Madrid Segura es un tablero interactivo desarrollado en Streamlit para analizar la lesividad en accidentes de tráfico en Madrid.

La aplicación permite explorar la distribución de personas implicadas en accidentes según nivel de lesividad, tipo de accidente, tipo de vehículo, perfil de las personas implicadas, patrones temporales, distribución espacial y exposición vial a partir de datos de aforos permanentes.

## Objetivo

El objetivo del proyecto es apoyar el análisis descriptivo de la seguridad vial en Madrid mediante una herramienta visual e interactiva que facilite la identificación de patrones asociados a la lesividad de las personas implicadas en accidentes de tráfico.

## Funcionalidades principales

- Resumen general de personas implicadas, lesiones leves y casos graves/fallecidos.
- Distribución de la lesividad por año, distrito, tipo de accidente y tipo de vehículo.
- Análisis de perfiles vulnerables según edad, sexo, tipo de persona y alcohol.
- Visualización de patrones temporales por hora y día de la semana.
- Mapa interactivo de accidentes según nivel de lesividad.
- Comparación descriptiva entre flujo vehicular y lesividad usando aforos permanentes.
- Indicador exploratorio de prioridad distrital basado en volumen y gravedad.

## Fuente de datos

Los datos utilizados proceden del Portal de Datos Abiertos del Ayuntamiento de Madrid.

El tablero trabaja principalmente con:

- Registros de accidentes de tráfico.
- Datos de aforos permanentes de tráfico.
- Variables asociadas a fecha, hora, distrito, tipo de accidente, tipo de vehículo, tipo de persona y nivel de lesividad.

## Estructura del repositorio

```text
.
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
├── assets/
│   ├── escudo_madrid.png
│   └── escudo_madrid1.png
└── data/
    ├── accidentes.csv
    └── flujo.csv