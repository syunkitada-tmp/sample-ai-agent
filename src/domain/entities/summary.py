from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class SummaryType(str, Enum):
    """Types of summaries that can be generated."""
    DAILY_OVERVIEW = "daily_overview"
    STOCK_ANALYSIS = "stock_analysis"
    SECTOR_SUMMARY = "sector_summary"
    RISK_ALERT = "risk_alert"


class InsightLevel(str, Enum):
    """Level of insight importance."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Insight(BaseModel):
    """Individual insight or recommendation."""
    
    level: InsightLevel = Field(..., description="Importance level of the insight")
    title: str = Field(..., description="Short title of the insight")
    description: str = Field(..., description="Detailed description")
    stock_symbols: List[str] = Field(default_factory=list, description="Related stock symbols")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence level (0-1)")


class Summary(BaseModel):
    """Summary entity containing analysis summaries and insights."""
    
    id: Optional[str] = Field(None, description="Unique summary identifier")
    summary_type: SummaryType = Field(..., description="Type of summary")
    title: str = Field(..., description="Summary title")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    # Content
    executive_summary: str = Field(..., description="Brief executive summary")
    detailed_analysis: str = Field(..., description="Detailed analysis content")
    key_metrics: Dict[str, str] = Field(default_factory=dict, description="Key metrics and values")
    
    # Insights and Recommendations
    insights: List[Insight] = Field(default_factory=list, description="Generated insights")
    recommendations: List[str] = Field(default_factory=list, description="Action recommendations")
    
    # Metadata
    stocks_analyzed: List[str] = Field(default_factory=list, description="List of analyzed stock symbols")
    analysis_period: str = Field(..., description="Time period of analysis")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall confidence")
    
    # Additional data
    charts_data: Dict[str, List] = Field(default_factory=dict, description="Data for chart generation")
    tags: List[str] = Field(default_factory=list, description="Summary tags")
    
    def add_insight(self, level: InsightLevel, title: str, description: str, 
                   stocks: List[str] = None, confidence: float = None) -> None:
        """Add a new insight to the summary."""
        insight = Insight(
            level=level,
            title=title,
            description=description,
            stock_symbols=stocks or [],
            confidence=confidence
        )
        self.insights.append(insight)
    
    def get_critical_insights(self) -> List[Insight]:
        """Get only critical insights."""
        return [insight for insight in self.insights if insight.level == InsightLevel.CRITICAL]
    
    def get_warning_insights(self) -> List[Insight]:
        """Get warning level insights."""
        return [insight for insight in self.insights if insight.level == InsightLevel.WARNING]
    
    def has_alerts(self) -> bool:
        """Check if summary contains any warnings or critical insights."""
        return any(insight.level in [InsightLevel.WARNING, InsightLevel.CRITICAL] 
                  for insight in self.insights)