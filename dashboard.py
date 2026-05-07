import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Tentar importar módulos do Meta Business
try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.campaign import Campaign
    META_AVAILABLE = True
except ImportError:
    META_AVAILABLE = False

st.set_page_config(layout="wide", page_title="Dashboard Campanhas", page_icon="📊")

# CSS personalizado
st.markdown("""
    <style>
        [data-testid="stHeader"] {display: none;}
        .main .block-container {padding-top: 2rem;}
    </style>
""", unsafe_allow_html=True)

# ============================================
# FUNÇÃO PARA CARREGAR DADOS DO META BUSINESS (AUTOMÁTICO)
# ============================================
@st.cache_data(ttl=300)
def load_data_from_meta_auto():
    """Carrega dados automaticamente do Meta Business usando secrets.toml"""
    try:
        # Pegar credenciais do secrets.toml
        app_id = st.secrets["META_APP_ID"]
        app_secret = st.secrets["META_APP_SECRET"]
        access_token = st.secrets["META_ACCESS_TOKEN"]
        ad_account_id = st.secrets["DEFAULT_AD_ACCOUNT_ID"]
        
        # Inicializar API
        FacebookAdsApi.init(app_id, app_secret, access_token)
        account = AdAccount(f'act_{ad_account_id}')
        
        # Buscar campanhas
        params = {
            'fields': [
                Campaign.Field.id,
                Campaign.Field.name,
                Campaign.Field.status,
                Campaign.Field.objective,
                Campaign.Field.start_time,
                Campaign.Field.stop_time,
            ],
            'limit': 100
        }
        
        campaigns_raw = account.get_campaigns(params=params)
        
        # Buscar insights (métricas)
        insights_params = {
            'level': 'campaign',
            'date_preset': 'last_30d',
            'fields': [
                'campaign_id',
                'impressions',
                'clicks',
                'spend',
                'ctr'
            ]
        }
        
        insights_raw = account.get_insights(params=insights_params)
        
        # Criar dicionário de métricas
        metrics_dict = {}
        for insight in insights_raw:
            campaign_id = insight.get('campaign_id')
            if campaign_id:
                metrics_dict[campaign_id] = {
                    'impressions': int(insight.get('impressions', 0)),
                    'clicks': int(insight.get('clicks', 0)),
                    'spend': float(insight.get('spend', 0)),
                    'ctr': float(insight.get('ctr', 0))
                }
        
        # Montar DataFrame
        data = []
        for campaign in campaigns_raw:
            campaign_id = campaign.get('id')
            metric = metrics_dict.get(campaign_id, {})
            
            row = {
                'Nome da campanha': campaign.get('name', 'Sem nome'),
                'Status': campaign.get('status', 'UNKNOWN'),
                'Objetivo': campaign.get('objective', 'N/A'),
                'Valor usado (BRL)': metric.get('spend', 0),
                'Resultados': metric.get('clicks', 0),
                'Cliques no link': metric.get('clicks', 0),
                'Impressões': metric.get('impressions', 0),
                'CTR': metric.get('ctr', 0),
                'Início dos relatórios': campaign.get('start_time') or datetime.now() - timedelta(days=30),
                'Encerramento dos relatórios': campaign.get('stop_time') or datetime.now()
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Converter datas
        df['Início dos relatórios'] = pd.to_datetime(df['Início dos relatórios'])
        df['Encerramento dos relatórios'] = pd.to_datetime(df['Encerramento dos relatórios'])
        
        return df, True
        
    except Exception as e:
        st.error(f"Erro ao carregar dados do Meta Business: {str(e)}")
        return pd.DataFrame(), False

# ============================================
# FUNÇÃO PARA CARREGAR CSV
# ============================================
def load_data_from_csv(uploaded_file):
    """Carrega dados do CSV"""
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
        
        # Adicionar colunas que não existem no CSV
        if 'Status' not in df.columns:
            df['Status'] = 'Ativa'
        if 'Objetivo' not in df.columns:
            df['Objetivo'] = 'Não informado'
        
        # Converter datas
        df['Início dos relatórios'] = pd.to_datetime(df['Início dos relatórios'])
        df['Encerramento dos relatórios'] = pd.to_datetime(df['Encerramento dos relatórios'])
        
        # Converter colunas numéricas
        numeric_cols = ['Valor usado (BRL)', 'Resultados', 'Cliques no link', 'Impressões']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('R\$', '', regex=True)
                df[col] = df[col].str.replace(',', '.')
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Converter CTR
        if 'CTR (taxa de cliques no link)' in df.columns:
            df['CTR'] = df['CTR (taxa de cliques no link)'].astype(str).str.replace('%', '').str.replace(',', '.')
            df['CTR'] = pd.to_numeric(df['CTR'], errors='coerce').fillna(0)
        else:
            df['CTR'] = 0
        
        return df, True
        
    except Exception as e:
        st.error(f"Erro ao carregar CSV: {str(e)}")
        return pd.DataFrame(), False

# ============================================
# HEADER
# ============================================
header = st.container()
with header:
    col_busca, col_empty, col_notif, col_avatar = st.columns([2, 5, 0.4, 0.4])
    
    with col_busca:
        busca_texto = st.text_input("Buscar...", placeholder="Buscar campanhas...", label_visibility="collapsed", key="busca_input")
    
    with col_notif:
        st.markdown("<p style='text-align:center; font-size:22px; margin-top:5px; cursor:pointer;'>🔔</p>", unsafe_allow_html=True)
        
    with col_avatar:
        st.image("https://www.w3schools.com/howto/img_avatar.png", width=35)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.title("📁 Fonte de Dados")
    
    # Opção de fonte com radio button mais claro
    fonte_opcao = st.radio(
        "Selecione a fonte:",
        ["📁 CSV (Upload manual)", "🔗 Meta Business API (Automático)"],
        index=0
    )
    
    st.markdown("---")
    
    if fonte_opcao == "📁 CSV (Upload manual)":
        st.info("📁 Upload do CSV")
        uploaded_file = st.file_uploader("Importar CSV", type=["csv"], key="csv_uploader")
        use_meta = False
    else:
        st.info("🔗 Usando Meta Business API")
        st.caption("✅ Dados carregados automaticamente do secrets.toml")
        
        # Verificar se secrets.toml está configurado
        try:
            if st.secrets.get("META_APP_ID"):
                st.success("✅ Credenciais encontradas no secrets.toml")
                st.caption(f"Conta: {st.secrets.get('DEFAULT_AD_ACCOUNT_ID', 'N/A')}")
            else:
                st.warning("⚠️ secrets.toml não configurado")
        except:
            st.warning("⚠️ Arquivo secrets.toml não encontrado")
        
        use_meta = True
        
        # Botão para recarregar manualmente
        if st.button("🔄 Recarregar dados da API", type="secondary"):
            st.cache_data.clear()
            st.rerun()

# ============================================
# CARREGAR DADOS
# ============================================
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'fonte_atual' not in st.session_state:
    st.session_state.fonte_atual = None

df = pd.DataFrame()

# Carregar dados baseado na opção selecionada
if use_meta:
    # Carregar do Meta Business automaticamente
    if META_AVAILABLE:
        # Verificar se já tem dados em cache ou se precisa recarregar
        if st.session_state.fonte_atual != "meta" or st.session_state.df.empty:
            with st.spinner("🔄 Carregando dados automaticamente do Meta Business API..."):
                df, success = load_data_from_meta_auto()
                if success and not df.empty:
                    st.session_state.df = df
                    st.session_state.fonte_atual = "meta"
                    st.success(f"✅ {len(df)} campanhas carregadas automaticamente do Meta Business!")
                    st.rerun()
                else:
                    st.error("❌ Falha ao carregar dados da Meta API. Verifique suas credenciais no secrets.toml")
        else:
            df = st.session_state.df
            if not df.empty:
                st.success(f"✅ {len(df)} campanhas carregadas do Meta Business (cache)")
    else:
        st.error("❌ facebook_business não instalado. Execute: pip install facebook_business")
else:
    # Carregar do CSV manual
    if uploaded_file:
        with st.spinner("Carregando CSV..."):
            df, success = load_data_from_csv(uploaded_file)
            if success:
                st.session_state.df = df
                st.session_state.fonte_atual = "csv"
                st.success(f"✅ {len(df)} campanhas carregadas com sucesso!")
                st.rerun()
    else:
        df = st.session_state.df if st.session_state.fonte_atual == "csv" else pd.DataFrame()
        if not df.empty:
            st.success(f"✅ {len(df)} campanhas carregadas (cache)")

# ============================================
# DASHBOARD PRINCIPAL
# ============================================
if not df.empty:
    # Filtros
    st.markdown("<br>", unsafe_allow_html=True)
    col_title, col_f1, col_f2, col_f3 = st.columns([3, 1.5, 1.5, 1.5])
    
    with col_title:
        st.subheader("📊 Dashboard de Campanhas")
    
    with col_f1:
        min_date = df['Início dos relatórios'].min()
        max_date = df['Encerramento dos relatórios'].max()
        data_inicio = st.date_input("Início", value=min_date, min_value=min_date, max_value=max_date)
    
    with col_f2:
        data_fim = st.date_input("Fim", value=max_date, min_value=min_date, max_value=max_date)
    
    with col_f3:
        frequencia = st.selectbox("Frequência", ["Daily", "Weekly", "Monthly"])
    
    # Mostrar fonte atual
    fonte_texto = "Meta Business API" if st.session_state.fonte_atual == "meta" else "CSV"
    st.caption(f"📌 Fonte: {fonte_texto} | Total: {len(df)} campanhas")
    
    # Filtrar dados
    filtered_df = df[
        (df['Início dos relatórios'] >= pd.Timestamp(data_inicio)) & 
        (df['Encerramento dos relatórios'] <= pd.Timestamp(data_fim))
    ]
    
    if busca_texto:
        filtered_df = filtered_df[filtered_df['Nome da campanha'].str.contains(busca_texto, case=False, na=False)]
    
    # ============================================
    # MÉTRICAS
    # ============================================
    if not filtered_df.empty:
        total_invest = filtered_df['Valor usado (BRL)'].sum()
        total_res = filtered_df['Resultados'].sum()
        total_cliques = filtered_df['Cliques no link'].sum()
        total_impressions = filtered_df['Impressões'].sum()
        avg_ctr = (total_cliques / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = total_invest / total_cliques if total_cliques > 0 else 0
        num_campaigns = len(filtered_df)
        active_campaigns = len(filtered_df[filtered_df['Valor usado (BRL)'] > 0])
    else:
        total_invest = total_res = total_cliques = avg_ctr = num_campaigns = active_campaigns = avg_cpc = total_impressions = 0
    
    # Cards
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Investimento Total", f"R$ {total_invest:,.2f}", f"{len(filtered_df)} campanhas")
    with col2:
        st.metric("🎯 Resultados", f"{total_res:,.0f}")
    with col3:
        st.metric("🖱️ Cliques", f"{total_cliques:,.0f}", f"CPC: R$ {avg_cpc:.2f}")
    with col4:
        st.metric("📊 CTR Médio", f"{avg_ctr:.2f}%", f"{active_campaigns}/{num_campaigns} ativas")
    
    # Segunda linha
    if not filtered_df.empty:
        st.markdown("---")
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric("📈 Impressões", f"{total_impressions:,.0f}")
        with col6:
            st.metric("✅ Campanhas Ativas", f"{active_campaigns}")
        with col7:
            st.metric("📅 Período", f"{(data_fim - data_inicio).days} dias")
        with col8:
            roi = (total_res / total_invest * 100) if total_invest > 0 else 0
            st.metric("💵 ROI", f"{roi:.1f}%")
    
    # ============================================
    # GRÁFICO DE LINHA (ÚNICO GRÁFICO)
    # ============================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Total Revenue")
    
    if not filtered_df.empty:
        # Gráfico de linha igual ao seu original
        fig = go.Figure(go.Scatter(
            x=filtered_df['Nome da campanha'], 
            y=filtered_df['Valor usado (BRL)'], 
            mode='lines+markers', 
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        fig.update_layout(
            height=350, 
            template='plotly_dark', 
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title="Campanha",
            yaxis_title="Investimento (R$)"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aguardando dados para gerar gráficos.")
    
    # ============================================
    # TABELA
    # ============================================
    st.markdown("### Detalhamento das Campanhas")
    
    if not filtered_df.empty:
        display_cols = ['Nome da campanha', 'Resultados', 'Valor usado (BRL)', 'Cliques no link', 'Impressões']
        existing_cols = [col for col in display_cols if col in filtered_df.columns]
        
        display_df = filtered_df[existing_cols].copy()
        display_df['Valor usado (BRL)'] = display_df['Valor usado (BRL)'].apply(lambda x: f"R$ {x:,.2f}")
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Exportar
        csv_export = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar dados (CSV)",
            data=csv_export,
            file_name=f"campanhas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhuma campanha encontrada no período selecionado.")
    
    # Footer
    st.markdown("---")
    st.caption(f"📊 Dashboard atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Total: {len(df)} campanhas")

else:
    st.info("👈 Selecione uma fonte de dados na barra lateral para começar")