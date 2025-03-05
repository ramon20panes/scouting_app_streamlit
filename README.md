# Scouting App Streamlit

Aplicación web interactiva desarrollada como herramienta de análisis y scouting para direcciones deportivas. Este proyecto nace de la necesidad de centralizar y visualizar datos deportivos de múltiples fuentes en una única plataforma intuitiva y funcional.

La aplicación permite realizar un seguimiento completo del rendimiento del equipo y sus jugadores, facilitando la toma de decisiones tanto en el análisis post-partido como en la identificación de potenciales fichajes. Integra datos de diversas fuentes, incluyendo estadísticas avanzadas, eventos de partidos y métricas de rendimiento.

## Características Principales

- **Análisis Histórico**: 
 Seguimiento detallado de la evolución del equipo durante la temporada actual, presentando métricas clave, rankings y tendencias de rendimiento.

- **Visualizaciones**:
 Muestra tres gráficos relacionados con la evolución en la clasificación, de resultados y el xG.

- **Análisis de Jornada**: 
 Estudio profundo de cada partido con comparativas entre equipos, visualización de eventos clave, mapas de calor y patrones de juego.

- **Perfiles de Jugadores**/**Herramienta de Scouting**: 
Posibles dos nuevas páginas en un futuro.

## Estructura

- **.streamlit**:
    Archivo config.toml con los patrones de toda la aplicación.

- **assets**:
    Escudos equipos LaLiga 24/25, logos SDC y LaLiga, y players (foto jugadores ATM 24/25)

- **common**:
    _init_.py
    pdf_export.py con las funciones para generar informe en pdf
    session.py opciones para el usuario

- **data**:
    api_handlers/football_data_api.py tratamiento de datos con la api
    data_processing/understat_data.py extracción xG de los partidos del Atleti, primero para la evolución temporal, después para cada jornada
    database/database.py tratamiento con la base de datos de las big_5_24_25 de FBREF
    FData/master archivos para mapear id y url y rutas de escudos de equipos, jugadores, y partidos. Actualizar tras jornadas understat y sofascore 
        matches csv y json para redes de pase desde whoscored (actualizar tras jornada)
        stats csv de clasificación y de estadísticas básicas de los partidos del atleti (actualizar tras jornada)
        stats_big5_24_25.db base de datos que se debe actualizar tras cada jornada (Sqlite)
    jornada_data/csv_lectura.py estadísticas de partido y lectura para red de pases
                url_mapeo.py sincronización para elección de jornada
    
- **entorno**

- **Pages**:
    1_Stats 24 25.py tabla métricas más rankings

    2_Visualizaciones_24_25.py Clasificación, timeline y xG durante la liga 24/25

    3_Análisis Jornada.py Selección de jornada para representación de métricas, resultado y escudos, y gráficos de match  momentum, redes de pase, xG y mapa de tiros

- **utils**:
    auth.py login
    cache.py experiencia del usuario
    styles.py css 
    visualization.py funciones hoja 2
    visualization_2.py funciones hoja 3

- **env.example**

- **.gitignore**

- **Aplic_Direcc_Deport.py**

    Streamlit run Aplic_Direcc_Deport.py

- **LICENSE**

- **README.md**

- **requiretments.txt**

## Tecnologías
- Python + Streamlit
- SQLite para almacenamiento
- Análisis de datos con Pandas
- Visualizaciones con Plotly
- Web Scraping ético

## Instalación
1. Clonar repositorio
2. Crear entorno virtual: `python -m venv venv`
3. Instalar dependencias: `pip install -r requirements.txt`
4. Ejecutar: `streamlit run Aplic_Direcc_Deport.py`

## Problemas y retos

1. Agilizar velocidad de representación de datos
2. Mejora de exportación a PDF
3. Escalabilidad

## Licencia
MIT License


## Agradecimientos

[Lucas Bracamonte](https://github.com/lucbra21?tab=repositories)

[Adnaaan433](https://github.com/adnaaan433/Post-Match-Report-2.0)

[Federico Rabanos](https://github.com/federicorabanos)

[Ben Griffish](https://github.com/griffisben/Soccer-Analyses)

[Mckay Johns](https://www.youtube.com/@McKayJohns)

[Oseymour](https://github.com/oseymour/ScraperFC)

[José González](https://www.kaggle.com/code/josegabrielgonzalez/understat-series-xg-rolling-averages)