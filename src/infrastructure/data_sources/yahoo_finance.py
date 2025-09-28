import yfinance as yf
import requests
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
import logging
from ...domain.entities.stock import Stock

logger = logging.getLogger(__name__)


class YahooFinanceCollector:
    """Data collector for Yahoo Finance Japan stock data."""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def collect_stock_data(self, symbol: str) -> Optional[Stock]:
        """Collect data for a single stock symbol."""
        try:
            # Add .T suffix for Tokyo Stock Exchange if not present
            if not symbol.endswith('.T'):
                symbol_with_suffix = f"{symbol}.T"
            else:
                symbol_with_suffix = symbol
            
            logger.info(f"Collecting data for {symbol_with_suffix}")
            
            # Use yfinance to get stock data
            ticker = yf.Ticker(symbol_with_suffix)
            info = ticker.info
            hist = ticker.history(period="5d")
            
            if hist.empty:
                logger.warning(f"No historical data found for {symbol_with_suffix}")
                return None
            
            # Get the most recent data
            latest_data = hist.iloc[-1]
            previous_close = hist.iloc[-2]['Close'] if len(hist) > 1 else latest_data['Close']
            
            # Extract company information
            company_name = info.get('longName') or info.get('shortName') or symbol
            
            # Create Stock entity
            stock = Stock(
                symbol=symbol_with_suffix,
                name=company_name,
                current_price=Decimal(str(latest_data['Close'])),
                previous_close=Decimal(str(previous_close)),
                volume=int(latest_data['Volume']) if latest_data['Volume'] else None,
                market_cap=info.get('marketCap'),
                pe_ratio=Decimal(str(info['trailingPE'])) if info.get('trailingPE') else None,
                dividend_yield=Decimal(str(info['dividendYield'] * 100)) if info.get('dividendYield') else None,
                last_updated=datetime.now()
            )
            
            logger.info(f"Successfully collected data for {stock.name}")
            return stock
            
        except Exception as e:
            logger.error(f"Error collecting data for {symbol}: {str(e)}")
            return None
    
    def collect_multiple_stocks(self, symbols: List[str]) -> List[Stock]:
        """Collect data for multiple stock symbols."""
        stocks = []
        
        for symbol in symbols:
            stock = self.collect_stock_data(symbol)
            if stock:
                stocks.append(stock)
        
        logger.info(f"Successfully collected data for {len(stocks)}/{len(symbols)} stocks")
        return stocks
    
    def get_major_japanese_stocks(self) -> List[str]:
        """Get list of major Japanese stock symbols."""
        # Major Japanese stocks (Nikkei 225 components)
        return [
            "7203",  # Toyota Motor
            "6758",  # Sony Group
            "9984",  # SoftBank Group
            "8306",  # Mitsubishi UFJ Financial Group
            "4502",  # Takeda Pharmaceutical
            "6861",  # Keyence
            "9432",  # NTT
            "4612",  # Nippon Paint Holdings
            "7974",  # Nintendo
            "6367",  # Daikin Industries
        ]
    
    def collect_major_stocks(self) -> List[Stock]:
        """Collect data for major Japanese stocks."""
        symbols = self.get_major_japanese_stocks()
        return self.collect_multiple_stocks(symbols)
    
    def health_check(self) -> bool:
        """Check if the data source is accessible."""
        try:
            # Try to fetch data for Toyota as a health check
            stock = self.collect_stock_data("7203")
            return stock is not None
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False