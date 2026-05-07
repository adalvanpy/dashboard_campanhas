# models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class CampaignModel:
    """Sua classe para armazenar dados da campanha"""
    id: str
    name: str
    objective: str
    status: str
    daily_budget: Optional[float] = None
    lifetime_budget: Optional[float] = None
    start_time: Optional[datetime] = None
    stop_time: Optional[datetime] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    buying_type: Optional[str] = None
    bid_strategy: Optional[str] = None
    
    def __post_init__(self):
        """Converte centavos para unidades monetárias"""
        if self.daily_budget:
            self.daily_budget = self.daily_budget / 100
        if self.lifetime_budget:
            self.lifetime_budget = self.lifetime_budget / 100
    
    @property
    def status_emoji(self) -> str:
        """Retorna emoji baseado no status"""
        emojis = {
            'ACTIVE': '🟢',
            'PAUSED': '⏸️',
            'DELETED': '❌',
            'ARCHIVED': '📦'
        }
        return emojis.get(self.status, '⚪')
    
    @property
    def formatted_budget(self) -> str:
        """Retorna orçamento formatado"""
        if self.daily_budget:
            return f"R$ {self.daily_budget:,.2f}/dia"
        if self.lifetime_budget:
            return f"R$ {self.lifetime_budget:,.2f} total"
        return "N/A"


@dataclass
class CampaignMetrics:
    """Métricas adicionais da campanha"""
    campaign_id: str
    impressions: int = 0
    clicks: int = 0
    spend: float = 0.0
    ctr: float = 0.0  # Click-through rate
    cpc: float = 0.0  # Cost per click
    
    @property
    def formatted_spend(self) -> str:
        return f"R$ {self.spend:,.2f}"
    
    @property
    def formatted_ctr(self) -> str:
        return f"{self.ctr:.2f}%"