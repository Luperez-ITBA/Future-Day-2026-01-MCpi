import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image # Necesitamos esta librería para manejar la imagen

# Configuración de página
st.set_page_config(page_title="Cálculo de Pi - Monte Carlo", layout="wide")

# Título solicitado
st.title("✨ Calculando Pi con Puntos al Azar!")
st.write("---")

# Barra lateral con el logo y el dial
with st.sidebar:
    # --- INSERCIÓN ELEGANTE DEL LOGO ---
    try:
        # Cargamos la imagen
        logo = Image.open('logo_itba.png')
        # La mostramos en la sidebar, centrada y con un ancho adecuado
        st.image(logo, use_container_width=True)
        # Un pequeño espacio separador
        st.write("---")
    except FileNotFoundError:
        # Si por alguna razón no encuentra el archivo en local,
        # mostramos un texto para que no de error la app.
        st.warning("No se encontró el archivo 'logo_itba.png'. Asegúrate de que esté en la misma carpeta.")

    # --- CONTROLES EXISTENTES ---
    st.header("Configuración")
    n_puntos = st.slider("Cantidad de puntos (N):", 
                         min_value=1000, 
                         max_value=1000000, 
                         value=500000, 
                         step=50000)
    st.info("Para optimizar el rendimiento, se visualiza una muestra representativa de los puntos.")

# --- LÓGICA MATEMÁTICA ---
x = np.random.uniform(-1, 1, n_puntos)
y = np.random.uniform(-1, 1, n_puntos)

distancia = x**2 + y**2
dentro = distancia <= 1
puntos_dentro = np.sum(dentro)

pi_estimado = 4 * (puntos_dentro / n_puntos)
error = abs(np.pi - pi_estimado)

# --- INTERFAZ ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Explicación: Método de Monte Carlo")
    st.markdown(r"""
    Utilizamos la relación entre el área de un círculo inscrito en un cuadrado:
    
    1. El área del **cuadrado** de lado 2 es $4$.
    2. El área del **círculo** de radio 1 es $\pi$.
    3. La proporción de puntos que caen dentro del círculo tiende a:
    
    $$\frac{N_{dentro}}{N_{total}} \approx \frac{\pi}{4}$$
    
    Multiplicando por 4, obtenemos nuestra aproximación de $\pi$.
    """)
    
    st.write("---")
    st.metric("π Estimado", f"{pi_estimado:.6f}")
    st.metric("Error Absoluto", f"{error:.6f}")

with col2:
    # Muestra para el gráfico
    max_ver = 50000
    if n_puntos > max_ver:
        indices = np.random.choice(range(n_puntos), max_ver, replace=False)
        x_v, y_v, d_v = x[indices], y[indices], dentro[indices]
    else:
        x_v, y_v, d_v = x, y, dentro

    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Dibujar puntos
    ax.scatter(x_v[d_v], y_v[d_v], color='#2ecc71', s=0.1, alpha=0.5, label='Dentro')
    ax.scatter(x_v[~d_v], y_v[~d_v], color='#e74c3c', s=0.1, alpha=0.5, label='Fuera')
    
    # Círculo y Radio
    circulo = plt.Circle((0, 0), 1, color='black', fill=False, linewidth=2)
    ax.add_artist(circulo)
    
    # Línea del radio indicativa
    ax.plot([0, 1], [0, 0], color='blue', linewidth=3, label='Radio (r=1)')
    ax.text(0.5, 0.05, 'r = 1', color='blue', fontsize=12, fontweight='bold')
    
    # Estética
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect('equal')
    ax.axis('off')
    
    st.pyplot(fig)