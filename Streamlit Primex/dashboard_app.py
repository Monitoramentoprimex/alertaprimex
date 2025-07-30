# -*- coding: utf-8 -*-
# 🏗️ SISTEMA PRIME - DASHBOARD DE MONITORAMENTO
# Dashboard interativo para análise de oportunidades de subcontratação
# PRIMEX Consultoria - Sistema de Monitoramento de Obras e Oportunidades

# ============================================================================
# CÓDIGO PARA STREAMLIT
# ============================================================================

# --- Importações de Bibliotecas Essenciais para Streamlit ---
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# --- Importações para Geocodificação (Geopy) ---
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# --- REMOVIDO: Configurações de !pip install e !apt install (não necessárias no Streamlit) ---
# --- REMOVIDO: Importações e configurações de Selenium (não suportado facilmente no Streamlit Cloud) ---
# --- REMOVIDO: CHROME_PATH (não necessário) ---
# --- REMOVIDO: from google.colab import files e drive (não aplicável no Streamlit Cloud) ---

# Configuração de estilo (apenas para Plotly, Matplotlib/Seaborn não são usados diretamente para exibição)
# plt.style.use('seaborn-v0_8') # Comentado, pois não usaremos matplotlib/seaborn para exibir no Streamlit
# sns.set_palette("husl") # Comentado

# ============================================================================
# FUNÇÕES DE CARREGAMENTO E PROCESSAMENTO DE DADOS
# ============================================================================

# Função para carregar dados (AGORA APENAS DADOS DE EXEMPLO)
@st.cache_data # Adiciona cache para evitar recarregar dados a cada interação
def load_opportunities_data():
    """Carrega dados de oportunidades do sistema PRIME (usando dados de exemplo)."""
    st.info("⚠️ Carregando dados de exemplo para demonstração. A coleta real de dados não está configurada para este ambiente.")

    sample_data = [
        {
            'id_oportunidade': 1,
            'tipo_oportunidade': 'Alvará de Obra',
            'numero_alvara': '001/2024',
            'valor_obra': 1500000,
            'municipio': 'São Paulo',
            'status': 'Em execução',
            'score_oportunidade': 0.85,
            'prioridade': 'Alta',
            'sugestao_acao': 'Contato imediato - Obra em execução',
            'data_coleta': '2024-01-15T10:30:00',
            'endereco': 'Rua do exemplo, 100, São Paulo' # Adicionado endereço para geocodificação
        },
        {
            'id_oportunidade': 2,
            'tipo_oportunidade': 'Licenciamento Ambiental',
            'numero_processo': 'CETESB-2024-001',
            'valor_investimento': 2500000,
            'municipio': 'Guarulhos',
            'status': 'Em análise',
            'score_oportunidade': 0.92,
            'prioridade': 'Alta',
            'sugestao_acao': 'Acompanhar processo - Grande obra em análise',
            'data_coleta': '2024-01-15T10:30:00',
            'endereco': 'Avenida do exemplo, 200, Guarulhos'
        },
        {
            'id_oportunidade': 3,
            'tipo_oportunidade': 'REURB/Loteamento',
            'numero_processo': 'SPU-2024-001',
            'valor_estimado': 800000,
            'municipio': 'Osasco',
            'status': 'Em planejamento',
            'score_oportunidade': 0.65,
            'prioridade': 'Média',
            'sugestao_acao': 'Monitorar desenvolvimento - Projeto em planejamento',
            'data_coleta': '2024-01-15T10:30:00',
            'endereco': 'Praça do exemplo, 300, Osasco'
        },
        {
            'id_oportunidade': 4,
            'tipo_oportunidade': 'Alvará de Obra',
            'numero_alvara': '002/2024',
            'valor_obra': 800000,
            'municipio': 'Santo André',
            'status': 'Aprovado',
            'score_oportunidade': 0.75,
            'prioridade': 'Média',
            'sugestao_acao': 'Contato em 1-2 semanas',
            'data_coleta': '2024-01-15T10:30:00',
            'endereco': 'Rua dos testes, 400, Santo André'
        },
        {
            'id_oportunidade': 5,
            'tipo_oportunidade': 'Licenciamento Ambiental',
            'numero_processo': 'CETESB-2024-002',
            'valor_investimento': 1800000,
            'municipio': 'São Bernardo do Campo',
            'status': 'Em análise',
            'score_oportunidade': 0.88,
            'prioridade': 'Alta',
            'sugestao_acao': 'Acompanhar processo - Grande obra em análise',
            'data_coleta': '2024-01-15T10:30:00',
            'endereco': 'Avenida Brasil, 500, São Bernardo do Campo'
        },
        # NOVOS DADOS DE EXEMPLO PARA TESTE DE GEOLOCALIZAÇÃO E FOCO
        {
            'id_oportunidade': 6,
            'tipo_oportunidade': 'Infraestrutura Viária',
            'numero_processo': 'DER-SP-001',
            'valor_investimento': 50000000,
            'municipio': 'Campinas',
            'status': 'Em licitação',
            'score_oportunidade': 0.95,
            'prioridade': 'Alta',
            'sugestao_acao': 'Contato DER para projeto',
            'data_coleta': '2024-02-01T09:00:00',
            'endereco': 'Avenida Guilherme Campos, Campinas'
        },
        {
            'id_oportunidade': 7,
            'tipo_oportunidade': 'Polo Industrial',
            'numero_processo': 'DESENV-SP-001',
            'valor_investimento': 120000000,
            'municipio': 'Jundiaí',
            'status': 'Aprovado',
            'score_oportunidade': 0.90,
            'prioridade': 'Alta',
            'sugestao_acao': 'Visita ao local e reunião',
            'data_coleta': '2024-02-05T14:15:00',
            'endereco': 'Rodovia Anhanguera, Jundiaí'
        }
    ]

    df = pd.DataFrame(sample_data)
    # Adiciona colunas de valor consistentes para facilitar o processamento
    df['valor_total_oportunidade'] = df.apply(lambda row: row.get('valor_obra', row.get('valor_investimento', row.get('valor_estimado', 0))), axis=1)
    return df

# Geocodificador (usando Nominatim)
geolocator = Nominatim(user_agent="primex_monitoramento_app", timeout=10)

@st.cache_data # Adiciona cache para geocodificação
def geocode_address(address, attempt=1):
    """
    Tenta geocodificar um endereço.
    Implementa um mecanismo de retry simples e delay para evitar bloqueios.
    """
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        if attempt <= 3: # Tentar até 3 vezes
            st.warning(f"Erro de geocodificação para '{address}' (tentativa {attempt}): {e}. Tentando novamente em 2 segundos...")
            time.sleep(2) # Espera 2 segundos antes de tentar novamente
            return geocode_address(address, attempt + 1)
        else:
            st.error(f"Falha na geocodificação para '{address}' após múltiplas tentativas: {e}")
            return None, None
    except Exception as e:
        st.error(f"Erro inesperado na geocodificação para '{address}': {e}")
        return None, None

# ============================================================================
# FUNÇÃO PRINCIPAL DO DASHBOARD STREAMLIT
# ============================================================================

def main_dashboard():
    st.title("🏗️ SISTEMA PRIME - DASHBOARD DE MONITORAMENTO")
    st.markdown("Dashboard interativo para análise de oportunidades de subcontratação")
    st.markdown("---")

    df_opportunities = load_opportunities_data()

    if df_opportunities is not None and not df_opportunities.empty:
        # --- PROCESSAMENTO DE DADOS NO STREAMLIT ---
        df_opportunities['data_coleta'] = pd.to_datetime(df_opportunities['data_coleta'])

        # Aplicar geocodificação
        st.subheader("📍 Geocodificação das Oportunidades")
        if 'endereco' in df_opportunities.columns:
            # st.progress bar para mostrar o progresso da geocodificação
            addresses_to_geocode = df_opportunities['endereco'].dropna().unique()
            total_addresses = len(addresses_to_geocode)
            if total_addresses > 0:
                st.info(f"Geocodificando {total_addresses} endereços únicos. Isso pode levar um tempo.")
                progress_bar = st.progress(0)
                latitudes = []
                longitudes = []
                for i, address in enumerate(df_opportunities['endereco']):
                    lat, lon = geocode_address(address)
                    latitudes.append(lat)
                    longitudes.append(lon)
                    progress_bar.progress((i + 1) / len(df_opportunities))
                df_opportunities['latitude'] = latitudes
                df_opportunities['longitude'] = longitudes
                st.success("✅ Geocodificação concluída!")
            else:
                st.warning("Nenhum endereço encontrado para geocodificação.")
        else:
            st.warning("Coluna 'endereco' não encontrada para geocodificação.")
            df_opportunities['latitude'] = np.nan
            df_opportunities['longitude'] = np.nan


        # Define a coluna de valor para os gráficos
        valor_col_name = 'valor_total_oportunidade'

        # ============================================================================
        # VISÃO GERAL DAS OPORTUNIDADES
        # ============================================================================
        st.header("📊 Visão Geral das Oportunidades")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total de Oportunidades", len(df_opportunities))
        with col2:
            st.metric("Tipos de Oportunidade", df_opportunities['tipo_oportunidade'].nunique())
        with col3:
            st.metric("Municípios Cobertos", df_opportunities['municipio'].nunique())
        with col4:
            st.metric("Valor Total Estimado", f"R$ {df_opportunities[valor_col_name].sum():,.2f}")

        st.markdown("---")

        # ============================================================================
        # VISUALIZAÇÕES INTERATIVAS
        # ============================================================================
        st.header("📈 Visualizações Interativas")

        # Layout com colunas para gráficos
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            # 1. Gráfico de pizza - Distribuição por prioridade
            fig1 = px.pie(
                df_opportunities,
                names='prioridade',
                title='🎯 Distribuição por Prioridade',
                color_discrete_map={
                    'Alta': '#e74c3c', # Vermelho
                    'Média': '#f39c12', # Laranja
                    'Baixa': '#27ae60' # Verde
                }
            )
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)

        with chart_col2:
            # 2. Gráfico de barras - Distribuição por tipo
            tipo_counts = df_opportunities['tipo_oportunidade'].value_counts().reset_index()
            tipo_counts.columns = ['Tipo', 'Quantidade']
            fig2 = px.bar(
                tipo_counts,
                x='Tipo',
                y='Quantidade',
                title='📋 Distribuição por Tipo de Oportunidade',
                labels={'Tipo': 'Tipo de Oportunidade', 'Quantidade': 'Quantidade'},
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)

        # Gráfico de dispersão - Score vs Valor
        fig3 = px.scatter(
            df_opportunities,
            x=valor_col_name,
            y='score_oportunidade',
            color='prioridade',
            size='valor_total_oportunidade', # Tamanho da bolha pelo valor
            hover_data=['municipio', 'status', 'tipo_oportunidade', 'sugestao_acao'],
            title='💰 Score vs Valor das Oportunidades',
            labels={valor_col_name: 'Valor (R$)', 'score_oportunidade': 'Score'},
            color_discrete_map={
                'Alta': '#e74c3c',
                'Média': '#f39c12',
                'Baixa': '#27ae60'
            }
        )
        st.plotly_chart(fig3, use_container_width=True)

        # Gráfico de barras - Top municípios
        top_municipios = df_opportunities['municipio'].value_counts().head(10).reset_index()
        top_municipios.columns = ['Município', 'Quantidade']
        fig4 = px.bar(
            top_municipios,
            x='Município',
            y='Quantidade',
            title='🏙️ Top 10 Municípios com Mais Oportunidades',
            labels={'Município': 'Município', 'Quantidade': 'Quantidade de Oportunidades'},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig4, use_container_width=True)

        st.markdown("---")

        # ============================================================================
        # MAPA DE OPORTUNIDADES
        # ============================================================================
        st.header("🗺️ Mapa de Oportunidades")

        df_map = df_opportunities.dropna(subset=['latitude', 'longitude']).copy()

        if not df_map.empty:
            # Criar mapa centrado na média das coordenadas das oportunidades geocodificadas
            map_center_lat = df_map['latitude'].mean()
            map_center_lon = df_map['longitude'].mean()

            mapa = folium.Map(
                location=[map_center_lat, map_center_lon],
                zoom_start=9,
                tiles='OpenStreetMap'
            )

            # Adicionar marcadores para cada oportunidade geocodificada
            for idx, row in df_map.iterrows():
                if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                    popup_html = f"""
                    <div style='width: 250px;'>
                        <h4>{row.get('tipo_oportunidade', 'Oportunidade')} - {row.get('municipio', 'N/A')}</h4>
                        <p><strong>Endereço:</strong> {row.get('endereco', 'N/A')}</p>
                        <p><strong>Valor:</strong> R$ {row.get(valor_col_name, 0):,.2f}</p>
                        <p><strong>Score:</strong> {row.get('score_oportunidade', 0):.2f}</p>
                        <p><strong>Prioridade:</strong> {row.get('prioridade', 'N/A')}</p>
                        <p><strong>Ação Sugerida:</strong> {row.get('sugestao_acao', 'N/A')}</p>
                        <p><strong>Status:</strong> {row.get('status', 'N/A')}</p>
                    </div>
                    """
                    # Cor do marcador baseada na prioridade
                    color_map = {
                        'Alta': 'red',
                        'Média': 'orange',
                        'Baixa': 'green'
                    }
                    marker_color = color_map.get(row.get('prioridade', 'Baixa'), 'blue') # Padrão azul

                    folium.Marker(
                        location=[row['latitude'], row['longitude']],
                        popup=folium.Popup(popup_html, max_width=300),
                        tooltip=f"{row.get('tipo_oportunidade', 'Oportunidade')} - {row.get('municipio', 'N/A')}",
                        icon=folium.Icon(color=marker_color, icon='info-sign')
                    ).add_to(mapa)

            # Exibir mapa usando streamlit-folium
            st.folium_static(mapa) # Usar st.folium_static() para exibir mapas Folium no Streamlit

        else:
            st.warning("⚠️ Nenhum dado com coordenadas válidas para exibir no mapa.")

        st.markdown("---")

        # ============================================================================
        # ANÁLISE DETALHADA E RECOMENDAÇÕES
        # ============================================================================
        st.header("🔍 Análise Detalhada e Recomendações")

        # Filtros interativos
        selected_tipo = st.selectbox(
            "Filtrar por Tipo de Oportunidade:",
            ['Todos'] + list(df_opportunities['tipo_oportunidade'].unique())
        )

        if selected_tipo != 'Todos':
            df_filtered = df_opportunities[df_opportunities['tipo_oportunidade'] == selected_tipo]
        else:
            df_filtered = df_opportunities

        st.subheader(f"Resumo para {selected_tipo.lower()} oportunidades")
        col_det1, col_det2, col_det3 = st.columns(3)
        with col_det1:
            st.metric("Total Filtrado", len(df_filtered))
        with col_det2:
            st.metric("Score Médio", f"{df_filtered['score_oportunidade'].mean():.2f}")
        with col_det3:
            st.metric("Valor Médio", f"R$ {df_filtered[valor_col_name].mean():,.2f}")

        st.write("### Oportunidades de Alta Prioridade (Filtradas)")
        alta_prioridade = df_filtered[df_filtered['prioridade'] == 'Alta']
        if not alta_prioridade.empty:
            st.dataframe(alta_prioridade[['tipo_oportunidade', 'municipio', 'valor_total_oportunidade', 'score_oportunidade', 'sugestao_acao']].sort_values('valor_total_oportunidade', ascending=False))
        else:
            st.info("Nenhuma oportunidade de alta prioridade encontrada para esta seleção.")

        st.write("### Top Municípios com Oportunidades (Filtradas)")
        top_municipios_filtered = df_filtered['municipio'].value_counts().head(5)
        st.dataframe(top_municipios_filtered)

        st.markdown("---")

        # ============================================================================
        # FOOTER (Informações de Contato)
        # ============================================================================
        st.markdown("---")
        st.markdown("### 🏢 PRIMEX CONSULTORIA")
        st.markdown("**Dashboard de Monitoramento de Obras e Oportunidades**")
        st.markdown("📧 Email: primexconsultoria4data@gmail.com")
        st.markdown("📱 WhatsApp: +55 11 97662 2584")
        st.markdown(f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
        st.markdown("---")

    else:
        st.error("❌ Não foi possível carregar os dados das oportunidades. Verifique a função de carregamento.")

# ============================================================================
# LÓGICA DE LOGIN
# ============================================================================

def login_page():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type="password")

    if st.sidebar.button("Entrar"):
        if username == "primex" and password == "primex@123": # Credenciais fixas de exemplo
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.sidebar.success("Login realizado com sucesso!")
            st.rerun() # Recarrega a página para mostrar o dashboard
        else:
            st.sidebar.error("Usuário ou senha incorretos.")

# --- Ponto de Entrada do Aplicativo Streamlit ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()