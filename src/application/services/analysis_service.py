from typing import List, Dict, Any
from decimal import Decimal
from statistics import mean, stdev
import logging
from ...domain.entities.stock import Stock
from ...domain.entities.analysis import Analysis, TrendDirection, RiskLevel

logger = logging.getLogger(__name__)


class SimpleAnalysisEngine:
    """Simple analysis engine for basic stock analysis."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_stock(self, stock: Stock, historical_data: List[Dict[str, Any]] = None) -> Analysis:
        """Perform basic analysis on a single stock."""
        analysis = Analysis(stock_symbol=stock.symbol)
        
        try:
            # Basic trend analysis based on price change
            if stock.price_change_percent:
                analysis.daily_return = stock.price_change_percent
                
                if stock.price_change_percent > 2:
                    analysis.trend_direction = TrendDirection.UP
                elif stock.price_change_percent < -2:
                    analysis.trend_direction = TrendDirection.DOWN
                else:
                    analysis.trend_direction = TrendDirection.SIDEWAYS
            
            # Calculate volatility (simplified)
            if historical_data and len(historical_data) > 1:
                returns = []
                for i in range(1, len(historical_data)):
                    prev_price = historical_data[i-1].get('close', 0)
                    curr_price = historical_data[i].get('close', 0)
                    if prev_price > 0:
                        daily_return = ((curr_price - prev_price) / prev_price) * 100
                        returns.append(daily_return)
                
                if returns:
                    analysis.volatility = Decimal(str(stdev(returns)))
                    
                    # Calculate moving averages
                    if len(historical_data) >= 5:
                        recent_5 = historical_data[-5:]
                        analysis.moving_average_5d = Decimal(str(mean([d.get('close', 0) for d in recent_5])))
                    
                    if len(historical_data) >= 20:
                        recent_20 = historical_data[-20:]
                        analysis.moving_average_20d = Decimal(str(mean([d.get('close', 0) for d in recent_20])))
            
            # Simple RSI calculation (simplified version)
            analysis.rsi = self._calculate_simple_rsi(historical_data) if historical_data else None
            
            # Basic valuation scoring
            analysis.valuation_score = self._calculate_valuation_score(stock)
            
            # Growth potential (simplified)
            analysis.growth_potential = self._calculate_growth_potential(stock)
            
            # Risk assessment
            analysis.risk_level = self._assess_risk_level(stock, analysis)
            analysis.risk_factors = self._identify_risk_factors(stock, analysis)
            
            logger.info(f"Analysis completed for {stock.symbol}")
            
        except Exception as e:
            logger.error(f"Error analyzing stock {stock.symbol}: {str(e)}")
        
        return analysis
    
    def analyze_multiple_stocks(self, stocks: List[Stock]) -> List[Analysis]:
        """Analyze multiple stocks."""
        analyses = []
        for stock in stocks:
            analysis = self.analyze_stock(stock)
            analyses.append(analysis)
        
        logger.info(f"Completed analysis for {len(analyses)} stocks")
        return analyses
    
    def _calculate_simple_rsi(self, historical_data: List[Dict[str, Any]], period: int = 14) -> Decimal:
        """Calculate a simplified RSI."""
        if not historical_data or len(historical_data) < period + 1:
            return Decimal('50')  # Neutral RSI
        
        gains = []
        losses = []
        
        for i in range(1, min(len(historical_data), period + 1)):
            prev_price = historical_data[i-1].get('close', 0)
            curr_price = historical_data[i].get('close', 0)
            change = curr_price - prev_price
            
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if not gains or not losses:
            return Decimal('50')
        
        avg_gain = mean(gains) if gains else 0
        avg_loss = mean(losses) if losses else 0
        
        if avg_loss == 0:
            return Decimal('100')
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return Decimal(str(round(rsi, 2)))
    
    def _calculate_valuation_score(self, stock: Stock) -> int:
        """Calculate a simple valuation score (1-10)."""
        score = 5  # Neutral starting point
        
        try:
            if stock.pe_ratio:
                # Adjust score based on P/E ratio
                if stock.pe_ratio < 10:
                    score += 2  # Potentially undervalued
                elif stock.pe_ratio < 15:
                    score += 1
                elif stock.pe_ratio > 25:
                    score -= 1
                elif stock.pe_ratio > 35:
                    score -= 2  # Potentially overvalued
            
            if stock.dividend_yield:
                # Reward dividend-paying stocks
                if stock.dividend_yield > 3:
                    score += 1
                elif stock.dividend_yield > 5:
                    score += 2
            
            # Ensure score is within bounds
            score = max(1, min(10, score))
            
        except Exception as e:
            logger.warning(f"Error calculating valuation score for {stock.symbol}: {str(e)}")
            score = 5
        
        return score
    
    def _calculate_growth_potential(self, stock: Stock) -> int:
        """Calculate growth potential score (1-10)."""
        score = 5  # Neutral starting point
        
        try:
            # Simple heuristics for growth potential
            if stock.price_change_percent:
                if stock.price_change_percent > 5:
                    score += 1
                elif stock.price_change_percent > 10:
                    score += 2
                elif stock.price_change_percent < -5:
                    score -= 1
                elif stock.price_change_percent < -10:
                    score -= 2
            
            # Market cap considerations (smaller companies might have more growth potential)
            if stock.market_cap:
                if stock.market_cap < 10_000_000_000:  # < 10B JPY
                    score += 1
                elif stock.market_cap > 1_000_000_000_000:  # > 1T JPY
                    score -= 1
            
            # Ensure score is within bounds
            score = max(1, min(10, score))
            
        except Exception as e:
            logger.warning(f"Error calculating growth potential for {stock.symbol}: {str(e)}")
            score = 5
        
        return score
    
    def _assess_risk_level(self, stock: Stock, analysis: Analysis) -> RiskLevel:
        """Assess overall risk level."""
        risk_score = 0
        
        # High volatility increases risk
        if analysis.volatility and analysis.volatility > 5:
            risk_score += 1
        if analysis.volatility and analysis.volatility > 10:
            risk_score += 1
        
        # Extreme P/E ratios increase risk
        if stock.pe_ratio:
            if stock.pe_ratio > 30 or stock.pe_ratio < 5:
                risk_score += 1
        
        # Large price movements increase risk
        if stock.price_change_percent:
            if abs(stock.price_change_percent) > 10:
                risk_score += 1
        
        # Determine risk level
        if risk_score >= 3:
            return RiskLevel.HIGH
        elif risk_score >= 1:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _identify_risk_factors(self, stock: Stock, analysis: Analysis) -> List[str]:
        """Identify specific risk factors."""
        factors = []
        
        if analysis.volatility and analysis.volatility > 8:
            factors.append("High price volatility")
        
        if stock.pe_ratio and stock.pe_ratio > 35:
            factors.append("High P/E ratio - potentially overvalued")
        
        if stock.price_change_percent and stock.price_change_percent < -15:
            factors.append("Significant recent price decline")
        
        if analysis.rsi and analysis.rsi > 80:
            factors.append("Overbought conditions (RSI > 80)")
        elif analysis.rsi and analysis.rsi < 20:
            factors.append("Oversold conditions (RSI < 20)")
        
        if not stock.dividend_yield or stock.dividend_yield < 1:
            factors.append("Low or no dividend yield")
        
        return factors