import requests
import pandas as pd

def get_long_lived_token(app_id, app_secret, short_token):
    """Troca o token de 2 horas por um de 60 dias."""
    url = "https://graph.facebook.com/v18.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_token
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("access_token")
    raise Exception(f"Erro ao renovar token: {response.text}")

def extract_leads(actions):
    """Extrai métricas de conversão do campo 'actions' da API."""
    if not actions or not isinstance(actions, list):
        return 0
    lead_types = ["lead", "onsite_conversion.lead_grouped", "offsite_conversion.fb_pixel_lead"]
    for action in actions:
        if action.get("action_type") in lead_types:
            return int(action.get("value", 0))
    return 0

def get_meta_data(access_token, ad_account_id):
    """Busca dados de insights da conta de anúncios."""
    if not ad_account_id.startswith('act_'):
        ad_account_id = f"act_{ad_account_id}"
        
    url = f"https://graph.facebook.com/v18.0/{ad_account_id}/insights"
    params = {
        "fields": "campaign_name,impressions,clicks,spend,actions,reach",
        "level": "campaign",
        "date_preset": "last_30d",
        "access_token": access_token
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Erro na API Meta: {response.json().get('error', {}).get('message')}")

    data = response.json().get("data", [])
    rows = []
    for item in data:
        rows.append({
            "Nome da campanha": item.get("campaign_name"),
            "Valor usado (BRL)": float(item.get("spend", 0)),
            "Impressões": int(item.get("impressions", 0)),
            "Cliques no link": int(item.get("clicks", 0)),
            "Resultados": extract_leads(item.get("actions")),
            "Alcance": int(item.get("reach", 0))
        })
    return pd.DataFrame(rows)