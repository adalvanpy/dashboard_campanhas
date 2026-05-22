import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64

# Tentar importar módulos do Meta Business
try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.campaign import Campaign
    META_AVAILABLE = True
except ImportError:
    META_AVAILABLE = False

# Configuração da página
st.set_page_config(layout="wide", page_title="Dashboard", page_icon="📊")

# --- DICIONÁRIO PARA CONVERSÃO DE MESES (PT -> EN) ---
MESES_PT = {
    "Janeiro": "January",
    "Fevereiro": "February", 
    "Março": "March",
    "Abril": "April",
    "Maio": "May",
    "Junho": "June",
    "Julho": "July",
    "Agosto": "August",
    "Setembro": "September",
    "Outubro": "October",
    "Novembro": "November",
    "Dezembro": "December"
}

# --- CSS PARA LAYOUT ---
st.markdown("""
    <style>
        /* Remove header padrão */
        [data-testid="stHeader"] {
            display: none;
        }

        /* Container principal */
        .main .block-container {
            padding-top: 1.5rem;
            background-color: #FFFFFF;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: white;
            padding: 1rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }

        /* =========================
           MÉTRICAS
        ========================== */
        .metric-container {
            display: flex;
            justify-content: space-between;
            padding: 20px 0;
            border-top: 1px solid #f0f0f0;
            border-bottom: 1px solid #f0f0f0;
            margin: 10px 0 30px 0;
        }
        .metric-container-2 {
          display: flex;
          justify-content: space-between;
          padding-top: 6px;
          padding-bottom: 20px;
          border-bottom: 1px solid #f0f0f0;
          margin: 0 0 30px 0;
        }

        .metric-card {
            flex: 1;
            padding: 0 25px;
            border-right: 1px solid #eeeeee;
            transform: translateY(10px);
            transition: 0.3s ease;
        }

        .metric-card:last-child {
            border-right: none;
        }
             
        .metric-card:hover{
          transform: translateY(-6px);
        }

        .metric-label {
            color: #666666;
            font-size: 14px;
            font-weight: 500;
        }

        .metric-value {
            color: #111111;
            font-size: 28px;
            font-weight: 700;
            margin: 5px 0;
        }

        .metric-delta {
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .delta-up {
            color: #219653;
            background: #EBF7F0;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: bold;
        }

        .delta-down {
            color: #EB5757;
            background: #FDEEEE;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: bold;
        }
        .delta-neutral {
            color: #666666;
            background: #F0F0F0;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: bold;
        }

        /* =========================
           PAINEL UNIFICADO
        ========================== */
        .painel-unificado {
            border-radius: 28px;
            padding: 22px;
            background: linear-gradient(180deg, #0066FF, #0047B3);
            display: flex;
            flex-direction: column;
            gap: 14px;
            width: 320px;
            min-height: 500px;
            margin: 20px auto;
            box-shadow: 0 12px 35px rgba(0,0,0,0.18);
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            box-sizing: border-box;
        }
        .painel-unificado .nome {
            font-size: 18px;
            font-weight: 700;
            color: white;
            background: rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
            display: flex;
            align-items: center;
            justify-content: space-between;
            min-height: 60px;
            padding: 0 18px;
            width: 100%;
            border-radius: 18px;
            box-sizing: border-box;
        }
        .painel-unificado .valor,
        .painel-unificado .cliques,
        .painel-unificado .impressoes,
        .painel-unificado .ctr {
            font-size: 16px;
            font-weight: 700;
            color: #111827;
            background: rgba(255,255,255,0.96);
            display: flex;
            align-items: center;
            justify-content: space-between;
            min-height: 60px;
            padding: 0 18px;
            width: 100%;
            border-radius: 18px;
            box-sizing: border-box;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .painel-unificado .mesano {
            display: flex;
            gap: 12px;
            justify-content: space-between;
            width: 100%;
            box-sizing: border-box;
        }
        .painel-unificado .mesano .mes,
        .painel-unificado .mesano .ano {
            background: rgba(255,255,255,0.96);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            padding: 12px 18px;
            border-radius: 16px;
            font-size: 14px;
            font-weight: 700;
            color: #111827;
            text-align: flex-start;
        }
        .painel-unificado .mesano .mes {
          flex: 1.5;
         }

        .painel-unificado .mesano .ano {
          flex: 1;
        }
            
        .painel-unificado .logo {
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            width: 140px;
            height: 70px;
            margin: auto;
            margin-top: 18px;
        }
        .painel-unificado .delta-up {
            color: #219653;
            background: #EBF7F0;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 10px;
            display: inline-block;
        }
        .painel-unificado .delta-down {
            color: #EB5757;
            background: #FDEEEE;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 10px;
            display: inline-block;
        }
        .painel-unificado .delta-neutral {
            color: #666666;
            background: #F0F0F0;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 10px;
            display: inline-block;
        }

        /* =========================
           SELECTBOX
        ========================== */
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            min-height: 45px;
            border-radius: 8px !important;
            background-color: white !important;
            color: #333333 !important;
            border: 1px solid #E5E7EB !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
            padding: 0 10px !important;
        }

        [data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {
            border: 1px solid #D1D5DB !important;
        }

        [data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-visible,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
            border: 1px solid #2563EB !important;
            outline: none !important;
            box-shadow: 0 0 0 2px rgba(37,99,235,0.15) !important;
        }

        [data-testid="stSelectbox"] * {
            outline: none !important;
        }

        /* =========================
           FILE UPLOADER
        ========================== */
        [data-testid="stFileUploader"] {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }

        [data-testid="stFileUploader"] section {
            border-radius: 10px !important;
            border: 1px dashed #D1D5DB !important;
            background-color: #FAFAFA !important;
            padding: 1rem !important;
        }

        /* =========================
           BOTÕES
        ========================== */
        .stButton > button {
            width: 100%;
            border-radius: 10px;
            height: 45px;
            border: 1px solid #D1D5DB;
            background-color: white;
            color: #111827;
            font-weight: 500;
            transition: 0.2s ease;
        }

        .stButton > button:hover {
            border-color: #2563EB;
            color: #2563EB;
        }
        .linhas {
          background-color: #0066FF;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
    
        .linhas th {
        text-align: center;
        padding: 12px;
        background-color: #0066FF;
        color: white;
    }
    
    .coluna td {
        border-top: 1px solid #ddd; /* Apenas borda superior */
        padding: 8px;
        text-align: center; /* Centraliza os dados */
    }
    
    /* Para remover bordas laterais e inferiores */
    .coluna td:first-child {
        border-left: none;
    }
    
    .coluna td:last-child {
        border-right: none;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# FUNÇÕES DE CARREGAMENTO DE DADOS
# ============================================

@st.cache_data(ttl=300)
def load_data_from_meta_auto():
    """Carrega dados do Meta Business API"""
    try:
        app_id = st.secrets["META_APP_ID"]
        app_secret = st.secrets["META_APP_SECRET"]
        access_token = st.secrets["META_ACCESS_TOKEN"]
        ad_account_id = st.secrets["DEFAULT_AD_ACCOUNT_ID"]
        
        FacebookAdsApi.init(app_id, app_secret, access_token)
        account = AdAccount(f'act_{ad_account_id}')
        
        # Buscar insights
        insights_params = {
            'level': 'campaign',
            'date_preset': 'last_30d',
            'fields': ['campaign_name', 'spend', 'clicks', 'impressions', 'ctr', 'date_start']
        }
        insights = account.get_insights(params=insights_params)
        
        data = []
        for i in insights:
            data.append({
                'Nome': i.get('campaign_name', 'Sem nome'),
                'Investimento': float(i.get('spend', 0)),
                'Cliques': int(i.get('clicks', 0)),
                'Impressões': int(i.get('impressions', 0)),
                'CTR': float(i.get('ctr', 0)) * 100,
                'Data': pd.to_datetime(i.get('date_start', datetime.now()))
            })
        
        df = pd.DataFrame(data)
        return df, True
        
    except Exception as e:
        st.error(f"Erro Meta API: {str(e)}")
        return pd.DataFrame(), False

@st.cache_data(ttl=300)
def load_data_from_csv(uploaded_file):
    """Carrega dados do CSV"""
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
        
        # Normalizar colunas
        if 'Valor usado (BRL)' in df.columns:
            invest_col = 'Valor usado (BRL)'
        elif 'spend' in df.columns:
            invest_col = 'spend'
        else:
            invest_col = 'Investimento'
            if invest_col not in df.columns:
                df[invest_col] = 0
        
        if 'Cliques no link' in df.columns:
            clicks_col = 'Cliques no link'
        elif 'clicks' in df.columns:
            clicks_col = 'clicks'
        else:
            clicks_col = 'Cliques'
            if clicks_col not in df.columns:
                df[clicks_col] = 0
        
        if 'CTR (taxa de cliques no link)' in df.columns:
            ctr_col = 'CTR (taxa de cliques no link)'
        elif 'ctr' in df.columns:
            ctr_col = 'ctr'
        else:
            ctr_col = 'CTR'
            if ctr_col not in df.columns:
                df[ctr_col] = 0
        
        # Converter para numérico
        df[invest_col] = pd.to_numeric(df[invest_col], errors='coerce').fillna(0)
        df[clicks_col] = pd.to_numeric(df[clicks_col], errors='coerce').fillna(0)
        
        if ctr_col == 'CTR (taxa de cliques no link)':
            df[ctr_col] = df[ctr_col].astype(str).str.replace('%', '').str.replace(',', '.')
            df[ctr_col] = pd.to_numeric(df[ctr_col], errors='coerce').fillna(0)
        else:
            df[ctr_col] = pd.to_numeric(df[ctr_col], errors='coerce').fillna(0) * 100
        
        # Criar dataframe padronizado
        data = []
        for _, row in df.iterrows():
            # Verificar coluna de data
            data_col = None
            if 'Início dos relatórios' in df.columns:
                data_col = 'Início dos relatórios'
            elif 'Data' in df.columns:
                data_col = 'Data'
            elif 'date_start' in df.columns:
                data_col = 'date_start'
            elif 'date' in df.columns:
                data_col = 'date'
            
            if data_col:
                try:
                    data_value = pd.to_datetime(row[data_col])
                except:
                    data_value = datetime.now()
            else:
                data_value = datetime.now()
            
# Pegar nome da campanha / conjunto de anúncios
            nome_campanha = 'Sem nome'

            if 'Nome da campanha' in df.columns:
              nome_campanha = row['Nome da campanha']
            elif 'campaign_name' in df.columns:
                nome_campanha = row['campaign_name']
            elif 'Nome do conjunto de anúncios' in df.columns:
                nome_campanha = row['Nome do conjunto de anúncios']
            elif 'Nome' in df.columns:
                nome_campanha = row['Nome']

            data.append({
                'Nome': nome_campanha,

                # Investimento
                'Investimento': row.get(
                    'Valor usado (BRL)',
                    row.get('amount_spent', 0)
                ),

                # Status
                'Status': row.get(
                    'Veiculação do conjunto de anúncios',
                    row.get('Veiculação da campanha', 'Desconhecido')
                ),

                # Métricas principais
                'Resultados': row.get('Resultados', 0),
                'Indicador': row.get('Indicador de resultados', 'Desconhecido'),
                'CPR': row.get('Custo por resultados', 0),

                # Orçamento
                'Orçamento': row.get(
                    'Orçamento do conjunto de anúncios',
                    0
                ),

                'Tipo_Orçamento': row.get(
                    'Tipo de orçamento do conjunto de anúncios',
                    'Desconhecido'
                ),

                # Alcance e impressões
                'Alcance': row.get('Alcance', 0),
                'Impressões': row.get(
                    'Impressões',
                    row.get('impressions', 0)
                ),

                # Datas
                'Início_Relatório': row.get(
                    'Início dos relatórios',
                    'Desconhecido'
                ),

                'Fim_Relatorio': row.get(
                    'Encerramento dos relatórios',
                    'Desconhecido'
                ),

                'Início_Campanha': row.get(
                    'Início',
                    'Desconhecido'
                ),

                'Fim_Campanha': row.get(
                    'Término',
                    'Desconhecido'
                ),

                # Configurações
                'Atribuição': row.get(
                    'Configuração de atribuição',
                    'Desconhecido'
                ),

                'Lance': row.get('Lance', 'Desconhecido'),

                'Tipo_Lance': row.get(
                    'Tipo de lance',
                    'Desconhecido'
                ),

            # Controle
                'Última_Edição': row.get(
                    'Última edição significativa',
                    'Desconhecido'
                ),

            # Cliques e CTR (caso existam)
                'Cliques': row.get(
                    'Cliques no link',
                    row.get('clicks', 0)
                ),

                'CTR': row.get(
                'CTR (taxa de cliques no link)',
                row.get('ctr', 0)
                ),

            # Data auxiliar
                'Data': data_value
                })
        
        df_result = pd.DataFrame(data)
        return df_result, True
        
    except Exception as e:
        st.error(f"Erro ao carregar CSV: {str(e)}")
        return pd.DataFrame(), False

# ============================================
# FUNÇÃO PARA GERAR O PAINEL HTML
# ============================================
def gerar_painel_html(nome_campanha, total_spend, total_alcance, total_cpr, total_res, total_cliques, total_impressions, avg_ctr, 
                      variacao_spend, variacao_alcance, variacao_res,variacao_cpr, variacao_cliques, variacao_impressions, variacao_ctr,
                      mes_texto="", ano_texto=""):
    """Gera o HTML do painel com os dados fornecidos"""
    
    # Tentar carregar o logo
    try:
        with open("logob.png", "rb") as img:
            logo_base64 = base64.b64encode(img.read()).decode()
        logo_style = f"background-image: url('data:image/png;base64,{logo_base64}');"
    except:
        logo_style = "background-image: url('');"
    
    # Formatar valores
    investido_str = f" {total_spend:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    alcance_str = f"{total_alcance:,.0f}".replace(",", ".")
    cpr_str = f" {total_cpr:,.0f}".replace(",", ".")
    total_res_str = f"{total_res:,.0f}".replace(",", ".")
    cliques_str = f"{total_cliques:,.0f}".replace(",", ".")
    impressoes_str = f"{total_impressions:,.0f}".replace(",", ".")
    ctr_str = f"{avg_ctr:.2f}%".replace(".", ",")
    
    # Definir classe CSS para variação
    def get_variation_class(variacao):
        if variacao > 0:
            return "delta-up"
        elif variacao < 0:
            return "delta-down"
        return "delta-neutral"
    
    def get_variation_arrow(variacao):
        if variacao > 0:
            return "▲"
        elif variacao < 0:
            return "▼"
        return "■"
    
    html = f"""
<div class="painel-unificado" id="painel-para-exportar">

    <div class="nome">{nome_campanha}</div>

    <div class="valor">
        <span style="display:flex; flex-direction:column;"">
            <span style="font-size:13px;">Alcance: </span>
            <span>{alcance_str}</span>
        </span>

        <span class="{get_variation_class(variacao_alcance)}"
              style="flex-shrink:0; white-space:nowrap">
            {get_variation_arrow(variacao_alcance)}
            {abs(variacao_alcance):.1f}%
        </span>
    </div>

    <div class="impressoes">
        <span style="display:flex; flex-direction:column;">
            <span style="font-size:13px;">Impressões: </span>
            <span>{impressoes_str}</span>
        </span>

        <span class="{get_variation_class(variacao_impressions)}"
              style="flex-shrink:0; white-space:nowrap">
            {get_variation_arrow(variacao_impressions)}
            {abs(variacao_impressions):.1f}%
        </span>
    </div>

    <div class="valor">
        <span style="display:flex; flex-direction:column;">
            <span style="font-size:13px;">Total investido: </span>
            <span>{investido_str}</span>
        </span>

        <span class="{get_variation_class(variacao_spend)}"
              style="flex-shrink:0; white-space:nowrap">
            {get_variation_arrow(variacao_spend)}
            {abs(variacao_spend):.1f}%
        </span>
    </div>

    <div class="valor">
        <span style="display:flex; flex-direction:column;">
            <span style="font-size:13px;">Custo por Resultados: </span>
            <span>{cpr_str}</span>
        </span>

        <span class="{get_variation_class(variacao_cpr)}"
              style="flex-shrink:0; white-space:nowrap">
            {get_variation_arrow(variacao_cpr)}
            {abs(variacao_cpr):.1f}%
        </span>
    </div>

    <div class="cliques">
        <span style="display:flex; flex-direction:column;">
            <span style="font-size:13px;">Resultados: </span>
            <span>{total_res_str}</span>
        </span>

        <span class="{get_variation_class(variacao_res)}"
              style="flex-shrink:0; white-space:nowrap">
            {get_variation_arrow(variacao_res)}
            {abs(variacao_res):.1f}%
        </span>
    </div>

    <div class="mesano">
        <span class="mes">Mês: {mes_texto if mes_texto else 'Todos'}</span>
        <span class="ano">Ano: {ano_texto if ano_texto else 'Todos'}</span>
    </div>

    <div class="logo" style="{logo_style}"></div>

</div>
    """
    return html

# ============================================
# FUNÇÃO PARA EXPORTAR O PAINEL COMO PNG
# ============================================
def exportar_painel_png( 
    nome_campanha,
    total_spend,
    total_alcance,
    total_cpr,
    total_res,
    total_cliques,
    total_impressions,
    avg_ctr,
    variacao_spend,
    variacao_alcance,
    variacao_res,
    variacao_cpr,
    variacao_cliques,
    variacao_impressions,
    variacao_ctr,
    mes_texto="",
    ano_texto=""):
    """Exporta o painel como PNG usando html2canvas"""
    
    html_painel = gerar_painel_html(
    nome_campanha,
    total_spend,
    total_alcance,
    total_cpr,
    total_res,
    total_cliques,
    total_impressions,
    avg_ctr,
    variacao_spend,
    variacao_alcance,
    variacao_res,
    variacao_cpr,
    variacao_cliques,
    variacao_impressions,
    variacao_ctr,
    mes_texto,
    ano_texto
)
    
    # HTML completo com estilos garantidos para exportação
    export_script = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
        <style>
            /* Reset e estilos garantidos para exportação */
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                background: transparent;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            }}
            
            .painel-unificado {{
                border-radius: 28px;
                padding: 22px;
                background: linear-gradient(180deg, #0066FF, #0047B3);
                display: flex;
                flex-direction: column;
                gap: 14px;
                width: 320px;
                min-height: 500px;
                margin: 0 auto;
                box-shadow: 0 12px 35px rgba(0,0,0,0.18);
                overflow: hidden;
                box-sizing: border-box;
            }}
            .painel-unificado .nome {{
                font-size: 18px;
                font-weight: 700;
                color: white;
                background: rgba(0,0,0,0.3);
                backdrop-filter: blur(10px);
                display: flex;
                align-items: center;
                justify-content: space-between;
                min-height: 60px;
                padding: 0 18px;
                width: 100%;
                border-radius: 18px;
                box-sizing: border-box;
            }}
            .painel-unificado .valor,
            .painel-unificado .cliques,
            .painel-unificado .impressoes,
            .painel-unificado .ctr {{
                font-size: 16px;
                font-weight: 700;
                color: #111827;
                background: rgba(255,255,255,0.96);
                display: flex;
                align-items: center;
                justify-content: space-between;
                min-height: 60px;
                padding: 0 18px;
                width: 100%;
                border-radius: 18px;
                box-sizing: border-box;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }}
            .painel-unificado .mesano {{
                display: flex;
                gap: 12px;
                justify-content: space-between;
                width: 100%;
                box-sizing: border-box;
            }}
            .painel-unificado .mesano .mes,
            .painel-unificado .mesano .ano {{
                background: rgba(255,255,255,0.96);
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                padding: 12px 18px;
                border-radius: 16px;
                font-size: 14px;
                font-weight: 700;
                color: #111827;
                flex: 1;
                text-align: center;
            }}
            .painel-unificado .mesano .mes {{
                flex: 1.5;}}
            .painel-unificado .mesano .ano {{
                flex: 1;}}
            .painel-unificado .logo {{
                background-size: contain;
                background-repeat: no-repeat;
                background-position: center;
                width: 140px;
                height: 70px;
                margin: auto;
                margin-top: 18px;
            }}
            .painel-unificado .delta-up {{
                color: #219653;
                background: #EBF7F0;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 12px;
                margin-left: 10px;
                display: inline-block;
            }}
            .painel-unificado .delta-down {{
                color: #EB5757;
                background: #FDEEEE;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 12px;
                margin-left: 10px;
                display: inline-block;
            }}
            .painel-unificado .delta-neutral {{
                color: #666666;
                background: #F0F0F0;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 12px;
                margin-left: 10px;
                display: inline-block;
            }}
        </style>
    </head>
    <body>
        <div id="container-para-exportar" style="position: relative;">
            {html_painel}
        </div>
        <script>
            (function() {{
                // Aguardar o DOM e todos os recursos carregarem
                window.addEventListener('load', function() {{
                    setTimeout(function() {{
                        var element = document.querySelector('#container-para-exportar .painel-unificado');
                        if (element) {{
                            console.log('Elemento encontrado, iniciando captura...');
                            html2canvas(element, {{
                                scale: 3,
                                backgroundColor: '#0066FF',
                                logging: true,
                                useCORS: true,
                                allowTaint: false,
                                windowWidth: element.scrollWidth,
                                windowHeight: element.scrollHeight
                            }}).then(function(canvas) {{
                                console.log('Canvas gerado com sucesso!');
                                var link = document.createElement('a');
                                var timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
                                link.download = 'painel_campanha_' + timestamp + '.png';
                                link.href = canvas.toDataURL('image/png');
                                link.click();
                                console.log('Download iniciado!');
                            }}).catch(function(error) {{
                                console.error('Erro detalhado ao gerar PNG:', error);
                                alert('Erro ao gerar a imagem: ' + error.message);
                            }});
                        }} else {{
                            console.error('Elemento .painel-unificado não encontrado!');
                        }}
                    }}, 1000);
                }});
            }})();
        </script>
    </body>
    </html>
    """
    
    return export_script

# ============================================
# FUNÇÃO PARA CALCULAR VARIAÇÃO
# ============================================
def calcular_variacao_atual_anterior(atual, anterior):
    if anterior == 0:
        return 0 if atual == 0 else 100
    else:
        variacao = ((atual - anterior) / abs(anterior)) * 100
        return round(variacao, 2)

def get_delta_style(variacao):
    if variacao > 0:
        return "delta-up", "▲"
    elif variacao < 0:
        return "delta-down", "▼"
    else:
        return "delta-neutral", "■"

# ============================================
# SIDEBAR & CONTROLE DE FONTE
# ============================================
campanhas = 0
with st.sidebar:
    st.header("⬈ Fonte de Dados")
    st.text("Escolha a fonte dos dados para o dashboard:")
    fonte_opcao = st.selectbox("",
           ["🔗 Meta Business API", "📁 CSV Upload"])
    
    if fonte_opcao == "📁 CSV Upload":
        uploaded_file = st.file_uploader("", type=["csv"])
        if uploaded_file:
            with st.spinner("Carregando CSV..."):
                df, success = load_data_from_csv(uploaded_file)
                if success and not df.empty:
                    st.session_state.df = df
                    st.session_state.mostrar = False
                else:
                    st.error("Falha ao carregar o arquivo")
        else:
            df = st.session_state.get('df', pd.DataFrame())
    else:
        if META_AVAILABLE:
            if st.button("🔄 Carregar dados do Meta", use_container_width=True):
                with st.spinner("Carregando Meta API..."):
                    df, success = load_data_from_meta_auto()
                    if success and not df.empty:
                        st.session_state.df = df
                    else:
                        st.error("Falha ao carregar dados do Meta")
            df = st.session_state.get('df', pd.DataFrame())
        else:
            st.warning("⚠️ Biblioteca facebook_business não instalada. Use: pip install facebook_business")
            df = st.session_state.get('df', pd.DataFrame())

# Inicializar df no session state
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'df_filtered_previous' not in st.session_state:
    st.session_state.df_filtered_previous = pd.DataFrame()
if 'show_toast' not in st.session_state:
    st.session_state.show_toast = False

df = st.session_state.df

# ============================================
# VERIFICAR SE HÁ DADOS
# ============================================
if df.empty:
    st.warning("⚠️ Nenhum dado carregado. Por favor, carregue um arquivo CSV ou conecte-se à Meta API.")
    st.stop()

# Garantir que Data seja datetime

df['Fim_Relatorio'] = pd.to_datetime(
    df['Fim_Relatorio'],
    dayfirst=True,
    errors='coerce'
)
# Última data válida do relatório
ultima_data = df['Fim_Relatorio'].max()

# Mês e ano atuais do encerramento
mes_padrao_num = ultima_data.month
ano_padrao = str(ultima_data.year)

mes_padrao = list(MESES_PT.keys())[mes_padrao_num - 1]

inicio_campanha = ""
fim_campanha = ""

# ============================================
# LAYOUT PRINCIPAL
# ============================================

# Header
h1, campanhas, mes_select, ano_select, status, export_png = st.columns([3, 1, 1, 1, 1, 1.2])
with h1:
    st.markdown("<h2 style='margin:0'>Dashboard</h2>", unsafe_allow_html=True)

# Filtros
with campanhas:
    nomes_unicos = df['Nome'].unique().tolist()
    campanha_opcao = st.selectbox("Campanha", ["Todas"] + nomes_unicos, label_visibility="collapsed")

with mes_select:
    meses_lista = ["Todos"] + list(MESES_PT.keys())

    mes_index = meses_lista.index(mes_padrao)

    mes_opcao = st.selectbox(
        "Mês",
        meses_lista,
        index=mes_index,
        label_visibility="collapsed"
    )

with ano_select:
    anos_disponiveis = sorted(
        df['Fim_Relatorio'].dt.year.dropna().unique()
    )

    anos_lista = ["Todos"] + [
        str(int(ano)) for ano in anos_disponiveis
    ]

    ano_index = anos_lista.index(ano_padrao)

    ano_opcao = st.selectbox(
        "Ano",
        anos_lista,
        index=ano_index,
        label_visibility="collapsed"
    )

with status:
    status_pt = {'active': 'Ativa', 'not_delivering':'Sem entrega','inactive':'Inativa', 'completed': 'Completa' }
    status_reverse = {v: k for k, v in status_pt.items()}
    status_list = df["Status"].unique().tolist()
    status_traduzido = [status_pt.get(s.lower(),s) for s in status_list]
    status_list = ["Todos"] + status_traduzido
    status_opcao = st.selectbox("Status", status_list, label_visibility="collapsed")


# ============================================
# APLICAR FILTROS
# ============================================
nome_campanha = ""
mes_texto = ""
ano_texto = ""
df_filtered = df.copy()

# Aplicar filtro por campanha
if campanha_opcao != "Todas":
    df_filtered = df_filtered[df_filtered['Nome'] == campanha_opcao]
    nome_campanha = campanha_opcao

    inicio_campanha = df_filtered['Início_Campanha'].iloc[0]
    fim_campanha = df_filtered['Fim_Campanha'].iloc[0]
else:
    nome_campanha = "Todas as Campanhas"

# Aplicar filtro por mês
# Garantir datetime
df_filtered['Início_Campanha'] = pd.to_datetime(
    df_filtered['Início_Campanha'],
    dayfirst=True,
    errors='coerce'
)

month_num = None

if mes_opcao != "Todos":
    mes_texto = mes_opcao

    mes_ingles = MESES_PT.get(mes_opcao)

    if mes_ingles:
        month_num = datetime.strptime(
            mes_ingles,
            "%B"
        ).month

        df_filtered = df_filtered[
            df_filtered['Início_Campanha'].dt.month == month_num
        ]
else:
    mes_texto = ''

# Aplicar filtro por status
if status_opcao != "Todos":
    status_real = status_reverse.get(status_opcao, status_opcao)

    df_filtered = df_filtered[
        df_filtered['Status'].str.lower() == status_real.lower()
    ]

# Aplicar filtro por ano
year_num = None
if ano_opcao != "Todos":
    ano_texto = ano_opcao
    year_num = int(ano_opcao)
    df_filtered = df_filtered[df_filtered['Fim_Relatorio'].dt.year == year_num]
else:
    ano_texto = ''

# Dataframe anterior para comparação de variação percentual
df_previous = df.copy()
if campanha_opcao != "Todas":
    df_previous = df_previous[df_previous['Nome'] == campanha_opcao]
if month_num and year_num:
    if month_num == 1:
        month_prev = 12
        year_prev = year_num - 1
    else:
        month_prev = month_num - 1
        year_prev = year_num
    df_previous = df_previous[(df_previous['Fim_Relatorio'].dt.month == month_prev) & (df_previous['Fim_Relatorio'].dt.year == year_prev)]
elif year_num:
    df_previous = df_previous[df_previous['Fim_Relatorio'].dt.year == (year_num - 1)]

# Verificar se os filtros removeram todos os dados
if df_filtered.empty:
    st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# ============================================
# CÁLCULO DE MÉTRICAS ATUAIS
# ============================================
total_spend = df_filtered['Investimento'].sum()
total_alcance = df_filtered['Alcance'].sum()
custo_por_res = df_filtered['CPR'].sum()
total_res = df_filtered['Resultados'].sum()
total_cliques = df_filtered['Cliques'].sum()
total_impressions = df_filtered['Impressões'].sum()
avg_ctr = df_filtered['CTR'].mean() if not df_filtered['CTR'].empty else 0

# Cálculo de métricas anteriores
total_spend_previous = df_previous['Investimento'].sum() if not df_previous.empty else 0
total_alcance_previous = df_previous['Alcance'].sum() if not df_previous.empty else 0
total_por_res_previous = df_previous['CPR'].sum() if not df_previous.empty else 0
total_res_previous = df_previous['Resultados'].sum() if not df_previous.empty else 0
total_cliques_previous = df_previous['Cliques'].sum() if not df_previous.empty else 0
total_impressions_previous = df_previous['Impressões'].sum() if not df_previous.empty else 0
avg_ctr_previous = df_previous['CTR'].mean() if not df_previous.empty and not df_previous['CTR'].empty else 0

# Calcular variação percentual
variacao_spend = calcular_variacao_atual_anterior(total_spend, total_spend_previous)
variacao_alcance = calcular_variacao_atual_anterior(total_alcance, total_alcance_previous)
variacao_cpr = calcular_variacao_atual_anterior(custo_por_res, total_por_res_previous)
variacao_res = calcular_variacao_atual_anterior(total_res, total_res_previous)
variacao_cliques = calcular_variacao_atual_anterior(total_cliques, total_cliques_previous)
variacao_impressions = calcular_variacao_atual_anterior(total_impressions, total_impressions_previous)
variacao_ctr = calcular_variacao_atual_anterior(avg_ctr, avg_ctr_previous)

# Estilo variação
spend_class, spend_arrow = get_delta_style(variacao_spend)
alcance_class, alcance_arrow = get_delta_style(variacao_alcance)
cpr_class, cpr_arrow = get_delta_style(variacao_cpr)
res_class, res_arrow = get_delta_style(variacao_res)
cliques_class, cliques_arrow = get_delta_style(variacao_cliques)
impressions_class, impressions_arrow = get_delta_style(variacao_impressions)
ctr_class, ctr_arrow = get_delta_style(variacao_ctr)

# ============================================
# EXIBIR O PAINEL VISUAL
# ============================================

# Carregar logo para o painel visível
try:
    with open("logob.png", "rb") as img:
        logo_base64_visivel = base64.b64encode(img.read()).decode()
    logo_style = f"background-image: url('data:image/png;base64,{logo_base64_visivel}');"
except:
    logo_style = "background-image: url('');"

# Formatar valores para exibição
investido_str_visivel = f"{total_spend:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
alcance_str_visivel = f"{total_alcance:,.0f}".replace(",", ".")
custo_res_str_visivel = f"{custo_por_res:,.0f}".replace(",", ".")
res_str_visivel = f"{total_res:,.0f}".replace(",", ".")
cliques_str_visivel = f"{total_cliques:,.0f}".replace(",", ".")
impressoes_str_visivel = f"{total_impressions:,.0f}".replace(",", ".")
ctr_str_visivel = f"{avg_ctr:.2f}%".replace(".", ",")

# HTML do painel visível
painel_html = f"""
<div class="painel-unificado">
    <div class="nome">{nome_campanha}</div>
    <div class="valor"> Alcance: {alcance_str_visivel}
        <span class="{spend_class}">{spend_arrow} {abs(variacao_alcance):.1f}%</span>
    </div>
    <div class="impressoes">
        <span> 
          <span>Impressões:</span>
          <span>{impressoes_str_visivel}</span>
        </span>
        <span class="{impressions_class}" style="flex-shrink:0; white-space:nowrap">{impressions_arrow} {abs(variacao_impressions):.1f}%</span>
    </div>
    <div class="valor">
        <span>
          <span> Total investido: </span> 
          <span>{investido_str_visivel}</span>
        </span>
        <span class="{spend_class}" style="flex-shrink:0; white-space:nowrap">{spend_arrow} {abs(variacao_spend):.1f}%</span>
    </div>
    <div class="valor">
        <span>
         <span>Custo por Resultado: </span>
         <span>{custo_res_str_visivel}</span>
        </span>
        <span class="{cpr_class}" style="flex-shrink:0; white-space:nowrap">{cpr_arrow} {abs(variacao_cpr):.1f}%</span>
    </div>
    <div class="cliques">
        <span>
           <span>Resultados: </span>
           <span>{res_str_visivel}</span>
        </span>
        <span class="{res_class}" style="flex-shrink:0; white-space:nowrap">{res_arrow} {abs(variacao_res):.1f}%</span>
    </div>
    <div class="mesano">
        <span class="mes">Mês: {mes_texto if mes_texto else 'Todos'}</span>
        <span class="ano">Ano: {ano_texto if ano_texto else 'Todos'}</span>
    </div>
    <div class="logo" style="{logo_style}"></div>
</div>
"""
if st.session_state.mostrar:
  st.markdown(painel_html, unsafe_allow_html=True)

# ============================================
# BOTÃO DE EXPORTAÇÃO PNG
# ============================================
with export_png:
    if st.button("📸 Baixar PNG", use_container_width=True):
        with st.spinner("Gerando imagem..."):
            export_script = exportar_painel_png(
               nome_campanha,
               total_spend,
               total_alcance,
               custo_por_res,
               total_res,
               total_cliques,
               total_impressions,
               avg_ctr,
               variacao_spend,
               variacao_alcance,
               variacao_res,
               variacao_cpr,
               variacao_cliques,
               variacao_impressions,
               variacao_ctr,
                mes_texto if mes_texto else "",
                ano_texto if ano_texto else ""
            )
            st.components.v1.html(export_script, height=0)
#EXIBIR DATA INICIO E TERMINO
if inicio_campanha and fim_campanha:
    col1, col2, col3 = st.columns([6,1.4,1.4])

    with col2:
        st.markdown(f"""
        <div style="
            padding:14px;
            border-radius:10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            display:flex;
            align-items:center;
            gap:6px;
            font-size:14px;
        ">
            <span style="font-weight:600;">Início:</span>
            <span>{inicio_campanha}</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="
            padding:14px;
            border-radius:10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            display:flex;
            align-items:center;
            gap:6px;
            font-size:14px;
        ">
            <span style="font-weight:600;">Término:</span>
            <span>{fim_campanha}</span>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# EXIBIR MÉTRICAS
# ============================================

if total_alcance >= 1_000_000 or total_impressions >= 1_000_000:
  st.markdown(f"""
    <div class="metric-container">
        <div class="metric-card">
            <div class="metric-label">Alcance</div>
            <div class="metric-value"> {total_alcance:,.2f}</div>
            <div class="metric-delta"><span class={spend_class}>{spend_arrow} {abs(variacao_alcance)}%</span></div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Impressões</div>
            <div class="metric-value">{total_impressions:,.0f}</div>
            <div class="metric-delta"><span class={impressions_class}>{impressions_arrow} {abs(variacao_impressions)}%</span></div>
        </div>
    </div>
""", unsafe_allow_html=True)

  st.markdown(f"""
    <div class="metric-container-2">
        <div class="metric-card">
            <div class="metric-label">Total Investido</div>
            <div class="metric-value">R$ {total_spend:,.2f}</div>
            <div class="metric-delta"><span class={spend_class}>{spend_arrow} {abs(variacao_spend)}%</span></div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Custo por Resultados</div>
            <div class="metric-value">R$ {custo_por_res:,.2f}</div>
            <div class="metric-delta"><span class={spend_class}>{spend_arrow} {abs(variacao_cpr)}%</span></div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Resultados</div>
            <div class="metric-value">{total_res:,.2f}</div>
            <div class="metric-delta"><span class={spend_class}>{spend_arrow} {abs(variacao_res)}%</span></div>
        </div>
    </div>
""", unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-card">
            <div class="metric-label">Alcance</div>
            <div class="metric-value"> {total_alcance:,.2f}</div>
            <div class="metric-delta"><span class={spend_class}>{spend_arrow} {abs(variacao_alcance)}%</span></div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Impressões</div>
            <div class="metric-value">{total_impressions:,.0f}</div>
            <div class="metric-delta"><span class={impressions_class}>{impressions_arrow} {abs(variacao_impressions)}%</span></div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Total Investido</div>
            <div class="metric-value">R$ {total_spend:,.2f}</div>
            <div class="metric-delta"><span class={spend_class}>{spend_arrow} {abs(variacao_spend)}%</span></div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Custo por Resultados</div>
            <div class="metric-value">R$ {custo_por_res:,.2f}</div>
            <div class="metric-delta"><span class={spend_class}>{spend_arrow} {abs(variacao_cpr)}%</span></div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Resultados</div>
            <div class="metric-value">{total_res:,.2f}</div>
            <div class="metric-delta"><span class={spend_class}>{spend_arrow} {abs(variacao_res)}%</span></div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ============================================
# GRÁFICO DE LINHA
# ============================================
st.markdown("### 📈 Evolução do Investimento")

# Preparar dados para o gráfico
df_linhas = df_filtered.copy()

df_linhas['Início_Campanha'] = pd.to_datetime(
    df_linhas['Início_Campanha'],
    dayfirst=True,
    errors='coerce'
)

df_linhas['Data_agrupada'] = (
    df_linhas['Início_Campanha']
    .dt.strftime('%d/%m')
)

daily_revenue = (
    df_linhas.groupby('Data_agrupada')['Investimento']
    .sum()
    .reset_index()
)

if not daily_revenue.empty:
    x_days = daily_revenue['Data_agrupada'].tolist()
    y_rev = daily_revenue['Investimento'].tolist()
else:
    x_days = ["Sem dados"]
    y_rev = [0]

fig_line = go.Figure()

fig_line.add_trace(go.Scatter(
    x=x_days,
    y=y_rev,
    mode='lines+markers',
    line=dict(color='#0066FF', width=3),
    marker=dict(size=8, color='#0066FF'),
    fill='tozeroy',
    fillcolor='rgba(0, 102, 255, 0.1)',
    name='Investimento'
))

fig_line.update_layout(
    plot_bgcolor="white",
    height=350,
    margin=dict(l=0, r=0, t=30, b=0),
    xaxis=dict(
        showgrid=True,
        gridcolor='#F0F0F0',
        title="Data"
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='#F0F0F0',
        tickprefix='R$ ',
        title="Investimento (R$)"
    ),
    showlegend=False
)

st.plotly_chart(fig_line, use_container_width=True)

# ============================================
# GRID INFERIOR
# ============================================

st.markdown("<br>", unsafe_allow_html=True)

col_left, col_right = st.columns([2, 1])

with col_left:

    st.markdown("### 📊 Resultados Mensais")

    # ============================================
    # DADOS MENSAIS
    # ============================================

    df_barras = df_filtered.copy()

    df_barras['Início_Campanha'] = pd.to_datetime(
        df_barras['Início_Campanha'],
        dayfirst=True,
        errors='coerce'
    )

    df_barras['Mês'] = (
        df_barras['Início_Campanha']
        .dt.strftime('%b')
    )

    meses_ordem = [
        'Jan', 'Feb', 'Mar', 'Apr',
        'May', 'Jun', 'Jul', 'Aug',
        'Sep', 'Oct', 'Nov', 'Dec'
    ]

    monthly_data = (
        df_barras.groupby('Mês')
        .agg({
            'Resultados': 'sum',
            'Cliques': 'sum',
            'Alcance': 'sum',
            'Impressões': 'sum',
            'Investimento': 'sum'
        })
        .reindex(meses_ordem, fill_value=0)
        .reset_index()
    )

    # ============================================
    # LISTAS
    # ============================================

    meses = monthly_data['Mês'].tolist()

    resultados = monthly_data['Resultados'].tolist()
    cliques = monthly_data['Cliques'].tolist()
    alcance = monthly_data['Alcance'].tolist()
    impressoes = monthly_data['Impressões'].tolist()
    investimento = monthly_data['Investimento'].tolist()

    # ============================================
    # GRÁFICO
    # ============================================

    fig_bar = go.Figure()

    fig_bar.add_trace(go.Bar(
        name='Resultados',
        x=meses,
        y=resultados,
        marker_color='#0066FF'
    ))

    fig_bar.add_trace(go.Bar(
        name='Cliques',
        x=meses,
        y=cliques,
        marker_color='#00A86B'
    ))

    fig_bar.add_trace(go.Bar(
        name='Alcance',
        x=meses,
        y=alcance,
        marker_color='#FFB800'
    ))

    fig_bar.add_trace(go.Bar(
        name='Impressões',
        x=meses,
        y=impressoes,
        marker_color='#FF6B6B'
    ))

    fig_bar.add_trace(go.Bar(
        name='Investimento',
        x=meses,
        y=investimento,
        marker_color='#6C63FF'
    ))

    # ============================================
    # LAYOUT
    # ============================================

    fig_bar.update_layout(
        barmode='group',
        plot_bgcolor="white",
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),

        xaxis=dict(
            showgrid=False
        ),

        yaxis=dict(
            showgrid=False,
            showticklabels=True
        )
    )

    st.plotly_chart(fig_bar, use_container_width=True)
# ============================================
# TABELA DE DADOS (opcional)
# ============================================

lista_c = df_filtered[['Nome','Alcance','Impressões','Investimento', 'Resultados', 'Cliques', 'CTR', 'Fim_Relatorio']].sort_values('Fim_Relatorio', ascending=False)

html = '<table style="width:100%; border-collapse: collapse; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-top:20px;">'
html += '<tr class="linhas">'
html += '<th>Nome</th>'
html += '<th>Alcançe</th>'
html += '<th>Impressões</th>'
html += '<th>Investimento</th>'
html += '<th>Custo por resultados</th>'
html += '<th>Cliques</th>'
html += '<th>CTR</th>'
html += '<th>Data inicio</th>'
html += '</tr>'

for _, linha in lista_c.iterrows():
    html += f'<tr class="coluna">'
    html += f'<td>{linha["Nome"]}</td>'
    html += f'<td>{linha["Alcance"]:.2f}</td>'
    html += f'<td>{linha["Impressões"]:.2f}</td>'
    html += f'<td>R$ {linha["Investimento"]:.2f}</td>'
    html += f'<td>{linha["Resultados"]}</td>'
    html += f'<td>{linha["Cliques"]:.2f}</td>'
    html += f'<td>{linha["CTR"]:.2f} % </td>'
    html += f'<td>{linha["Fim_Relatorio"].strftime("%d/%m/%Y")}</td>'
    html += '</tr>'

html += '</table>'
st.markdown(html, unsafe_allow_html=True)
# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.caption(f"📊 Dashboard atualizado em {datetime.now().strftime('%d/%m/%Y')}")
st.caption("🔹 Dados atualizados automaticamente a cada 5 minutos | 🔹 Clique em 'Baixar PNG' para exportar o painel")