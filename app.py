import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración
st.set_page_config(
    page_title="Ingeniería de Materiales",
    layout="wide"
)

# Leer base de datos
df = pd.read_csv(
    "aceros.csv"
)

# Título principal
st.title("Análisis de Propiedades Mecánicas del Acero")

st.write("""
Aplicación interactiva para analizar la influencia del porcentaje
de carbono y los tratamientos térmicos sobre las propiedades
mecánicas del acero.
""")

# Sidebar
st.sidebar.header("Opciones")

property_selected = st.sidebar.selectbox(
    "Selecciona propiedad mecánica",
    [
        "UTS (MPa)",
        "YS (MPa)",
        "Hardness (HB)",
        "Elongation (%)"
    ]
)

# =========================
# GRÁFICA 1
# =========================

st.header("Propiedades mecánicas vs porcentaje de carbono")

fig1 = px.scatter(
    df,
    x="C (Max)",
    y=property_selected,
    color="Conditions",
    title=f"{property_selected} vs porcentaje de carbono",
    template="plotly_dark"
)

st.plotly_chart(fig1, use_container_width=True)

# =========================
# GRÁFICA 2
# =========================

st.header("Distribución según tratamiento térmico")

main_conditions = [
    "Hot Rolled",
    "Cold Drawn",
    "Normalized At 870 °C (1600 °F)",
    "Annealed At 855 °C (1575 °F)"
]

filtered_box = df[df["Conditions"].isin(main_conditions)]

fig2 = px.box(
    filtered_box,
    y="Conditions",
    x=property_selected,
    color="Conditions",
    title=f"Distribución de {property_selected}",
    template="plotly_dark"
)

fig2.update_layout(
    height=600,
    showlegend=False
)

st.plotly_chart(fig2, use_container_width=True)

# =========================
# GRÁFICA 3
# =========================

st.header("Annealed vs temperatura")

annealed_df = df[
    df["Conditions"].str.contains("Annealed", case=False, na=False)
].copy()

annealed_df["Temperature"] = (
    annealed_df["Conditions"]
    .str.extract(r'(\d+)')
    .astype(float)
)

fig3 = px.scatter(
    annealed_df,
    x="Temperature",
    y=property_selected,
    color="C (Max)",
    title=f"{property_selected} vs temperatura Annealed",
    template="plotly_dark"
)

st.plotly_chart(fig3, use_container_width=True)

# =========================
# GRÁFICA 4
# =========================

st.header("Normalized vs temperatura")

normalized_df = df[
    df["Conditions"].str.contains("Normalized", case=False, na=False)
].copy()

normalized_df["Temperature"] = (
    normalized_df["Conditions"]
    .str.extract(r'(\d+)')
    .astype(float)
)

fig4 = px.scatter(
    normalized_df,
    x="Temperature",
    y=property_selected,
    color="C (Max)",
    title=f"{property_selected} vs temperatura Normalized",
    template="plotly_dark"
)

st.plotly_chart(fig4, use_container_width=True)

# =========================
# CONCLUSIONES
# =========================

st.header("Conclusiones")

st.write("""
- El porcentaje de carbono influye significativamente
en las propiedades mecánicas del acero.

- Los tratamientos térmicos modifican el comportamiento
mecánico del material.

- El incremento de carbono generalmente aumenta
la dureza y resistencia.

- La visualización interactiva facilita el análisis
de materiales en ingeniería.
""")
