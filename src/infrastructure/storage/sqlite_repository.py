import sqlite3
from typing import List, Optional
from datetime import datetime
import json
import logging
from ...domain.entities.stock import Stock
from ...domain.entities.analysis import Analysis
from ...domain.entities.summary import Summary

logger = logging.getLogger(__name__)


class SQLiteRepository:
    """SQLite repository for storing stock data, analysis, and summaries."""
    
    def __init__(self, db_path: str = "stock_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create stocks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    symbol TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    current_price REAL,
                    previous_close REAL,
                    volume INTEGER,
                    market_cap INTEGER,
                    pe_ratio REAL,
                    dividend_yield REAL,
                    last_updated TEXT NOT NULL
                )
            """)
            
            # Create analysis table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_symbol TEXT NOT NULL,
                    analysis_date TEXT NOT NULL,
                    trend_direction TEXT,
                    volatility REAL,
                    moving_average_5d REAL,
                    moving_average_20d REAL,
                    rsi REAL,
                    valuation_score INTEGER,
                    growth_potential INTEGER,
                    risk_level TEXT,
                    risk_factors TEXT,
                    daily_return REAL,
                    weekly_return REAL,
                    monthly_return REAL,
                    beta REAL,
                    sharpe_ratio REAL,
                    raw_data TEXT,
                    FOREIGN KEY (stock_symbol) REFERENCES stocks (symbol)
                )
            """)
            
            # Create summaries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS summaries (
                    id TEXT PRIMARY KEY,
                    summary_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    executive_summary TEXT NOT NULL,
                    detailed_analysis TEXT NOT NULL,
                    key_metrics TEXT,
                    insights TEXT,
                    recommendations TEXT,
                    stocks_analyzed TEXT,
                    analysis_period TEXT NOT NULL,
                    confidence_score REAL,
                    charts_data TEXT,
                    tags TEXT
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def save_stock(self, stock: Stock) -> bool:
        """Save or update a stock record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO stocks 
                    (symbol, name, current_price, previous_close, volume, market_cap, 
                     pe_ratio, dividend_yield, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    stock.symbol,
                    stock.name,
                    float(stock.current_price) if stock.current_price else None,
                    float(stock.previous_close) if stock.previous_close else None,
                    stock.volume,
                    stock.market_cap,
                    float(stock.pe_ratio) if stock.pe_ratio else None,
                    float(stock.dividend_yield) if stock.dividend_yield else None,
                    stock.last_updated.isoformat()
                ))
                conn.commit()
                logger.info(f"Saved stock data for {stock.symbol}")
                return True
        except Exception as e:
            logger.error(f"Error saving stock {stock.symbol}: {str(e)}")
            return False
    
    def save_stocks(self, stocks: List[Stock]) -> int:
        """Save multiple stocks and return count of successfully saved."""
        saved_count = 0
        for stock in stocks:
            if self.save_stock(stock):
                saved_count += 1
        return saved_count
    
    def get_stock(self, symbol: str) -> Optional[Stock]:
        """Retrieve a stock by symbol."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT symbol, name, current_price, previous_close, volume, 
                           market_cap, pe_ratio, dividend_yield, last_updated
                    FROM stocks WHERE symbol = ?
                """, (symbol,))
                
                row = cursor.fetchone()
                if row:
                    return Stock(
                        symbol=row[0],
                        name=row[1],
                        current_price=row[2],
                        previous_close=row[3],
                        volume=row[4],
                        market_cap=row[5],
                        pe_ratio=row[6],
                        dividend_yield=row[7],
                        last_updated=datetime.fromisoformat(row[8])
                    )
                return None
        except Exception as e:
            logger.error(f"Error retrieving stock {symbol}: {str(e)}")
            return None
    
    def get_all_stocks(self) -> List[Stock]:
        """Retrieve all stocks."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT symbol, name, current_price, previous_close, volume, 
                           market_cap, pe_ratio, dividend_yield, last_updated
                    FROM stocks ORDER BY name
                """)
                
                stocks = []
                for row in cursor.fetchall():
                    stock = Stock(
                        symbol=row[0],
                        name=row[1],
                        current_price=row[2],
                        previous_close=row[3],
                        volume=row[4],
                        market_cap=row[5],
                        pe_ratio=row[6],
                        dividend_yield=row[7],
                        last_updated=datetime.fromisoformat(row[8])
                    )
                    stocks.append(stock)
                
                return stocks
        except Exception as e:
            logger.error(f"Error retrieving all stocks: {str(e)}")
            return []
    
    def save_analysis(self, analysis: Analysis) -> bool:
        """Save analysis data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO analysis 
                    (stock_symbol, analysis_date, trend_direction, volatility,
                     moving_average_5d, moving_average_20d, rsi, valuation_score,
                     growth_potential, risk_level, risk_factors, daily_return,
                     weekly_return, monthly_return, beta, sharpe_ratio, raw_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis.stock_symbol,
                    analysis.analysis_date.isoformat(),
                    analysis.trend_direction.value if analysis.trend_direction else None,
                    float(analysis.volatility) if analysis.volatility else None,
                    float(analysis.moving_average_5d) if analysis.moving_average_5d else None,
                    float(analysis.moving_average_20d) if analysis.moving_average_20d else None,
                    float(analysis.rsi) if analysis.rsi else None,
                    analysis.valuation_score,
                    analysis.growth_potential,
                    analysis.risk_level.value if analysis.risk_level else None,
                    json.dumps(analysis.risk_factors),
                    float(analysis.daily_return) if analysis.daily_return else None,
                    float(analysis.weekly_return) if analysis.weekly_return else None,
                    float(analysis.monthly_return) if analysis.monthly_return else None,
                    float(analysis.beta) if analysis.beta else None,
                    float(analysis.sharpe_ratio) if analysis.sharpe_ratio else None,
                    json.dumps(analysis.raw_data)
                ))
                conn.commit()
                logger.info(f"Saved analysis for {analysis.stock_symbol}")
                return True
        except Exception as e:
            logger.error(f"Error saving analysis for {analysis.stock_symbol}: {str(e)}")
            return False
    
    def save_summary(self, summary: Summary) -> bool:
        """Save summary data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO summaries 
                    (id, summary_type, title, created_at, executive_summary,
                     detailed_analysis, key_metrics, insights, recommendations,
                     stocks_analyzed, analysis_period, confidence_score,
                     charts_data, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    summary.id,
                    summary.summary_type.value,
                    summary.title,
                    summary.created_at.isoformat(),
                    summary.executive_summary,
                    summary.detailed_analysis,
                    json.dumps(summary.key_metrics),
                    json.dumps([insight.model_dump() for insight in summary.insights]),
                    json.dumps(summary.recommendations),
                    json.dumps(summary.stocks_analyzed),
                    summary.analysis_period,
                    summary.confidence_score,
                    json.dumps(summary.charts_data),
                    json.dumps(summary.tags)
                ))
                conn.commit()
                logger.info(f"Saved summary: {summary.title}")
                return True
        except Exception as e:
            logger.error(f"Error saving summary {summary.title}: {str(e)}")
            return False
    
    def get_latest_summaries(self, limit: int = 10) -> List[Summary]:
        """Get the most recent summaries."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, summary_type, title, created_at, executive_summary,
                           detailed_analysis, key_metrics, insights, recommendations,
                           stocks_analyzed, analysis_period, confidence_score,
                           charts_data, tags
                    FROM summaries ORDER BY created_at DESC LIMIT ?
                """, (limit,))
                
                summaries = []
                for row in cursor.fetchall():
                    summary = Summary(
                        id=row[0],
                        summary_type=row[1],
                        title=row[2],
                        created_at=datetime.fromisoformat(row[3]),
                        executive_summary=row[4],
                        detailed_analysis=row[5],
                        key_metrics=json.loads(row[6]) if row[6] and isinstance(row[6], str) else {},
                        insights=[],  # Would need to reconstruct Insight objects
                        recommendations=json.loads(row[8]) if row[8] and isinstance(row[8], str) else [],
                        stocks_analyzed=json.loads(row[9]) if row[9] and isinstance(row[9], str) else [],
                        analysis_period=row[10],
                        confidence_score=row[11] if isinstance(row[11], (int, float)) else None,
                        charts_data=json.loads(row[12]) if row[12] and isinstance(row[12], str) else {},
                        tags=json.loads(row[13]) if row[13] and isinstance(row[13], str) else []
                    )
                    summaries.append(summary)
                
                return summaries
        except Exception as e:
            logger.error(f"Error retrieving summaries: {str(e)}")
            return []