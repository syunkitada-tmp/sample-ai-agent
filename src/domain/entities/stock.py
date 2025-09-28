from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class Stock(BaseModel):
    """Stock entity representing a Japanese stock."""
    
    symbol: str = Field(..., description="Stock symbol (e.g., '7203.T' for Toyota)")
    name: str = Field(..., description="Company name")
    current_price: Optional[Decimal] = Field(None, description="Current stock price in JPY")
    previous_close: Optional[Decimal] = Field(None, description="Previous closing price")
    volume: Optional[int] = Field(None, description="Trading volume")
    market_cap: Optional[int] = Field(None, description="Market capitalization")
    pe_ratio: Optional[Decimal] = Field(None, description="Price-to-earnings ratio")
    dividend_yield: Optional[Decimal] = Field(None, description="Dividend yield percentage")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    @property
    def price_change(self) -> Optional[Decimal]:
        """Calculate price change from previous close."""
        if self.current_price and self.previous_close:
            return self.current_price - self.previous_close
        return None
    
    @property
    def price_change_percent(self) -> Optional[Decimal]:
        """Calculate percentage price change."""
        if self.current_price and self.previous_close and self.previous_close > 0:
            return ((self.current_price - self.previous_close) / self.previous_close) * 100
        return None
    
    def __str__(self) -> str:
        return f"{self.name} ({self.symbol}): ¥{self.current_price}"