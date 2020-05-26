import numpy as np
import pandas as pd
import math
from decimal import Decimal, InvalidOperation
from datetime import date
from dataclasses import dataclass
from typing import List


PENNY = Decimal("0.01")


@dataclass
class Asset:
    ticker: str

    weight: Decimal

    # pd.DataFrame("Open", "Low", "High", "Close") indexed and sorted by date.
    values: pd.DataFrame

    # pd.DataFrame("Dividend") indexed by date
    dividends: pd.DataFrame = pd.DataFrame()


APPROX_TDAY_PER_YEAR = 252
APPROX_DAY_PER_YEAR = 365.25


class InsufficientTimeframe(Exception):
    pass


class Strategy:
    def __init__(
        self,
        start_date: date,
        end_date: date,
        starting_balance: Decimal,
        assets: List[Asset],
        contribution_dates,  # implements __contains__ for date
        contribution_amount: Decimal,
        rebalancing_dates,  # implements __contains__ for date
    ):
        self.dates = pd.date_range(start_date, end_date, freq="D")
        self.starting_balance = starting_balance
        self.assets = assets
        self.contribution_dates = contribution_dates
        self.contribution_amount = contribution_amount
        self.rebalancing_dates = rebalancing_dates

        # Caches for expensive repeated calculations.
        self.returns = None
        self.annual_returns = None


# INTERNAL
def _allocate_investments(
    balance: Decimal, asset_weights: List[Decimal], asset_vals: List[Decimal]
) -> List[Decimal]:
    return [
        balance * weight / price for (weight, price) in zip(asset_weights, asset_vals)
    ]


# INTERNAL
def _measure_weights(asset_vals: List[Decimal]) -> List[Decimal]:
    # asset_vals is the current amount of money invested in each asset.
    total = sum(asset_vals)
    return [val / total for val in asset_vals]


# INTERNAL
def _calc_balance(invesments: List[Decimal], asset_vals: List[Decimal]) -> Decimal:
    return Decimal(
        sum(holdings * value for holdings, value in zip(invesments, asset_vals))
    ).quantize(PENNY)


# INTERNAL
def _collect_dividend(dividend: Decimal, holdings: Decimal, price: Decimal) -> Decimal:
    return holdings + (holdings * dividend) / price


# TODO: make numpy and pandas do the work.
def total_return(strat) -> pd.Series:
    if strat.returns is not None:
        return strat.returns
    # Returns the value of the portfolio at each day in the time frame.

    ret = pd.Series(Decimal("0"), index=strat.dates)
    ideal_weights = np.array([asset.weight for asset in strat.assets])
    asset_values = [asset.values["Close"] for asset in strat.assets]
    balance = strat.starting_balance

    for day in strat.dates:
        asset_vals_today = [values.at[day] for values in asset_values]
        if day == strat.dates[0] or day in strat.rebalancing_dates:
            investments = _allocate_investments(
                balance, ideal_weights, asset_vals_today
            )
        for idx, asset in enumerate(strat.assets):
            if day in asset.dividends.index:
                investments[idx] = _collect_dividend(
                    asset.dividends["Dividends"][day],
                    investments[idx],
                    asset_vals_today[idx],
                )
        if day in strat.contribution_dates:
            try:
                current_weights = _measure_weights(
                    [balance * holdings for holdings in investments]
                )
            except InvalidOperation:  # no money
                current_weights = ideal_weights
            balance += strat.contribution_amount
            investments = _allocate_investments(
                balance, current_weights, asset_vals_today,
            )
        balance = _calc_balance(investments, asset_vals_today)
        ret.at[day] = balance

    strat.returns = ret
    return ret


def final_balance(strat: Strategy) -> Decimal:
    returns = total_return(strat)
    return returns.at[strat.dates[len(strat.dates) - 1]]


# Compound Annual Growth Rate
def cagr(strat: Strategy) -> float:
    begin = strat.starting_balance
    end = final_balance(strat)

    growth = float(end / begin)
    time = strat.dates[-1] - strat.dates[0]
    years = time.total_seconds() / (APPROX_DAY_PER_YEAR * 24 * 60 * 60)
    growth_factor = math.pow(growth, 1.0 / years)

    return (growth_factor - 1.0) * 100


def _risk_adjusted_returns(
    strat: Strategy, risk_free_rate: pd.DataFrame
) -> List[Decimal]:
    returns = total_return(strat)
    """ flake8 doesn't like unused variables
    risk_free_rate_daily = risk_free_rate.map(
        lambda x: Decimal(pow(math.e, math.log(x) / APPROX_DAY_PER_YEAR))
    )
    """
    # TODO Risk free rate of return is assumed to be 0 for now
    return [
        (returns.iat[i] / returns.iat[i - 1]) - Decimal(1.000)
        for i in range(1, returns.size)
    ]


def sortino_ratio(strat: Strategy, risk_free_rate: pd.DataFrame) -> float:
    risk_adjusted_returns = _risk_adjusted_returns(strat, risk_free_rate)
    below_target_std = np.std(list(map(lambda x: min(0, x), risk_adjusted_returns)))

    return (
        np.mean(risk_adjusted_returns)
        / Decimal(below_target_std)
        * Decimal(math.sqrt(APPROX_DAY_PER_YEAR))
    )


def sharpe_ratio(strat: Strategy, risk_free_rate: pd.DataFrame) -> float:
    risk_adjusted_returns = _risk_adjusted_returns(strat, risk_free_rate)
    return (
        np.mean(risk_adjusted_returns)
        / np.std(risk_adjusted_returns)
        * Decimal(math.sqrt(APPROX_DAY_PER_YEAR))
    )


def max_drawdown(strat: Strategy) -> Decimal:
    returns = total_return(strat)
    max_seen, max_diff = Decimal(0.0), Decimal(1.0)
    for i in range(returns.size):
        max_seen = max(max_seen, returns.iat[i])
        max_diff = min(max_diff, returns.iat[i] / max_seen)
    return (Decimal(1.0) - max_diff) * Decimal(100.0)


# INTERNAL
def _jan_firsts(dates: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """
    Takes a DatetimeIndex and the largest sub-range of dates that only
    include the beginnings of each year.
    """
    # TODO: find a way to do this efficiently.
    jan_firsts_list = [d for d in dates if d.month == d.day == 1]
    if len(jan_firsts_list) == 0:
        return pd.DatetimeIndex([])
    begin = jan_firsts_list[0]
    end = jan_firsts_list[-1]
    return pd.date_range(begin, end, freq="AS")  # Annual start


def relative_yearly_returns(strat: Strategy) -> pd.Series:
    """
    Returns a yearly-indexed series of the percentage rise/fall in the
    portfolio's value.
    The value associated with 2018-01-01 is the difference between the
    portfolio's value at 2019-01-01 and 2018-01-01, relative to the value
    of the portfolio at 2018-01-01.
    """
    if strat.annual_returns is not None:
        return strat.annual_returns

    returns = total_return(strat)
    year_begins = _jan_firsts(returns.index)
    rel_diffs = [
        (returns.at[next_year] / returns.at[this_year]) - Decimal("1")
        for this_year, next_year in zip(year_begins, year_begins[1:])
    ]

    ret = pd.Series(
        [x * Decimal("100") for x in rel_diffs], index=year_begins[:-1], dtype=object
    )
    strat.annual_returns = ret
    return ret


def best_year(strat: Strategy) -> Decimal:
    """
    Returns the highest percentage increase in a portfolio's value between
    one Jan 1. and the next Jan 1.
    """
    rel_diff = relative_yearly_returns(strat)
    if len(rel_diff) > 0:
        return rel_diff.max()
    else:
        raise InsufficientTimeframe


def worst_year(strat: Strategy) -> Decimal:
    """
    Same convention as best_year, but takes the *lowest* percentage
    increase (probably negative).
    """
    rel_diff = relative_yearly_returns(strat)
    if len(rel_diff) > 0:
        return rel_diff.min()
    else:
        raise InsufficientTimeframe


def best_year_no(strat: Strategy) -> int:
    """
    Returns the year number (Gregorian calandar) of the best year.
    """
    rel_diff = relative_yearly_returns(strat)
    if len(rel_diff) > 0:
        # Would use .idxmax(), but pandas hates Decimal.
        return max(rel_diff.index, key=lambda day: rel_diff.at[day]).year
    else:
        raise InsufficientTimeframe


def convert_usd(exchange_rate: pd.DataFrame, usd_vals: pd.Series) -> pd.Series:
    """
    usd_vals -  Series indexed by non-continuous subset of dates from currency_pair index; decimal values
    """
    return pd.Series(
        [val * exchange_rate.at[idx, "Close"] for idx, val in usd_vals.iteritems()],
        usd_vals.index,
    )


def worst_year_no(strat: Strategy) -> int:
    """
    Returns the year number (Gregorian calandar) of the worst year.
    """
    rel_diff = relative_yearly_returns(strat)
    if len(rel_diff) > 0:
        return min(rel_diff.index, key=lambda day: rel_diff.at[day]).year
    else:
        raise InsufficientTimeframe


def drawdowns(balance: pd.Series) -> pd.Series:
    """
    balance is a timeseries - like something obtained from total_return.
    But it need not be daily - it can have any index - eg monthly.

    Returns a timeseries of drawdowns, represented as a nonpositive
    floating-pointer percentage. It has the same index as balance.
    """
    ret = pd.Series(0.0, index=balance.index)
    last_peak = Decimal("-Infinity")
    for day in balance.index:
        balance_today = balance.at[day]
        last_peak = max(balance_today, last_peak)
        diff = balance_today - last_peak
        ret.at[day] = 100.0 * float(diff / last_peak)
    return ret


# INTERNAL
def _drawdown_periods(drawdown: pd.Series) -> List[pd.DataFrame]:
    """
    Splits a drawdown timeseries into separate, nonoverlapping periods of
    drawdown.
    """

    # This is a very FSM-like approach.
    ret = []
    in_drawdown = False
    for day in drawdown.index:
        if not in_drawdown:
            if drawdown.at[day] < 0.0:
                in_drawdown = True
                drawdown_start = day
        else:
            if drawdown.at[day] == 0.0:
                in_drawdown = False
                drawdown_end = day
                ret.append(drawdown[drawdown_start:drawdown_end])
    # We ignore any unrecovered drawdown period.
    return ret


def drawdown_summary(drawdown: pd.Series) -> pd.DataFrame:
    """
    Input: the return value of drawdowns().

    Output: a dataframe with columns:
        Drawdown: float (negative percentage)
        Start: datetime
        End: datetime
        Recovery: datetime
        Length: timedelta
        Recovery Time: timedelta
        Underwater Period: timedelta
    sorted ascending by Drawdown (most severe first), sorting by Start
    to break ties.
    """
    periods = _drawdown_periods(drawdown)

    def make_row(period):
        start = period.index[0]
        end = period.idxmin()
        recovery = period.index[-1]
        length = end - start
        recovery_time = recovery - end
        underwater_period = recovery - start
        drawdown = period.at[end]
        return [
            drawdown,
            start,
            end,
            recovery,
            length,
            recovery_time,
            underwater_period,
        ]

    rows = [make_row(p) for p in periods]
    rows.sort(key=lambda p: p[0])
    df = pd.DataFrame(
        rows,
        columns=[
            "Drawdown",
            "Start",
            "End",
            "Recovery",
            "Length",
            "Recovery Time",
            "Underwater Period",
        ],
    )
    return df
