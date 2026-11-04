# Cine-Match — Recomendador de películas (Streamlit)

Demo web en **Python + Streamlit**: el usuario elige tono, duración y clasificación por edad; la app sugiere una película del catálogo y un snack.

## Requisitos

- Python 3.10 o superior
- Dependencias: `pip install -r requirements.txt`

## Ejecutar la app

```bash
cd recomendador-peliculas-streamlit
python -m streamlit run app.py
```

Abre la URL que muestra la terminal (normalmente `http://localhost:8501`).

## Estructura del proyecto

| Archivo | Uso |
|---------|-----|
| `app.py` | Interfaz y lógica de recomendación |
| `peliculas.json` | Catálogo de películas (editar aquí o en Excel + export) |
| `estilos_app.css` | Colores y diseño de la página |
| `estilos_boleto.css` | Estilo de la tarjeta tipo boleto |
| `requirements.txt` | Librerías necesarias |

## Exportar tablas para Excel (opcional)

```bash
python _export_excel.py
python _export_matriz.py
```

Genera `catalogo_peliculas_excel.xlsx` y `matriz_tono_edad.xlsx`.

## Subir a GitHub

1. Crea un repositorio vacío en GitHub.
2. En esta carpeta (con [Git](https://git-scm.com/) instalado):

```bash
git init
git add .
git commit -m "Initial commit: Cine-Match Streamlit demo"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

3. Sustituye `TU_USUARIO` y `TU_REPO` por los tuyos.

## Notas

- Los pósters usan URLs externas (por ejemplo TMDB); si una imagen no carga, revisa `poster_url` en `peliculas.json`.
- Scripts que empiezan con `_` son herramientas de mantenimiento (exportación); no hace falta ejecutarlos para la demo.
