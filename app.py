from pathlib import Path
import base64

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
import folium
from folium.plugins import Fullscreen, MarkerCluster
from streamlit_folium import st_folium


# ============================================================
# RUTAS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

LOGO_PAGE_PATH = ASSETS_DIR / "escudo_madrid.png"
LOGO_TAB_PATH = ASSETS_DIR / "escudo_madrid1.png"
LOADING_GIF_PATH = ASSETS_DIR / "cargando.gif"


# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================

# Para la pestaña del navegador se usa primero escudo_madrid1.png.
# Si no existe, usa escudo_madrid.png. Si tampoco existe, usa el emoji.
if LOGO_TAB_PATH.exists():
    page_icon = str(LOGO_TAB_PATH)
elif LOGO_PAGE_PATH.exists():
    page_icon = str(LOGO_PAGE_PATH)
else:
    page_icon = "🚗"

st.set_page_config(
    page_title="Madrid Segura",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONSTANTES
# ============================================================

COLOR_LESIVIDAD = {
    "Sin asistencia sanitaria": "#2E86C1",
    "Leve": "#F39C12",
    "Grave/Fallecido": "#922B21",
    "Sin dato": "#95A5A6",
}

ORDEN_LESIVIDAD = [
    "Sin asistencia sanitaria",
    "Leve",
    "Grave/Fallecido",
]

ORDEN_LESIVIDAD_RADIO = [
    "Grave/Fallecido",
    "Leve",
    "Sin asistencia sanitaria",
]

ORDEN_DIAS = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
]

MESES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}

ESCALA_RIESGO = [
    [0.00, "#FCD34D"],
    [0.35, "#FB923C"],
    [0.70, "#DC2626"],
    [1.00, "#7F1D1D"],
]

NOMBRES_VARIABLES = {
    "accidente_cat": "Tipo de accidente",
    "tipo_accidente": "Tipo de accidente",
    "vehiculo_cat": "Tipo de vehículo",
    "tipo_vehiculo": "Tipo de vehículo",
    "persona_cat": "Tipo de persona",
    "tipo_persona": "Tipo de persona",
    "edad_cat": "Rango de edad",
    "rango_edad": "Rango de edad",
    "sexo": "Sexo",
    "positiva_alcohol": "Alcohol",
    "meteo_cat": "Estado meteorológico",
    "estado_meteorológico": "Estado meteorológico",
    "estado_meteorologico": "Estado meteorológico",
    "distrito": "Distrito",
    "hora": "Hora",
    "dia_semana": "Día de la semana",
    "lesividad_cat": "Lesividad",
    "lesividad": "Lesividad",
}


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 8.2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    h1, h2, h3, h4 {
        color: #16324F;
        font-weight: 700;
    }

    .fixed-header {
        position: fixed;
        top: 2.75rem;
        left: 0;
        right: 0;
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 1.4rem;
        background: rgba(248, 250, 252, 0.98);
        backdrop-filter: blur(8px);
        border-bottom: 1px solid #D9E2EC;
        padding: 0.55rem 2.1rem 0.55rem 5.4rem;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05);
        min-height: 92px;
    }

    .header-logo-box {
        width: 115px;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-shrink: 0;
    }

    .header-logo {
        max-height: 82px;
        max-width: 105px;
        object-fit: contain;
    }

    .header-title-box {
        flex: 1;
        min-width: 0;
    }

    .header-title {
        font-size: 2.15rem;
        font-weight: 800;
        color: #1E293B;
        line-height: 1.05;
    }

    .metric-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 0.95rem 1rem;
        box-shadow: 0px 4px 14px rgba(15, 23, 42, 0.04);
        min-height: 108px;
    }

    .metric-label {
        font-size: 0.95rem;
        color: #334155;
        margin-bottom: 0.4rem;
        font-weight: 600;
    }

    .metric-value {
        font-size: 2.15rem;
        color: #1E293B;
        font-weight: 750;
        line-height: 1.1;
        word-break: break-word;
    }

    .metric-value-small {
        font-size: 1.35rem;
        color: #1E293B;
        font-weight: 750;
        line-height: 1.2;
        word-break: break-word;
    }

    .section-card {
        background-color: white;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1rem 1.2rem;
        box-shadow: 0px 4px 14px rgba(15, 23, 42, 0.04);
        margin-bottom: 1rem;
    }

    .intro-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #16324F;
        margin-bottom: 0.35rem;
    }

    .intro-text {
        color: #475569;
        font-size: 0.98rem;
        line-height: 1.55;
    }

    .context-note {
        color: #475569;
        font-size: 0.98rem;
        line-height: 1.55;
        margin-bottom: 1rem;
    }

    .footer-note {
        margin-top: 1rem;
        padding-top: 0.8rem;
        border-top: 1px solid #E2E8F0;
        color: #64748B;
        font-size: 0.88rem;
    }

    .loading-wrapper {
        min-height: 72vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding-top: 2.5rem;
    }

    .loading-card {
        width: min(620px, 92vw);
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 24px;
        padding: 2.4rem 2.2rem;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
        text-align: center;
    }

    .loading-title {
        font-size: 1.55rem;
        font-weight: 800;
        color: #16324F;
        margin-top: 1rem;
        margin-bottom: 0.45rem;
    }

    .loading-text {
        color: #64748B;
        font-size: 0.98rem;
        line-height: 1.55;
        margin-bottom: 0.8rem;
    }

    .loading-question {
        color: #16324F;
        font-size: 1rem;
        line-height: 1.55;
        font-weight: 650;
        margin-bottom: 0.35rem;
    }

    .loading-subquestion {
        color: #16324F;
        font-size: 1rem;
        line-height: 1.55;
        font-weight: 650;
        margin-bottom: 1.3rem;
    }

    .loading-gif {
        width: 150px;
        max-height: 150px;
        object-fit: contain;
        margin-bottom: 0.5rem;
    }

    .loader-road {
        width: 210px;
        height: 8px;
        background: linear-gradient(
            90deg,
            #CBD5E1 0%,
            #CBD5E1 35%,
            transparent 35%,
            transparent 50%,
            #CBD5E1 50%,
            #CBD5E1 85%,
            transparent 85%
        );
        background-size: 70px 8px;
        border-radius: 999px;
        margin: 1.1rem auto 0;
        animation: roadMove 0.8s linear infinite;
    }

    .loader-car {
        width: 68px;
        height: 34px;
        background: #16324F;
        border-radius: 18px 22px 10px 10px;
        margin: 0 auto;
        position: relative;
        animation: carBounce 0.9s ease-in-out infinite;
    }

    .loader-car:before {
        content: "";
        position: absolute;
        width: 30px;
        height: 16px;
        background: #93C5FD;
        border-radius: 14px 14px 4px 4px;
        top: -10px;
        left: 19px;
    }

    .loader-car:after {
        content: "";
        position: absolute;
        width: 82px;
        height: 4px;
        background: #E2E8F0;
        left: -7px;
        bottom: -10px;
        border-radius: 999px;
    }

    .loader-wheel {
        width: 13px;
        height: 13px;
        background: #0F172A;
        border: 3px solid #FFFFFF;
        border-radius: 50%;
        position: absolute;
        bottom: -6px;
    }

    .loader-wheel.left {
        left: 10px;
    }

    .loader-wheel.right {
        right: 10px;
    }

    .loading-progress {
        width: 100%;
        height: 7px;
        background: #E2E8F0;
        border-radius: 999px;
        overflow: hidden;
        margin-top: 1.2rem;
    }

    .loading-progress-bar {
        width: 45%;
        height: 100%;
        background: linear-gradient(90deg, #16324F, #2E86C1);
        border-radius: 999px;
        animation: progressMove 1.15s ease-in-out infinite;
    }

    @keyframes roadMove {
        from { background-position: 0 0; }
        to { background-position: -70px 0; }
    }

    @keyframes carBounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-4px); }
    }

    @keyframes progressMove {
        0% { transform: translateX(-115%); }
        100% { transform: translateX(255%); }
    }

    @media (max-width: 900px) {
        .fixed-header {
            top: 2.75rem;
            padding-left: 1.2rem;
            gap: 0.9rem;
            min-height: 82px;
        }

        .header-logo-box {
            width: 80px;
        }

        .header-logo {
            max-height: 68px;
            max-width: 80px;
        }

        .header-title {
            font-size: 1.65rem;
        }

        .block-container {
            padding-top: 7.4rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def leer_csv_robusto(ruta):
    try:
        df = pd.read_csv(ruta, encoding="utf-8-sig")
        if df.shape[1] == 1:
            df = pd.read_csv(ruta, encoding="utf-8-sig", sep=";")
        return df
    except UnicodeDecodeError:
        df = pd.read_csv(ruta, encoding="latin1")
        if df.shape[1] == 1:
            df = pd.read_csv(ruta, encoding="latin1", sep=";")
        return df


def seleccionar_columna(df, opciones):
    for col in opciones:
        if col in df.columns:
            return col
    return None


def nombre_variable(variable):
    return NOMBRES_VARIABLES.get(variable, variable.replace("_", " ").capitalize())


def imagen_base64(path):
    if not Path(path).exists():
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def render_loading_screen():
    loader_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            html, body {
                margin: 0;
                padding: 0;
                background: transparent;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }

            .loading-wrapper {
                min-height: 540px;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 1rem;
                box-sizing: border-box;
            }

            .loading-card {
                width: min(720px, 94vw);
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 24px;
                padding: 2.2rem 2.2rem 2rem 2.2rem;
                box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
                text-align: center;
                box-sizing: border-box;
            }

            .loading-scene {
                width: 360px;
                height: 205px;
                margin: 0 auto 0.9rem auto;
                position: relative;
                overflow: hidden;
                border-radius: 20px;
                background: linear-gradient(
                    180deg,
                    #E0F2FE 0%,
                    #F8FAFC 62%,
                    #374151 62%,
                    #374151 100%
                );
                border: 1px solid #E2E8F0;
                box-sizing: border-box;
            }

            .scene-sun {
                position: absolute;
                top: 25px;
                right: -42px;
                width: 32px;
                height: 32px;
                background: #FACC15;
                border-radius: 50%;
                box-shadow: 0 0 22px rgba(250, 204, 21, 0.85);
                animation: sunMoveRightToLeft 5.5s linear infinite;
                z-index: 1;
            }

            .scene-star {
                position: absolute;
                width: 5px;
                height: 5px;
                background: #FFFFFF;
                border-radius: 50%;
                opacity: 0.9;
                animation: starBlink 1.8s ease-in-out infinite;
                z-index: 1;
            }

            .star-1 { top: 22px; left: 62px; animation-delay: 0s; }
            .star-2 { top: 46px; left: 126px; animation-delay: 0.4s; }
            .star-3 { top: 28px; right: 92px; animation-delay: 0.8s; }
            .star-4 { top: 60px; right: 42px; animation-delay: 1.2s; }

            .scene-car {
                position: absolute;
                width: 270px;
                height: 128px;
                left: 45px;
                top: 54px;
                animation: carBounceScene 1.05s ease-in-out infinite;
                z-index: 4;
            }

            .scene-car-body {
                position: absolute;
                left: 22px;
                bottom: 28px;
                width: 228px;
                height: 66px;
                background: #2E86C1;
                border-radius: 34px 50px 28px 28px;
                box-shadow: inset 9px 0 0 rgba(22, 50, 79, 0.20);
            }

            .scene-car-roof {
                position: absolute;
                left: 58px;
                bottom: 84px;
                width: 150px;
                height: 66px;
                background: #1E293B;
                clip-path: polygon(13% 100%, 25% 17%, 66% 17%, 100% 100%);
                border-top: 6px solid #CBD5E1;
                z-index: 5;
            }

            .scene-window {
                position: absolute;
                top: 18px;
                height: 35px;
                background: #DFF6F4;
            }

            .scene-window-left {
                left: 29px;
                width: 50px;
                clip-path: polygon(18% 100%, 30% 0, 100% 0, 100% 100%);
            }

            .scene-window-right {
                left: 89px;
                width: 51px;
                clip-path: polygon(0 0, 62% 0, 100% 100%, 0 100%);
            }

            .scene-car-handle {
                position: absolute;
                right: 88px;
                top: 31px;
                width: 36px;
                height: 8px;
                background: #FFFFFF;
                border-radius: 999px;
                opacity: 0.92;
            }

            .scene-car-light {
                position: absolute;
                right: 5px;
                top: 18px;
                width: 12px;
                height: 21px;
                background: #FFFFFF;
                border-radius: 999px;
                transform: rotate(-28deg);
                opacity: 0.95;
            }

            .scene-wheel {
                position: absolute;
                bottom: 0;
                width: 60px;
                height: 60px;
                background: #2F3333;
                border-radius: 50%;
                border: 8px solid #2F3333;
                z-index: 6;
                animation: wheelSpinScene 0.85s linear infinite;
                box-sizing: border-box;
            }

            .scene-wheel-left { left: 64px; }
            .scene-wheel-right { right: 48px; }

            .scene-wheel-inner {
                width: 100%;
                height: 100%;
                background: #FFFFFF;
                border-radius: 50%;
                position: relative;
            }

            .scene-wheel-inner::before {
                content: "";
                position: absolute;
                inset: 10px;
                background:
                    linear-gradient(90deg, transparent 42%, #333333 42%, #333333 58%, transparent 58%),
                    linear-gradient(0deg, transparent 42%, #333333 42%, #333333 58%, transparent 58%),
                    linear-gradient(45deg, transparent 43%, #333333 43%, #333333 57%, transparent 57%),
                    linear-gradient(-45deg, transparent 43%, #333333 43%, #333333 57%, transparent 57%);
                border-radius: 50%;
            }

            .scene-wheel-inner::after {
                content: "";
                position: absolute;
                width: 9px;
                height: 9px;
                background: #333333;
                border-radius: 50%;
                top: 17px;
                left: 17px;
            }

            .scene-road {
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 78px;
                background: #374151;
                overflow: hidden;
                z-index: 2;
            }

            .scene-road::before {
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 5px;
                background: rgba(255, 255, 255, 0.22);
            }

            .scene-road-line {
                position: absolute;
                top: 37px;
                left: 0;
                width: 200%;
                height: 6px;
                background: repeating-linear-gradient(
                    90deg,
                    #F9FAFB 0px,
                    #F9FAFB 38px,
                    transparent 38px,
                    transparent 76px
                );
                border-radius: 999px;
                animation: roadMoveScene 0.72s linear infinite;
            }

            .loading-title {
                font-size: 1.65rem;
                font-weight: 800;
                color: #16324F;
                margin-top: 1rem;
                margin-bottom: 0.45rem;
            }

            .loading-text {
                color: #64748B;
                font-size: 0.98rem;
                line-height: 1.55;
                margin-bottom: 0.8rem;
            }

            .loading-question {
                color: #16324F;
                font-size: 1rem;
                line-height: 1.55;
                font-weight: 650;
                margin-bottom: 0.35rem;
            }

            .loading-subquestion {
                color: #16324F;
                font-size: 1rem;
                line-height: 1.55;
                font-weight: 650;
                margin-bottom: 1.3rem;
            }

            .loading-progress {
                width: 100%;
                height: 7px;
                background: #E2E8F0;
                border-radius: 999px;
                overflow: hidden;
                margin-top: 1.2rem;
            }

            .loading-progress-bar {
                width: 45%;
                height: 100%;
                background: linear-gradient(90deg, #16324F, #2E86C1);
                border-radius: 999px;
                animation: progressMove 1.15s ease-in-out infinite;
            }

            @keyframes sunMoveRightToLeft {
                0% { transform: translateX(0) translateY(6px); opacity: 0; }
                10% { opacity: 1; }
                50% { transform: translateX(-190px) translateY(-12px); opacity: 1; }
                90% { opacity: 1; }
                100% { transform: translateX(-420px) translateY(6px); opacity: 0; }
            }

            @keyframes starBlink {
                0%, 100% { opacity: 0.35; transform: scale(0.8); }
                50% { opacity: 1; transform: scale(1.15); }
            }

            @keyframes carBounceScene {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-5px); }
            }

            @keyframes wheelSpinScene {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }

            @keyframes roadMoveScene {
                from { transform: translateX(0); }
                to { transform: translateX(-76px); }
            }

            @keyframes progressMove {
                0% { transform: translateX(-115%); }
                100% { transform: translateX(255%); }
            }
        </style>
    </head>

    <body>
        <div class="loading-wrapper">
            <div class="loading-card">
                <div class="loading-scene">
                    <div class="scene-sun"></div>

                    <div class="scene-star star-1"></div>
                    <div class="scene-star star-2"></div>
                    <div class="scene-star star-3"></div>
                    <div class="scene-star star-4"></div>

                    <div class="scene-car">
                        <div class="scene-car-roof">
                            <div class="scene-window scene-window-left"></div>
                            <div class="scene-window scene-window-right"></div>
                        </div>

                        <div class="scene-car-body">
                            <div class="scene-car-handle"></div>
                            <div class="scene-car-light"></div>
                        </div>

                        <div class="scene-wheel scene-wheel-left">
                            <div class="scene-wheel-inner"></div>
                        </div>

                        <div class="scene-wheel scene-wheel-right">
                            <div class="scene-wheel-inner"></div>
                        </div>
                    </div>

                    <div class="scene-road">
                        <div class="scene-road-line"></div>
                    </div>
                </div>

                <div class="loading-title">Preparando Madrid Segura</div>

                <div class="loading-text">
                    Estamos cargando los datos de accidentalidad, aforos viales y visualizaciones.
                </div>

                <div class="loading-question">
                    ¿Sabes cuántas personas se ven implicadas cada día en accidentes de tráfico en Madrid y qué consecuencias sufren?
                </div>

                <div class="loading-subquestion">
                    Explora cómo varía la lesividad según el momento, el lugar y las características del accidente.
                </div>

                <div class="loading-progress">
                    <div class="loading-progress-bar"></div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    components.html(loader_html, height=580, scrolling=False)


def render_header():
    logo_b64 = imagen_base64(LOGO_PAGE_PATH)

    if logo_b64:
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="header-logo">'
    else:
        logo_html = ""

    st.markdown(
        f"""
        <div class="fixed-header">
            <div class="header-logo-box">
                {logo_html}
            </div>
            <div class="header-title-box">
                <div class="header-title">Madrid Segura</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown(
        """
        <div class="footer-note">
            Fuente principal: Portal de Datos Abiertos del Ayuntamiento de Madrid. Elaboración propia a partir de registros de accidentes de tráfico y aforos permanentes.
        </div>
        """,
        unsafe_allow_html=True,
    )


def formato_numero_es(valor):
    if pd.isna(valor):
        return "Sin dato"
    return f"{valor:,.0f}".replace(",", ".")


def formato_porcentaje_es(valor, decimales=2):
    if pd.isna(valor):
        return "Sin dato"
    return f"{valor:.{decimales}f}".replace(".", ",") + "%"


def formatear_hora(valor):
    if pd.isna(valor):
        return "Sin dato"
    try:
        valor = int(float(valor))
        return f"{valor}:00"
    except Exception:
        return "Sin dato"


def parsear_hora(serie):
    s = serie.astype(str).str.strip()
    resultado = pd.Series(index=serie.index, dtype="float64")
    mask_colon = s.str.contains(":", regex=False)

    if mask_colon.any():
        resultado.loc[mask_colon] = pd.to_datetime(
            s.loc[mask_colon],
            errors="coerce",
        ).dt.hour

    if (~mask_colon).any():
        resultado.loc[~mask_colon] = pd.to_numeric(
            s.loc[~mask_colon],
            errors="coerce",
        )

    return resultado


def normalizar_numero(serie):
    return pd.to_numeric(
        serie.astype(str).str.replace(",", ".", regex=False),
        errors="coerce",
    )


def convertir_utm_a_latlon(df):
    if "lat" in df.columns and "lon" in df.columns:
        return df

    col_x = seleccionar_columna(df, ["coordenada_x_utm", "coord_x", "x"])
    col_y = seleccionar_columna(df, ["coordenada_y_utm", "coord_y", "y"])

    if col_x is None or col_y is None:
        return df

    try:
        from pyproj import Transformer

        transformer = Transformer.from_crs(
            "EPSG:25830",
            "EPSG:4326",
            always_xy=True,
        )

        mask = df[col_x].notna() & df[col_y].notna()

        lon, lat = transformer.transform(
            df.loc[mask, col_x].values,
            df.loc[mask, col_y].values,
        )

        df.loc[mask, "lon"] = lon
        df.loc[mask, "lat"] = lat

    except Exception:
        pass

    return df


def aplicar_estilo_figura(fig, titulo_x=None, titulo_y=None, alto=500):
    fig.update_layout(
        template="plotly_white",
        title=dict(
            x=0,
            xanchor="left",
            font=dict(size=18, color="#16324F"),
            pad=dict(b=24),
        ),
        font=dict(size=12, color="#334155"),
        legend_title_text="",
        margin=dict(l=25, r=25, t=110, b=50),
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=alto,
        bargap=0.08,
        bargroupgap=0.04,
    )

    if titulo_x is not None:
        fig.update_xaxes(title_text=titulo_x, title_font=dict(size=12))

    if titulo_y is not None:
        fig.update_yaxes(title_text=titulo_y, title_font=dict(size=12))

    fig.update_xaxes(tickfont=dict(size=11))
    fig.update_yaxes(tickfont=dict(size=11))

    return fig


def aplicar_espacio_leyenda(fig, y=1.18, top=145):
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=y,
            xanchor="left",
            x=0,
        ),
        margin=dict(l=25, r=25, t=top, b=50),
    )
    return fig


def render_metric_card(label, value, small=False):
    clase_valor = "metric-value-small" if small else "metric-value"
    return f"""
    <div class="metric-box">
        <div class="metric-label">{label}</div>
        <div class="{clase_valor}">{value}</div>
    </div>
    """


def ordenar_desconocido_final(lista):
    lista = [x for x in lista if pd.notna(x)]
    desconocidos = []
    resto = []

    for x in lista:
        texto = str(x).strip().lower()
        if texto in ["desconocido", "desconocida", "sin dato", "desconocidos", "nan"]:
            desconocidos.append(x)
        else:
            resto.append(x)

    resto = sorted(resto, key=lambda x: str(x))
    return resto + desconocidos


def obtener_orden_edad(valores):
    valores = list(pd.Series(valores).dropna().unique())
    orden_preferido = [
        "Menor_15",
        "15_35",
        "35_65",
        "Mayor_65",
        "Desconocido",
        "Menor de 15 años",
        "De 15 a 35 años",
        "De 35 a 65 años",
        "Mayor de 65 años",
    ]
    presentes = [x for x in orden_preferido if x in valores]
    restantes = [x for x in valores if x not in presentes]
    return presentes + ordenar_desconocido_final(restantes)


def obtener_orden_sexo(valores):
    valores = list(pd.Series(valores).dropna().unique())
    orden_preferido = ["Hombre", "Mujer", "Desconocido"]
    presentes = [x for x in orden_preferido if x in valores]
    restantes = [x for x in valores if x not in presentes]
    return presentes + ordenar_desconocido_final(restantes)


def obtener_orden_vehiculo_por_gravedad(df, col_vehiculo, col_lesividad):
    tabla = pd.crosstab(
        df[col_vehiculo],
        df[col_lesividad],
        normalize="index",
    ) * 100

    if "Grave/Fallecido" in tabla.columns:
        orden = tabla["Grave/Fallecido"].sort_values(ascending=False).index.tolist()
    else:
        orden = tabla.sum(axis=1).sort_values(ascending=False).index.tolist()

    orden_limpio = [
        x for x in orden
        if str(x).strip().lower() not in ["desconocido", "sin dato", "nan"]
    ]
    desconocidos = [
        x for x in orden
        if str(x).strip().lower() in ["desconocido", "sin dato", "nan"]
    ]

    return orden_limpio + desconocidos


def safe_value(row, col):
    if col is None:
        return "Sin dato"
    val = row.get(col, "Sin dato")
    if pd.isna(val):
        return "Sin dato"
    return val


def color_lesividad_folium(valor):
    if valor == "Grave/Fallecido":
        return "darkred"
    if valor == "Leve":
        return "orange"
    if valor == "Sin asistencia sanitaria":
        return "blue"
    return "gray"


def acortar_etiqueta(texto):
    mapa = {
        "Motocicleta más 125cc": "Moto >125cc",
        "Motocicleta más de 125cc": "Moto >125cc",
        "Vehículos entidades": "Vehíc. entidades",
        "Vehículo ligero": "Vehíc. ligero",
        "Transporte pesado": "Transp. pesado",
        "Motor/Especial": "Motor/Esp.",
        "Pérdida control/Otro": "Pérdida control",
        "Grave/Fallecido": "Grave/Fall.",
    }
    return mapa.get(str(texto), str(texto))


def grafico_porcentaje_agrupado(df, variable, orden_categorias, titulo, alto=480):
    tabla = pd.crosstab(
        df[variable],
        df[COL_LESIVIDAD],
        normalize="index",
    ) * 100

    columnas = [c for c in ORDEN_LESIVIDAD if c in tabla.columns]
    tabla = tabla[columnas]

    if orden_categorias is not None:
        orden_valid = [x for x in orden_categorias if x in tabla.index]
        tabla = tabla.reindex(orden_valid)
    else:
        orden_valid = tabla.index.tolist()

    tabla_long = tabla.reset_index().melt(
        id_vars=variable,
        var_name="Lesividad",
        value_name="Porcentaje",
    )

    tabla_long["Texto"] = tabla_long["Porcentaje"].apply(
        lambda x: f"{x:.1f}%" if x >= 2 else ""
    )

    fig = px.bar(
        tabla_long,
        x=variable,
        y="Porcentaje",
        color="Lesividad",
        barmode="group",
        category_orders={
            variable: orden_valid,
            "Lesividad": ORDEN_LESIVIDAD,
        },
        color_discrete_map=COLOR_LESIVIDAD,
        title=titulo,
        text="Texto",
    )

    fig.update_traces(textposition="outside", cliponaxis=False)

    fig = aplicar_estilo_figura(
        fig,
        titulo_x=nombre_variable(variable),
        titulo_y="Porcentaje",
        alto=alto,
    )
    fig = aplicar_espacio_leyenda(fig, y=1.20, top=150)
    fig.update_xaxes(tickangle=-25)
    return fig


def obtener_offset_etiqueta(categoria, indice):
    texto = str(categoria).strip()

    offsets_especificos = {
        # Tipo de vehículo
        "Motocicleta más 125cc": (78, 46),
        "Motocicleta más de 125cc": (78, 46),
        "Ciclomotor": (-78, -52),
        "Patinete": (86, -10),
        "Bicicleta": (-92, -60),
        "Motor/Especial": (90, 12),
        "Vehículos entidades": (86, 52),
        "Vehículo ligero": (94, -34),
        "Transporte pesado": (100, 18),
        "Turismo": (82, 20),
        "Vehículo ligero/Transporte": (96, 18),

        # Tipo de accidente
        "Atropello": (86, -50),
        "Caída": (78, 44),
        "Colisión": (90, -8),
        "Alcance": (84, 36),
        "Obstáculo": (-90, -40),
        "Pérdida control/Otro": (-96, 42),
        "Pérdida control": (-96, 42),
        "Salida/Vuelco": (92, 24),
    }

    if texto in offsets_especificos:
        return offsets_especificos[texto]

    offsets_genericos = [
        (88, -46),
        (88, 46),
        (-88, -46),
        (-88, 46),
        (104, 12),
        (-104, 12),
        (64, -64),
        (64, 64),
    ]
    return offsets_genericos[indice % len(offsets_genericos)]


def obtener_anchor_etiqueta(ax, ay):
    if ax >= 0:
        xanchor = "left"
    else:
        xanchor = "right"

    if ay >= 0:
        yanchor = "bottom"
    else:
        yanchor = "top"

    return xanchor, yanchor


def grafico_frecuencia_vs_lesividad(df, variable, nivel_lesividad, titulo):
    temp = df.dropna(subset=[variable, COL_LESIVIDAD]).copy()
    temp["nivel_bin"] = (temp[COL_LESIVIDAD] == nivel_lesividad).astype(int)

    resumen = (
        temp.groupby(variable, observed=False)
        .agg(
            frecuencia=("nivel_bin", "count"),
            porcentaje=("nivel_bin", "mean"),
        )
        .reset_index()
    )

    if resumen.empty:
        return go.Figure(), pd.DataFrame()

    resumen["porcentaje"] = resumen["porcentaje"] * 100
    resumen["categoria"] = resumen[variable].astype(str)
    resumen["etiqueta_corta"] = resumen[variable].apply(acortar_etiqueta)

    resumen = resumen.sort_values(
        ["porcentaje", "frecuencia"],
        ascending=[False, False],
    ).reset_index(drop=True)

    resumen["punto"] = range(1, len(resumen) + 1)

    max_freq = resumen["frecuencia"].max()
    resumen["tamano"] = ((resumen["frecuencia"] / max_freq) ** 0.5) * 42 + 14

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=resumen["frecuencia"],
            y=resumen["porcentaje"],
            mode="markers",
            customdata=resumen[["categoria"]].to_numpy(),
            marker=dict(
                size=resumen["tamano"],
                color=resumen["porcentaje"],
                colorscale=ESCALA_RIESGO,
                showscale=True,
                colorbar=dict(title=f"% {nivel_lesividad}"),
                line=dict(color="#1E293B", width=1.2),
                opacity=0.9,
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Personas implicadas: %{x:,.0f}<br>"
                f"% {nivel_lesividad}: "
                "%{y:.2f}<extra></extra>"
            ),
        )
    )

    for i, fila in resumen.iterrows():
        ax, ay = obtener_offset_etiqueta(fila["categoria"], i)
        xanchor, yanchor = obtener_anchor_etiqueta(ax, ay)

        fig.add_annotation(
            x=fila["frecuencia"],
            y=fila["porcentaje"],
            text=fila["etiqueta_corta"],
            showarrow=True,
            arrowhead=0,
            arrowwidth=1.1,
            arrowcolor="#334155",
            ax=ax,
            ay=ay,
            xanchor=xanchor,
            yanchor=yanchor,
            font=dict(size=11, color="#334155"),
            bgcolor="rgba(255,255,255,0.88)",
            bordercolor="rgba(226,232,240,0.95)",
            borderwidth=1,
            borderpad=3,
        )

    fig = aplicar_estilo_figura(
        fig,
        titulo_x="Número de personas implicadas",
        titulo_y=f"% {nivel_lesividad.lower()}",
        alto=560,
    )

    max_pct = resumen["porcentaje"].max()

    fig.update_layout(
        title=titulo,
        margin=dict(l=70, r=150, t=100, b=60),
    )

    fig.update_xaxes(range=[-max_freq * 0.16, max_freq * 1.22])
    fig.update_yaxes(range=[-max(0.35, max_pct * 0.10), max(max_pct * 1.22, 5)])

    tabla_detalle = resumen.copy()
    tabla_detalle["Personas implicadas"] = tabla_detalle["frecuencia"].apply(formato_numero_es)
    tabla_detalle[f"% {nivel_lesividad}"] = tabla_detalle["porcentaje"].apply(
        lambda x: formato_porcentaje_es(x, 2)
    )

    tabla_detalle = tabla_detalle[
        ["punto", "categoria", "Personas implicadas", f"% {nivel_lesividad}"]
    ].rename(
        columns={
            "punto": "Punto",
            "categoria": nombre_variable(variable),
        }
    )

    return fig, tabla_detalle


def grafico_prioridad_distrital(df, col_distrito, col_lesividad, nivel_lesividad="Grave/Fallecido"):
    base = df.dropna(subset=[col_distrito]).copy()

    if base.empty:
        return go.Figure()

    tabla = (
        base.groupby(col_distrito, observed=False)
        .agg(personas=(col_distrito, "size"))
        .reset_index()
    )

    max_personas = max(tabla["personas"].max(), 1)
    tabla["personas_idx"] = tabla["personas"] / max_personas * 100

    if nivel_lesividad == "Todos":
        tabla["casos_nivel"] = tabla["personas"]
        tabla["casos_idx"] = tabla["personas_idx"]
        tabla["indice_prioridad"] = tabla["personas_idx"]
        titulo = "Top 10 distritos por volumen total de personas implicadas"
        colorbar_title = "Personas implicadas"
        etiqueta_casos = "Personas implicadas"
    else:
        casos = (
            base[base[col_lesividad] == nivel_lesividad]
            .groupby(col_distrito, observed=False)
            .size()
            .reset_index(name="casos_nivel")
        )

        tabla = tabla.merge(casos, on=col_distrito, how="left")
        tabla["casos_nivel"] = tabla["casos_nivel"].fillna(0)

        max_casos = max(tabla["casos_nivel"].max(), 1)
        tabla["casos_idx"] = tabla["casos_nivel"] / max_casos * 100

        # Indicador exploratorio 50/50:
        # 50% volumen total de personas implicadas + 50% casos del nivel seleccionado.
        tabla["indice_prioridad"] = tabla["casos_idx"] * 0.5 + tabla["personas_idx"] * 0.5

        titulo = f"Top 10 distritos por indicador combinado: volumen y {nivel_lesividad}"
        colorbar_title = nivel_lesividad
        etiqueta_casos = f"Casos {nivel_lesividad}"

    tabla = tabla.sort_values("indice_prioridad", ascending=False).head(10)
    tabla = tabla.sort_values("indice_prioridad", ascending=True)
    tabla["texto"] = tabla["indice_prioridad"].round(1).astype(str)

    fig = px.scatter(
        tabla,
        x="indice_prioridad",
        y=col_distrito,
        size="personas",
        color="casos_nivel",
        color_continuous_scale=ESCALA_RIESGO,
        text="texto",
        title=titulo,
        labels={
            "indice_prioridad": "Índice de prioridad",
            col_distrito: "Distrito",
            "casos_nivel": etiqueta_casos,
            "personas": "Personas implicadas",
        },
        hover_data={
            "personas": True,
            "casos_nivel": True,
            "indice_prioridad": ":.1f",
        },
    )

    fig.update_traces(
        textposition="middle right",
        marker=dict(opacity=0.92, line=dict(width=1.2, color="#1E293B")),
    )

    fig = aplicar_estilo_figura(
        fig,
        titulo_x="Índice de prioridad",
        titulo_y="Distrito",
        alto=520,
    )

    fig.update_coloraxes(colorbar_title=colorbar_title)

    fig.update_xaxes(
        range=[
            max(0, tabla["indice_prioridad"].min() - 5),
            tabla["indice_prioridad"].max() * 1.08,
        ]
    )

    return fig


# ============================================================
# CARGA DE DATOS
# ============================================================

@st.cache_resource(show_spinner=False)
def cargar_accidentes():
    ruta = DATA_DIR / "accidentes.csv"
    df = leer_csv_robusto(ruta)

    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(
            df["fecha"].astype(str).str.strip(),
            format="%Y-%m-%d",
            errors="coerce",
        )
        df["fecha_mostrar"] = df["fecha"].dt.strftime("%d/%m/%Y")
        df["fecha_mostrar"] = df["fecha_mostrar"].fillna("Sin dato")
        df["anio"] = df["fecha"].dt.year
        df["mes"] = df["fecha"].dt.month
        df["nombre_mes"] = df["mes"].map(MESES)

    if "hora" in df.columns:
        df["hora"] = parsear_hora(df["hora"])
        df["hora_mostrar"] = df["hora"].apply(formatear_hora)

    if "dia_semana" not in df.columns and "fecha" in df.columns:
        dias = {
            0: "Lunes",
            1: "Martes",
            2: "Miércoles",
            3: "Jueves",
            4: "Viernes",
            5: "Sábado",
            6: "Domingo",
        }
        df["dia_semana"] = df["fecha"].dt.dayofweek.map(dias)
        df["dia_semana_num"] = df["fecha"].dt.dayofweek + 1

    df = convertir_utm_a_latlon(df)

    col_lesividad = seleccionar_columna(df, ["lesividad_cat", "lesividad"])
    if col_lesividad is not None:
        df[col_lesividad] = df[col_lesividad].fillna("Sin dato")

    columnas_categoricas = [
        "distrito",
        "lesividad_cat",
        "lesividad",
        "accidente_cat",
        "tipo_accidente",
        "vehiculo_cat",
        "tipo_vehiculo",
        "persona_cat",
        "tipo_persona",
        "edad_cat",
        "rango_edad",
        "meteo_cat",
        "estado_meteorológico",
        "estado_meteorologico",
        "positiva_alcohol",
        "sexo",
        "dia_semana",
        "nombre_mes",
        "fecha_mostrar",
        "hora_mostrar",
    ]

    for col in columnas_categoricas:
        if col in df.columns:
            df[col] = df[col].astype("category")

    for col in ["anio", "mes", "dia_semana_num", "hora"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce", downcast="integer")

    for col in ["lat", "lon", "coordenada_x_utm", "coordenada_y_utm"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce", downcast="float")

    return df


@st.cache_resource(show_spinner=False)
def cargar_flujo():
    ruta = DATA_DIR / "flujo.csv"

    if not ruta.exists():
        return pd.DataFrame()

    flujo = leer_csv_robusto(ruta)

    col_fecha = seleccionar_columna(flujo, ["FDIA", "fecha", "Fecha"])
    col_estacion = seleccionar_columna(flujo, ["ESTACIÓN", "ESTACION", "Estación", "estacion"])
    col_lat = seleccionar_columna(flujo, ["LATITUD", "latitud", "lat"])
    col_lon = seleccionar_columna(flujo, ["LONGITUD", "longitud", "lon"])

    if col_fecha is None:
        return pd.DataFrame()

    flujo[col_fecha] = pd.to_datetime(flujo[col_fecha], errors="coerce")
    cols_horas = [c for c in flujo.columns if str(c).upper().startswith("HOR")]

    if len(cols_horas) == 0:
        return pd.DataFrame()

    id_vars = [col_fecha]

    if col_estacion:
        id_vars.append(col_estacion)
    if col_lat:
        id_vars.append(col_lat)
    if col_lon:
        id_vars.append(col_lon)

    flujo_long = flujo.melt(
        id_vars=id_vars,
        value_vars=cols_horas,
        var_name="hora",
        value_name="vehiculos",
    )

    flujo_long["hora"] = (
        flujo_long["hora"]
        .astype(str)
        .str.upper()
        .str.replace("HOR", "", regex=False)
        .astype(int)
    )

    flujo_long["vehiculos"] = pd.to_numeric(flujo_long["vehiculos"], errors="coerce").fillna(0)
    flujo_long["anio"] = flujo_long[col_fecha].dt.year
    flujo_long["mes"] = flujo_long[col_fecha].dt.month
    flujo_long["nombre_mes"] = flujo_long["mes"].map(MESES)

    rename_dict = {col_fecha: "fecha"}

    if col_estacion:
        rename_dict[col_estacion] = "estacion"
    if col_lat:
        rename_dict[col_lat] = "lat"
    if col_lon:
        rename_dict[col_lon] = "lon"

    flujo_long = flujo_long.rename(columns=rename_dict)

    if "lat" in flujo_long.columns:
        flujo_long["lat"] = normalizar_numero(flujo_long["lat"])
    if "lon" in flujo_long.columns:
        flujo_long["lon"] = normalizar_numero(flujo_long["lon"])

    return flujo_long


# ============================================================
# PANTALLA DE CARGA SOLO AL INICIO DE LA SESIÓN
# ============================================================

if "pantalla_carga_mostrada" not in st.session_state:
    st.session_state["pantalla_carga_mostrada"] = False

mostrar_carga_inicial = not st.session_state["pantalla_carga_mostrada"]
loading_placeholder = st.empty()

if mostrar_carga_inicial:
    with loading_placeholder.container():
        render_loading_screen()

accidentes = cargar_accidentes()
flujo_long = cargar_flujo()

if mostrar_carga_inicial:
    loading_placeholder.empty()
    st.session_state["pantalla_carga_mostrada"] = True


# ============================================================
# IDENTIFICACIÓN DE COLUMNAS
# ============================================================

COL_LESIVIDAD = seleccionar_columna(accidentes, ["lesividad_cat", "lesividad"])
COL_ACCIDENTE = seleccionar_columna(accidentes, ["accidente_cat", "tipo_accidente"])
COL_VEHICULO = seleccionar_columna(accidentes, ["vehiculo_cat", "tipo_vehiculo"])
COL_PERSONA = seleccionar_columna(accidentes, ["persona_cat", "tipo_persona"])
COL_EDAD = seleccionar_columna(accidentes, ["edad_cat", "rango_edad"])
COL_METEO = seleccionar_columna(accidentes, ["meteo_cat", "estado_meteorológico", "estado_meteorologico"])
COL_ALCOHOL = seleccionar_columna(accidentes, ["positiva_alcohol"])
COL_SEXO = seleccionar_columna(accidentes, ["sexo"])

if COL_LESIVIDAD is None:
    st.error(
        "No se encontró la columna de lesividad. "
        "Revisa si se llama 'lesividad_cat' o 'lesividad'."
    )
    st.stop()

if accidentes[COL_LESIVIDAD].isna().any():
    accidentes = accidentes.copy()
    accidentes[COL_LESIVIDAD] = accidentes[COL_LESIVIDAD].fillna("Sin dato")


# ============================================================
# ENCABEZADO
# ============================================================

render_header()


# ============================================================
# FILTROS
# ============================================================

st.sidebar.title("Filtros")

if "anio" not in accidentes.columns:
    st.error("No se pudo construir la variable de año. Revisa la columna 'fecha'.")
    st.stop()

anios_disponibles = sorted(accidentes["anio"].dropna().astype(int).unique())

if len(anios_disponibles) == 0:
    st.error("No hay años disponibles.")
    st.stop()

anio_min = min(anios_disponibles)
anio_max = max(anios_disponibles)

rango_anios = st.sidebar.slider(
    "Rango de años",
    min_value=anio_min,
    max_value=anio_max,
    value=(anio_min, anio_max),
    step=1,
)

anio_sel = list(range(rango_anios[0], rango_anios[1] + 1))
df = accidentes[accidentes["anio"].isin(anio_sel)].copy()

if "distrito" in df.columns:
    distritos = sorted(df["distrito"].dropna().unique())
    distrito_sel = st.sidebar.selectbox("Distrito", ["Todos"] + distritos)

    if distrito_sel != "Todos":
        df = df[df["distrito"] == distrito_sel].copy()

lesividades = [x for x in ORDEN_LESIVIDAD if x in df[COL_LESIVIDAD].unique()]
otras_lesividades = [x for x in df[COL_LESIVIDAD].dropna().unique() if x not in lesividades]
lesividades = lesividades + sorted(otras_lesividades)

lesividad_sel = st.sidebar.selectbox("Nivel de lesividad", ["Todos"] + lesividades)

if lesividad_sel != "Todos":
    df = df[df[COL_LESIVIDAD] == lesividad_sel].copy()

with st.sidebar.expander("Filtros avanzados"):
    if COL_ACCIDENTE:
        opciones = sorted(df[COL_ACCIDENTE].dropna().unique())
        seleccion = st.selectbox("Tipo de accidente", ["Todos"] + opciones)
        if seleccion != "Todos":
            df = df[df[COL_ACCIDENTE] == seleccion].copy()

    if COL_VEHICULO:
        opciones = sorted(df[COL_VEHICULO].dropna().unique())
        seleccion = st.selectbox("Tipo de vehículo", ["Todos"] + opciones)
        if seleccion != "Todos":
            df = df[df[COL_VEHICULO] == seleccion].copy()

    if COL_PERSONA:
        opciones = sorted(df[COL_PERSONA].dropna().unique())
        seleccion = st.selectbox("Tipo de persona", ["Todos"] + opciones)
        if seleccion != "Todos":
            df = df[df[COL_PERSONA] == seleccion].copy()

    if COL_SEXO:
        opciones = obtener_orden_sexo(df[COL_SEXO].dropna().unique())
        seleccion = st.selectbox("Sexo", ["Todos"] + opciones)
        if seleccion != "Todos":
            df = df[df[COL_SEXO] == seleccion].copy()

    if COL_EDAD:
        opciones = obtener_orden_edad(df[COL_EDAD].dropna().unique())
        seleccion = st.selectbox("Rango de edad", ["Todos"] + opciones)
        if seleccion != "Todos":
            df = df[df[COL_EDAD] == seleccion].copy()

if df.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()


# ============================================================
# PESTAÑAS
# ============================================================

tab_inicio, tab_lesividad, tab_perfil, tab_tiempo, tab_mapa, tab_exposicion = st.tabs(
    [
        "Inicio",
        "Lesividad",
        "Perfil vulnerable",
        "Patrones temporales",
        "Mapa",
        "Exposición vial",
    ]
)


# ============================================================
# 1. INICIO
# ============================================================

with tab_inicio:
    st.markdown(
        """
        <div class="section-card">
            <div class="intro-title">Tablero interactivo de seguridad vial</div>
            <div class="intro-text">
                Esta herramienta analiza la lesividad en accidentes de tráfico en Madrid combinando registros de siniestralidad, patrones temporales, distribución espacial y aforos permanentes como contexto de exposición vial.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Resumen general")

    total_personas = len(df)
    total_leves = int(df[COL_LESIVIDAD].eq("Leve").sum())
    total_graves = int(df[COL_LESIVIDAD].eq("Grave/Fallecido").sum())

    rango_anios_texto = (
        f"{int(df['anio'].min())} - {int(df['anio'].max())}"
        if df["anio"].notna().any()
        else "Sin datos"
    )

    distrito_top = (
        df["distrito"].value_counts().idxmax()
        if "distrito" in df.columns and df["distrito"].notna().any()
        else "No disponible"
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(render_metric_card("Años analizados", rango_anios_texto), unsafe_allow_html=True)
    with c2:
        st.markdown(render_metric_card("Personas implicadas", formato_numero_es(total_personas)), unsafe_allow_html=True)
    with c3:
        st.markdown(render_metric_card("Leves", formato_numero_es(total_leves)), unsafe_allow_html=True)
    with c4:
        st.markdown(render_metric_card("Graves/fallecidos", formato_numero_es(total_graves)), unsafe_allow_html=True)
    with c5:
        st.markdown(render_metric_card("Distrito con más registros", distrito_top, small=True), unsafe_allow_html=True)

    st.markdown("")

    col_a, col_b = st.columns([1.15, 1])

    with col_a:
        st.markdown(
            """
            <div class="section-card">
                El tablero muestra registros por persona implicada en accidentes de tráfico, no únicamente por accidente. Por ello, un mismo siniestro puede aparecer más de una vez cuando involucra a varias personas.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_b:
        tabla_resumen = (
            df[COL_LESIVIDAD]
            .value_counts()
            .reindex(ORDEN_LESIVIDAD)
            .dropna()
            .reset_index()
        )
        tabla_resumen.columns = ["Lesividad", "Número de personas"]

        fig_donut = px.pie(
            tabla_resumen,
            names="Lesividad",
            values="Número de personas",
            hole=0.58,
            color="Lesividad",
            color_discrete_map=COLOR_LESIVIDAD,
            title="Distribución general de la lesividad",
        )
        fig_donut = aplicar_estilo_figura(fig_donut, alto=430)
        fig_donut = aplicar_espacio_leyenda(fig_donut, y=1.15, top=130)
        st.plotly_chart(fig_donut, use_container_width=True)

    st.subheader("Evolución anual")
    tabla_anio = df.groupby(["anio", COL_LESIVIDAD], observed=False).size().reset_index(name="n")

    fig_anio = px.bar(
        tabla_anio,
        x="anio",
        y="n",
        color=COL_LESIVIDAD,
        category_orders={COL_LESIVIDAD: ORDEN_LESIVIDAD},
        color_discrete_map=COLOR_LESIVIDAD,
        title="Personas implicadas por año y nivel de lesividad",
    )
    fig_anio = aplicar_estilo_figura(fig_anio, titulo_x="Año", titulo_y="Número de personas", alto=440)
    fig_anio.update_layout(barmode="group")
    fig_anio = aplicar_espacio_leyenda(fig_anio, y=1.15, top=140)
    st.plotly_chart(fig_anio, use_container_width=True)

    if "distrito" in df.columns:
        st.subheader("Distritos con mayor número de registros")
        tabla_distrito = df["distrito"].value_counts().head(10).reset_index()
        tabla_distrito.columns = ["Distrito", "Número de personas"]
        tabla_distrito = tabla_distrito.sort_values("Número de personas", ascending=True)
        tabla_distrito["Texto"] = tabla_distrito["Número de personas"].apply(formato_numero_es)

        fig_dist = px.bar(
            tabla_distrito,
            x="Número de personas",
            y="Distrito",
            orientation="h",
            text="Texto",
            title="Top 10 distritos por número de personas implicadas",
        )
        fig_dist.update_traces(marker_color="#2E86C1", textposition="outside", cliponaxis=False)
        fig_dist = aplicar_estilo_figura(fig_dist, titulo_x="Número de personas", titulo_y="Distrito", alto=520)
        fig_dist.update_layout(showlegend=False, bargap=0.03)
        fig_dist.update_yaxes(tickfont=dict(size=10))
        st.plotly_chart(fig_dist, use_container_width=True)

    if "distrito" in df.columns:
        st.subheader("Índice orientativo de prioridad distrital")

        nivel_prioridad = st.selectbox(
            "Seleccione el nivel de lesividad para el indicador distrital",
            options=["Todos"] + ORDEN_LESIVIDAD_RADIO,
            index=1,
            key="nivel_prioridad_distrital",
        )

        fig_prioridad = grafico_prioridad_distrital(
            df=df,
            col_distrito="distrito",
            col_lesividad=COL_LESIVIDAD,
            nivel_lesividad=nivel_prioridad,
        )

        st.plotly_chart(fig_prioridad, use_container_width=True)

        if nivel_prioridad == "Todos":
            st.caption(
                "Indicador exploratorio construido para el tablero. Para la opción Todos, "
                "el ranking se ordena por el volumen total de personas implicadas por distrito. "
                "No corresponde a una métrica oficial."
            )
        else:
            st.caption(
                "Indicador exploratorio construido para el tablero. Combina en partes iguales "
                "el volumen total de personas implicadas y los casos del nivel de lesividad seleccionado. "
                "No corresponde a una métrica oficial."
            )

    render_footer()


# ============================================================
# 2. LESIVIDAD
# ============================================================

with tab_lesividad:
    st.subheader("Análisis de lesividad")

    col1, col2 = st.columns(2)

    with col1:
        tabla_les = (
            df[COL_LESIVIDAD]
            .value_counts()
            .reindex(ORDEN_LESIVIDAD)
            .dropna()
            .reset_index()
        )
        tabla_les.columns = ["Lesividad", "Número de personas"]
        tabla_les["Texto"] = tabla_les["Número de personas"].apply(formato_numero_es)

        fig_les = px.bar(
            tabla_les,
            x="Lesividad",
            y="Número de personas",
            text="Texto",
            color="Lesividad",
            category_orders={"Lesividad": ORDEN_LESIVIDAD},
            color_discrete_map=COLOR_LESIVIDAD,
            title="Personas implicadas según nivel de lesividad",
        )
        fig_les.update_traces(textposition="outside")
        fig_les = aplicar_estilo_figura(fig_les, titulo_x="Nivel de lesividad", titulo_y="Número de personas", alto=480)
        fig_les = aplicar_espacio_leyenda(fig_les, y=1.20, top=150)
        fig_les.update_layout(bargap=0.03)
        st.plotly_chart(fig_les, use_container_width=True)

    with col2:
        tabla_pct = tabla_les.copy()
        tabla_pct["Porcentaje"] = tabla_pct["Número de personas"] / tabla_pct["Número de personas"].sum() * 100
        tabla_pct["Texto"] = tabla_pct["Porcentaje"].apply(lambda x: f"{x:.2f}%")

        fig_pct = px.bar(
            tabla_pct,
            x="Lesividad",
            y="Porcentaje",
            text="Texto",
            color="Lesividad",
            category_orders={"Lesividad": ORDEN_LESIVIDAD},
            color_discrete_map=COLOR_LESIVIDAD,
            title="Porcentaje por nivel de lesividad",
        )
        fig_pct.update_traces(textposition="outside")
        fig_pct = aplicar_estilo_figura(fig_pct, titulo_x="Nivel de lesividad", titulo_y="Porcentaje", alto=480)
        fig_pct = aplicar_espacio_leyenda(fig_pct, y=1.20, top=150)
        fig_pct.update_layout(bargap=0.03)
        st.plotly_chart(fig_pct, use_container_width=True)

    if COL_ACCIDENTE:
        st.subheader("Lesividad por tipo de accidente")
        orden_acc = ordenar_desconocido_final(df[COL_ACCIDENTE].dropna().unique())
        fig_acc = grafico_porcentaje_agrupado(
            df=df,
            variable=COL_ACCIDENTE,
            orden_categorias=orden_acc,
            titulo="Distribución porcentual de lesividad por tipo de accidente",
            alto=500,
        )
        st.plotly_chart(fig_acc, use_container_width=True)

        st.subheader("Frecuencia y severidad por tipo de accidente")
        nivel_scatter_acc = st.selectbox(
            "Nivel de lesividad para analizar en tipo de accidente",
            options=ORDEN_LESIVIDAD,
            index=2,
            key="nivel_scatter_acc",
        )
        fig_freq_acc, tabla_freq_acc = grafico_frecuencia_vs_lesividad(
            df=df,
            variable=COL_ACCIDENTE,
            nivel_lesividad=nivel_scatter_acc,
            titulo=f"Frecuencia vs porcentaje de '{nivel_scatter_acc}' por tipo de accidente",
        )
        st.plotly_chart(fig_freq_acc, use_container_width=True)
    if COL_VEHICULO:
        st.subheader("Lesividad por tipo de vehículo")
        orden_veh = obtener_orden_vehiculo_por_gravedad(df, COL_VEHICULO, COL_LESIVIDAD)
        fig_veh = grafico_porcentaje_agrupado(
            df=df,
            variable=COL_VEHICULO,
            orden_categorias=orden_veh,
            titulo="Distribución porcentual de lesividad por tipo de vehículo",
            alto=500,
        )
        st.plotly_chart(fig_veh, use_container_width=True)

        st.subheader("Frecuencia y severidad por tipo de vehículo")
        nivel_scatter_veh = st.selectbox(
            "Nivel de lesividad para analizar en tipo de vehículo",
            options=ORDEN_LESIVIDAD,
            index=2,
            key="nivel_scatter_veh",
        )
        fig_freq_veh, tabla_freq_veh = grafico_frecuencia_vs_lesividad(
            df=df,
            variable=COL_VEHICULO,
            nivel_lesividad=nivel_scatter_veh,
            titulo=f"Frecuencia vs porcentaje de '{nivel_scatter_veh}' por tipo de vehículo",
        )
        st.plotly_chart(fig_freq_veh, use_container_width=True)

    render_footer()


# ============================================================
# 3. PERFIL VULNERABLE
# ============================================================

with tab_perfil:
    st.subheader("Perfil vulnerable")
    st.markdown(
        """
        <p class="context-note">
            Esta sección resume cómo cambia la composición de la lesividad según características de las personas implicadas y permite detectar perfiles con mayor presencia de casos.
        </p>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    if COL_EDAD:
        with col1:
            orden_edad = obtener_orden_edad(df[COL_EDAD].dropna().unique())
            fig_edad = grafico_porcentaje_agrupado(
                df=df,
                variable=COL_EDAD,
                orden_categorias=orden_edad,
                titulo="Distribución porcentual de lesividad por rango de edad",
                alto=490,
            )
            st.plotly_chart(fig_edad, use_container_width=True)

    if COL_SEXO:
        with col2:
            orden_sexo = obtener_orden_sexo(df[COL_SEXO].dropna().unique())
            fig_sexo = grafico_porcentaje_agrupado(
                df=df,
                variable=COL_SEXO,
                orden_categorias=orden_sexo,
                titulo="Distribución porcentual de lesividad por sexo",
                alto=490,
            )
            st.plotly_chart(fig_sexo, use_container_width=True)

    col3, col4 = st.columns(2)

    if COL_ALCOHOL:
        with col3:
            orden_alcohol = ordenar_desconocido_final(df[COL_ALCOHOL].dropna().unique())
            fig_alcohol = grafico_porcentaje_agrupado(
                df=df,
                variable=COL_ALCOHOL,
                orden_categorias=orden_alcohol,
                titulo="Distribución porcentual de lesividad según alcohol",
                alto=470,
            )
            st.plotly_chart(fig_alcohol, use_container_width=True)

    if COL_PERSONA:
        with col4:
            orden_persona = ordenar_desconocido_final(df[COL_PERSONA].dropna().unique())
            fig_persona = grafico_porcentaje_agrupado(
                df=df,
                variable=COL_PERSONA,
                orden_categorias=orden_persona,
                titulo="Distribución porcentual de lesividad por tipo de persona",
                alto=490,
            )
            st.plotly_chart(fig_persona, use_container_width=True)

    if COL_PERSONA and COL_EDAD:
        st.subheader("Ranking de perfiles vulnerables")
        nivel_perfil = st.radio(
            "Seleccione el nivel de lesividad para el ranking de perfiles:",
            options=ORDEN_LESIVIDAD_RADIO,
            horizontal=True,
            key="nivel_perfil",
        )

        perfiles = df.dropna(subset=[COL_PERSONA, COL_EDAD, COL_LESIVIDAD]).copy()
        perfiles["perfil"] = perfiles[COL_PERSONA].astype(str) + " · " + perfiles[COL_EDAD].astype(str)
        perfiles["nivel_bin"] = (perfiles[COL_LESIVIDAD] == nivel_perfil).astype(int)

        min_registros = st.slider(
            "Mínimo de registros por perfil para incluirlo en el ranking",
            min_value=50,
            max_value=1000,
            value=200,
            step=50,
        )

        tabla_perfiles = (
            perfiles.groupby("perfil", observed=False)
            .agg(
                personas=("nivel_bin", "count"),
                casos_nivel=("nivel_bin", "sum"),
            )
            .reset_index()
        )

        tabla_perfiles = tabla_perfiles[tabla_perfiles["personas"] >= min_registros].copy()
        tabla_perfiles = tabla_perfiles[tabla_perfiles["casos_nivel"] > 0].copy()
        tabla_perfiles = tabla_perfiles.sort_values("casos_nivel", ascending=True).tail(10)

        if tabla_perfiles.empty:
            st.info("No hay perfiles suficientes con el mínimo de registros seleccionado.")
        else:
            tabla_perfiles["Texto"] = tabla_perfiles["casos_nivel"].apply(formato_numero_es)

            fig_perfiles = px.scatter(
                tabla_perfiles,
                x="casos_nivel",
                y="perfil",
                size="personas",
                color="casos_nivel",
                color_continuous_scale=ESCALA_RIESGO,
                text="Texto",
                title=f"Perfiles con mayor número de casos '{nivel_perfil}'",
                hover_data={"personas": True, "casos_nivel": True},
            )
            fig_perfiles.update_traces(
                marker=dict(opacity=0.9, line=dict(width=1.1, color="#1E293B")),
                textposition="middle right",
            )
            fig_perfiles = aplicar_estilo_figura(fig_perfiles, titulo_x=nivel_perfil, titulo_y="Perfil", alto=520)
            fig_perfiles.update_coloraxes(colorbar_title=nivel_perfil)
            fig_perfiles.update_xaxes(range=[0, tabla_perfiles["casos_nivel"].max() * 1.14])
            st.plotly_chart(fig_perfiles, use_container_width=True)

    if COL_METEO:
        st.subheader("Lesividad por estado meteorológico")
        orden_meteo = ordenar_desconocido_final(df[COL_METEO].dropna().unique())
        fig_meteo = grafico_porcentaje_agrupado(
            df=df,
            variable=COL_METEO,
            orden_categorias=orden_meteo,
            titulo="Distribución porcentual de lesividad por estado meteorológico",
            alto=460,
        )
        st.plotly_chart(fig_meteo, use_container_width=True)

    render_footer()


# ============================================================
# 4. PATRONES TEMPORALES
# ============================================================

with tab_tiempo:
    st.subheader("Patrones temporales")

    col1, col2 = st.columns(2)

    with col1:
        tabla_hora = (
            df.groupby(["hora", COL_LESIVIDAD], observed=False)
            .size()
            .reset_index(name="n")
            .dropna()
        )

        fig_hora = px.line(
            tabla_hora,
            x="hora",
            y="n",
            color=COL_LESIVIDAD,
            markers=True,
            category_orders={COL_LESIVIDAD: ORDEN_LESIVIDAD},
            color_discrete_map=COLOR_LESIVIDAD,
            title="Personas implicadas por hora y nivel de lesividad",
        )
        fig_hora.update_traces(marker=dict(size=8))
        fig_hora = aplicar_estilo_figura(fig_hora, titulo_x="Hora del día", titulo_y="Número de personas", alto=480)
        fig_hora.update_xaxes(dtick=1)
        fig_hora = aplicar_espacio_leyenda(fig_hora, y=1.18, top=145)
        st.plotly_chart(fig_hora, use_container_width=True)

    with col2:
        if "dia_semana" in df.columns:
            tabla_dia = df.groupby(["dia_semana", COL_LESIVIDAD], observed=False).size().reset_index(name="n")
            tabla_dia["dia_semana"] = pd.Categorical(tabla_dia["dia_semana"], categories=ORDEN_DIAS, ordered=True)
            tabla_dia = tabla_dia.sort_values("dia_semana")

            fig_dia = px.bar(
                tabla_dia,
                x="dia_semana",
                y="n",
                color=COL_LESIVIDAD,
                barmode="group",
                category_orders={
                    "dia_semana": ORDEN_DIAS,
                    COL_LESIVIDAD: ORDEN_LESIVIDAD,
                },
                color_discrete_map=COLOR_LESIVIDAD,
                title="Personas implicadas por día de la semana",
            )
            fig_dia = aplicar_estilo_figura(fig_dia, titulo_x="Día de semana", titulo_y="Número de personas", alto=480)
            fig_dia.update_xaxes(tickangle=-20)
            fig_dia = aplicar_espacio_leyenda(fig_dia, y=1.18, top=145)
            st.plotly_chart(fig_dia, use_container_width=True)

    st.subheader("Heatmap temporal")
    categoria_heatmap = st.radio(
        "Seleccione el nivel de lesividad para el heatmap:",
        ORDEN_LESIVIDAD_RADIO,
        horizontal=True,
    )

    df_heat = df[df[COL_LESIVIDAD] == categoria_heatmap].copy()

    if "dia_semana" in df_heat.columns and "hora" in df_heat.columns and not df_heat.empty:
        tabla_heat = df_heat.groupby(["dia_semana", "hora"], observed=False).size().reset_index(name="n")
        tabla_heat["dia_semana"] = pd.Categorical(tabla_heat["dia_semana"], categories=ORDEN_DIAS, ordered=True)
        pivot_heat = (
            tabla_heat
            .pivot(index="dia_semana", columns="hora", values="n")
            .reindex(ORDEN_DIAS)
            .fillna(0)
        )

        fig_heat = px.imshow(
            pivot_heat,
            aspect="auto",
            text_auto=False,
            color_continuous_scale=ESCALA_RIESGO,
            title=f"Concentración de casos de '{categoria_heatmap}' por hora y día de semana",
        )
        fig_heat = aplicar_estilo_figura(fig_heat, titulo_x="Hora del día", titulo_y="Día de semana", alto=430)
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("No hay datos suficientes para mostrar el heatmap con los filtros seleccionados.")

    render_footer()


# ============================================================
# 5. MAPA
# ============================================================

with tab_mapa:
    st.subheader("Distribución espacial de los accidentes")
    st.markdown(
        """
        <p class="context-note">
            El mapa permite explorar la localización de los accidentes según el nivel de lesividad. Para mantener el rendimiento, se muestra una muestra de puntos cuando el número de registros es muy elevado.
        </p>
        """,
        unsafe_allow_html=True,
    )

    if "lat" in df.columns and "lon" in df.columns:
        tipo_mapa = st.radio(
            "Seleccione los casos a visualizar:",
            ["Todos los niveles", "Sin asistencia sanitaria", "Leve", "Grave/Fallecido"],
            horizontal=True,
        )

        if tipo_mapa == "Todos los niveles":
            df_mapa = df.copy()
            valor_default = 3000
        elif tipo_mapa == "Sin asistencia sanitaria":
            df_mapa = df[df[COL_LESIVIDAD] == "Sin asistencia sanitaria"].copy()
            valor_default = 3500
        elif tipo_mapa == "Leve":
            df_mapa = df[df[COL_LESIVIDAD] == "Leve"].copy()
            valor_default = 2500
        else:
            df_mapa = df[df[COL_LESIVIDAD] == "Grave/Fallecido"].copy()
            valor_default = 2000

        df_mapa = df_mapa.dropna(subset=["lat", "lon"])

        if df_mapa.empty:
            st.warning("No hay registros con coordenadas para los filtros seleccionados.")
        else:
            limite_puntos = st.slider(
                "Número máximo de puntos a mostrar",
                min_value=500,
                max_value=8000,
                value=valor_default,
                step=500,
            )

            if len(df_mapa) > limite_puntos:
                df_mapa = df_mapa.sample(limite_puntos, random_state=123)

            mapa = folium.Map(location=[40.4167, -3.7033], zoom_start=11, tiles="CartoDB positron")
            Fullscreen().add_to(mapa)
            marker_cluster = MarkerCluster().add_to(mapa)

            for _, fila in df_mapa.iterrows():
                les = safe_value(fila, COL_LESIVIDAD)
                popup_texto = f"""
                <b>Fecha:</b> {safe_value(fila, 'fecha_mostrar')}<br>
                <b>Hora:</b> {safe_value(fila, 'hora_mostrar')}<br>
                <b>Distrito:</b> {safe_value(fila, 'distrito')}<br>
                <b>Lesividad:</b> {safe_value(fila, COL_LESIVIDAD)}<br>
                <b>Tipo de accidente:</b> {safe_value(fila, COL_ACCIDENTE)}<br>
                <b>Vehículo:</b> {safe_value(fila, COL_VEHICULO)}<br>
                <b>Tipo de persona:</b> {safe_value(fila, COL_PERSONA)}
                """

                folium.CircleMarker(
                    location=[fila["lat"], fila["lon"]],
                    radius=6 if les == "Grave/Fallecido" else 5,
                    color=color_lesividad_folium(les),
                    fill=True,
                    fill_color=color_lesividad_folium(les),
                    fill_opacity=0.72,
                    weight=1.1,
                    popup=folium.Popup(popup_texto, max_width=320),
                ).add_to(marker_cluster)

            st_folium(mapa, width=1200, height=680)
    else:
        st.warning("No se encontraron coordenadas geográficas o UTM convertibles en la base de accidentes.")

    render_footer()


# ============================================================
# 6. EXPOSICIÓN VIAL
# ============================================================

with tab_exposicion:
    st.subheader("Exposición vial y lesividad")
    st.markdown(
        """
        <p class="context-note">
            Esta sección usa los aforos permanentes como aproximación descriptiva a la exposición vial. El objetivo es comparar patrones de circulación con accidentes y lesividad, no establecer una relación causal directa.
        </p>
        """,
        unsafe_allow_html=True,
    )

    if flujo_long.empty:
        st.warning("No se pudo cargar flujo.csv o no se encontraron columnas horarias.")
    else:
        flujo = flujo_long[flujo_long["anio"].isin(anio_sel)].copy()

        if flujo.empty:
            st.warning("No hay datos de flujo vehicular para los años seleccionados.")
        else:
            total_vehiculos = flujo["vehiculos"].sum()
            num_estaciones = flujo["estacion"].nunique() if "estacion" in flujo.columns else "Sin dato"

            flujo_hora_kpi = flujo.groupby("hora", as_index=False, observed=False)["vehiculos"].sum()
            hora_pico = flujo_hora_kpi.loc[flujo_hora_kpi["vehiculos"].idxmax(), "hora"]

            flujo_mes_kpi = flujo.groupby(["anio", "mes"], as_index=False, observed=False)["vehiculos"].sum()
            flujo_mes_kpi["periodo"] = flujo_mes_kpi["anio"].astype(str) + "-" + flujo_mes_kpi["mes"].astype(str).str.zfill(2)
            mes_pico = flujo_mes_kpi.loc[flujo_mes_kpi["vehiculos"].idxmax(), "periodo"]

            fc1, fc2, fc3, fc4 = st.columns(4)
            with fc1:
                st.markdown(render_metric_card("Vehículos registrados", formato_numero_es(total_vehiculos)), unsafe_allow_html=True)
            with fc2:
                st.markdown(render_metric_card("Estaciones de aforo", num_estaciones), unsafe_allow_html=True)
            with fc3:
                st.markdown(render_metric_card("Hora de mayor flujo", formatear_hora(hora_pico)), unsafe_allow_html=True)
            with fc4:
                st.markdown(render_metric_card("Mes con mayor flujo", mes_pico), unsafe_allow_html=True)

            st.markdown("")
            st.subheader("Patrón horario: flujo vehicular y lesividad")

            acc_hora_les = (
                df.groupby(["hora", COL_LESIVIDAD], observed=False)
                .size()
                .reset_index(name="personas_implicadas")
                .dropna()
            )
            flujo_hora = flujo.groupby("hora", as_index=False, observed=False)["vehiculos"].sum()
            comparacion_hora = acc_hora_les.merge(flujo_hora, on="hora", how="inner")
            comparacion_hora = comparacion_hora[comparacion_hora["vehiculos"] > 0].copy()

            if not comparacion_hora.empty:
                comparacion_hora["personas_por_100k_vehiculos"] = (
                    comparacion_hora["personas_implicadas"] / comparacion_hora["vehiculos"]
                ) * 100000

                fig_tasa_hora = px.line(
                    comparacion_hora,
                    x="hora",
                    y="personas_por_100k_vehiculos",
                    color=COL_LESIVIDAD,
                    markers=True,
                    category_orders={COL_LESIVIDAD: ORDEN_LESIVIDAD},
                    color_discrete_map=COLOR_LESIVIDAD,
                    title="Personas implicadas por cada 100.000 vehículos registrados, según hora y lesividad",
                )
                fig_tasa_hora.update_traces(marker=dict(size=8))
                fig_tasa_hora = aplicar_estilo_figura(
                    fig_tasa_hora,
                    titulo_x="Hora del día",
                    titulo_y="Personas por 100.000 vehículos",
                    alto=480,
                )
                fig_tasa_hora.update_xaxes(dtick=1)
                fig_tasa_hora = aplicar_espacio_leyenda(fig_tasa_hora, y=1.18, top=145)
                st.plotly_chart(fig_tasa_hora, use_container_width=True)

                st.caption(
                    "Indicador descriptivo agregado. Los aforos proceden de estaciones permanentes "
                    "y no representan la totalidad exacta del tráfico de toda la red vial."
                )

            st.subheader("Comparación normalizada: flujo y accidentes por lesividad")
            nivel_flujo = st.selectbox(
                "Seleccione el nivel de lesividad para comparar con el flujo vehicular",
                options=ORDEN_LESIVIDAD,
                index=2,
            )

            acc_hora_nivel = (
                df[df[COL_LESIVIDAD] == nivel_flujo]
                .groupby("hora", observed=False)
                .size()
                .reset_index(name="personas_implicadas")
            )
            comparacion_norm = acc_hora_nivel.merge(flujo_hora, on="hora", how="inner")
            comparacion_norm = comparacion_norm[
                (comparacion_norm["personas_implicadas"] > 0)
                & (comparacion_norm["vehiculos"] > 0)
            ].copy()

            if not comparacion_norm.empty:
                comparacion_norm["accidentes_indice"] = (
                    comparacion_norm["personas_implicadas"] / comparacion_norm["personas_implicadas"].max()
                )
                comparacion_norm["flujo_indice"] = (
                    comparacion_norm["vehiculos"] / comparacion_norm["vehiculos"].max()
                )
                comparacion_long = comparacion_norm.melt(
                    id_vars="hora",
                    value_vars=["accidentes_indice", "flujo_indice"],
                    var_name="Indicador",
                    value_name="Índice normalizado",
                )
                comparacion_long["Indicador"] = comparacion_long["Indicador"].replace(
                    {
                        "accidentes_indice": f"Personas implicadas: {nivel_flujo}",
                        "flujo_indice": "Flujo vehicular",
                    }
                )

                fig_norm = px.line(
                    comparacion_long,
                    x="hora",
                    y="Índice normalizado",
                    color="Indicador",
                    markers=True,
                    title=f"Patrón horario normalizado: flujo vehicular vs {nivel_flujo}",
                    color_discrete_map={
                        f"Personas implicadas: {nivel_flujo}": COLOR_LESIVIDAD.get(nivel_flujo, "#922B21"),
                        "Flujo vehicular": "#16324F",
                    },
                )
                fig_norm.update_traces(marker=dict(size=8))
                fig_norm = aplicar_estilo_figura(fig_norm, titulo_x="Hora del día", titulo_y="Índice normalizado", alto=460)
                fig_norm.update_xaxes(dtick=1)
                fig_norm = aplicar_espacio_leyenda(fig_norm, y=1.18, top=145)
                st.plotly_chart(fig_norm, use_container_width=True)

            st.subheader("Evolución mensual: flujo y lesividad")
            acc_mes_les = df.groupby(["anio", "mes", COL_LESIVIDAD], observed=False).size().reset_index(name="personas_implicadas")
            flujo_mes = flujo.groupby(["anio", "mes"], as_index=False, observed=False)["vehiculos"].sum()
            comparacion_mes = acc_mes_les.merge(flujo_mes, on=["anio", "mes"], how="inner")
            comparacion_mes = comparacion_mes[comparacion_mes["vehiculos"] > 0].copy()

            if not comparacion_mes.empty:
                comparacion_mes["periodo"] = (
                    comparacion_mes["anio"].astype(int).astype(str)
                    + "-"
                    + comparacion_mes["mes"].astype(int).astype(str).str.zfill(2)
                )
                comparacion_mes["personas_por_100k_vehiculos"] = (
                    comparacion_mes["personas_implicadas"] / comparacion_mes["vehiculos"]
                ) * 100000

                fig_mes = px.line(
                    comparacion_mes,
                    x="periodo",
                    y="personas_por_100k_vehiculos",
                    color=COL_LESIVIDAD,
                    markers=True,
                    category_orders={COL_LESIVIDAD: ORDEN_LESIVIDAD},
                    color_discrete_map=COLOR_LESIVIDAD,
                    title="Personas implicadas por cada 100.000 vehículos registrados, según mes y lesividad",
                )
                fig_mes.update_traces(marker=dict(size=7))
                fig_mes = aplicar_estilo_figura(
                    fig_mes,
                    titulo_x="Periodo",
                    titulo_y="Personas por 100.000 vehículos",
                    alto=500,
                )
                fig_mes.update_xaxes(tickangle=-35)
                fig_mes = aplicar_espacio_leyenda(fig_mes, y=1.18, top=145)
                st.plotly_chart(fig_mes, use_container_width=True)

            st.subheader("Mapa de estaciones permanentes de aforo")
            if {"lat", "lon", "estacion"}.issubset(set(flujo.columns)):
                estaciones = (
                    flujo.dropna(subset=["lat", "lon"])
                    .groupby(["estacion", "lat", "lon"], as_index=False, observed=False)["vehiculos"]
                    .sum()
                )

                mapa_est = folium.Map(location=[40.4167, -3.7033], zoom_start=11, tiles="CartoDB positron")
                Fullscreen().add_to(mapa_est)

                for _, fila in estaciones.iterrows():
                    popup_texto = f"""
                    <b>Estación:</b> {fila.get('estacion', 'Sin dato')}<br>
                    <b>Vehículos registrados:</b> {formato_numero_es(fila.get('vehiculos', 0))}
                    """
                    folium.CircleMarker(
                        location=[fila["lat"], fila["lon"]],
                        radius=6,
                        color="#16324F",
                        fill=True,
                        fill_color="#2E86C1",
                        fill_opacity=0.78,
                        popup=folium.Popup(popup_texto, max_width=280),
                    ).add_to(mapa_est)

                st_folium(mapa_est, width=1200, height=620)
            else:
                st.info("No se encontraron columnas de estación, latitud y longitud en flujo.csv.")

    render_footer()


# ============================================================
# PIE DE PÁGINA
# ============================================================
