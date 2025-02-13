import numpy as np
import logging
import json
import os
import aiohttp
import asyncio
from typing import Dict, Optional, List, Tuple
import time
from datetime import datetime, timedelta
import aiofiles

logger = logging.getLogger(__name__)

class DCFModel:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.cache_dir = os.path.join(os.path.dirname(__file__), 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        self.timeout = aiohttp.ClientTimeout(total=10)  # 10 seconds timeout
        
    async def fetch_financials(self, ticker: str) -> Dict:
        """
        Busca dados financeiros do Alpha Vantage com foco em Cash Flow e Income Statement
        """
        try:
            # Tenta obter dados do cache primeiro
            cached_data = await self._get_from_cache(ticker)
            if cached_data:
                logger.info(f"Usando dados em cache para {ticker}")
                return cached_data
            
            # Se não estiver em cache, busca da API com retentativas
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Busca dados dos endpoints principais
                    tasks = [
                        self._fetch_data("CASH_FLOW", ticker),        # Principal: Fluxo de Caixa
                        self._fetch_data("INCOME_STATEMENT", ticker),  # Secundário: Demonstração de Resultados
                        self._fetch_data("OVERVIEW", ticker),         # Dados gerais da empresa
                    ]
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Verifica erros
                    errors = [r for r in results if isinstance(r, Exception)]
                    if errors:
                        error_msg = str(errors[0])
                        if "API rate limit exceeded" in error_msg:
                            raise ValueError("Limite de requisições da API excedido. Tente novamente em alguns minutos.")
                        elif "timeout" in error_msg.lower():
                            if attempt < max_retries - 1:
                                logger.warning(f"Timeout na tentativa {attempt + 1}, tentando novamente...")
                                await asyncio.sleep(1)
                                continue
                            raise ValueError("Timeout na conexão. Verifique sua conexão com a internet.")
                        else:
                            raise ValueError(f"Erro na API: {error_msg}")
                    
                    cash_flow, income, overview = results
                    break  # Sucesso, sai do loop de tentativas
                    
                except asyncio.TimeoutError:
                    if attempt < max_retries - 1:
                        logger.warning(f"Timeout na tentativa {attempt + 1}, tentando novamente...")
                        await asyncio.sleep(1)
                        continue
                    raise ValueError("Timeout na conexão. Verifique sua conexão com a internet.")
            
            # Validação inicial dos dados
            if not cash_flow or not income or not overview:
                missing = []
                if not cash_flow: missing.append("fluxo de caixa")
                if not income: missing.append("demonstração de resultados")
                if not overview: missing.append("visão geral da empresa")
                raise ValueError(f"Dados financeiros ausentes: {', '.join(missing)}")
            
            # Processa dados da empresa
            metadata = {
                'name': overview.get('Name', ''),
                'sector': overview.get('Sector', ''),
                'industry': overview.get('Industry', ''),
                'description': overview.get('Description', '')
            }
            
            def safe_float(value, default=0.0):
                try:
                    return float(value) if value else default
                except (ValueError, TypeError):
                    return default
            
            # Obtém relatórios anuais
            cash_flow_reports = cash_flow.get('annualReports', [])
            income_reports = income.get('annualReports', [])
            
            # Verifica se temos pelo menos 1 ano de dados
            if not cash_flow_reports or not income_reports:
                raise ValueError("Não foram encontrados dados financeiros para esta empresa")
            
            # Pega o máximo de anos disponíveis (até 5)
            num_years = min(5, len(cash_flow_reports), len(income_reports))
            if num_years < 1:
                raise ValueError("Dados financeiros insuficientes para análise")
                
            logger.info(f"Usando {num_years} anos de dados históricos para {ticker}")
            
            recent_cash_flows = cash_flow_reports[:num_years]
            recent_income = income_reports[:num_years]
            
            # Calcula médias e tendências
            fcf_values = []
            revenue_growth = []
            
            for i in range(num_years):
                # Fluxo de Caixa
                cf_data = recent_cash_flows[i]
                operating_cf = safe_float(cf_data.get('operatingCashflow'))
                capex = safe_float(cf_data.get('capitalExpenditures'))
                fcf = operating_cf - capex
                fcf_values.append(fcf)
                
                # Crescimento da Receita (se tivermos mais de 1 ano)
                if i < num_years - 1:
                    current_revenue = safe_float(recent_income[i].get('totalRevenue'))
                    prev_revenue = safe_float(recent_income[i + 1].get('totalRevenue'))
                    if prev_revenue > 0:
                        growth = (current_revenue - prev_revenue) / prev_revenue
                        revenue_growth.append(growth)
            
            # Calcula médias (com pesos maiores para anos mais recentes)
            if len(fcf_values) > 0:
                weights = [1.0, 0.8, 0.6, 0.4, 0.2][:len(fcf_values)]
                weight_sum = sum(weights)
                avg_fcf = sum(fcf * w for fcf, w in zip(fcf_values, weights)) / weight_sum
            else:
                raise ValueError("Não foi possível calcular o fluxo de caixa livre médio")
            
            # Calcula crescimento médio (ou usa valor padrão se não tivermos dados suficientes)
            if revenue_growth:
                avg_growth = sum(revenue_growth) / len(revenue_growth)
            else:
                # Se não tivermos dados de crescimento, usa crescimento do setor ou valor conservador
                avg_growth = 0.03  # 3% como valor base conservador
                logger.warning(f"Usando taxa de crescimento padrão de {avg_growth:.1%} para {ticker}")
            
            # Dados de mercado
            market_data = {
                'market_cap': safe_float(overview.get('MarketCapitalization')),
                'shares_outstanding': safe_float(overview.get('SharesOutstanding')),
                'beta': safe_float(overview.get('Beta')),
                'pe_ratio': safe_float(overview.get('PERatio')),
                'market_price': safe_float(overview.get('52WeekHigh'))
            }
            
            # Validações críticas
            if avg_fcf <= 0:
                raise ValueError("Fluxo de caixa livre médio negativo ou zero. Empresa pode estar em dificuldades financeiras.")
            
            if market_data['shares_outstanding'] <= 0:
                raise ValueError("Dados de ações em circulação indisponíveis")
            
            # Processa métricas financeiras
            latest_cf = recent_cash_flows[0]
            latest_income = recent_income[0]
            
            processed_data = {
                'metadata': metadata,
                'market_data': market_data,
                'financial_metrics': {
                    'cash_flow': {
                        'recent_free_cash_flows': fcf_values,
                        'average_fcf': avg_fcf,
                        'operating_cash_flow': safe_float(latest_cf.get('operatingCashflow')),
                        'capital_expenditure': safe_float(latest_cf.get('capitalExpenditures')),
                        'free_cash_flow': fcf_values[0] if fcf_values else 0
                    },
                    'income': {
                        'revenue': safe_float(latest_income.get('totalRevenue')),
                        'operating_income': safe_float(latest_income.get('operatingIncome')),
                        'net_income': safe_float(latest_income.get('netIncome')),
                        'historical_growth': avg_growth
                    }
                }
            }
            
            # Cache os dados processados
            await self._save_to_cache(ticker, processed_data)
            
            return processed_data
            
        except ValueError as e:
            logger.error(f"Erro de validação para {ticker}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar dados para {ticker}: {str(e)}")
            raise ValueError(f"Falha ao buscar dados financeiros: {str(e)}")

    async def _fetch_data(self, function: str, ticker: str) -> Dict:
        """Helper method to fetch data from Alpha Vantage API with rate limiting"""
        try:
            params = {
                'function': function,
                'symbol': ticker,
                'apikey': self.api_key
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status != 200:
                        raise ValueError(f"API request failed with status {response.status}")
                    
                    data = await response.json()
                    
                    if "Error Message" in data:
                        raise ValueError(data["Error Message"])
                    
                    if "Note" in data and "Thank you for using Alpha Vantage!" in data["Note"]:
                        raise ValueError("API rate limit exceeded")
                    
                    await asyncio.sleep(0.25)  # Rate limiting
                    return data
                    
        except asyncio.TimeoutError:
            raise ValueError(f"Timeout while fetching {function} data")
        except Exception as e:
            logger.error(f"Error fetching {function} data for {ticker}: {str(e)}")
            raise

    async def _get_from_cache(self, ticker: str) -> Optional[Dict]:
        """Get data from cache if available and not expired"""
        cache_file = os.path.join(self.cache_dir, f"{ticker.lower()}.json")
        try:
            if not os.path.exists(cache_file):
                return None
                
            async with aiofiles.open(cache_file, 'r') as f:
                cached = json.loads(await f.read())
                
            # Check if cache is expired (24 hours)
            cache_time = datetime.fromisoformat(cached['cache_timestamp'])
            if datetime.now() - cache_time > timedelta(hours=24):
                return None
                
            return cached['data']
            
        except Exception as e:
            logger.error(f"Error reading cache for {ticker}: {str(e)}")
            return None
            
    async def _save_to_cache(self, ticker: str, data: Dict):
        """Save data to cache"""
        cache_file = os.path.join(self.cache_dir, f"{ticker.lower()}.json")
        try:
            cache_data = {
                'cache_timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            async with aiofiles.open(cache_file, 'w') as f:
                await f.write(json.dumps(cache_data, indent=2))
                
        except Exception as e:
            logger.error(f"Error saving cache for {ticker}: {str(e)}")

    def calculate_owners_earnings(self, operating_cashflow: float, maintenance_capex: float) -> float:
        """Calculate owner's earnings (Warren Buffett's metric)"""
        return operating_cashflow - maintenance_capex

    def calculate_terminal_value(self, final_cashflow: float, growth_rate: float, 
                               discount_rate: float, method: str = 'gordon') -> float:
        """Calculate terminal value using either Gordon Growth or P/E Multiple method"""
        if method == 'gordon':
            terminal_growth = min(growth_rate / 2, 0.04)  # Conservative terminal growth
            return final_cashflow * (1 + terminal_growth) / (discount_rate - terminal_growth)
        else:  # P/E Multiple
            pe_multiple = 15  # Industry average P/E
            return final_cashflow * pe_multiple

    def calculate_npv(self, cash_flows: List[float], discount_rate: float) -> float:
        """Calculate Net Present Value of cash flows"""
        return sum(cf / (1 + discount_rate) ** (i + 1) for i, cf in enumerate(cash_flows))

    async def calculate_intrinsic_value(
        self, 
        ticker: str, 
        growth_rate: float = None,  # Se None, usa crescimento histórico
        discount_rate: float = 0.1,
        years: int = 10,
        terminal_method: str = 'gordon'
    ) -> Dict:
        """
        Realiza análise DCF usando média histórica de FCF e crescimento
        """
        try:
            # Busca dados financeiros
            financials = await self.fetch_financials(ticker)
            
            # Extrai métricas principais
            fcf_data = financials['financial_metrics']['cash_flow']
            income_data = financials['financial_metrics']['income']
            market_data = financials['market_data']
            
            # Usa média do FCF como base para projeções
            base_fcf = fcf_data['average_fcf']
            
            # Se growth_rate não foi especificado, usa crescimento histórico
            if growth_rate is None:
                growth_rate = max(min(income_data['historical_growth'], 0.20), 0.02)
                logger.info(f"Usando taxa de crescimento histórica de {growth_rate:.1%}")
            
            # Projeta fluxos de caixa futuros
            cash_flows = []
            for year in range(1, years + 1):
                # Aplica taxa de crescimento decrescente após 5 anos
                if year <= 5:
                    year_growth = growth_rate
                else:
                    # Reduz gradualmente para 3% (crescimento perpétuo conservador)
                    year_growth = max(growth_rate * (1 - (year - 5) / 10), 0.03)
                
                projected_fcf = base_fcf * (1 + year_growth) ** year
                cash_flows.append(projected_fcf)
            
            # Calcula valor terminal
            if terminal_method == 'gordon':
                # Usa taxa de crescimento perpétuo conservadora
                perpetual_growth = min(growth_rate / 2, 0.03)  # Máximo de 3%
                
                if discount_rate <= perpetual_growth:
                    raise ValueError("Taxa de desconto deve ser maior que a taxa de crescimento perpétuo")
                
                terminal_value = cash_flows[-1] * (1 + perpetual_growth) / (discount_rate - perpetual_growth)
            else:  # exit_multiple
                # Usa múltiplo de saída conservador baseado no setor
                exit_multiple = 12  # Múltiplo EV/FCFF conservador
                terminal_value = cash_flows[-1] * exit_multiple
            
            # Calcula valor presente
            def calculate_present_value(future_value, rate, year):
                if rate <= -1:  # Evita divisão por zero ou denominadores negativos
                    raise ValueError("Taxa de desconto inválida")
                return future_value / ((1 + rate) ** year)
            
            # Calcula VPL dos fluxos de caixa e valor terminal
            try:
                npv_cash_flows = sum(calculate_present_value(cf, discount_rate, year) 
                                   for year, cf in enumerate(cash_flows, 1))
                npv_terminal = calculate_present_value(terminal_value, discount_rate, years)
            except (ValueError, ZeroDivisionError) as e:
                raise ValueError(f"Erro nos cálculos de valor presente: {str(e)}")
            
            # Calcula valor total e por ação
            total_value = npv_cash_flows + npv_terminal
            shares_outstanding = market_data['shares_outstanding']
            
            if shares_outstanding <= 0:
                raise ValueError("Número de ações em circulação inválido")
            
            per_share_value = total_value / shares_outstanding
            
            if per_share_value <= 0:
                raise ValueError("Valor intrínseco calculado é negativo ou zero")
            
            # Prepara resposta detalhada
            return {
                'metadata': financials['metadata'],
                'market_data': market_data,
                'financial_metrics': financials['financial_metrics'],
                'dcf_analysis': {
                    'base_fcf': round(base_fcf, 2),
                    'growth_rate': round(growth_rate, 4),
                    'discount_rate': round(discount_rate, 4),
                    'projected_cash_flows': [round(cf, 2) for cf in cash_flows],
                    'terminal_value': round(terminal_value, 2),
                    'npv_cash_flows': round(npv_cash_flows, 2),
                    'npv_terminal': round(npv_terminal, 2),
                    'total_value': round(total_value, 2),
                    'per_share_value': round(per_share_value, 2)
                }
            }
            
        except ValueError as e:
            logger.error(f"Erro de valuation para {ticker}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado no cálculo DCF para {ticker}: {str(e)}")
            raise ValueError(f"Falha ao calcular valor intrínseco: {str(e)}")
