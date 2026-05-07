# facebook_service.py
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adreportrun import AdReportRun

from models import CampaignModel, CampaignMetrics

class FacebookCampaignService:
    """Serviço para buscar campanhas e converter para seus modelos"""
    
    def __init__(self, app_id: str, app_secret: str, access_token: str, ad_account_id: str):
        FacebookAdsApi.init(app_id, app_secret, access_token)
        self.account = AdAccount(f'act_{ad_account_id}')
    
    def get_campaigns(self, status_filter: Optional[List[str]] = None) -> List[CampaignModel]:
        """Busca campanhas e converte para seu modelo"""
        
        # Parâmetros da requisição
        params = {
            'fields': [
                Campaign.Field.id,
                Campaign.Field.name,
                Campaign.Field.objective,
                Campaign.Field.status,
                Campaign.Field.daily_budget,
                Campaign.Field.lifetime_budget,
                Campaign.Field.start_time,
                Campaign.Field.stop_time,
                Campaign.Field.created_time,
                Campaign.Field.updated_time,
                Campaign.Field.buying_type,
                Campaign.Field.bid_strategy,
            ],
            'limit': 50  # Máximo por página
        }
        
        # Filtro de status (se fornecido)
        if status_filter:
            params['filtering'] = [{
                'field': 'status',
                'operator': 'IN',
                'value': status_filter
            }]
        
        # Buscar campanhas
        campaigns_raw = self.account.get_campaigns(params=params)
        
        # Converter para seu modelo
        campaigns = []
        for camp in campaigns_raw:
            campaign_model = CampaignModel(
                id=camp.get('id'),
                name=camp.get('name', 'Sem nome'),
                objective=camp.get('objective', 'N/A'),
                status=camp.get('status', 'UNKNOWN'),
                daily_budget=camp.get('daily_budget'),
                lifetime_budget=camp.get('lifetime_budget'),
                start_time=camp.get('start_time'),
                stop_time=camp.get('stop_time'),
                created_time=camp.get('created_time'),
                updated_time=camp.get('updated_time'),
                buying_type=camp.get('buying_type'),
                bid_strategy=camp.get('bid_strategy')
            )
            campaigns.append(campaign_model)
        
        return campaigns
    
    def get_campaign_insights(self, campaign_ids: List[str]) -> Dict[str, CampaignMetrics]:
        """Busca métricas das campanhas (insights)"""
        
        # Parâmetros para insights
        params = {
            'level': 'campaign',
            'date_preset': 'last_30d',
            'fields': [
                'campaign_id',
                'impressions',
                'clicks',
                'spend',
                'ctr',
                'cpc',
                'unique_clicks',
                'cost_per_unique_click'
            ]
        }
        
        # Buscar insights
        insights_raw = self.account.get_insights(params=params)
        
        metrics_dict = {}
        for insight in insights_raw:
            campaign_id = insight.get('campaign_id')
            if campaign_id:
                metrics = CampaignMetrics(
                    campaign_id=campaign_id,
                    impressions=int(insight.get('impressions', 0)),
                    clicks=int(insight.get('clicks', 0)),
                    spend=float(insight.get('spend', 0)),
                    ctr=float(insight.get('ctr', 0)),
                    cpc=float(insight.get('cpc', 0))
                )
                metrics_dict[campaign_id] = metrics
        
        return metrics_dict