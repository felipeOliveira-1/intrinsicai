import asyncio
import logging
from yahoo_finance import YahooFinanceAPI
from typing import List, Optional, Dict
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from ai_analysis import AIAnalyst

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    force=True
)
logger = logging.getLogger(__name__)

# Initialize API and CLI
yahoo_api = YahooFinanceAPI()
app = typer.Typer()
console = Console()

def format_number(num: float, precision: int = 2) -> str:
    """Format a number with commas and specified precision"""
    try:
        if abs(num) >= 1e9:
            return f"${num/1e9:.{precision}f}B"
        elif abs(num) >= 1e6:
            return f"${num/1e6:.{precision}f}M"
        else:
            return f"${num:,.{precision}f}"
    except Exception:
        return "$0.00"

def format_percentage(num: float, precision: int = 1) -> str:
    """Format a number as percentage"""
    try:
        return f"{num:,.{precision}f}%"
    except Exception:
        return "0.0%"

def get_growth_rating(growth_rate: float) -> str:
    """Get a qualitative rating for growth rate"""
    if growth_rate > 20:
        return "[bold green]Excellent[/bold green]"
    elif growth_rate > 15:
        return "[green]Very Good[/green]"
    elif growth_rate > 10:
        return "[blue]Good[/blue]"
    elif growth_rate > 5:
        return "[yellow]Moderate[/yellow]"
    else:
        return "[red]Low[/red]"

def get_fcf_quality_rating(metrics: dict) -> str:
    """Get a qualitative rating for FCF quality"""
    score = 0
    
    # FCF to Income ratio
    if metrics['fcf_to_income'] > 90:
        score += 2
    elif metrics['fcf_to_income'] > 80:
        score += 1
    elif metrics['fcf_to_income'] < 70:
        score -= 1
        
    # Debt to FCF ratio
    if metrics['debt_to_fcf'] < 3:
        score += 2
    elif metrics['debt_to_fcf'] < 5:
        score += 1
    else:
        score -= 1
        
    # Working capital changes
    if abs(metrics['working_capital_change']) < 0.1 * metrics['fcf_to_income']:
        score += 1
    
    if score >= 4:
        return "[bold green]High Quality[/bold green]"
    elif score >= 2:
        return "[green]Good Quality[/green]"
    elif score >= 0:
        return "[yellow]Average Quality[/yellow]"
    else:
        return "[red]Low Quality[/red]"

def display_analysis(ticker: str, data: Dict) -> None:
    """Display stock analysis results"""
    try:
        # Extract data
        current_price = data['market_data']['current_price']
        shares = data['market_data']['shares_outstanding']
        market_cap = current_price * shares
        
        latest_fcf = data['cash_flow']['free_cashflow']['latest']
        fcf_history = data['cash_flow']['free_cashflow']['history']
        growth_rate = data['cash_flow']['free_cashflow']['growth_rate']
        
        quality_metrics = data['cash_flow']['quality']
        wacc = data['valuation'].get('wacc', 'N/A')
        multiple = data['valuation']['suggested_multiple']
        
        # Calculate valuation
        fcf_per_share = latest_fcf / shares
        fair_value = fcf_per_share * multiple
        upside = ((fair_value / current_price) - 1) * 100

        # Create table
        table = Table(title=f"Stock Analysis for {ticker}", show_header=True)
        
        # Market Data
        table.add_column("Metric", style="default")
        table.add_column("Value", justify="right")
        
        table.add_row("Current Price", f"${current_price:,.2f}")
        table.add_row("Market Cap", f"${market_cap/1e9:,.2f}B")
        table.add_row("Shares Outstanding", f"{shares:,.0f}")
        
        # Cash Flow Analysis
        table.add_section()
        table.add_row("Latest FCF", f"${latest_fcf/1e9:,.2f}B")
        table.add_row("FCF Growth Rate", f"{growth_rate:.1f}%")
        table.add_row("FCF per Share", f"${fcf_per_share:.2f}")
        
        # Quality Metrics
        table.add_section()
        table.add_row("FCF/Net Income", f"{quality_metrics['fcf_to_income']:.1f}%")
        table.add_row("Debt/FCF", f"{quality_metrics['debt_to_fcf']:.1f}x")
        table.add_row("Working Capital Change", f"${quality_metrics['working_capital_change']/1e9:,.2f}B")
        
        # Valuation
        table.add_section()
        table.add_row("WACC", f"{wacc}%")
        table.add_row("Suggested Multiple", f"{multiple:.1f}x")
        table.add_row("Fair Value", f"${fair_value:.2f}")
        table.add_row("Upside Potential", f"{upside:+.1f}%")
        
        # Print results
        console.print(table)
        
        # Print recommendation
        if upside > 20:
            console.print("\n[green]Strong Buy[/green]: Stock appears significantly undervalued")
        elif upside > 5:
            console.print("\n[green]Buy[/green]: Stock appears moderately undervalued")
        elif upside > -5:
            console.print("\n[yellow]Hold[/yellow]: Stock appears fairly valued")
        elif upside > -20:
            console.print("\n[red]Sell[/red]: Stock appears moderately overvalued")
        else:
            console.print("\n[red]Strong Sell[/red]: Stock appears significantly overvalued")
            
        # Get AI Analysis
        ai_analyst = AIAnalyst()
        ai_analysis = asyncio.run(ai_analyst.get_analysis(ticker, data))
        console.print("\n[bold blue]AI Expert Analysis:[/bold blue]")
        console.print(Panel(ai_analysis, title="Investment Recommendation", border_style="blue"))
            
    except Exception as e:
        console.print(f"\n[red]Error displaying analysis: {str(e)}[/red]")

@app.command()
def analyze(
    ticker: str = typer.Argument(..., help="Stock ticker symbol to analyze"),
    multiple: float = typer.Option(None, help="Override the suggested FCF multiple"),
    margin: float = typer.Option(0.3, help="Margin of safety (0.3 = 30%)")
):
    """Analyze a stock and determine if it's a good buy based on FCF analysis"""
    try:
        # Show loading message
        with console.status(f"[bold green]Analyzing {ticker.upper()}...", spinner="dots") as status:
            # Run the analysis
            try:
                data = asyncio.run(yahoo_api.get_financials(ticker))
                status.stop()
                # Display results
                display_analysis(ticker, data)
            except Exception as e:
                status.stop()
                console.print(f"\n[red]Error analyzing {ticker}:[/red]")
                console.print(f"[red]{str(e)}[/red]")
                return
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Unexpected error:[/red]")
        console.print(f"[red]{str(e)}[/red]")

@app.command()
def analyze_multiple(
    tickers: List[str] = typer.Argument(..., help="List of stock tickers to analyze"),
    multiple: float = typer.Option(None, help="Override the suggested FCF multiple"),
    margin: float = typer.Option(0.3, help="Margin of safety (0.3 = 30%)")
):
    """Analyze multiple stocks at once"""
    for i, ticker in enumerate(tickers):
        if i > 0:
            console.print()
        console.rule(f"[bold]Analysis for {ticker.upper()}[/bold]")
        analyze(ticker, multiple, margin)

if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Program terminated by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Fatal error:[/red]")
        console.print(f"[red]{str(e)}[/red]")
