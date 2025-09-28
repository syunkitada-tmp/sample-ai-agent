from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TrendDirection(str, Enum):
    """Stock trend direction."""
    UP = "up"
    DOWN = "down"
    SIDEWAYS = "sideways"


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Analysis(BaseModel):
    """Analysis entity containing stock analysis results."""
    
    stock_symbol: str = Field(..., description="Stock symbol being analyzed")
    analysis_date: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    
    # Technical Analysis
    trend_direction: Optional[TrendDirection] = Field(None, description="Overall trend direction")
    volatility: Optional[Decimal] = Field(None, description="Price volatility percentage")
    moving_average_5d: Optional[Decimal] = Field(None, description="5-day moving average")
    moving_average_20d: Optional[Decimal] = Field(None, description="20-day moving average")
    rsi: Optional[Decimal] = Field(None, description="Relative Strength Index")
    
    # Fundamental Analysis
    valuation_score: Optional[int] = Field(None, ge=1, le=10, description="Valuation score (1-10)")
    growth_potential: Optional[int] = Field(None, ge=1, le=10, description="Growth potential score (1-10)")
    
    # Risk Assessment
    risk_level: Optional[RiskLevel] = Field(None, description="Overall risk level")
    risk_factors: list[str] = Field(default_factory=list, description="Identified risk factors")
    
    # Performance Metrics
    daily_return: Optional[Decimal] = Field(None, description="Daily return percentage")
    weekly_return: Optional[Decimal] = Field(None, description="Weekly return percentage")
    monthly_return: Optional[Decimal] = Field(None, description="Monthly return percentage")
    
    # Additional Metrics
    beta: Optional[Decimal] = Field(None, description="Beta coefficient vs market")
    sharpe_ratio: Optional[Decimal] = Field(None, description="Risk-adjusted return metric")
    
    # Raw data for calculations
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw analysis data")
    
    def get_trend_strength(self) -> str:
        """Get human-readable trend strength."""
        if not self.volatility:
            return "Unknown"
        
        if self.volatility < 2:
            return "Weak"
        elif self.volatility < 5:
            return "Moderate"
        else:
            return "Strong"
    
    def is_oversold(self) -> bool:
        """Check if stock is oversold based on RSI."""
        return self.rsi is not None and self.rsi < 30
    
    def is_overbought(self) -> bool:
        """Check if stock is overbought based on RSI."""
        return self.rsi is not None and self.rsi > 70