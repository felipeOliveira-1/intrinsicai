import os
from typing import Dict
from openai import OpenAI
from rich.console import Console

class AIAnalyst:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.console = Console()
        self.system_prompt = """As an assistant personifying an Expert in Markets and Stock Market, your task is to provide counsel to the user regarding a stock after analyzing the information given to you. Utilize your deep understanding of macroeconomic indicators and market dynamics, expertise in fundamental and technical analysis, proficiency in risk management and portfolio construction, quantitative and analytical skills, ability to interpret financial statements and market data, familiarity with trading strategies and market microstructure, and skill in using financial modeling tools and data analytics.

In addition, draw upon your strategic vision and leadership to design and implement complex investment strategies, mastery of advanced risk management and capital allocation techniques, knowledge of alternative investments, derivatives, and leverage strategies, quantitative analysis and financial modeling skills, expertise in identifying and exploiting market inefficiencies, regulatory and compliance knowledge, proficiency in investor relations and capital raising, team management and mentorship abilities, resilience and adaptability in changing market environments, and robust decision-making skills under pressure and uncertainty.

Provide comprehensive counsel that considers the user's needs and the current market conditions, offering a balanced and informed recommendation based on your expertise. Your response should be well-reasoned, insightful, and tailored to the specific stock in question, taking into account both the potential benefits and risks associated with the investment. Give your final answer in pt-br"""

    def format_analysis_data(self, ticker: str, data: Dict) -> str:
        """Format the stock analysis data for the AI prompt"""
        current_price = data['market_data']['current_price']
        shares = data['market_data']['shares_outstanding']
        market_cap = current_price * shares
        
        latest_fcf = data['cash_flow']['free_cashflow']['latest']
        fcf_history = data['cash_flow']['free_cashflow']['history']
        growth_rate = data['cash_flow']['free_cashflow']['growth_rate']
        
        quality_metrics = data['cash_flow']['quality']
        wacc = data.get('valuation', {}).get('wacc', 'N/A')
        multiple = data['valuation']['suggested_multiple']
        
        fcf_per_share = latest_fcf / shares
        fair_value = fcf_per_share * multiple
        upside = ((fair_value / current_price) - 1) * 100

        analysis = f"""
Stock Analysis for {ticker}:

Market Data:
- Current Price: ${current_price:,.2f}
- Market Cap: ${market_cap/1e9:,.2f}B
- Shares Outstanding: {shares:,.0f}

Cash Flow Analysis:
- Latest Free Cash Flow: ${latest_fcf/1e9:,.2f}B
- FCF Growth Rate: {growth_rate:.1f}%
- FCF per Share: ${fcf_per_share:.2f}

Quality Metrics:
- FCF/Net Income: {quality_metrics['fcf_to_income']:.1f}%
- Debt/FCF: {quality_metrics['debt_to_fcf']:.1f}x
- Working Capital Change: ${quality_metrics['working_capital_change']/1e9:,.2f}B

Valuation:
- WACC: {wacc}%
- Suggested Multiple: {multiple:.1f}x
- Fair Value: ${fair_value:.2f}
- Upside Potential: {upside:+.1f}%

Historical FCF:
"""
        for i, fcf in enumerate(fcf_history):
            analysis += f"Year {len(fcf_history) - i}: ${fcf/1e9:,.2f}B\n"
        
        return analysis

    async def get_analysis(self, ticker: str, data: Dict) -> str:
        """Get AI analysis for the stock"""
        try:
            analysis_data = self.format_analysis_data(ticker, data)
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Please analyze this stock data and provide your expert recommendation:\n\n{analysis_data}"}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.17,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.console.print(f"\n[red]Error getting AI analysis: {str(e)}[/red]")
            return "AI analysis unavailable at the moment."
