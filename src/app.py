import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
 
# ─── Configuração da página ────────────────────────────────────────────────
 
st.set_page_config(
    page_title="ATC Radar",
    page_icon="✈",
    layout="wide",
)
 
st.title("✈ ATC Radar — Tráfego Aéreo em Tempo Real")
 
# ─── Sidebar: configurações ────────────────────────────────────────────────
 
with st.sidebar:
    st.header("⚙ Configurações")
 
    st.subheader("Área de cobertura")
    col1, col2 = st.columns(2)
    with col1:
        lat_min = st.number_input("Lat mín", value=-24.5, format="%.1f")
        lon_min = st.number_input("Lon mín", value=-48.5, format="%.1f")
    with col2:
        lat_max = st.number_input("Lat máx", value=-18.5, format="%.1f")
        lon_max = st.number_input("Lon máx", value=-42.5, format="%.1f")
 
    st.subheader("Filtros")
    alt_min = st.slider("Altitude mínima (ft)", 0, 50000, 0, step=1000)
    alt_max = st.slider("Altitude máxima (ft)", 0, 60000, 60000, step=1000)
    mostrar_solo = st.checkbox("Mostrar aeronaves no solo", value=False)
 
    st.subheader("Atualização")
    auto_refresh = st.checkbox("Auto-atualizar", value=False)
    if auto_refresh:
        intervalo = st.slider("Intervalo (segundos)", 10, 60, 15)
        st.rerun() if st.session_state.get("auto") else None
 
    atualizar = st.button("🔄 Atualizar dados", use_container_width=True)
 
# ─── Busca de dados (OpenSky Network) ─────────────────────────────────────
 
@st.cache_data(ttl=15)
def buscar_aeronaves(lamin, lamax, lomin, lomax):
    url = "https://opensky-network.org/api/states/all"
    params = {
        "lamin": lamin,
        "lamax": lamax,
        "lomin": lomin,
        "lomax": lomax,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("states", []) or []
    except requests.exceptions.Timeout:
        st.error("⚠ Timeout ao conectar com OpenSky. Tente novamente.")
        return []
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 429:
            st.warning("⚠ Rate limit atingido. Aguarde alguns segundos.")
        else:
            st.error(f"⚠ Erro HTTP: {e}")
        return []
    except Exception as e:
        st.error(f"⚠ Erro ao buscar dados: {e}")
        return []
 
# ─── Parsing dos dados ─────────────────────────────────────────────────────
 
def metros_para_pes(m):
    return round(m * 3.28084) if m is not None else None
 
def ms_para_knots(ms):
    return round(ms * 1.94384) if ms is not None else None
 
def formatar_altitude(ft):
    if ft is None:
        return "—"
    if ft > 1000:
        return f"FL{round(ft / 100):03d}"
    return f"{ft:,}ft"
 
def cor_por_altitude(ft, no_solo):
    if no_solo:
        return "gray"
    if ft is None:
        return "gray"
    if ft > 30000:
        return "blue"
    if ft > 15000:
        return "green"
    if ft > 5000:
        return "orange"
    return "red"
 
def squawk_alerta(squawk):
    alertas = {"7500": "🔴 HIJACK", "7600": "🟡 RADIO FAIL", "7700": "🔴 EMERGENCY"}
    return alertas.get(squawk, "")
 
def parsear_estados(estados):
    aeronaves = []
    for s in estados:
        if s[5] is None or s[6] is None:
            continue
        alt_ft = metros_para_pes(s[7])
        aeronaves.append({
            "icao24": s[0],
            "callsign": (s[1] or "").strip() or s[0].upper(),
            "pais": s[2],
            "longitude": s[5],
            "latitude": s[6],
            "altitude_ft": alt_ft,
            "altitude_str": formatar_altitude(alt_ft),
            "no_solo": s[8],
            "velocidade_kt": ms_para_knots(s[9]),
            "heading": s[10] or 0,
            "squawk": s[14] or "",
            "alerta": squawk_alerta(s[14] or ""),
            "fonte": ["ADS-B", "ASTERIX", "MLAT", "FLARM"][s[16]] if s[16] < 4 else "ADS-B",
        })
    return aeronaves
 
# ─── Busca e filtragem ─────────────────────────────────────────────────────
 
if atualizar:
    st.cache_data.clear()
 
estados_raw = buscar_aeronaves(lat_min, lat_max, lon_min, lon_max)
aeronaves = parsear_estados(estados_raw)
 
# Aplica filtros
aeronaves_filtradas = [
    a for a in aeronaves
    if (mostrar_solo or not a["no_solo"])
    and (a["altitude_ft"] is None or alt_min <= a["altitude_ft"] <= alt_max)
]
 
# ─── Métricas ──────────────────────────────────────────────────────────────
 
col1, col2, col3, col4 = st.columns(4)
col1.metric("✈ Aeronaves", len(aeronaves_filtradas))
col2.metric("🚨 Emergências", sum(1 for a in aeronaves_filtradas if "7700" in a["squawk"]))
col3.metric("📡 No solo", sum(1 for a in aeronaves_filtradas if a["no_solo"]))
col4.metric("🕐 Atualizado", datetime.now().strftime("%H:%M:%S"))
 
st.divider()
 
# ─── Layout: mapa + tabela ─────────────────────────────────────────────────
 
col_mapa, col_tabela = st.columns([2, 1])
 
with col_mapa:
    st.subheader("🗺 Radar")
 
    centro_lat = (lat_min + lat_max) / 2
    centro_lon = (lon_min + lon_max) / 2
 
    mapa = folium.Map(
        location=[centro_lat, centro_lon],
        zoom_start=7,
        tiles="CartoDB dark_matter",
    )
 
    for ac in aeronaves_filtradas:
        cor = cor_por_altitude(ac["altitude_ft"], ac["no_solo"])
        alerta_str = f"<br>⚠ {ac['alerta']}" if ac["alerta"] else ""
 
        popup_html = f"""
        <div style='font-family:monospace;min-width:160px'>
            <b style='font-size:14px'>{ac['callsign']}</b><br>
            <span style='color:gray'>{ac['icao24'].upper()}</span>{alerta_str}<br><br>
            🏳 {ac['pais']}<br>
            📡 {ac['fonte']}<br>
            ✈ Alt: <b>{ac['altitude_str']}</b><br>
            💨 Vel: <b>{ac['velocidade_kt'] or '—'} kt</b><br>
            🧭 Hdg: <b>{round(ac['heading'])}°</b><br>
            🔢 Squawk: {ac['squawk'] or '—'}
        </div>
        """
 
        folium.Marker(
            location=[ac["latitude"], ac["longitude"]],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=ac["callsign"],
            icon=folium.Icon(
                color=cor,
                icon="plane",
                prefix="fa",
            ),
        ).add_to(mapa)
 
    st_folium(mapa, use_container_width=True, height=520)
 
with col_tabela:
    st.subheader("📋 Faixas de voo")
 
    busca = st.text_input("🔍 Buscar callsign", placeholder="GLO1234...")
 
    df = pd.DataFrame(aeronaves_filtradas, columns=[
        "icao24", "callsign", "pais", "longitude", "latitude",
        "altitude_ft", "altitude_str", "no_solo", "velocidade_kt",
        "heading", "squawk", "alerta", "fonte",
    ])
 
    if busca:
        df = df[df["callsign"].str.contains(busca.upper(), na=False)]
 
    # Ordena emergências no topo
    df["_sort"] = df["squawk"].isin(["7700", "7500"]).astype(int)
    df = df.sort_values(["_sort", "altitude_ft"], ascending=[False, False])
 
    tabela = df[["callsign", "altitude_str", "velocidade_kt", "pais", "alerta"]].rename(columns={
        "callsign": "Callsign",
        "altitude_str": "Altitude",
        "velocidade_kt": "Vel (kt)",
        "pais": "País",
        "alerta": "Alerta",
    })
 
    st.dataframe(
        tabela,
        use_container_width=True,
        height=480,
        hide_index=True,
    )
 
# ─── Rodapé ────────────────────────────────────────────────────────────────
 
st.caption("Dados: OpenSky Network · Atualização manual ou automática · Uso não comercial")