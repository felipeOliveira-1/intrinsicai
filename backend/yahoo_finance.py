import asyncio
import traceback
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Dict, Optional, List
import numpy as np

import yfinance as yf
import pandas as pd

class YahooFinanceAPI:
    def __init__(self):
        """Initialize the Yahoo Finance API wrapper"""
        self._executor = ThreadPoolExecutor(max_workers=3)
        print("Initialized YahooFinanceAPI")

    def calculate_cagr(self, values: List[float], years: int) -> float:
        """Calculate Compound Annual Growth Rate"""
        if len(values) < 2 or years < 1:
            return 0.0
        try:
            start_value = values[-1]  # Oldest value
            end_value = values[0]     # Newest value
            if start_value <= 0:
                return 0.0
            return (pow(end_value / start_value, 1/years) - 1) * 100
        except Exception:
            return 0.0

    def calculate_quality_metrics(self, stock: yf.Ticker) -> Dict:
        """Calculate FCF quality metrics"""
        try:
            # Get financial statements
            income = stock.income_stmt  # Try income_stmt first
            if income.empty:
                income = stock.financials  # Fall back to financials
                
            balance = stock.balance_sheet
            cash_flow = stock.cashflow

            if any(df.empty for df in [income, balance, cash_flow]):
                raise ValueError("Missing financial statements")

            # Get latest values
            net_income = None
            for field in ['Net Income', 'Net Income Common Stockholders']:
                if field in income.index:
                    net_income = float(income.loc[field].iloc[0])
                    break
            
            if net_income is None:
                raise ValueError("Could not find Net Income")

            # Get FCF from cash flow
            ocf = None
            ocf_fields = [
                'Total Cash From Operating Activities',
                'Operating Cash Flow',
                'Cash Flow From Operating Activities',
                'Net Operating Cash Flow',
                'Cash Flow from Operating Activities'
            ]
            for field in ocf_fields:
                if field in cash_flow.index:
                    ocf = float(cash_flow.loc[field].iloc[0])
                    break
            
            if ocf is None:
                raise ValueError("Could not find Operating Cash Flow")

            capex = 0
            capex_fields = [
                'Capital Expenditures',
                'Purchase Of Plant And Equipment',
                'Purchase Of Property And Equipment',
                'Property Plant And Equipment',
                'Capex',
                'Capital Expenditure'
            ]
            for field in capex_fields:
                if field in cash_flow.index:
                    capex = float(cash_flow.loc[field].iloc[0])
                    break

            fcf = ocf + capex

            # Get total debt
            total_debt = 0
            debt_fields = [
                'Total Debt',
                'Long Term Debt',
                'Short Long Term Debt',
                'Current Debt'
            ]
            for field in debt_fields:
                if field in balance.index:
                    total_debt += float(balance.loc[field].iloc[0])
            
            # Calculate metrics
            fcf_to_income = (fcf / net_income * 100) if net_income != 0 else 0
            debt_to_fcf = total_debt / fcf if fcf != 0 else float('inf')
            
            # Get working capital changes
            wc_change = 0
            wc_fields = [
                'Change In Working Capital',
                'Changes In Working Capital'
            ]
            for field in wc_fields:
                if field in cash_flow.index:
                    wc_change = float(cash_flow.loc[field].iloc[0])
                    break
            
            return {
                'fcf_to_income': fcf_to_income,
                'debt_to_fcf': debt_to_fcf,
                'working_capital_change': wc_change
            }
        except Exception as e:
            print(f"Error calculating quality metrics: {str(e)}")
            return {
                'fcf_to_income': 0,
                'debt_to_fcf': float('inf'),
                'working_capital_change': 0
            }

    def calculate_wacc(self, stock: yf.Ticker) -> float:
        """Calculate Weighted Average Cost of Capital"""
        try:
            info = stock.info
            balance = stock.balance_sheet
            income = stock.income_stmt
            if income.empty:
                income = stock.financials

            if any(df.empty for df in [balance, income]):
                raise ValueError("Missing financial statements")

            # Cost of Equity using CAPM
            risk_free_rate = 0.0425  # 10-year Treasury yield (approximate)
            market_premium = 0.06     # Historical market risk premium
            beta = info.get('beta', 1.0)
            cost_of_equity = risk_free_rate + (beta * market_premium)

            # Get total debt
            total_debt = 0
            debt_fields = [
                'Total Debt',
                'Long Term Debt',
                'Short Long Term Debt',
                'Current Debt'
            ]
            for field in debt_fields:
                if field in balance.index:
                    total_debt += float(balance.loc[field].iloc[0])

            # Get interest expense
            interest_expense = 0
            interest_fields = [
                'Interest Expense',
                'Interest Expense Non Operating',
                'Interest Expense Net'
            ]
            for field in interest_fields:
                if field in income.index:
                    interest_expense += abs(float(income.loc[field].iloc[0]))

            # Cost of Debt
            cost_of_debt = (interest_expense / total_debt) if total_debt > 0 else 0
            tax_rate = 0.21  # Approximate corporate tax rate
            after_tax_cost_of_debt = cost_of_debt * (1 - tax_rate)

            # Capital Structure
            market_cap = info.get('marketCap', 0)
            total_capital = market_cap + total_debt
            equity_weight = market_cap / total_capital if total_capital > 0 else 1
            debt_weight = 1 - equity_weight

            # WACC
            wacc = (cost_of_equity * equity_weight) + (after_tax_cost_of_debt * debt_weight)
            return wacc * 100  # Return as percentage
        except Exception as e:
            print(f"Error calculating WACC: {str(e)}")
            return 8.0  # Return default WACC of 8%

    def get_dynamic_multiple(self, growth_rate: float, quality_metrics: Dict, wacc: float) -> float:
        """Calculate dynamic FCF multiple based on growth and quality"""
        try:
            # Base multiple based on growth rate
            if growth_rate > 15:
                base_multiple = 15
            elif growth_rate > 10:
                base_multiple = 12
            elif growth_rate > 5:
                base_multiple = 10
            else:
                base_multiple = 8

            # Adjust for FCF quality
            quality_score = 1.0
            if quality_metrics['fcf_to_income'] > 90:
                quality_score += 0.2
            elif quality_metrics['fcf_to_income'] < 70:
                quality_score -= 0.2

            if quality_metrics['debt_to_fcf'] < 3:
                quality_score += 0.2
            elif quality_metrics['debt_to_fcf'] > 5:
                quality_score -= 0.2

            # Adjust for WACC
            wacc_adjustment = 1.0
            if wacc < 8:
                wacc_adjustment = 1.1
            elif wacc > 12:
                wacc_adjustment = 0.9

            return base_multiple * quality_score * wacc_adjustment
        except Exception as e:
            print(f"Error calculating dynamic multiple: {str(e)}")
            return 10.0  # Default to 10x multiple

    def _get_data_sync(self, ticker: str) -> Dict:
        """Synchronously fetch stock data"""
        try:
            stock = yf.Ticker(ticker)
            print(f"Fetching data for {ticker}")
            
            # Get basic info
            info = stock.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            shares_outstanding = info.get('sharesOutstanding')
            
            if not current_price or not shares_outstanding:
                raise ValueError("Could not get basic stock information")

            # Get financial statements
            print("Fetching financial statements...")
            
            # Try different approaches to get cash flow data
            cash_flow = None
            try:
                print("Trying annual cash flow...")
                cf = stock.cashflow
                if not cf.empty:
                    cash_flow = cf
                    print("Got annual cash flow data")
                    print(cash_flow)
            except Exception as e:
                print(f"Error getting annual cash flow: {str(e)}")
                
            if cash_flow is None:
                try:
                    print("Trying quarterly cash flow...")
                    cf = stock.quarterly_cashflow
                    if not cf.empty:
                        cash_flow = cf
                        print("Got quarterly cash flow data")
                        print(cash_flow)
                except Exception as e:
                    print(f"Error getting quarterly cash flow: {str(e)}")

            if cash_flow is None:
                raise ValueError("No cash flow data available")

            print("\nAvailable cash flow fields:")
            for field in cash_flow.index:
                print(f"  - {field}")

            # Calculate historical FCF
            fcf_history = []
            
            # Try to get FCF directly first
            if 'Free Cash Flow' in cash_flow.index:
                print("\nFound Free Cash Flow field, using it directly")
                for period in cash_flow.columns:
                    try:
                        value = cash_flow.loc['Free Cash Flow', period]
                        if pd.notna(value):
                            fcf = float(value)
                            print(f"Period {period}: FCF = {fcf:,.2f}")
                            fcf_history.append(fcf)
                    except Exception as e:
                        print(f"Error getting FCF for period {period}: {str(e)}")
                        continue
            
            # If we couldn't get FCF directly, try calculating it
            if not fcf_history:
                print("\nCould not get FCF directly, trying to calculate from components")
                for period in cash_flow.columns:
                    try:
                        print(f"\nAnalyzing period: {period}")
                        
                        # Try to get Operating Cash Flow and Capital Expenditure
                        ocf = None
                        capex = None
                        
                        # Look for Operating Cash Flow
                        for field in cash_flow.index:
                            if any(term in field.lower() for term in ['operating', 'operations']):
                                try:
                                    value = cash_flow.loc[field, period]
                                    if pd.notna(value):
                                        ocf = float(value)
                                        print(f"Found OCF in field '{field}': {ocf:,.2f}")
                                        break
                                except Exception as e:
                                    print(f"Error getting OCF from {field}: {str(e)}")
                                    continue
                        
                        # Look for Capital Expenditure
                        if 'Capital Expenditure' in cash_flow.index:
                            try:
                                value = cash_flow.loc['Capital Expenditure', period]
                                if pd.notna(value):
                                    capex = float(value)
                                    print(f"Found CapEx: {capex:,.2f}")
                            except Exception as e:
                                print(f"Error getting CapEx: {str(e)}")
                        
                        if capex is None:
                            for field in cash_flow.index:
                                if any(term in field.lower() for term in ['capex', 'capital expenditure', 'fixed assets']):
                                    try:
                                        value = cash_flow.loc[field, period]
                                        if pd.notna(value):
                                            capex = float(value)
                                            print(f"Found CapEx in field '{field}': {capex:,.2f}")
                                            break
                                    except Exception as e:
                                        print(f"Error getting CapEx from {field}: {str(e)}")
                                        continue
                        
                        if capex is None:
                            print(f"Could not find CapEx for period {period}, using 0")
                            capex = 0
                        
                        if ocf is not None:
                            fcf = ocf + capex  # CapEx is typically negative
                            print(f"Calculated FCF: {fcf:,.2f}")
                            fcf_history.append(fcf)
                        
                    except Exception as e:
                        print(f"Could not calculate FCF for period {period}: {str(e)}")
                        print(f"Traceback: {traceback.format_exc()}")
                        continue

            if not fcf_history:
                raise ValueError("Could not calculate historical FCF. Available fields: " + 
                               ", ".join(cash_flow.index))

            # Calculate growth rate
            growth_rate = self.calculate_cagr(fcf_history, len(fcf_history))
            print(f"Calculated growth rate: {growth_rate:.2f}%")
            
            # Calculate quality metrics
            quality_metrics = self.calculate_quality_metrics(stock)
            print("Calculated quality metrics")
            
            # Calculate WACC
            wacc = self.calculate_wacc(stock)
            print(f"Calculated WACC: {wacc:.2f}%")
            
            # Get dynamic multiple
            multiple = self.get_dynamic_multiple(growth_rate, quality_metrics, wacc)
            print(f"Suggested multiple: {multiple:.1f}x")

            # Current FCF
            latest_fcf = fcf_history[0]
            
            # Prepare final data
            data = {
                'cash_flow': {
                    'free_cashflow': {
                        'latest': latest_fcf,
                        'history': fcf_history,
                        'growth_rate': growth_rate
                    },
                    'quality': quality_metrics
                },
                'market_data': {
                    'shares_outstanding': shares_outstanding,
                    'current_price': current_price
                },
                'valuation': {
                    'wacc': wacc,
                    'suggested_multiple': multiple
                }
            }
            
            return data
            
        except Exception as e:
            print(f"Error in _get_data_sync for {ticker}: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise

    async def _get_stock_data(self, ticker: str) -> Dict:
        """Asynchronously fetch stock data"""
        try:
            print(f"Starting data fetch for {ticker}")
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(self._executor, self._get_data_sync, ticker)
        except Exception as e:
            print(f"Error in _get_stock_data for {ticker}: {str(e)}")
            raise

    async def get_financials(self, ticker: str) -> Dict:
        """
        Get financial data for a stock
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict containing processed financial data
        """
        try:
            data = await self._get_stock_data(ticker)
            return data
        except Exception as e:
            print(f"Error in get_financials for {ticker}: {str(e)}")
            raise Exception(f"Failed to fetch Yahoo Finance data: {str(e)}")
