# =============================================================================
# RECOMENDADOR DE PELÍCULAS POR ESTADO DE ÁNIMO Y SNACKS
# Demo educativa — ejecutar con: streamlit run app.py
# =============================================================================

import html
import json
import os
import random
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

CARPETA_APP = Path(__file__).parent
# CSS público en GitHub (Streamlit Cloud a veces no aplica <style> inline en markdown).
CSS_APP_URL = (
    "https://raw.githubusercontent.com/caracolgris/cine-match/main/estilos_app.css"
)


def cargar_peliculas():
    """Catálogo en peliculas.json (fácil de editar y subir a GitHub)."""
    ruta = CARPETA_APP / "peliculas.json"
    return json.loads(ruta.read_text(encoding="utf-8"))


PELICULAS = cargar_peliculas()


st.set_page_config(
    page_title="El Cine-Match",
    page_icon="🎬",
    layout="wide",
)


def aplicar_estilos_cine():
    """estilos_app.css: enlace en Streamlit Cloud; inline en tu PC."""
    st.markdown(
        f'<link rel="stylesheet" href="{CSS_APP_URL}">',
        unsafe_allow_html=True,
    )
    if not os.getenv("GITHUB_REPOSITORY"):
        css = (CARPETA_APP / "estilos_app.css").read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


aplicar_estilos_cine()


def calificacion_palomitas(titulo_es):
    """
    Medidor decorativo 🍿/🎟️ (3–5 palomitas) sin modificar datos del catálogo.
    Mismo título = misma calificación siempre.
    """
    nivel = 3 + (sum(ord(c) for c in titulo_es) % 3)
    return "🍿" * nivel + "🎟️" * (5 - nivel)


def estilos_boleto_html():
    """CSS del iframe del boleto (estilos_boleto.css)."""
    css = (CARPETA_APP / "estilos_boleto.css").read_text(encoding="utf-8")
    return f"<style>{css}</style>"


# -----------------------------------------------------------------------------
# OPCIONES DE LOS FILTROS (deben coincidir con los valores dentro de PELICULAS)
# -----------------------------------------------------------------------------
OPCIONES_TONO = ["Acción", "Biografías", "Algo de romance", "Algo de suspenso criminal", "Amistad", "Animación familiar", "Cine de duelo", "Cine de injusticia", "Cine de venganza", "Cine político", "Cine reconfortante", "Ciencia ficción", "Comedia", "Comunidad", "Cuenta regresiva", "Drama", "Giros narrativos", "Horror corporal", "Musical", "Persecuciones", "Revelaciones", "Suspenso", "Suspenso psicológico", "Terror", "Tragedia"]
OPCIONES_TIEMPO = ["Menos de 90 min", "90-120 min", "120-150 min", "Más de 150 minutos"]
OPCIONES_CLASIFICACION = ["Para todo público", "12 años en adelante", "18 años en adelante"]


def filtrar_peliculas(tono, tiempo, clasificacion):
    """
    Devuelve una lista de películas que cumplen los tres criterios elegidos.
    Si ninguna coincide exactamente, devolvemos las que coinciden en al menos
    tono Y clasificación (relajamos solo el tiempo).
    """
    coincidencias_exactas = []
    for pelicula in PELICULAS:
        if (
            tono in pelicula["tono"]
            and pelicula["tiempo"] == tiempo
            and pelicula["clasificacion_edad"] == clasificacion
        ):
            coincidencias_exactas.append(pelicula)

    if coincidencias_exactas:
        return coincidencias_exactas

    # Plan B: misma edad y ánimo, cualquier duración.
    coincidencias_parciales = []
    for pelicula in PELICULAS:
        if (
            tono in pelicula["tono"]
            and pelicula["clasificacion_edad"] == clasificacion
        ):
            coincidencias_parciales.append(pelicula)

    return coincidencias_parciales


def elegir_otra_pelicula(pool, actual):
    """Elige otra película del mismo pool; evita repetir si hay más de una."""
    if not pool:
        return None
    if not actual:
        return random.choice(pool)
    otras = [p for p in pool if p["titulo_es"] != actual["titulo_es"]]
    return random.choice(otras if otras else pool)


def ordenar_catalogo(peliculas, criterio):
    """Devuelve una copia ordenada del catálogo según el criterio elegido."""
    lista = list(peliculas)
    if criterio == "Nombre (A → Z)":
        lista.sort(key=lambda p: p["titulo_es"].casefold())
    elif criterio == "Clasificación por edad":
        orden_edad = {c: i for i, c in enumerate(OPCIONES_CLASIFICACION)}
        lista.sort(
            key=lambda p: (
                orden_edad.get(p["clasificacion_edad"], 99),
                p["titulo_es"].casefold(),
            )
        )
    elif criterio == "Duración (menor a mayor)":
        orden_tiempo = {t: i for i, t in enumerate(OPCIONES_TIEMPO)}
        lista.sort(
            key=lambda p: (
                orden_tiempo.get(p["tiempo"], 99),
                p["titulo_es"].casefold(),
            )
        )
    return lista


def mostrar_resumen_coincidencia(pelicula, tono_elegido=None):
    """
    Muestra chips de tono (el buscado + otros de la película), duración y edad
    fuera del boleto, antes de la tarjeta principal.
    """
    tonos_pelicula = pelicula.get("tono", [])
    otros_tonos = [
        t for t in tonos_pelicula if not tono_elegido or t != tono_elegido
    ]

    chips = []
    if tono_elegido:
        chips.append(
            f'<span class="chip chip-tono-activo">✨ Tono que buscaste: '
            f"{html.escape(tono_elegido)}</span>"
        )
        titulo_bloque = "🎭 Encaje con tu búsqueda"
    else:
        titulo_bloque = "🎭 Tonos de esta película"

    if not tono_elegido:
        for t in tonos_pelicula:
            chips.append(
                f'<span class="chip chip-tono">{html.escape(t)}</span>'
            )
    else:
        for t in otros_tonos:
            chips.append(
                f'<span class="chip chip-tono">+ {html.escape(t)}</span>'
            )

    chips.append(
        f'<span class="chip chip-tiempo">⏱ {html.escape(pelicula["tiempo"])}</span>'
    )
    chips.append(
        f'<span class="chip chip-edad">👥 {html.escape(pelicula["clasificacion_edad"])}</span>'
    )

    bloque = f"""
    <div class="resumen-match">
        <p class="resumen-match-titulo">{titulo_bloque}</p>
        <div class="resumen-chips">{"".join(chips)}</div>
    </div>
    """
    st.markdown(bloque, unsafe_allow_html=True)


def mostrar_tarjeta_pelicula(pelicula):
    """Muestra título, descripción, póster, director y hasta 3 actores dentro del boleto."""
    titulo_completo = (
        f"{pelicula['titulo_es']} ({pelicula['titulo_original']} — "
        f"{pelicula['idioma_original']})"
    )
    palomitas = calificacion_palomitas(pelicula["titulo_es"])
    actores_texto = ", ".join(pelicula["actores"][:3])

    url_poster = (pelicula.get("poster_url") or "").strip()
    poster_pendiente = not url_poster
    if poster_pendiente:
        url_poster = (
            "https://placehold.co/400x600/FFF0F5/FF8787?text=Sin+p%C3%B3ster"
        )

    titulo_esc = html.escape(titulo_completo)
    desc_esc = html.escape(pelicula["descripcion"])
    director_esc = html.escape(pelicula["director"])
    actores_esc = html.escape(actores_texto)
    snack_esc = html.escape(pelicula["snack_sugerido"])
    url_esc = html.escape(url_poster, quote=True)

    aviso_poster = (
        '<p class="poster-aviso">Póster pendiente en el catálogo.</p>'
        if poster_pendiente
        else ""
    )

    # components.html evita que Streamlit corte el HTML y lo muestre como texto plano.
    tarjeta_html = f"""
    {estilos_boleto_html()}
    <div class="boleto-cine">
        <p class="boleto-titulo">🎬 {titulo_esc}</p>
        <p class="calificacion-palomitas"><strong>Cine-Match:</strong> {palomitas}</p>
        <p class="boleto-sinopsis">{desc_esc}</p>
        <div class="boleto-cuerpo">
            <div class="boleto-poster">
                <img src="{url_esc}" alt="Póster" loading="lazy" />
                {aviso_poster}
            </div>
            <div class="boleto-datos">
                <p class="dato-pelicula"><strong>Director:</strong> {director_esc}</p>
                <p class="dato-pelicula"><strong>Actores principales:</strong> {actores_esc}</p>
                <span class="snack-tag">🍿 Snack sugerido: {snack_esc}</span>
            </div>
        </div>
    </div>
    """
    components.html(tarjeta_html, height=520, scrolling=False)


def mostrar_catalogo_completo():
    """Lista todas las películas del catálogo en tarjetas expandibles."""
    st.markdown("### 🎟️ Catálogo completo")
    st.caption("Explora todas las películas disponibles en la demo.")

    orden_catalogo = st.selectbox(
        "Ordenar catálogo por",
        options=[
            "Nombre (A → Z)",
            "Clasificación por edad",
            "Duración (menor a mayor)",
        ],
        help="Cambia el orden de la lista sin modificar el catálogo.",
    )
    peliculas_ordenadas = ordenar_catalogo(PELICULAS, orden_catalogo)

    for pelicula in peliculas_ordenadas:
        titulo_corto = f"🍿 {pelicula['titulo_es']} ({pelicula['titulo_original']})"
        with st.expander(titulo_corto):
            mostrar_resumen_coincidencia(pelicula)
            mostrar_tarjeta_pelicula(pelicula)


# =============================================================================
# INTERFAZ PRINCIPAL
# =============================================================================

# Menú arriba a la derecha (columna más ancha); título centrado en toda la pantalla abajo.
_fila_vacia, _fila_menu = st.columns([3, 2], vertical_alignment="top")
with _fila_menu:
    pagina_actual = st.selectbox(
        "Menú",
        options=["Nuestra recomendación", "Catálogo de películas"],
        label_visibility="collapsed",
        key="menu_pagina_cinematch",
    )

st.markdown(
    """
    <div class="hero-centrado-pantalla">
    <p class="encabezado-kawaii" style="
        font-size: 2.75rem !important;
        color: #FF6B6B !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
        margin: 0.25rem auto 0.35rem auto !important;
        text-align: center !important;
    ">🎬✨ El Cine-Match:<br>Película y snack para tu noche 🍿💖</p>
    <p class="subtitulo-bienvenida">
    <strong>¡Hola!</strong> Elige el tono de la película, cuánto tiempo tienes y para quién es la
    función. Te sugeriremos una película de nuestro catálogo y un snack que combine con la experiencia.
    </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="espacio-despues-hero"></div>', unsafe_allow_html=True)

 
# -----------------------------------------------------------------------------
# BARRA LATERAL IZQUIERDA — preferencias del usuario
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("🎬 ¡Arma tu noche de cine!")
    st.caption("Tres pasos: tono, tiempo y edad. Luego busca tu match.")

    tono = st.selectbox(
        "Tono de la película",
        options=OPCIONES_TONO,
        help="Elige el tono principal que transmite la película: cómo te hace sentir mientras la ves o al terminarla.",
    )

    tiempo_disponible = st.selectbox(
        "Tiempo disponible",
        options=OPCIONES_TIEMPO,
        help="¿Cuánto tiempo tienes para ver la película?",
    )

    clasificacion_edad = st.selectbox(
        "Clasificación según edad",
        options=OPCIONES_CLASIFICACION,
        help="Indica para qué edad es apta la película según su contenido",
    )

    st.divider()
    buscar = st.button(
        "🎟️ ¡Encuentra mi película ideal!",
        type="primary",
        use_container_width=True,
    )


# -----------------------------------------------------------------------------
# CONTENIDO CENTRAL — según la página del menú desplegable
# -----------------------------------------------------------------------------
st.markdown('<div class="bloque-contenido-app">', unsafe_allow_html=True)

if pagina_actual == "Catálogo de películas":
    mostrar_catalogo_completo()
else:
    st.markdown("### 🎟️ Tu función de esta noche")
    st.caption(
        "Usa la barra lateral, elige tus opciones y pulsa **🎟️ ¡Encuentra mi película ideal!**"
    )

    if buscar:
        resultados = filtrar_peliculas(
            tono, tiempo_disponible, clasificacion_edad
        )
        st.session_state.pool_recomendacion = resultados
        st.session_state.pelicula_recomendada = (
            random.choice(resultados) if resultados else None
        )

    pelicula_actual = st.session_state.get("pelicula_recomendada")

    if pelicula_actual:
        st.markdown(
            '<div class="caja-exito-turquesa">'
            "✨ ¡Encontramos una película para ti! Disfruta tu función 🍿"
            "</div>",
            unsafe_allow_html=True,
        )
        mostrar_resumen_coincidencia(pelicula_actual, tono_elegido=tono)
        mostrar_tarjeta_pelicula(pelicula_actual)
        pool = st.session_state.get("pool_recomendacion", [])
        if len(pool) > 1:
            st.caption(
                f"Hay **{len(pool)}** películas con tus filtros. "
                "Pulsa el botón de abajo para ver otra."
            )
            if st.button(
                "🔄 Otra película, por favor",
                help="Muestra otra opción con los mismos filtros de la barra lateral.",
            ):
                st.session_state.pelicula_recomendada = elegir_otra_pelicula(
                    pool, pelicula_actual
                )
                st.rerun()
        else:
            st.caption("Solo hay una película con esta combinación de filtros.")
    elif buscar:
        st.warning(
            "No hay coincidencias con esos filtros. Prueba otra combinación "
            "o visita el **Catálogo de películas** en el menú de arriba a la derecha."
        )
    else:
        st.markdown(
            """
            <div class="caja-configura">
                👈 Configura el tono, tiempo y clasificación en la barra lateral
                y pulsa <strong>🎟️ ¡Encuentra mi película ideal!</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("</div>", unsafe_allow_html=True)
