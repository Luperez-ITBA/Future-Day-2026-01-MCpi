import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import base64
import os

# Configuración de la página (layout ancho)
st.set_page_config(page_title="Pi - Simulación de Montecarlo - ITBA", layout="wide", initial_sidebar_state="collapsed")

# Inicialización del Session State
if 'all_pi_estimates' not in st.session_state:
    st.session_state.all_pi_estimates = []
if 'total_points_global' not in st.session_state:
    st.session_state.total_points_global = 0

# Función para cargar imágenes locales en Base64
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    return "https://via.placeholder.com/180x240?text=Imagen+Local"

# --- Branding Hub (Logo ITBA + Título) ---
# Ocultar sidebar nativo
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        .main { background-color: #f1f5f9; }
        div.block-container { padding-top: 2rem; }
    </style>
""", unsafe_allow_html=True)

# Cabecera con Columnas
col_hub_l, col_hub_r = st.columns([1, 4])

with col_hub_l:
    if os.path.exists('logo_itba.png'):
        st.image('logo_itba.png', width=150)
    else:
        st.write("### ITBA")

with col_hub_r:
    # Título estilizado Hub
    st.markdown("<h1 style='font-size: 40px; margin-bottom: 0;'><span style='color: #000000;'>Pi (π):</span> <span style='color: #0074D9;'>Simulación de Montecarlo</span></h1>", unsafe_allow_html=True)
    st.write("Future Day 2026 - Departamento de Ciencias Exactas y Naturales")

st.write("---")

# --- INTRODUCCIÓN TEÓRICA ---
c_einstein_fp, c_fp_texto = st.columns([1.5, 6])

with c_einstein_fp:
    img_montecarlo = get_base64_image('montecarlo_teoria.png')
    st.markdown(f'<img src="{img_montecarlo}" width="180" style="border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">', unsafe_allow_html=True)

with c_fp_texto:
    st.markdown("""
    <div style="font-size: 20px; line-height: 1.6; background-color: #e2e8f0; padding: 25px; border-radius: 12px; border-left: 8px solid #0074D9; color: #0f172a; margin-bottom: 15px;">
        La simulación de Montecarlo es un método estadístico para estimar valores matemáticos difíciles de calcular analíticamente, 
        utilizando la <b>aleatoriedad</b> a nuestro favor. 
        <br><br>
        En este ejemplo, estimaremos <b>π (Pi)</b>. Imagina que lanzas dardos al azar dentro de un cuadrado de 2x2. 
        Si el cuadrado encierra un círculo unitario (de radio 1) centrado en el origen (0,0), la proporción de dardos 
        que caen dentro del círculo nos permite aproximar Pi utilizando la fórmula:
        
        <div style="text-align: center; font-size: 24px; margin: 15px 0;">
            <b>π ≈ 4 · (# Ocurrencias / # Repeticiones)</b>
        </div>
        
        <i>Piense en el hint que dio en la Intro la rifa, como la proporción de veces que ocurrió en el pasado un fenómeno
        bajo ciertas condiciones estableces sus probabilidades.</i>
    </div>
    """, unsafe_allow_html=True)

st.write("---")

# --- NUEVA DISPOSICIÓN EN COLUMNAS FIJAS ---
col_control, col_display = st.columns([1, 2.5], gap="large")

with col_control:
    st.subheader("Configuración")
    
    # User input N_puntos, semsibilidad slider
    n_puntos = st.slider("Número de dardos (N):", 100, 100000, 10000, step=100)
    st.write(f"Precalibrando simulación para tirar {n_puntos:,} dardos al azar...")
    
    st.write("") # Espaciador
    
    # Botón Simular (genera puntos)
    if st.button("🚶‍♂️ Generar Dardos", use_container_width=True):
        st.session_state.n_puntos = n_puntos
        st.session_state.total_points_global += n_puntos
        st.session_state.pi_points_generated = True
        
    st.write("") # Espaciador

    # Botón Reiniciar
    if st.button("🗑️ Reiniciar", use_container_width=True):
        st.session_state.all_pi_estimates = []
        st.session_state.total_points_global = 0
        st.session_state.pi_points_generated = False
        st.rerun()

# Espacio principal de visualización (Gráfico y Pestañas)
with col_display:
    N = st.session_state.get('n_puntos', 0)
    
    if N > 0:
        # Cálculos de Montecarlo
        # Coordenadas aleatorias entre [-1, 1]x[-1, 1] para un cuadrado area 4
        x = np.random.uniform(-1, 1, N)
        y = np.random.uniform(-1, 1, N)
        
        # Condición: adentro del círculo unitario (x^2 + y^2 <= 1^2) radio=1
        inside = x**2 + y**2 <= 1
        points_inside = np.sum(inside)
        
        # Estimación de Pi
        # Area(circulo)/Area(cuadrado) = pi*1^2 / (2*2) = pi/4
        # Area(circulo)/Area(cuadrado) appx points_inside / N
        ratio = points_inside / N
        pi_estimate = 4 * ratio
        st.session_state.all_pi_estimates.append(pi_estimate)

        st.divider()

        # =========================================================================
        # SECCIÓN MODIFICADA: VISUALIZACIÓN DEL GRÁFICO (Borde Cuadrado y Radio R=1)
        # =========================================================================
        # El resto del código de la simulación queda EXACTAMENTE IGUAL.
        
        st.subheader("Simulación Visual")
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Puntos adentro y afuera (logic remains same s=1 alpha=0.5)
        ax.scatter(x[inside], y[inside], color='#1f77b4', s=1, label='Adentro', alpha=0.5)
        ax.scatter(x[~inside], y[~inside], color='#ff7f0e', s=1, label='Afuera', alpha=0.5)
        
        # 1. Contorno del círculo unitario (Symmetric full circle to match symmetric point generation range [-1, 1]x[-1, 1])
        theta = np.linspace(0, 2 * np.pi, 200) # Changed from 0 to Pi/2 QI quarter circle
        x_circ = np.cos(theta)
        y_circ = np.sin(theta)
        ax.plot(x_circ, y_circ, color='black', linewidth=1.5) # Thin black line for boundary boundary line

        # 2. Add Square Border (Cuadrado $[-1, 1] \times [-1, 1]$ bounding box matching point range)
        import matplotlib.patches as patches # Safe insertion for necessary components locally
        rect = patches.Rectangle((-1, -1), 2, 2, linewidth=1.5, edgecolor='black', facecolor='none', linestyle='-') # Solid black border border bounding box
        ax.add_patch(rect)
        
        # 3. Add Radius Visual Indication line (Horizontal on positive x axis)
        ax.plot([0, 1], [0, 0], color='gray', linestyle='-') # Gray solid line origin to x=1 labeled 'R=1'
        ax.text(0.5, 0.05, 'R=1', fontsize=12, color='black') # label for R=1 explicit segment midpoint R=1 indication indication line text label

        ax.set_xlim(-1.1, 1.1) 
        ax.set_ylim(-1.1, 1.1)
        ax.set_aspect('equal')
        
        st.pyplot(fig, use_container_width=True)
        # =========================================================================
        # FIN DE LA SECCIÓN MODIFICADA
        # =========================================================================

        # Pestañas de análisis estadístico
        tab_pi_results, tab_pi_historico = st.tabs(["📉 Resultados de la Simulación Actual", "📈 Historial de Estimaciones"])

        with tab_pi_results:
            st.write(f"### Dardos tirados en esta tanda (N): {N:,}")
            
            # Métricas
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="✅ Dardos Adentro", value=f"{points_inside:,}")
            with col2:
                st.metric(label="❌ Dardos Afuera", value=f"{N - points_inside:,}")

            st.write("### Estimación de Pi")
            st.markdown(f"""
            <div style="font-size: 18px; line-height: 1.6; background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #cbd5e1; margin-bottom: 20px;">
                Usando la Ley de los Grandes Números del hint de Intro, sabemos que la frecuencia de ocurrencia se acerca a la probabilidad. 
                <br><br>
                Proporción de dardos adentro $\\approx \\pi / 4$
                <br>
                Por lo tanto, $\\pi \\approx 4 \cdot ( \\text{{Dardos Adentro}} / \\text{{Total Dardos}} )$
                <br><br>
                <b>Estimación actual de Pi para N={N:,} dardos:</b>
            </div>
            """, unsafe_allow_html=True)
            
            # Métrica Pi final
            error_abs = np.abs(np.pi - pi_estimate)
            st.metric(label="Estimación de Pi (π)", value=f"{pi_estimate:.6f}", delta=f"Real: {np.pi:.6f}, Error: {error_abs:.6f}")
            
            st.info("""
            💡 **Curiosidad:** Esta estimación es **probabilística**. No 'calcula' Pi, sino que se acerca a su valor 
            a medida que tiramos más y más dardos al azar.
            """)

        with tab_pi_historico:
            st.subheader("Historial de Estimaciones de Pi")
            
            if len(st.session_state.all_pi_estimates) > 0:
                hist_data = pd.DataFrame({
                    'Simulación #': range(1, len(st.session_state.all_pi_estimates) + 1),
                    'Estimación de Pi': st.session_state.all_pi_estimates
                })
                
                # Gráfico histórico
                st.write(f"Número total de estimaciones guardadas: {len(st.session_state.all_pi_estimates):,}")
                st.line_chart(hist_data, x='Simulación #', y='Estimación de Pi', color="#ff7f0e")
                
                st.write("---")
                
                # Promedio global de Pi
                pi_avg_global = np.mean(st.session_state.all_pi_estimates)
                error_abs_global = np.abs(np.pi - pi_avg_global)
                
                st.write("### Promedio Global acumulado")
                st.metric(label="Promedio Global de Pi (π) acumulado", value=f"{pi_avg_global:.6f}", delta=f"Error Abs Promedio: {error_abs_global:.6f}")
                st.write(f"Número total acumulado de dardos generados entre todas las simulaciones: {st.session_state.total_points_global:,}...")
            else:
                st.warning("No hay estimaciones guardadas aún. Dale clic a '🚶‍♂️ Generar Dardos' para simular.")
