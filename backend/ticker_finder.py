import os
from typing import Optional, Dict
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

class TickerFinder:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.console = Console()
        self.system_prompt = """Você é um especialista em mercado financeiro. Forneça APENAS as informações solicitadas no formato especificado.

Para empresas brasileiras:
- Use o sufixo .SA
- Identifique ações ON (ordinárias) e PN (preferenciais)

Para empresas americanas:
- Use o ticker da NYSE/NASDAQ
- Não use sufixos

Responda EXATAMENTE neste formato:
TICKER_PRINCIPAL: <ticker>
MERCADO: <BR/US>
NOTA: <explicação_curta>"""

    def get_company_ticker(self, company_name: str) -> Optional[Dict[str, str]]:
        """
        Busca o ticker de uma empresa usando IA.
        Retorna um dicionário com ticker principal, mercado e explicação.
        """
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Qual o ticker para: {company_name}?"}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.1,
                max_tokens=100  # Reduzido para respostas mais rápidas
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse da resposta
            info = {
                "ticker_principal": "",
                "mercado": "",
                "nota": ""
            }
            
            for line in result.split('\n'):
                if line.startswith('TICKER_PRINCIPAL:'):
                    info['ticker_principal'] = line.replace('TICKER_PRINCIPAL:', '').strip()
                elif line.startswith('MERCADO:'):
                    info['mercado'] = line.replace('MERCADO:', '').strip()
                elif line.startswith('NOTA:'):
                    info['nota'] = line.replace('NOTA:', '').strip()
            
            if not info['ticker_principal']:
                return None
                
            return info
            
        except Exception as e:
            self.console.print(f"[red]Erro ao buscar ticker: {str(e)}[/red]")
            return None

    def display_ticker_info(self, info: Dict[str, str]) -> None:
        """Exibe as informações do ticker de forma formatada"""
        if not info:
            return
            
        panel_content = [
            f"[bold blue]Ticker:[/bold blue] {info['ticker_principal']}",
            f"[bold green]Mercado:[/bold green] {'Brasil' if info['mercado'] == 'BR' else 'Estados Unidos'}",
            f"[bold white]Nota:[/bold white] {info['nota']}"
        ]
        
        self.console.print(Panel(
            "\n".join(panel_content),
            title="Informações do Ticker",
            border_style="blue"
        ))

    def is_valid_ticker(self, input_str: str) -> bool:
        """Verifica se o input parece ser um ticker válido"""
        if not input_str:
            return False
        
        # Remove espaços e converte para maiúsculo
        input_str = input_str.strip().upper()
        
        # Verifica se é ticker BR (.SA)
        if input_str.endswith('.SA'):
            base = input_str[:-3]  # Remove o .SA
            return (
                len(base) >= 4 and
                len(base) <= 6 and
                base[-1].isdigit() and  # Último caractere deve ser número
                all(c.isalpha() for c in base[:-1])  # Resto deve ser letras
            )
        
        # Verifica se é ticker US
        return (
            len(input_str) >= 1 and
            len(input_str) <= 5 and
            ' ' not in input_str and
            all(c.isalpha() for c in input_str)  # Deve ser apenas letras
        )
