import click
import logging
from typing import List
from datetime import datetime

from ...infrastructure.data_sources import YahooFinanceCollector
from ...infrastructure.storage import SQLiteRepository
from ...application.services import SimpleAnalysisEngine, SummaryService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@click.group()
def cli():
    """Japanese Stock Information AI Agent CLI"""
    pass


@cli.command()
@click.option('--symbols', default=None, help='Comma-separated stock symbols (e.g., 7203,6758)')
@click.option('--major', is_flag=True, help='Use major Japanese stocks')
def collect(symbols, major):
    """Collect stock data from Yahoo Finance."""
    collector = YahooFinanceCollector()
    repository = SQLiteRepository()
    
    try:
        if major:
            click.echo("Collecting data for major Japanese stocks...")
            stocks = collector.collect_major_stocks()
        elif symbols:
            symbol_list = [s.strip() for s in symbols.split(',')]
            click.echo(f"Collecting data for: {', '.join(symbol_list)}")
            stocks = collector.collect_multiple_stocks(symbol_list)
        else:
            click.echo("Please specify --symbols or use --major flag")
            return
        
        if not stocks:
            click.echo("No stock data collected")
            return
        
        # Save to database
        saved_count = repository.save_stocks(stocks)
        
        click.echo(f"Successfully collected and saved data for {saved_count}/{len(stocks)} stocks:")
        for stock in stocks:
            change_symbol = "+" if stock.price_change_percent and stock.price_change_percent > 0 else ""
            change_text = f"{change_symbol}{stock.price_change_percent:.2f}%" if stock.price_change_percent else "N/A"
            click.echo(f"  {stock.name} ({stock.symbol}): ¥{stock.current_price} ({change_text})")
            
    except Exception as e:
        click.echo(f"Error collecting data: {str(e)}")
        logger.error(f"Data collection error: {str(e)}")


@cli.command()
@click.option('--symbol', help='Analyze specific stock symbol')
@click.option('--all', 'analyze_all', is_flag=True, help='Analyze all stored stocks')
def analyze(symbol, analyze_all):
    """Analyze stock data and generate insights."""
    repository = SQLiteRepository()
    analysis_engine = SimpleAnalysisEngine()
    
    try:
        if symbol:
            stock = repository.get_stock(symbol)
            if not stock:
                click.echo(f"Stock {symbol} not found in database. Run 'collect' first.")
                return
            
            click.echo(f"Analyzing {stock.name} ({stock.symbol})...")
            analysis = analysis_engine.analyze_stock(stock)
            repository.save_analysis(analysis)
            
            _display_stock_analysis(stock, analysis)
            
        elif analyze_all:
            stocks = repository.get_all_stocks()
            if not stocks:
                click.echo("No stocks found in database. Run 'collect' first.")
                return
            
            click.echo(f"Analyzing {len(stocks)} stocks...")
            analyses = analysis_engine.analyze_multiple_stocks(stocks)
            
            for analysis in analyses:
                repository.save_analysis(analysis)
            
            # Display summary
            click.echo("\nAnalysis Summary:")
            for i, (stock, analysis) in enumerate(zip(stocks, analyses)):
                risk_color = "red" if analysis.risk_level and analysis.risk_level.value == 'high' else "yellow" if analysis.risk_level and analysis.risk_level.value == 'medium' else "green"
                trend_symbol = "↑" if analysis.trend_direction and analysis.trend_direction.value == 'up' else "↓" if analysis.trend_direction and analysis.trend_direction.value == 'down' else "→"
                
                click.echo(f"  {i+1:2d}. {stock.name[:30]:30} {trend_symbol} Risk: ", nl=False)
                click.secho(f"{analysis.risk_level.value if analysis.risk_level else 'unknown'}", fg=risk_color)
        else:
            click.echo("Please specify --symbol or use --all flag")
            
    except Exception as e:
        click.echo(f"Error during analysis: {str(e)}")
        logger.error(f"Analysis error: {str(e)}")


@cli.command()
@click.option('--type', 'summary_type', type=click.Choice(['daily', 'stock']), default='daily', help='Type of summary to generate')
@click.option('--symbol', help='Stock symbol for individual stock summary')
def summarize(summary_type, symbol):
    """Generate summaries from analysis data."""
    repository = SQLiteRepository()
    summary_service = SummaryService()
    
    try:
        if summary_type == 'daily':
            stocks = repository.get_all_stocks()
            if not stocks:
                click.echo("No stocks found in database. Run 'collect' first.")
                return
            
            # For simplicity, create basic analyses if not available
            analysis_engine = SimpleAnalysisEngine()
            analyses = analysis_engine.analyze_multiple_stocks(stocks)
            
            click.echo("Generating daily market overview...")
            summary = summary_service.generate_daily_overview(stocks, analyses)
            repository.save_summary(summary)
            
            _display_summary(summary)
            
        elif summary_type == 'stock':
            if not symbol:
                click.echo("Please specify --symbol for stock summary")
                return
            
            stock = repository.get_stock(symbol)
            if not stock:
                click.echo(f"Stock {symbol} not found in database. Run 'collect' first.")
                return
            
            analysis_engine = SimpleAnalysisEngine()
            analysis = analysis_engine.analyze_stock(stock)
            
            click.echo(f"Generating summary for {stock.name}...")
            summary = summary_service.generate_stock_analysis_summary(stock, analysis)
            repository.save_summary(summary)
            
            _display_summary(summary)
            
    except Exception as e:
        click.echo(f"Error generating summary: {str(e)}")
        logger.error(f"Summary generation error: {str(e)}")


@cli.command()
def list_stocks():
    """List all stored stocks."""
    repository = SQLiteRepository()
    
    try:
        stocks = repository.get_all_stocks()
        if not stocks:
            click.echo("No stocks found in database.")
            return
        
        click.echo(f"\nStored Stocks ({len(stocks)}):")
        click.echo("-" * 80)
        
        for i, stock in enumerate(stocks, 1):
            change_symbol = "+" if stock.price_change_percent and stock.price_change_percent > 0 else ""
            change_text = f"{change_symbol}{stock.price_change_percent:.2f}%" if stock.price_change_percent else "N/A"
            updated = stock.last_updated.strftime("%Y-%m-%d %H:%M")
            
            click.echo(f"{i:2d}. {stock.name[:40]:40} ({stock.symbol:8}) ¥{stock.current_price:>8} ({change_text:>8}) [{updated}]")
            
    except Exception as e:
        click.echo(f"Error listing stocks: {str(e)}")


@cli.command()
@click.option('--limit', default=5, help='Number of recent summaries to show')
def history(limit):
    """Show recent summaries."""
    repository = SQLiteRepository()
    
    try:
        summaries = repository.get_latest_summaries(limit)
        if not summaries:
            click.echo("No summaries found.")
            return
        
        click.echo(f"\nRecent Summaries ({len(summaries)}):")
        click.echo("-" * 80)
        
        for i, summary in enumerate(summaries, 1):
            created_at = summary.created_at.strftime("%Y-%m-%d %H:%M")
            click.echo(f"{i}. {summary.title} [{created_at}]")
            click.echo(f"   Type: {summary.summary_type.value}, Stocks: {len(summary.stocks_analyzed)}")
            click.echo(f"   {summary.executive_summary[:100]}...")
            if i < len(summaries):
                click.echo()
                
    except Exception as e:
        click.echo(f"Error retrieving history: {str(e)}")


@cli.command()
def health():
    """Check system health."""
    click.echo("Checking system health...")
    
    # Check data source
    collector = YahooFinanceCollector()
    if collector.health_check():
        click.secho("✓ Data source (Yahoo Finance): OK", fg="green")
    else:
        click.secho("✗ Data source (Yahoo Finance): FAILED", fg="red")
    
    # Check database
    try:
        repository = SQLiteRepository()
        stocks = repository.get_all_stocks()
        click.secho(f"✓ Database: OK ({len(stocks)} stocks stored)", fg="green")
    except Exception as e:
        click.secho(f"✗ Database: FAILED ({str(e)})", fg="red")
    
    # Check analysis engine
    try:
        engine = SimpleAnalysisEngine()
        click.secho("✓ Analysis engine: OK", fg="green")
    except Exception as e:
        click.secho(f"✗ Analysis engine: FAILED ({str(e)})", fg="red")


def _display_stock_analysis(stock, analysis):
    """Display detailed stock analysis."""
    click.echo(f"\n=== Analysis for {stock.name} ===")
    
    # Basic info
    change_symbol = "+" if stock.price_change_percent and stock.price_change_percent > 0 else ""
    change_text = f"{change_symbol}{stock.price_change_percent:.2f}%" if stock.price_change_percent else "N/A"
    click.echo(f"Price: ¥{stock.current_price} ({change_text})")
    
    if stock.pe_ratio:
        click.echo(f"P/E Ratio: {stock.pe_ratio}")
    if stock.dividend_yield:
        click.echo(f"Dividend Yield: {stock.dividend_yield}%")
    
    # Analysis results
    if analysis.trend_direction:
        trend_symbol = "↑" if analysis.trend_direction.value == 'up' else "↓" if analysis.trend_direction.value == 'down' else "→"
        click.echo(f"Trend: {trend_symbol} {analysis.trend_direction.value}")
    
    if analysis.rsi:
        rsi_color = "red" if analysis.rsi > 80 or analysis.rsi < 20 else "yellow" if analysis.rsi > 70 or analysis.rsi < 30 else "green"
        click.echo(f"RSI: ", nl=False)
        click.secho(f"{analysis.rsi}", fg=rsi_color)
    
    if analysis.risk_level:
        risk_color = "red" if analysis.risk_level.value == 'high' else "yellow" if analysis.risk_level.value == 'medium' else "green"
        click.echo(f"Risk Level: ", nl=False)
        click.secho(f"{analysis.risk_level.value}", fg=risk_color)
    
    if analysis.risk_factors:
        click.echo("Risk Factors:")
        for factor in analysis.risk_factors:
            click.echo(f"  • {factor}")


def _display_summary(summary):
    """Display summary information."""
    click.echo(f"\n=== {summary.title} ===")
    click.echo(f"Created: {summary.created_at.strftime('%Y-%m-%d %H:%M')}")
    click.echo(f"Type: {summary.summary_type.value}")
    click.echo(f"Stocks: {len(summary.stocks_analyzed)}")
    
    click.echo(f"\n{summary.executive_summary}")
    
    if summary.key_metrics:
        click.echo("\nKey Metrics:")
        for key, value in summary.key_metrics.items():
            click.echo(f"  {key}: {value}")
    
    if summary.insights:
        click.echo(f"\nInsights ({len(summary.insights)}):")
        for insight in summary.insights:
            level_color = "red" if insight.level.value == 'critical' else "yellow" if insight.level.value == 'warning' else "blue"
            click.echo(f"  ", nl=False)
            click.secho(f"[{insight.level.value.upper()}]", fg=level_color, nl=False)
            click.echo(f" {insight.title}")
            click.echo(f"    {insight.description}")
    
    if summary.recommendations:
        click.echo(f"\nRecommendations ({len(summary.recommendations)}):")
        for i, rec in enumerate(summary.recommendations, 1):
            click.echo(f"  {i}. {rec}")


if __name__ == '__main__':
    cli()