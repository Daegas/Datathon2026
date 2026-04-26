# Datathon2026

Proyecto del Datathon Tec Monterrey.

## Nota inicial

- Después de hacer `git clone`, actualiza el `PATH` en el archivo `.env` según tu entorno local.

## Estructura de directorios

- `bot/`: aplicación principal del bot, lógica de predicción y estilos.
- `data/`: contenido confidencial (sin detalle en este documento).
- `notebooks/`: análisis exploratorio y notebooks de trabajo.
- `Obs-Datathon26/`: documentación en [Obsidian](https://obsidian.md/)
- `datathon26/`: entorno virtual de Python del proyecto.

## Objetivo de cada carpeta

- `bot/`
	- Código ejecutable del bot.
	- Scripts como `app.py` y `predictor.py`.
	- Recursos de interfaz (por ejemplo, `styles.css`).

- `data/`
	- Carpeta reservada. Su contenido no se documenta aquí por confidencialidad.

- `notebooks/`
	- Notebooks de exploración de datos y pruebas analíticas.
	- Archivos de trabajo para experimentación y validación.

- `Obs-Datathon26/`
	- `chats/` vienen algunos chats con LLMs usados para la ejecución del proyecto
	- el resto de los archivos es la presentación con hallazgos, imágenes, etc

- `datathon26/`
	- Entorno virtual local con dependencias de Python.
	- Incluye binarios y paquetes instalados para ejecutar el proyecto.

## Librerias utilizadas

Dependencias detectadas por uso de `import` en `bot/` y `notebooks/`:

- `numpy`
- `pandas`
- `scikit-learn`
- `shiny`
- `python-dotenv`
- `matplotlib`
- `seaborn`
- `nltk`
- `sentence-transformers`
- `wordcloud`
- `xgboost`

Tambien se usan modulos de la libreria estandar de Python como `os`, `re`, `math` y `pathlib`.

### Modulos locales

- `predictor` (usado por `bot/app.py`)
- `manual_stopwords` (usado en notebooks)


