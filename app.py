import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="Acero al Carbono — Análisis de Propiedades",
    page_icon="🔩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .main { background-color: #0a0a0b; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }

    h1 { font-family: 'Bebas Neue', sans-serif !important; font-size: 3rem !important;
         letter-spacing: 0.06em !important; color: #e8c547 !important; }
    h2 { font-family: 'Bebas Neue', sans-serif !important; letter-spacing: 0.04em !important; color: #e8e8ec !important; }
    h3 { color: #e8c547 !important; }

    .hero-box {
        background: linear-gradient(135deg, #111114, #16161a);
        border: 1px solid #2a2a32;
        border-left: 4px solid #e8c547;
        border-radius: 4px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
    }
    .hero-box p { color: #6b6b7a; font-size: 1rem; line-height: 1.8; }

    .metric-card {
        background: #16161a;
        border: 1px solid #2a2a32;
        border-radius: 4px;
        padding: 1.2rem 1.5rem;
        text-align: center;
    }
    .metric-num {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2.5rem;
        color: #e8c547;
        line-height: 1;
    }
    .metric-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #6b6b7a;
        margin-top: 0.3rem;
    }

    .section-tag {
        font-family: 'DM Mono', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #e8c547;
        margin-bottom: 0.5rem;
    }

    .insight-box {
        background: #111114;
        border-left: 3px solid #e8c547;
        padding: 1rem 1.5rem;
        border-radius: 0 4px 4px 0;
        margin-top: 0.5rem;
        color: #6b6b7a;
        font-size: 0.88rem;
        line-height: 1.75;
    }
    .insight-box b { color: #e8e8ec; }

    .conc-card {
        background: #16161a;
        border: 1px solid #2a2a32;
        border-radius: 4px;
        padding: 1.5rem;
        height: 100%;
        transition: border-color 0.2s;
    }
    .conc-num {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2.5rem;
        color: #2a2a32;
        line-height: 1;
    }
    .conc-title { color: #e8c547 !important; font-size: 1rem !important; font-weight: 500; margin: 0.4rem 0; }
    .conc-text { color: #6b6b7a; font-size: 0.85rem; line-height: 1.7; }

    .stSelectbox label, .stMultiSelect label { color: #6b6b7a !important; font-family: 'DM Mono', monospace; font-size: 0.75rem; }
    div[data-testid="stSidebar"] { background: #111114; border-right: 1px solid #2a2a32; }
    div[data-testid="stSidebar"] * { color: #e8e8ec; }

    hr { border-color: #2a2a32; }
    .stTabs [data-baseweb="tab-list"] { background: #111114; border-bottom: 1px solid #2a2a32; }
    .stTabs [data-baseweb="tab"] { color: #6b6b7a; font-family: 'DM Mono', monospace; font-size: 0.75rem; letter-spacing: 0.1em; }
    .stTabs [aria-selected="true"] { color: #e8c547 !important; border-bottom: 2px solid #e8c547 !important; }
</style>
""", unsafe_allow_html=True)

# ── DARK PLOTLY THEME ────────────────────────────────────────
DARK = dict(
    paper_bgcolor='#16161a', plot_bgcolor='#16161a',
    font=dict(family='DM Mono, monospace', color='#6b6b7a', size=11),
    title_font=dict(family='Bebas Neue, sans-serif', size=20, color='#e8e8ec'),
    xaxis=dict(gridcolor='#2a2a32', zerolinecolor='#2a2a32', color='#6b6b7a'),
    yaxis=dict(gridcolor='#2a2a32', zerolinecolor='#2a2a32', color='#6b6b7a'),
    colorway=['#e8c547','#4fc3f7','#ef5350','#66bb6a','#ab47bc','#ff7043'],
    margin=dict(l=60, r=30, t=60, b=60),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#6b6b7a')),
    hoverlabel=dict(bgcolor='#111114', bordercolor='#2a2a32', font=dict(color='#e8e8ec'))
)

COLORS = ['#e8c547','#4fc3f7','#ef5350','#66bb6a','#ab47bc','#ff7043']
GROUPS = ['Quenched','Annealed','Normalized','Hot Rolled','Cold Drawn','Other']

# ── DATA LOADING ─────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(
            "Steel- Property and Composition (Carbon Steel) - Steel- Property and Composition (Carbon Steel).csv",
            sep=',', encoding='utf-8', dtype={'SAE Grade': str}
        )
    except FileNotFoundError:
        return None

    # Clean Conditions
    df['Conditions'] = df['Conditions'].str.replace('  ', ' ').str.strip().str.title()
    df['Conditions'] = df['Conditions'].str.replace('Cold Orawn', 'Cold Drawn', regex=False)
    df['Conditions'] = df['Conditions'].str.replace('Hot Rotted', 'Hot Rolled', regex=False)

    # %C average
    df['%C'] = df[['C (Min)', 'C (Max)']].mean(axis=1)

    # Mechanical props to numeric
    for col in ['UTS (MPa)', 'YS (MPa)', 'Hardness (HB)', 'Elongation (%)']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Treatment group
    def categorize(cond):
        cl = cond.lower()
        if 'quenched'    in cl: return 'Quenched'
        if 'annealed'    in cl: return 'Annealed'
        if 'normalized'  in cl: return 'Normalized'
        if 'hot rolled'  in cl: return 'Hot Rolled'
        if 'cold drawn'  in cl: return 'Cold Drawn'
        return 'Other'

    df['Treatment Group'] = df['Conditions'].apply(categorize)

    # Temperature extraction
    df['Temperature'] = df['Conditions'].str.extract(r'(\d+)').astype(float)

    return df


# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔩 Acero al Carbono")
    st.markdown("---")

    st.markdown("**Filtros**")

    df_raw = load_data()

    if df_raw is not None:
        selected_groups = st.multiselect(
            "Tratamientos",
            options=GROUPS,
            default=GROUPS,
        )
        c_range = st.slider(
            "Rango de %C",
            min_value=float(df_raw['%C'].min()),
            max_value=float(df_raw['%C'].max()),
            value=(float(df_raw['%C'].min()), float(df_raw['%C'].max())),
            step=0.01
        )

    st.markdown("---")
    st.markdown("""
    <div style="font-family:'DM Mono',monospace; font-size:0.65rem;
                letter-spacing:0.1em; color:#6b6b7a; text-align:center;">
        CIENCIA DE MATERIALES<br>ACEROS SAE AL CARBONO
    </div>
    """, unsafe_allow_html=True)


# ── MAIN CONTENT ─────────────────────────────────────────────
if df_raw is None:
    st.error("⚠️ No se encontró el archivo CSV. Asegúrate de que esté en la misma carpeta que app.py.")
    st.stop()

# Apply filters
df = df_raw[
    df_raw['Treatment Group'].isin(selected_groups) &
    df_raw['%C'].between(c_range[0], c_range[1])
].copy()


# ════════════════════════════════════════════════════════
#  HERO
# ════════════════════════════════════════════════════════
st.markdown("# 🔩 Propiedades del Acero al Carbono")
st.markdown("""
<div class="hero-box">
<p>
Exploración interactiva de las propiedades mecánicas de los aceros al carbono clasificados
según la norma <b style="color:#e8c547">SAE</b>. Analiza cómo la resistencia, dureza y ductilidad
varían en función del contenido de carbono (%C) y el tratamiento térmico aplicado.
Usa los filtros del panel izquierdo para personalizar el análisis.
</p>
</div>
""", unsafe_allow_html=True)

# Stats row
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-num">{len(df)}</div><div class="metric-label">Registros</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="metric-num">{df["SAE Grade"].nunique()}</div><div class="metric-label">Grados SAE</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="metric-num">{df["Treatment Group"].nunique()}</div><div class="metric-label">Tratamientos</div></div>', unsafe_allow_html=True)
with c4:
    avg_uts = int(df['UTS (MPa)'].mean()) if not df['UTS (MPa)'].isna().all() else 0
    st.markdown(f'<div class="metric-card"><div class="metric-num">{avg_uts}</div><div class="metric-label">UTS Promedio (MPa)</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
#  TABS
# ════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Tendencias vs %C",
    "📦 UTS por Tratamiento",
    "🔨 Dureza por Tratamiento",
    "🔥 Annealed vs Temp",
    "⚙️ Normalized vs Temp",
    "📝 Conclusiones"
])


# ── TAB 1: Trend lines ───────────────────────────────────────
with tab1:
    st.markdown('<div class="section-tag">/ Gráfica 01</div>', unsafe_allow_html=True)
    st.markdown("## Propiedades Mecánicas vs. %C")

    filtered = df[df['%C'] < 2.0].copy()
    props = {
        'UTS (MPa)':     ('#e8c547', 'UTS (MPa)'),
        'YS (MPa)':      ('#4fc3f7', 'YS (MPa)'),
        'Hardness (HB)': ('#ef5350', 'Dureza (HB)'),
        'Elongation (%)':('#66bb6a', 'Elongación (%)')
    }

    fig1 = go.Figure()
    xmin = filtered['%C'].min(); xmax = filtered['%C'].max()

    for col, (color, label) in props.items():
        tmp = filtered.dropna(subset=['%C', col])
        if len(tmp) < 2: continue
        slope, inter = np.polyfit(tmp['%C'], tmp[col], 1)
        fig1.add_trace(go.Scatter(
            x=[xmin, xmax], y=[slope*xmin+inter, slope*xmax+inter],
            mode='lines', name=label,
            line=dict(color=color, width=2.5)
        ))

    fig1.update_layout(
        **DARK,
        title="Líneas de Tendencia — Propiedades Mecánicas vs %C",
        xaxis_title="Contenido de Carbono Promedio (%C)",
        yaxis_title="Valor de Propiedad",
        height=480
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("""
    <div class="insight-box">
    <b>📌 Interpretación:</b> Se observa una tendencia <b>positiva</b> entre %C y las propiedades de resistencia
    (UTS, YS, Dureza), mientras que la <b>elongación disminuye</b> con mayor contenido de carbono.
    Esto refleja el endurecimiento por precipitación de carburo de hierro (cementita).
    </div>""", unsafe_allow_html=True)


# ── TAB 2: UTS Box ───────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-tag">/ Gráfica 02</div>', unsafe_allow_html=True)
    st.markdown("## UTS (MPa) por Grupo de Tratamiento")

    fig2 = go.Figure()
    for i, g in enumerate(GROUPS):
        vals = df[df['Treatment Group'] == g]['UTS (MPa)'].dropna()
        if vals.empty: continue
        fig2.add_trace(go.Box(
            y=vals, name=g,
            marker_color=COLORS[i], line_color=COLORS[i],
            opacity=0.7    #
        ))

    fig2.update_layout(
    
        title="UTS (MPa) por Grupo de Tratamiento",
        xaxis_title="Grupo de Tratamiento",
        yaxis_title="Resistencia a la Tracción (MPa)",
        showlegend=False, height=480
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("""
    <div class="insight-box">
    <b>📌 Interpretación:</b> El tratamiento de <b>Quenched & Tempered</b> produce los valores más altos de UTS.
    El <b>Cold Drawn</b> también incrementa la resistencia por endurecimiento por deformación.
    Los aceros <b>Annealed</b> muestran la menor resistencia, ideal para maquinabilidad.
    </div>""", unsafe_allow_html=True)


# ── TAB 3: Hardness Box ──────────────────────────────────────
with tab3:
    st.markdown('<div class="section-tag">/ Gráfica 03</div>', unsafe_allow_html=True)
    st.markdown("## Dureza (HB) por Grupo de Tratamiento")

    fig3 = go.Figure()
    for i, g in enumerate(GROUPS):
        vals = df[df['Treatment Group'] == g]['Hardness (HB)'].dropna()
        if vals.empty: continue
        fig3.add_trace(go.Box(
            y=vals, name=g,
            marker_color=COLORS[i], line_color=COLORS[i]
        ))

    fig3.update_layout(
        **DARK,
        title="Dureza (HB) por Grupo de Tratamiento",
        xaxis_title="Grupo de Tratamiento",
        yaxis_title="Dureza Brinell (HB)",
        showlegend=False, height=480
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("""
    <div class="insight-box">
    <b>📌 Interpretación:</b> La dureza Brinell sigue el mismo patrón que el UTS.
    El temple maximiza la dureza; el recocido produce aceros más blandos y deformables,
    adecuados para procesos de conformado metálico.
    </div>""", unsafe_allow_html=True)


# ── TAB 4: Annealed scatter ──────────────────────────────────
with tab4:
    st.markdown('<div class="section-tag">/ Gráfica 04</div>', unsafe_allow_html=True)
    st.markdown("## UTS vs Temperatura — Acero Recocido (Annealed)")

    ann = df[df['Conditions'].str.contains('Annealed', case=False, na=False)].dropna(subset=['Temperature','UTS (MPa)','%C'])

    if ann.empty:
        st.warning("No hay datos de Annealed en el rango filtrado.")
    else:
        # =================================================================
    # =================================================================
        # REEMPLAZO TOTALMENTE ALINEADO (CON DOBLE SANGRÍA)
        # =================================================================
        # Buscamos automáticamente las columnas correctas en tu archivo
        col_temp = [c for c in df.columns if 'temp' in c.lower()]
        col_uts_4 = [c for c in df.columns if 'uts' in c.lower() or 'tracc' in c.lower() or 'resis' in c.lower()]
        col_c_4 = [c for c in df.columns if '%c' in c.lower() or 'carbon' in c.lower()]
        col_grade = [c for c in df.columns if 'grade' in c.lower() or 'grado' in c.lower() or 'acer' in c.lower()]

        if col_temp and col_uts_4:
            n_temp = col_temp[0]
            n_uts = col_uts_4[0]
            n_c = col_c_4[0] if col_c_4 else None
            n_grade = col_grade[0] if col_grade else None
            
            # Limpiamos los datos para evitar que valores vacíos rompan la matemática
            ann_clean = ann.dropna(subset=[n_temp, n_uts])
            
            if len(ann_clean) > 0:
                fig4 = go.Figure()
                
                # 1. Configuración del color de los puntos (según %C si existe)
                color_data = ann_clean[n_c] if n_c else '#00CC96'
                
                # 2. Dibujamos los puntos reales
                fig4.add_trace(go.Scatter(
                    x=ann_clean[n_temp], 
                    y=ann_clean[n_uts],
                    mode='markers',
                    marker=dict(
                        color=color_data, 
                        colorscale='YlOrRd' if n_c else None, 
                        size=10,
                        showscale=True if n_c else False,
                        colorbar=dict(title='%C', thickness=12) if n_c else None
                    ),
                    text=ann_clean[n_grade] if n_grade else None,
                    hovertemplate="Grado: %{text}<br>T=%{x}°C<br>UTS=%{y} MPa<extra></extra>" if n_grade else "T=%{x}°C<br>UTS=%{y} MPa<extra></extra>",
                    name='Datos'
                ))
                
                # 3. Dibujamos la línea de tendencia solo si hay más de 1 punto disponible
                if len(ann_clean) > 1:
                    xs = ann_clean[n_temp].values
                    ys = ann_clean[n_uts].values
                    slope, inter = np.polyfit(xs, ys, 1)
                    
                    import numpy as np
                    xs_sorted = np.sort(xs)
                    ys_trend = slope * xs_sorted + inter
                    
                    fig4.add_trace(go.Scatter(
                        x=xs_sorted, 
                        y=ys_trend,
                        mode='lines', 
                        line=dict(color='#e8c547', width=2, dash='dash'),
                        name='Tendencia OLS'
                    ))
                
                # 4. Diseño estético de la gráfica
                fig4.update_layout(
                    title="UTS vs Temperatura - Annealed",
                    xaxis_title="Temperatura de Recocido",
                    yaxis_title="UTS (MPa)",
                    height=480,
                    template="plotly_dark"
                )
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.warning("No hay suficientes registros numéricos para mostrar la gráfica de Recocido.")
        else:
            st.warning("No se encontraron las columnas de Temperatura o UTS necesarias en tu archivo.")
        # =================================================================
    # =================================================================
        st.markdown("""
        <div class="insight-box">
        <b>📌 Interpretación:</b> En el recocido, temperaturas mayores tienden a <b>disminuir el UTS</b>
        (ablandamiento progresivo). Los puntos de mayor <b>%C</b> (colores más oscuros) mantienen
        valores de resistencia más altos incluso después del recocido.
        </div>""", unsafe_allow_html=True)


# ── TAB 5: Normalized scatter ────────────────────────────────
with tab5:
    st.markdown('<div class="section-tag">/ Gráfica 05</div>', unsafe_allow_html=True)
    st.markdown("## UTS vs Temperatura — Acero Normalizado (Normalized)")

    nor = df[df['Conditions'].str.contains('Normalized', case=False, na=False)].dropna(subset=['Temperature','UTS (MPa)','%C'])

    if nor.empty:
        st.warning("No hay datos de Normalized en el rango filtrado.")
    else:
        xs, ys = nor['Temperature'].values, nor['UTS (MPa)'].values
        slope, inter = np.polyfit(xs, ys, 1) if len(xs) > 1 else (0, ys.mean())
        xs_s = np.sort(xs)

        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(
            x=nor['Temperature'], y=nor['UTS (MPa)'],
            mode='markers',
            marker=dict(color=nor['%C'], colorscale='Viridis', size=10,
                colorbar=dict(title='%C', thickness=12, tickfont=dict(color='#6b6b7a'), titlefont=dict(color='#6b6b7a'))),
            text=nor['SAE Grade'], hovertemplate='SAE %{text}<br>T=%{x}°<br>UTS=%{y} MPa<extra></extra>',
            name='Datos'
        ))
        fig5.add_trace(go.Scatter(
            x=xs_s, y=slope*xs_s+inter,
            mode='lines', line=dict(color='#4fc3f7', width=2, dash='dash'),
            name='Tendencia OLS'
        ))
        fig5.update_layout(
            **DARK,
            title="UTS vs Temperatura — Normalized",
            xaxis_title="Temperatura de Normalizado",
            yaxis_title="UTS (MPa)", height=480
        )
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown("""
        <div class="insight-box">
        <b>📌 Interpretación:</b> El normalizado muestra <b>menor variación</b> de UTS con la temperatura
        respecto al recocido, produciendo una microestructura perlítica más uniforme.
        El %C sigue siendo el factor dominante para la resistencia final.
        </div>""", unsafe_allow_html=True)


# ── TAB 6: Conclusions ───────────────────────────────────────
with tab6:
    st.markdown('<div class="section-tag">/ Conclusiones</div>', unsafe_allow_html=True)
    st.markdown("## Hallazgos Principales")
    st.markdown("<br>", unsafe_allow_html=True)

    conclusions = [
        ("01", "Carbono como Factor Dominante",
         "El %C tiene correlación positiva con UTS, YS y dureza, y negativa con la elongación. Es el factor alótropo principal del acero."),
        ("02", "Temple Maximiza Resistencia",
         "Los aceros Quenched & Tempered alcanzan los valores más altos de UTS y dureza HB, con alta dispersión por efecto del revenido."),
        ("03", "Recocido Facilita Maquinabilidad",
         "El Annealed reduce resistencia y dureza, produciendo aceros más blandos y dúctiles, ideales para conformado y maquinado."),
        ("04", "Trefilado Refuerza Sin Calentar",
         "El Cold Drawn incrementa la resistencia por endurecimiento por deformación, sin alterar la composición química del acero."),
        ("05", "Temperatura Secundaria al %C",
         "En recocido y normalizado, la temperatura influye en las propiedades, pero su efecto es secundario frente al contenido de carbono."),
        ("06", "Variabilidad Intra-grupo en Temple",
         "Los box plots revelan alta variabilidad en el grupo Quenched, reflejando la influencia del grado SAE y la temperatura de revenido."),
    ]

    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]

    for i, (num, title, text) in enumerate(conclusions):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="conc-card">
                <div class="conc-num">{num}</div>
                <div class="conc-title">{title}</div>
                <div class="conc-text">{text}</div>
            </div>
            <br>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(232,197,71,0.06), rgba(79,195,247,0.04));
                border: 1px solid rgba(232,197,71,0.25); border-radius: 4px; padding: 2rem; margin-top: 1rem;">
    <h3 style="color:#e8c547 !important; font-family:'Bebas Neue',sans-serif; letter-spacing:0.06em;">
        🔬 Reflexión Final
    </h3>
    <p style="color:#6b6b7a; font-size:0.92rem; line-height:1.8; margin:0;">
        Los resultados confirman el modelo clásico de la metalurgia física: el carbono endurece el acero
        aumentando la resistencia a expensas de la ductilidad, y los tratamientos térmicos permiten ajustar
        este balance según las necesidades de la aplicación. Para la selección de materiales en ingeniería,
        es indispensable considerar simultáneamente el <b style="color:#e8c547">grado SAE</b> (composición) y el
        <b style="color:#4fc3f7">tratamiento térmico</b> (procesamiento), ya que ambos factores interactúan
        para definir el desempeño final de la pieza.
    </p>
    </div>
    """, unsafe_allow_html=True)
