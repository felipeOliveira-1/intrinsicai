import asyncio
import logging
from yahoo_finance import YahooFinanceAPI
from typing import Optional, Dict
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.markdown import Markdown
from rich import box
from ai_analysis import AIAnalyst
from ticker_finder import TickerFinder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    force=True
)
logger = logging.getLogger(__name__)

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

def show_welcome_message():
    """Exibe mensagem de boas-vindas"""
    welcome_md = """
    # 📈 Análise de Valor Intrínseco de Ações
    
    Bem-vindo ao analisador de ações! Esta ferramenta ajuda você a:
    
    * Avaliar o valor intrínseco de ações
    * Obter análises detalhadas usando IA
    * Tomar decisões de investimento mais informadas
    
    Desenvolvido por Felipe Oliveira
    """
    console.print(Markdown(welcome_md))
    console.print()

def show_main_menu() -> int:
    """Exibe o menu principal e retorna a opção escolhida"""
    menu = Table(show_header=False, box=box.ROUNDED)
    menu.add_column("Opção", style="cyan", justify="right")
    menu.add_column("Descrição", style="white")
    
    menu.add_row("1", "Analisar por nome da empresa")
    menu.add_row("2", "Analisar por ticker")
    menu.add_row("3", "Sobre o programa")
    menu.add_row("4", "Sair")
    
    console.print(Panel(menu, title="Menu Principal", border_style="blue"))
    
    return IntPrompt.ask(
        "\n[cyan]Escolha uma opção[/cyan]",
        choices=["1", "2", "3", "4"],
        show_choices=False
    )

def show_about():
    """Exibe informações sobre o programa"""
    about_md = """
    # Sobre o Programa
    
    Este programa utiliza técnicas avançadas de análise financeira e inteligência artificial para avaliar ações.
    
    ## Funcionalidades
    
    * **Análise Fundamentalista**: Cálculo do valor intrínseco usando DCF
    * **Inteligência Artificial**: Análise detalhada usando GPT-4
    * **Suporte**: Ações brasileiras (B3) e americanas (NYSE/NASDAQ)
    
    ## Como Usar
    
    1. Escolha entre buscar por nome da empresa ou ticker
    2. Forneça as informações solicitadas
    3. Analise os resultados apresentados
    
    ## Observações
    
    * Para ações brasileiras, os tickers terminam com .SA
    * A análise considera múltiplos fatores financeiros
    * As recomendações da IA são baseadas em dados históricos
    """
    console.print(Markdown(about_md))
    console.print("\nPressione Enter para voltar ao menu principal...", end="")
    input()

def analyze(input_str: str):
    """Analisa uma ação pelo nome da empresa ou ticker"""
    try:
        # Inicializa as APIs
        yahoo_api = YahooFinanceAPI()
        ticker_finder = TickerFinder()
        
        # Verifica se o input é um ticker válido
        if ticker_finder.is_valid_ticker(input_str):
            ticker = input_str.upper()
            if not ticker.endswith('.SA'):  # Se não for BR, verifica se tem .SA no final
                # Pergunta se é ação brasileira
                if Confirm.ask(f"\nO ticker {ticker} é de uma empresa brasileira?"):
                    ticker = f"{ticker}.SA"
            console.print(f"\n[blue]Usando ticker:[/blue] {ticker}")
        else:
            # Se não for ticker, busca usando a IA
            with console.status("[bold green]Buscando ticker...") as status:
                ticker_info = ticker_finder.get_company_ticker(input_str)
            
            if not ticker_info:
                console.print(f"\n[red]Não foi possível encontrar o ticker para: {input_str}[/red]")
                return
            
            # Exibe informações do ticker
            ticker_finder.display_ticker_info(ticker_info)
            
            if not Confirm.ask("\nDeseja continuar com este ticker?"):
                return
            
            ticker = ticker_info['ticker_principal']
        
        # Análise dos dados
        with console.status(f"[bold green]Analisando {ticker}...") as status:
            try:
                # Obtém dados financeiros
                data = asyncio.run(yahoo_api.get_financials(ticker))
                
                # Exibe resultados
                display_analysis(ticker, data)
            except Exception as e:
                if "Could not get basic stock information" in str(e):
                    console.print(f"\n[red]Não foi possível encontrar dados para o ticker {ticker}.[/red]")
                    console.print("[yellow]Verifique se o ticker está correto e tente novamente.[/yellow]")
                else:
                    raise e
        
    except Exception as e:
        console.print(f"\n[red]Erro ao analisar ação:[/red]")
        console.print(f"[red]{str(e)}[/red]")

def main_loop():
    """Loop principal do programa"""
    show_welcome_message()
    
    while True:
        console.clear()
        choice = show_main_menu()
        
        if choice == 1:
            company_name = Prompt.ask("\n[cyan]Digite o nome da empresa[/cyan]")
            analyze(company_name)
            console.print("\nPressione Enter para continuar...", end="")
            input()
            
        elif choice == 2:
            ticker = Prompt.ask(
                "\n[cyan]Digite o ticker[/cyan]",
                help="Para ações brasileiras, adicione .SA (ex: PETR4.SA)"
            )
            analyze(ticker)
            console.print("\nPressione Enter para continuar...", end="")
            input()
            
        elif choice == 3:
            console.clear()
            show_about()
            
        elif choice == 4:
            console.print("\n[green]Obrigado por usar o programa! Até a próxima! 👋[/green]")
            break

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        console.print("\n[yellow]Programa encerrado pelo usuário.[/yellow]")
    except Exception as e:
        console.print("\n[red]Erro inesperado:[/red]")
        console.print(f"[red]{str(e)}[/red]")
