import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import base64
import os

# Configuración de la página
st.set_page_config(page_title="Cálculo de Pi - Monte Carlo", layout="wide", initial_sidebar_state="collapsed")

# Función para cargar imágenes locales en el HTML (Base64)
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    return "https://via.placeholder.com/150?text=Imagen"

# --- MEMORIA ACUMULATIVA (Session State) ---
if 'n_total' not in st.session_state:
    st.session_state.n_total = 0
    st.session_state.n_inside = 0
    st.session_state.x_plot = np.array([], dtype=float)
    st.session_state.y_plot = np.array([], dtype=float)
    st.session_state.inside_plot = np.array([], dtype=bool)

# --- ESTILOS CSS UNIFICADOS Y RESPONSIVOS ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    
    /* Recuadro de contexto histórico adaptado */
    .context-box {
        background-color: #e2e8f0;
        border-radius: 15px;
        border-left: 10px solid #0074D9;
        padding: 30px;
        display: flex;
        align-items: center;
        gap: 35px;
        margin-bottom: 25px;
    }
    
    /* Contenedor de imágenes de la izquierda (Alineación vertical en PC) */
    .image-side {
        min-width: 150px;
        max-width: 150px;
        display: flex;
        flex-direction: column;
        gap: 15px;
        text-align: center;
    }
    .image-side img {
        width: 100%;
        height: auto;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Sección de texto a la derecha */
    .text-side {
        flex: 1;
    }
    .text-side p {
        font-size: 19px !important;
        line-height: 1.6;
        color: #1e293b;
        margin: 0;
    }

    /* Botón de navegación personalizado */
    .btn-nav {
        display: block;
        width: 100%;
        padding: 12px 0;
        background-color: #001f3f;
        color: #ffffff !important;
        text-align: center;
        border-radius: 10px;
        text-decoration: none !important;
        font-weight: 600;
        font-size: 16px;
        transition: background-color 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-top: 30px;
    }
    .btn-nav:hover, .btn-nav:visited, .btn-nav:active {
        text-decoration: none !important;
        color: white !important;
    }
    .btn-nav:hover {
        background-color: #0074D9;
    }

    /* --- PARCHE RESPONSIVO INTELIGENTE PARA CELULARES --- */
    @media (max-width: 768px) {
        h1 { font-size: 26px !important; }
        
        .context-box {
            flex-direction: column !important;
            padding: 20px !important;
            gap: 20px !important;
            text-align: center !important;
        }
        
        /* En el celular las imágenes se ponen una al lado de la otra en horizontal */
        .image-side {
            flex-direction: row !important;
            min-width: 100% !important;
            max-width: 100% !important;
            justify-content: center !important;
            gap: 15px !important;
        }
        .image-side img {
            width: 110px !important;
        }
        
        .text-side p {
            font-size: 16px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    if os.path.exists('logo_itba.png'):
        st.image('logo_itba.png', width=150)
    else:
        st.write("### ITBA")
with col_titulo:
    st.title("🎯 Calculando Pi con Dardos (Monte Carlo)")
st.write("---")

# Carga de imágenes en Base64
img_stokhos = get_base64_image('stokhos.png')
img_jvn = get_base64_image('jvn.png')

# --- RECUADRO DE CONTEXTO HISTÓRICO ---
st.markdown(f"""
    <div class="context-box">
        <div class="image-side">
            <img src="{img_stokhos}" alt="Stokhos - Arquero Griego">
            <img src="{img_jvn}" alt="John von Neumann">
        </div>
        <div class="text-side">
            <p>
                Los arqueros de la Antigua Grecia practicaban tirando a un blanco que llamaban <b><i>stokhos</i></b> (στόχος). 
                Pese a su proverbial puntería, se daban cuenta que había pequeños factores <b><i>al azar</i></b> que los 
                hacían fallar ligeramente al blanco, y de allí proviene el término "estocástico" que usamos en la matemática actual.
            </p>
            <p style="margin-top: 15px;">
                En el siglo XX, el matemático John von Neumann, inventor de las computadoras modernas, inspirado por el 
                Casino de Monte Carlo, notó que podía usar las simulaciones de <b><i>procesos estocásticos</i></b> para 
                realizar aproximaciones numéricas de ciertas cantidades.
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- CONTROLES DE ACUMULACIÓN ---
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
add_100 = col_btn1.button("➕ Agregar 100 puntos")
add_1000 = col_btn2.button("➕ Agregar 1.000 puntos")
add_10000 = col_btn3.button("🚀 Agregar 10.000 puntos")
reiniciar = col_btn4.button("🗑️ Reiniciar Simulación")

# Lógica de acumulación
if reiniciar:
    st.session_state.n_total = 0
    st.session_state.n_inside = 0
    st.session_state.x_plot = np.array([], dtype=float)
    st.session_state.y_plot = np.array([], dtype=float)
    st.session_state.inside_plot = np.array([], dtype=bool)
    st.rerun()

puntos_a_generar = 0
if add_100:
    puntos_a_generar = 100
elif add_1000:
    puntos_a_generar = 1000
elif add_10000:
    puntos_a_generar = 10000

if puntos_a_generar > 0:
    new_x = np.random.uniform(-1, 1, puntos_a_generar)
    new_y = np.random.uniform(-1, 1, puntos_a_generar)
    new_inside = (new_x**2 + new_y**2) <= 1
    
    st.session_state.n_total += puntos_a_generar
    st.session_state.n_inside += np.sum(new_inside)
    
    if len(st.session_state.x_plot) < 25000:
        espacio_libre = 25000 - len(st.session_state.x_plot)
        a_guardar = min(puntos_a_generar, espacio_libre)
        st.session_state.x_plot = np.append(st.session_state.x_plot, new_x[:a_guardar])
        st.session_state.y_plot = np.append(st.session_state.y_plot, new_y[:a_guardar])
        st.session_state.inside_plot = np.append(st.session_state.inside_plot, new_inside[:a_guardar])

st.write("---")

# --- DISPOSICIÓN CENTRADA SIMÉTRICA ---
if st.session_state.n_total > 0:
    col_pad1, col_izq, col_der, col_pad2 = st.columns([1, 4.5, 4.5, 1], gap="large")
    
    with col_izq:
        st.write("### 📊 Estado de la aproximación")
        
        pi_estimado = 4 * (st.session_state.n_inside / st.session_state.n_total)
        error_abs = abs(pi_estimado - np.pi)
        
        st.metric("Total de Dardos Lanzados", f"{st.session_state.n_total:,}")
        st.metric("Dardos dentro del blanco", f"{st.session_state.n_inside:,}")
        st.metric("Valor Estimado de π", f"{pi_estimado:.6f}")
        st.metric("Error Absoluto", f"{error_abs:.6f}")
        
        st.markdown(f"""
        $$\\frac{{N_{{dentro}}}}{{N_{{total}}}} \\approx \\frac{{\\text{{Área Círculo}}}}{{\\text{{Área Cuadrado}}}} = \\frac{{\\pi}}{{4}}$$
        
        Multiplicando la proporción por 4, obtenemos la estimación actual de $\\pi$. ¡Cuantos más puntos sumes, más estable se volverá el decimal!
        """)

    with col_der:
        fig, ax = plt.subplots(figsize=(5, 5))
        
        x_v = st.session_state.x_plot
        y_v = st.session_state.y_plot
        d_v = st.session_state.inside_plot.astype(bool) 
        
        if len(x_v) > 0:
            ax.scatter(x_v[d_v], y_v[d_v], color='#2ecc71', s=1.5, alpha=0.6, label='Dentro')
            ax.scatter(x_v[~d_v], y_v[~d_v], color='#e74c3c', s=1.5, alpha=0.6, label='Fuera')
        
        circle = plt.Circle((0, 0), 1, color='#001f3f', fill=False, linewidth=2.5, label='Blanco')
        ax.add_artist(circle)
        
        ax.set_xlim(-1.05, 1.05)
        ax.set_ylim(-1.05, 1.05)
        ax.set_aspect('equal')
        ax.axis('off') 
        
        st.pyplot(fig, use_container_width=True)
else:
    st.info("🎯 Hacé clic en los botones de arriba para empezar a lanzar dardos y ver la magia de Monte Carlo en tiempo real.")

# --- BOTÓN DE RETORNO AL HUB ---
st.write("---")
col_vacia1, col_boton_regreso, col_vacia2 = st.columns([1, 1, 1])
with col_boton_regreso:
    st.markdown('<a href="https://future-day-2026-hub.streamlit.app/" target="_blank" class="btn-nav">🔙 Volver al Hub Principal</a>', unsafe_allow_html=True)
