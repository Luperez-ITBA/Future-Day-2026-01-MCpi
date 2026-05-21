import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import os

# Configuración de la página
st.set_page_config(page_title="Cálculo de Pi - Monte Carlo", layout="wide", initial_sidebar_state="collapsed")

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
    
    /* Recuadro de contexto */
    .context-box {
        background-color: #e2e8f0;
        border-radius: 15px;
        border-left: 10px solid #0074D9;
        padding: 20px;
        margin-bottom: 20px;
    }
    .context-box p {
        font-size: 18px !important;
        line-height: 1.5;
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

    /* Ajustes responsivos para celulares */
    @media (max-width: 768px) {
        h1 { font-size: 26px !important; }
        .context-box p { font-size: 15px !important; }
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

# --- EXPLICACIÓN DE ENTRADA ---
st.markdown("""
    <div class="context-box">
        <p>
            Imaginá que lanzamos dardos completamente al azar dentro de un cuadrado. Si inscribimos un círculo perfecto 
            adentro, la proporción de dardos que caen dentro del círculo versus el total nos permite aproximar el 
            número matemático <b>π</b>. ¡Probá sumando puntos acumulados para ver la convergencia en acción!
        </p>
    </div>
""", unsafe_allow_html=True)

# --- CONTROLES DE ACUMULACIÓN (4 columnas) ---
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

# --- DISPOSICIÓN CENTRADA CON COLUMNAS DE COLCHÓN [1, 4.5, 4.5, 1] ---
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
        # Gráfico simétrico y perfectamente centrado en su columna
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
