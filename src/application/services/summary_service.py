from typing import List, Dict
from datetime import datetime
import uuid
import logging
from ...domain.entities.stock import Stock
from ...domain.entities.analysis import Analysis
from ...domain.entities.summary import Summary, SummaryType, InsightLevel

logger = logging.getLogger(__name__)


class SummaryService:
    """Service for generating summaries from stock analysis."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_daily_overview(self, stocks: List[Stock], analyses: List[Analysis]) -> Summary:
        """Generate a daily market overview summary."""
        summary_id = str(uuid.uuid4())
        
        # Calculate key metrics
        total_stocks = len(stocks)
        positive_stocks = len([s for s in stocks if s.price_change_percent and s.price_change_percent > 0])
        negative_stocks = len([s for s in stocks if s.price_change_percent and s.price_change_percent < 0])
        
        # Find top performers
        top_gainers = sorted(
            [s for s in stocks if s.price_change_percent], 
            key=lambda x: x.price_change_percent, 
            reverse=True
        )[:3]
        
        top_losers = sorted(
            [s for s in stocks if s.price_change_percent], 
            key=lambda x: x.price_change_percent
        )[:3]
        
        # Create executive summary
        executive_summary = f"""
        Market Overview: {positive_stocks}/{total_stocks} stocks gained today, while {negative_stocks} declined.
        Top gainer: {top_gainers[0].name} (+{top_gainers[0].price_change_percent:.2f}%)
        Top loser: {top_losers[0].name} ({top_losers[0].price_change_percent:.2f}%)
        """.strip()
        
        # Create detailed analysis
        detailed_analysis = self._create_detailed_market_analysis(stocks, analyses)
        
        # Key metrics
        key_metrics = {
            "Total Stocks Analyzed": str(total_stocks),
            "Stocks Up": str(positive_stocks),
            "Stocks Down": str(negative_stocks),
            "Average Change": f"{sum(s.price_change_percent or 0 for s in stocks) / total_stocks:.2f}%",
            "Market Sentiment": "Positive" if positive_stocks > negative_stocks else "Negative"
        }
        
        # Create summary
        summary = Summary(
            id=summary_id,
            summary_type=SummaryType.DAILY_OVERVIEW,
            title=f"Daily Market Overview - {datetime.now().strftime('%Y-%m-%d')}",
            executive_summary=executive_summary,
            detailed_analysis=detailed_analysis,
            key_metrics=key_metrics,
            stocks_analyzed=[s.symbol for s in stocks],
            analysis_period="1 day",
            confidence_score=0.8
        )
        
        # Add insights
        self._add_market_insights(summary, stocks, analyses)
        
        # Add recommendations
        summary.recommendations = self._generate_market_recommendations(stocks, analyses)
        
        logger.info(f"Generated daily overview summary for {total_stocks} stocks")
        return summary
    
    def generate_stock_analysis_summary(self, stock: Stock, analysis: Analysis) -> Summary:
        """Generate a detailed summary for a single stock."""
        summary_id = str(uuid.uuid4())
        
        # Executive summary
        change_text = f"+{analysis.daily_return:.2f}%" if analysis.daily_return and analysis.daily_return > 0 else f"{analysis.daily_return:.2f}%"
        trend_text = analysis.trend_direction.value if analysis.trend_direction else "sideways"
        
        executive_summary = f"""
        {stock.name} ({stock.symbol}) closed at ¥{stock.current_price} ({change_text}).
        Current trend: {trend_text}. Risk level: {analysis.risk_level.value if analysis.risk_level else 'medium'}.
        """.strip()
        
        # Detailed analysis
        detailed_analysis = self._create_detailed_stock_analysis(stock, analysis)
        
        # Key metrics
        key_metrics = {
            "Current Price": f"¥{stock.current_price}",
            "Daily Change": f"{analysis.daily_return:.2f}%" if analysis.daily_return else "N/A",
            "P/E Ratio": str(stock.pe_ratio) if stock.pe_ratio else "N/A",
            "Market Cap": f"¥{stock.market_cap:,}" if stock.market_cap else "N/A",
            "Risk Level": analysis.risk_level.value if analysis.risk_level else "N/A",
            "RSI": str(analysis.rsi) if analysis.rsi else "N/A"
        }
        
        # Create summary
        summary = Summary(
            id=summary_id,
            summary_type=SummaryType.STOCK_ANALYSIS,
            title=f"{stock.name} Analysis - {datetime.now().strftime('%Y-%m-%d')}",
            executive_summary=executive_summary,
            detailed_analysis=detailed_analysis,
            key_metrics=key_metrics,
            stocks_analyzed=[stock.symbol],
            analysis_period="1 day",
            confidence_score=0.7
        )
        
        # Add insights for individual stock
        self._add_stock_insights(summary, stock, analysis)
        
        # Add recommendations
        summary.recommendations = self._generate_stock_recommendations(stock, analysis)
        
        logger.info(f"Generated analysis summary for {stock.symbol}")
        return summary
    
    def _create_detailed_market_analysis(self, stocks: List[Stock], analyses: List[Analysis]) -> str:
        """Create detailed market analysis text."""
        analysis_parts = []
        
        # Market performance
        total_volume = sum(s.volume or 0 for s in stocks)
        avg_pe = sum(float(s.pe_ratio) for s in stocks if s.pe_ratio) / len([s for s in stocks if s.pe_ratio])
        
        analysis_parts.append(f"Market Activity: Total volume of {total_volume:,} shares traded.")
        analysis_parts.append(f"Average P/E ratio across analyzed stocks: {avg_pe:.2f}")
        
        # Sector performance (simplified)
        high_performers = [s for s in stocks if s.price_change_percent and s.price_change_percent > 5]
        if high_performers:
            analysis_parts.append(f"Strong performers: {', '.join([s.name for s in high_performers])}")
        
        # Risk assessment
        high_risk_count = len([a for a in analyses if a.risk_level and a.risk_level.value == 'high'])
        if high_risk_count > 0:
            analysis_parts.append(f"Risk Alert: {high_risk_count} stocks identified as high risk.")
        
        return "\n\n".join(analysis_parts)
    
    def _create_detailed_stock_analysis(self, stock: Stock, analysis: Analysis) -> str:
        """Create detailed analysis for a single stock."""
        analysis_parts = []
        
        # Price analysis
        if stock.price_change_percent:
            analysis_parts.append(f"Price Movement: {stock.name} moved {stock.price_change_percent:+.2f}% today.")
        
        # Technical analysis
        if analysis.moving_average_5d and analysis.moving_average_20d:
            ma_comparison = "above" if analysis.moving_average_5d > analysis.moving_average_20d else "below"
            analysis_parts.append(f"Technical: 5-day MA is {ma_comparison} 20-day MA, indicating {analysis.trend_direction.value if analysis.trend_direction else 'neutral'} momentum.")
        
        # Fundamental analysis
        if stock.pe_ratio:
            valuation_text = "undervalued" if stock.pe_ratio < 15 else "overvalued" if stock.pe_ratio > 25 else "fairly valued"
            analysis_parts.append(f"Valuation: P/E ratio of {stock.pe_ratio} suggests the stock may be {valuation_text}.")
        
        # Risk factors
        if analysis.risk_factors:
            analysis_parts.append(f"Risk Factors: {', '.join(analysis.risk_factors)}")
        
        return "\n\n".join(analysis_parts)
    
    def _add_market_insights(self, summary: Summary, stocks: List[Stock], analyses: List[Analysis]):
        """Add insights to market summary."""
        # Market trend insight
        positive_count = len([s for s in stocks if s.price_change_percent and s.price_change_percent > 0])
        total_count = len(stocks)
        
        if positive_count > total_count * 0.7:
            summary.add_insight(
                InsightLevel.INFO,
                "Strong Market Performance",
                f"Over 70% of analyzed stocks showed positive performance today.",
                [s.symbol for s in stocks if s.price_change_percent and s.price_change_percent > 0]
            )
        elif positive_count < total_count * 0.3:
            summary.add_insight(
                InsightLevel.WARNING,
                "Market Weakness",
                f"Less than 30% of analyzed stocks showed positive performance today.",
                [s.symbol for s in stocks if s.price_change_percent and s.price_change_percent < 0]
            )
        
        # High volatility alert
        high_vol_stocks = []
        for analysis in analyses:
            if analysis.volatility and analysis.volatility > 8:
                high_vol_stocks.append(analysis.stock_symbol)
        
        if high_vol_stocks:
            summary.add_insight(
                InsightLevel.WARNING,
                "High Volatility Alert",
                f"Several stocks showing elevated volatility: {', '.join(high_vol_stocks)}",
                high_vol_stocks,
                0.9
            )
    
    def _add_stock_insights(self, summary: Summary, stock: Stock, analysis: Analysis):
        """Add insights for individual stock."""
        # Overbought/oversold conditions
        if analysis.rsi:
            if analysis.rsi > 80:
                summary.add_insight(
                    InsightLevel.WARNING,
                    "Overbought Condition",
                    f"RSI of {analysis.rsi} indicates overbought conditions. Consider taking profits.",
                    [stock.symbol],
                    0.8
                )
            elif analysis.rsi < 20:
                summary.add_insight(
                    InsightLevel.INFO,
                    "Oversold Condition",
                    f"RSI of {analysis.rsi} indicates oversold conditions. Potential buying opportunity.",
                    [stock.symbol],
                    0.8
                )
        
        # Strong momentum
        if stock.price_change_percent and abs(stock.price_change_percent) > 10:
            level = InsightLevel.CRITICAL if abs(stock.price_change_percent) > 20 else InsightLevel.WARNING
            summary.add_insight(
                level,
                "Significant Price Movement",
                f"Stock moved {stock.price_change_percent:+.2f}% today - investigate underlying reasons.",
                [stock.symbol],
                0.9
            )
    
    def _generate_market_recommendations(self, stocks: List[Stock], analyses: List[Analysis]) -> List[str]:
        """Generate market-level recommendations."""
        recommendations = []
        
        # Market sentiment
        positive_count = len([s for s in stocks if s.price_change_percent and s.price_change_percent > 0])
        total_count = len(stocks)
        
        if positive_count > total_count * 0.6:
            recommendations.append("Market showing positive momentum - consider increasing equity exposure")
        elif positive_count < total_count * 0.4:
            recommendations.append("Market weakness detected - consider defensive positioning")
        
        # High volatility stocks
        high_vol_analyses = [a for a in analyses if a.volatility and a.volatility > 10]
        if high_vol_analyses:
            recommendations.append("Several stocks showing high volatility - use smaller position sizes")
        
        # Risk management
        high_risk_count = len([a for a in analyses if a.risk_level and a.risk_level.value == 'high'])
        if high_risk_count > total_count * 0.3:
            recommendations.append("Elevated risk levels detected - review portfolio risk management")
        
        return recommendations
    
    def _generate_stock_recommendations(self, stock: Stock, analysis: Analysis) -> List[str]:
        """Generate stock-specific recommendations."""
        recommendations = []
        
        # Based on trend and RSI
        if analysis.rsi:
            if analysis.rsi > 80 and analysis.trend_direction and analysis.trend_direction.value == 'up':
                recommendations.append("Consider taking profits - stock may be overbought")
            elif analysis.rsi < 30 and analysis.trend_direction and analysis.trend_direction.value == 'down':
                recommendations.append("Potential buying opportunity - stock may be oversold")
        
        # Based on valuation
        if analysis.valuation_score and analysis.valuation_score >= 8:
            recommendations.append("Stock appears undervalued based on fundamental metrics")
        elif analysis.valuation_score and analysis.valuation_score <= 3:
            recommendations.append("Stock may be overvalued - exercise caution")
        
        # Risk-based recommendations
        if analysis.risk_level and analysis.risk_level.value == 'high':
            recommendations.append("High risk detected - use appropriate position sizing")
        
        # Growth potential
        if analysis.growth_potential and analysis.growth_potential >= 8:
            recommendations.append("Strong growth potential identified - consider for growth portfolio")
        
        return recommendations