import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import base64
import os

# Configuración de la página
st.set_page_config(page_title="Cálculo de Pi - Monte Carlo", layout="wide", initial_sidebar_state="collapsed")

# Función a prueba de balas para cargar imágenes (busca la extensión automáticamente)
def get_base64_image(image_base_name):
    extensiones = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG']
    for ext in extensiones:
        path = image_base_name + ext
        if os.path.exists(path):
            mime = "image/jpeg" if ext.lower() in ['.jpg', '.jpeg'] else "image/png"
            with open(path, "rb") as img_file:
                return f"data:{mime};base64,{base64.b64encode(img_file.read()).decode()}"
    return "https://via.placeholder.com/150?text=Falta+" + image_base_name

# --- MEMORIA ACUMULATIVA (Session State) ---
if 'n_total' not in st.session_state:
    st.session_state.n_total = 0
    st.session_state.n_inside = 0
    # SOLUCIÓN AL BUG: Usamos listas nativas de Python en lugar de np.array
    # Esto evita que numpy rompa los tipos de datos al hacer "append"
    st.session_state.x_plot = []
    st.session_state.y_plot = []
    st.session_state.inside_plot = []

# --- ESTILOS CSS UNIFICADOS Y RESPONSIVOS ---
st.markdown("""
<style>
.main { background-color: #f8fafc; }

/* Recuadro de contexto histórico estructurado en filas */
.context-box {
    background-color: #e2e8f0;
    border-radius: 15px;
    border-left: 10px solid #0074D9;
    padding: 30px;
    display: flex;
    flex-direction: column;
    gap: 35px; /* Espacio generoso entre las dos historias */
    margin-bottom: 25px;
}

/* Cada fila que une una imagen con su texto específico */
.intro-row {
    display: flex;
    align-items: center;
    gap: 35px;
}

/* Contenedor individual para cada imagen */
.image-side-single {
    min-width: 150px;
    max-width: 150px;
    text-align: center;
}
.image-side-single img {
    width: 100%;
    height: auto;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* Sección de texto */
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
        padding: 20px !important;
        gap: 30px !important;
    }
    
    /* En el celular cada fila se apila verticalmente e individuales */
    .intro-row {
        flex-direction: column !important;
        gap: 12px !important;
        text-align: center !important;
    }
    
    .image-side-single {
        min-width: 120px !important;
        max-width: 120px !important;
        margin: 0 auto !important;
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
    img_logo = get_base64_image('logo_itba')
    if "Falta" not in img_logo:
        st.markdown(f'<img src="{img_logo}" width="150">', unsafe_allow_html=True)
    else:
        st.write("### ITBA")
with col_titulo:
    st.title("🎯 Calculando Pi con Dardos (Monte Carlo)")
st.write("---")

# Carga de imágenes
img_stokhos = get_base64_image('stokhos')
img_jvn = get_base64_image('jvn')

# --- RECUADRO DE CONTEXTO HISTÓRICO OPTIMIZADO ---
st.markdown(f"""
<div class="context-box">
    <div class="intro-row">
        <div class="image-side-single">
            <img src="{img_stokhos}" alt="Stokhos - Arquero Griego">
        </div>
        <div class="text-side">
            <p>
                Los arqueros de la Antigua Grecia practicaban tirando a un blanco que llamaban <b><i>stokhos</i></b> (στόχος). 
                Pese a su proverbial puntería, se daban cuenta que había pequeños factores <b><i>al azar</i></b> que los 
                hacían fallar ligeramente al blanco, y de allí proviene el término "estocástico" que usamos en la matemática actual.
            </p>
        </div>
    </div>
    
    <div class="intro-row">
        <div class="image-side-single">
            <img src="{img_jvn}" alt="John von Neumann">
        </div>
        <div class="text-side">
            <p>
                En el siglo XX, el matemático John von Neumann, inventor de las computadoras modernas, inspirado por el 
                Casino de Monte Carlo, notó que podía usar las simulaciones de <b><i>procesos estocásticos</i></b> para 
                realizar aproximaciones numéricas de ciertas cantidades.
            </p>
        </div>
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
    # Reiniciamos como listas
    st.session_state.x_plot = []
    st.session_state.y_plot = []
    st.session_state.inside_plot = []
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
        
        # Extendemos las listas, asegurando que no haya conflictos de Numpy
        st.session_state.x_plot.extend(new_x[:a_guardar].tolist())
        st.session_state.y_plot.extend(new_y[:a_guardar].tolist())
        st.session_state.inside_plot.extend(new_inside[:a_guardar].tolist())

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
        
        # Convertimos las listas a arrays JUSTO antes de graficar y forzando el tipo (dtype)
        x_v = np.array(st.session_state.x_plot, dtype=float)
        y_v = np.array(st.session_state.y_plot, dtype=float)
        d_v = np.array(st.session_state.inside_plot, dtype=bool) 
        
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
