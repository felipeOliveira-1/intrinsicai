from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum

class TerminalMethod(str, Enum):
    GORDON = 'gordon'
    MULTIPLE = 'multiple'

class ValuationRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    growth_rate: float = Field(..., ge=0.0, le=1.0)
    discount_rate: float = Field(..., ge=0.0, le=1.0)
    terminal_method: TerminalMethod = Field(default=TerminalMethod.GORDON)
    margin_of_safety: float = Field(..., ge=0.0, le=1.0)
    preferred_source: str = Field(default='yahoo')

    @validator('ticker')
    def validate_ticker(cls, v):
        if not v.isalnum():
            raise ValueError('Ticker must contain only letters and numbers')
        return v.upper()

    @validator('preferred_source')
    def validate_source(cls, v):
        valid_sources = ['yahoo', 'alpha_vantage', 'both']
        if v.lower() not in valid_sources:
            raise ValueError(f'Source must be one of {valid_sources}')
        return v.lower()

class HistoricalDataRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    period: str = Field(default="5y")
    interval: str = Field(default="1d")

    @validator('period')
    def validate_period(cls, v):
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        if v not in valid_periods:
            raise ValueError(f'Period must be one of {valid_periods}')
        return v

    @validator('interval')
    def validate_interval(cls, v):
        valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
        if v not in valid_intervals:
            raise ValueError(f'Interval must be one of {valid_intervals}')
        return v
