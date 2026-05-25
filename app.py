import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# =====================================
# CONFIGURACIÓN
# =====================================

st.set_page_config(
    page_title="Ingeniería de Materiales",
    layout="wide"
)

# =====================================
# CARGAR BASE DE DATOS
# =====================================

import os

# Buscamos de forma automática cualquier archivo que termine en .csv
archivos_csv = [f for f in os.listdir('.') if f.lower().endswith('.csv')]

if archivos_csv:
    # Si encuentra uno, agarra el primero que vea y lo lee
    df = pd.read_csv(archivos_csv[0])
else:
    # Si no encuentra ninguno, te avisa en la pantalla con un texto amigable
    st.error("¡Ups! No se encontró ningún archivo .csv en el repositorio. Revisa que esté subido.")
    st.stop()
# =====================================
# PROMEDIO CARBONO 
# =====================================    
# === PROMEDIO CARBONO (Búsqueda automática de columnas) ===
col_min = [c for c in df.columns if 'min' in c.lower() and ('c' in c.lower() or 'carb' in c.lower())]
col_max = [c for c in df.columns if 'max' in c.lower() and ('c' in c.lower() or 'carb' in c.lower())]

if col_min and col_max:
    # Si encuentra las columnas de mínimo y máximo, calcula el promedio real
    df['%C'] = df[[col_min[0], col_max[0]]].mean(axis=1)
else:
    # Si tu CSV solo tiene una columna directa de Carbono, la usa directamente
    col_directa = [c for c in df.columns if 'carb' in c.lower() or c.strip() == 'C']
    if col_directa:
        df['%C'] = df[col_directa[0]]
    else:
        # Si de plano no encuentra ninguna, crea valores de prueba para que no se rompa la gráfica
        df['%C'] = 0.5 
# =========================================================
# =====================================
# TÍTULO
# =====================================

st.title("Análisis de Propiedades Mecánicas del Acero")

st.write("""
Sitio web interactivo para analizar la influencia
del porcentaje de carbono y de los tratamientos térmicos
sobre las propiedades mecánicas del acero.
""")

# =====================================
# GRÁFICA 1
# =====================================

st.header("Líneas de tendencia: propiedades mecánicas vs porcentaje de carbono")

df_filtered = df[df['%C'] < 2.0]

fig1 = go.Figure()

mechanical_properties = {
    'UTS (MPa)': 'UTS (MPa)',
    'YS (MPa)': 'YS (MPa)',
    'Hardness (HB)': 'Hardness (HB)',
    'Elongation (%)': 'Elongation (%)'
}

x_min = df_filtered['%C'].min()
x_max = df_filtered['%C'].max()
x_range = np.array([x_min, x_max])

for prop_col, name in mechanical_properties.items():

    temp_df = df_filtered.dropna(subset=['%C', prop_col])

    if not temp_df.empty:

        slope, intercept = np.polyfit(
            temp_df['%C'],
            temp_df[prop_col],
            1
        )

        y_trend = slope * x_range + intercept

        fig1.add_trace(go.Scatter(
            x=x_range,
            y=y_trend,
            mode='lines',
            name=f'Tendencia {name}',
            line=dict(width=4)
        ))

fig1.update_layout(
    title="Propiedades mecánicas vs porcentaje de carbono",
    xaxis_title="Contenido de carbono promedio (%C)",
    yaxis_title="Valor de propiedad",
    template="plotly_dark",
    height=700
)

st.plotly_chart(fig1, use_container_width=True)

# =====================================
# GRÁFICA 2
# =====================================

st.header("UTS según grupo de tratamiento")

fig2 = px.box(
    df,
    x='Treatment Group',
    y='UTS (MPa)',
    title='UTS (MPa) por Grupo de Tratamiento',
    labels={
        'Treatment Group': 'Grupo de Tratamiento',
        'UTS (MPa)': 'Resistencia a la Tracción (MPa)'
    },
    template='plotly_dark',
    color='Treatment Group'
)

fig2.update_layout(
    height=650
)

st.plotly_chart(fig2, use_container_width=True)

# =====================================
# GRÁFICA 3
# =====================================

st.header("Dureza según grupo de tratamiento")

fig3 = px.box(
    df,
    x='Treatment Group',
    y='Hardness (HB)',
    title='Dureza (HB) por Grupo de Tratamiento',
    labels={
        'Treatment Group': 'Grupo de Tratamiento',
        'Hardness (HB)': 'Dureza (HB)'
    },
    template='plotly_dark',
    color='Treatment Group'
)

fig3.update_layout(
    height=650
)

st.plotly_chart(fig3, use_container_width=True)

# =====================================
# CONCLUSIONES
# =====================================

st.header("Conclusiones")

st.write("""
- El porcentaje de carbono influye significativamente
en las propiedades mecánicas del acero.

- Conforme aumenta el contenido de carbono,
la dureza y la resistencia mecánica tienden a aumentar.

- Los tratamientos térmicos producen variaciones importantes
en el comportamiento mecánico del material.

- Los diagramas tipo boxplot permiten visualizar
la dispersión y distribución de propiedades mecánicas
según el tratamiento aplicado.

- La visualización interactiva facilita el análisis
de grandes cantidades de datos experimentales.
""")
