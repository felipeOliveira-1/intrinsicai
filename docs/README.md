# Stock Intrinsic Value Analysis Tool

A command-line tool that analyzes stocks based on their Free Cash Flow (FCF) and provides AI-powered expert analysis to determine if they are good investment opportunities.

## Features

- Fetch real-time stock data using Yahoo Finance API
- Calculate intrinsic value using FCF analysis
- Apply margin of safety to determine buy price
- AI-powered expert analysis using GPT-4
- Beautiful terminal output with color-coded recommendations
- Support for analyzing multiple stocks at once
- Customizable FCF multiple and margin of safety
- Robust error handling and detailed logging
- Smart number formatting (B for billions, M for millions)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/instricvalue.git
cd instricvalue
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key in the .env file:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Analyze a Single Stock

```bash
cd backend
python main.py analyze AAPL
```

This will analyze Apple Inc. stock and show:
- Current price and market cap
- Operating Cash Flow and Capital Expenditures
- Free Cash Flow analysis
- Fair value calculation
- Buy/Hold recommendation with color-coded indicators
- AI expert analysis and recommendations
- Detailed financial insights

### Analyze Multiple Stocks

```bash
python main.py analyze-multiple AAPL MSFT GOOGL
```

### Customize Analysis

You can customize the FCF multiple and margin of safety:

```bash
python main.py analyze AAPL --multiple 12 --margin 0.25
```

- `--multiple`: FCF multiple for valuation (default: 10)
- `--margin`: Margin of safety as decimal (default: 0.3 for 30%)

## Detailed Usage Guide

### Initial Setup

1. Make sure you're in the correct directory:
```bash
cd backend  # If not already in the backend directory
```

2. Verify Python installation:
```bash
python --version  # Should be 3.8 or higher
```

3. Set up your OpenAI API key:
- Create an account at https://platform.openai.com/
- Get your API key from the dashboard
- Add it to your .env file

### Basic Usage

#### 1. Analyzing a Single Stock

For US stocks, use the ticker symbol directly:
```bash
python main.py analyze AAPL  # Apple Inc.
python main.py analyze MSFT  # Microsoft
```

For Brazilian stocks, add the .SA suffix:
```bash
python main.py analyze PETR4.SA  # Petrobras
python main.py analyze VALE3.SA  # Vale
```

#### 2. Analyzing Multiple Stocks

You can analyze several stocks at once:
```bash
python main.py analyze-multiple AAPL MSFT GOOGL
```

For a mix of US and Brazilian stocks:
```bash
python main.py analyze-multiple AAPL PETR4.SA VALE3.SA
```

## Features in Detail

### 1. Quantitative Analysis
- Free Cash Flow (FCF) calculation
- Growth rate estimation
- Quality metrics (FCF/Net Income, Debt/FCF)
- Working capital analysis
- Fair value calculation using FCF multiple
- Margin of safety application

### 2. AI Expert Analysis
- Market context and insights
- Risk assessment
- Growth prospects evaluation
- Competitive analysis
- Investment recommendation
- Industry-specific considerations

### 3. Output Format
- Clear, color-coded tables
- Visual indicators for buy/sell recommendations
- Detailed AI analysis panel
- Historical data comparison
- Quality metrics assessment

## Dependencies

- Python 3.8+
- yfinance: Stock data fetching
- pandas: Data manipulation
- rich: Terminal formatting
- openai: AI analysis
- python-dotenv: Environment variables
- typer: CLI interface

## Error Handling

The tool includes robust error handling for:
1. Invalid stock tickers
2. API connection issues
3. Missing financial data
4. AI service interruptions
5. Invalid user inputs

## Output Example

```
Stock Analysis for AAPL
╭────────────────────┬─────────────╮
│ Metric            │ Value       │
├────────────────────┼─────────────┤
│ Current Price     │ $182.31     │
│ Market Cap        │ $2.84T      │
│ FCF per Share     │ $6.42       │
│ Fair Value        │ $64.20      │
╰────────────────────┴─────────────╯

AI Expert Analysis:
╭──────────────────────────────────╮
│ Comprehensive market analysis...  │
│ Investment recommendation...      │
╰──────────────────────────────────╯
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## How It Works

1. Fetches latest financial data from Yahoo Finance
2. Extracts Operating Cash Flow and Capital Expenditures
3. Calculates Free Cash Flow (OCF - CapEx)
4. Determines FCF per share using current shares outstanding
5. Applies a multiple to determine fair value
6. Adds margin of safety to determine buy price
7. Compares current price to buy price
8. Provides a clear buy/hold recommendation with detailed insights
9. Uses OpenAI API for AI expert analysis

## License

This project is licensed under the MIT License - see the LICENSE file for details.
