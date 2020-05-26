import unittest
import pandas as pd
import sys
import os
import random

from unittest import TestCase
from datetime import date, timedelta
from decimal import Decimal

sys.path.insert(0, ".")
from analyse_data import analyse_data as anda

# TODO: these 3 have a lot of common code that can be DRY'd up.
def read_asset(path):
    asset_vals = pd.read_csv(
        "file://" + os.path.dirname(os.path.realpath(__file__)) + path,
        index_col="Date",
        converters={"Close": Decimal},
    )
    asset_vals.index = pd.to_datetime(asset_vals.index, format="%d/%m/%Y")
    return asset_vals


def read_risk_free():
    risk_free_vals = pd.read_csv(
        "file://"
        + os.path.dirname(os.path.realpath(__file__))
        + "/test_data/risk_free_rate.csv",
        index_col="Date",
    )
    risk_free_vals.index = pd.to_datetime(risk_free_vals.index, format="%d/%m/%Y")
    return risk_free_vals


def read_dividends(path):
    dividends = pd.read_csv(
        "file://" + os.path.dirname(os.path.realpath(__file__)) + path,
        index_col="Date",
        converters={"Dividends": Decimal},
    )
    dividends.index = pd.to_datetime(dividends.index, format="%Y-%m-%d")
    return dividends


class TestTotalReturn(TestCase):
    def setUp(self):
        self.start = date(2000, 1, 1)
        self.end = date(2000, 1, 20)
        self.dates = pd.date_range(self.start, self.end, freq=timedelta(days=1))
        gold_prices = [
            [
                Decimal("0.00"),
                Decimal("0.00"),
                Decimal("0.00"),
                Decimal("6.00") + i * Decimal("0.03"),
            ]
            for (i, _) in enumerate(self.dates)
        ]
        silver_prices = [
            [
                Decimal("0.00"),
                Decimal("0.00"),
                Decimal("0.00"),
                Decimal("1.00") + i * i * Decimal("0.01"),
            ]
            for (i, _) in enumerate(self.dates)
        ]
        rock_prices = [
            [Decimal("1.00"), Decimal("1.00"), Decimal("1.00"), Decimal("1.00")]
            for _ in self.dates
        ]
        self.gold_data = pd.DataFrame(
            gold_prices, index=self.dates, columns=["Open", "Low", "High", "Close"]
        )
        self.silver_data = pd.DataFrame(
            silver_prices, index=self.dates, columns=["Open", "Low", "High", "Close"]
        )
        self.rock_data = pd.DataFrame(
            rock_prices, index=self.dates, columns=["Open", "Low", "High", "Close"]
        )

    def test_single_asset(self):
        starting_balance = Decimal("23.46")
        contribution_dates = set()
        contribution_amount = None
        rebalancing_dates = set()

        assets = [anda.Asset("Gold", Decimal("1.0"), self.gold_data)]

        strategy = anda.Strategy(
            self.start,
            self.end,
            starting_balance,
            assets,
            contribution_dates,
            contribution_amount,
            rebalancing_dates,
        )

        roi = anda.total_return(strategy)
        self.assertEqual(roi.at[self.start], Decimal("23.46"))
        self.assertEqual(roi.at[date(2000, 1, 12)], Decimal("24.75"))
        self.assertEqual(roi.at[self.end], Decimal("25.69"))

    def test_contribution(self):
        starting_balance = Decimal("1.00")
        contribution_dates = self.dates
        contribution_amount = Decimal("1.00")
        rebalancing_dates = set()

        assets = [anda.Asset("ST", Decimal("1.00"), self.rock_data)]

        strategy = anda.Strategy(
            self.start,
            self.end,
            starting_balance,
            assets,
            contribution_dates,
            contribution_amount,
            rebalancing_dates,
        )

        roi = anda.total_return(strategy)
        self.assertEqual(Decimal("2.00"), roi.at[self.start])
        for (day, next_day) in zip(self.dates, self.dates[1:]):
            self.assertEqual(roi[day] + Decimal("1.00"), roi[next_day])

    def test_rebalancing(self):
        # TODO
        starting_balance = Decimal("10000.00")
        contribution_dates = set()
        contribution_amount = Decimal("0.0")
        rebalancing_dates = self.dates

        assets = [
            anda.Asset("GOLD", Decimal("0.5"), self.gold_data),
            anda.Asset("SLV", Decimal("0.5"), self.silver_data),
        ]

        strategy = anda.Strategy(
            self.start,
            self.end,
            starting_balance,
            assets,
            contribution_dates,
            contribution_amount,
            rebalancing_dates,
        )

        roi = anda.total_return(strategy)
        roi  # gotta keep flake8 happy.

    def test_no_money(self):
        starting_balance = Decimal("0.00")
        contribution_dates = pd.date_range(
            self.start, self.end, freq=timedelta(days=4)
        )[1:]
        contribution_amount = Decimal("1000.00")
        rebalancing_dates = set()

        assets = [anda.Asset("ST", Decimal("1.0"), self.rock_data)]

        strategy = anda.Strategy(
            self.start,
            self.end,
            starting_balance,
            assets,
            contribution_dates,
            contribution_amount,
            rebalancing_dates,
        )

        roi = anda.total_return(strategy)
        roi  # Just the lack of exception *should* be a sign of success.

    def test_mult_assets(self):
        starting_balance = Decimal("100.00")
        contribution_dates = set()
        contribution_amount = Decimal("0.0")
        rebalancing_dates = set()

        assets = [
            anda.Asset("GOLD", Decimal("0.4"), self.gold_data),
            anda.Asset("SLV", Decimal("0.6"), self.silver_data),
        ]

        strategy = anda.Strategy(
            self.start,
            self.end,
            starting_balance,
            assets,
            contribution_dates,
            contribution_amount,
            rebalancing_dates,
        )

        roi = anda.total_return(strategy)
        self.assertEqual(roi[self.start], Decimal("100.00"))
        self.assertEqual(roi[self.start + timedelta(days=14)], Decimal("220.40"))
        self.assertEqual(roi[self.end], Decimal("320.40"))


class TestCagr(TestCase):
    def setUp(self):
        self.starting_balance = Decimal("10000")
        self.contribution_dates = set()
        self.contribution_amount = None
        self.rebalancing_dates = set()

        self.msft_vals = read_asset("/test_data/MSFT.csv")

    def test_cagr(self):
        start_date = date(1986, 12, 31)
        end_date = date(2019, 12, 31)

        msft_vals = self.msft_vals.reindex(pd.date_range(start_date, end_date)).ffill()

        assets = [anda.Asset("MSFT", Decimal("1.00"), msft_vals)]

        strategy = anda.Strategy(
            start_date,
            end_date,
            self.starting_balance,
            assets,
            self.contribution_dates,
            self.contribution_amount,
            self.rebalancing_dates,
        )

        self.assertAlmostEqual(anda.cagr(strategy), 23.0, delta=0.5)


class TestSharpeRatio(TestCase):
    def setUp(self):
        self.starting_balance = Decimal("10000")
        self.contribution_dates = set()
        self.contribution_amount = None
        self.rebalancing_dates = set()

        self.msft_vals = read_asset("/test_data/MSFT.csv")
        self.berkshire_vals = read_asset("/test_data/BRK-A.csv")
        self.risk_free_vals = read_risk_free()

    def test_sharpe_ratio_single_asset(self):
        start_date = date(1986, 12, 31)
        end_date = date(2019, 12, 31)

        msft_vals = self.msft_vals.reindex(pd.date_range(start_date, end_date)).ffill()
        risk_free_vals = (
            self.risk_free_vals.dropna()["Close"]
            .reindex(pd.date_range(start_date, end_date))
            .ffill()
        )

        assets = [anda.Asset("MSFT", Decimal("1.00"), msft_vals)]

        strategy = anda.Strategy(
            start_date,
            end_date,
            self.starting_balance,
            assets,
            self.contribution_dates,
            self.contribution_amount,
            self.rebalancing_dates,
        )

        self.assertAlmostEqual(
            anda.sharpe_ratio(strategy, risk_free_vals), Decimal(0.75), delta=0.05
        )

    def test_sharpe_ratio_multi_asset(self):
        start_date = date(1989, 12, 29)
        end_date = date(2000, 12, 29)

        msft_vals = self.msft_vals.reindex(pd.date_range(start_date, end_date)).ffill()
        berkshire_vals = self.berkshire_vals.reindex(
            pd.date_range(start_date, end_date)
        ).ffill()
        risk_free_vals = (
            self.risk_free_vals.dropna()["Close"]
            .reindex(pd.date_range(start_date, end_date))
            .ffill()
        )

        assets = [
            anda.Asset("MSFT", Decimal(0.6), msft_vals),
            anda.Asset("BRK-A", Decimal(0.4), berkshire_vals),
        ]

        strategy = anda.Strategy(
            start_date,
            end_date,
            self.starting_balance,
            assets,
            self.contribution_dates,
            self.contribution_amount,
            self.rebalancing_dates,
        )
        self.assertAlmostEqual(
            anda.sharpe_ratio(strategy, risk_free_vals), Decimal("0.89"), delta=0.2
        )


class TestMaxDrawdown(TestCase):
    def setUp(self):
        self.starting_balance = Decimal("10000")
        self.contribution_dates = set()
        self.contribution_amount = None
        self.rebalancing_dates = set()

        self.msft_vals = read_asset("/test_data/MSFT.csv")
        self.berkshire_vals = read_asset("/test_data/BRK-A.csv")
        self.risk_free_vals = read_risk_free()

    def test_max_drawdown_single_asset(self):
        start_date = date(1986, 12, 31)
        end_date = date(2019, 12, 31)

        msft_vals = self.msft_vals.reindex(pd.date_range(start_date, end_date)).ffill()

        assets = [anda.Asset("MSFT", Decimal("1.0"), msft_vals)]

        strategy = anda.Strategy(
            start_date,
            end_date,
            self.starting_balance,
            assets,
            self.contribution_dates,
            self.contribution_amount,
            self.rebalancing_dates,
        )
        self.assertAlmostEqual(anda.max_drawdown(strategy), Decimal("72.33"), delta=2.5)

    def test_max_drawdown_multi_asset(self):
        start_date = date(1989, 12, 29)
        end_date = date(2000, 12, 29)

        msft_vals = self.msft_vals.reindex(pd.date_range(start_date, end_date)).ffill()
        berkshire_vals = self.berkshire_vals.reindex(
            pd.date_range(start_date, end_date)
        ).ffill()

        assets = [
            anda.Asset("MSFT", Decimal(0.6), msft_vals),
            anda.Asset("BRK-A", Decimal(0.4), berkshire_vals),
        ]

        strategy = anda.Strategy(
            start_date,
            end_date,
            self.starting_balance,
            assets,
            self.contribution_dates,
            self.contribution_amount,
            self.rebalancing_dates,
        )
        self.assertAlmostEqual(anda.max_drawdown(strategy), Decimal("59.03"), delta=3)


class TestSortinoRatio(TestCase):
    def setUp(self):
        self.starting_balance = Decimal("10000")
        self.contribution_dates = set()
        self.contribution_amount = None
        self.rebalancing_dates = set()

        self.msft_vals = read_asset("/test_data/MSFT.csv")
        self.berkshire_vals = read_asset("/test_data/BRK-A.csv")
        self.risk_free_vals = read_risk_free()

    def test_sortino_ratio_single_asset(self):
        start_date = date(1986, 12, 31)
        end_date = date(2019, 12, 31)

        msft_vals = self.msft_vals.reindex(pd.date_range(start_date, end_date)).ffill()
        risk_free_vals = (
            self.risk_free_vals.dropna()["Close"]
            .reindex(pd.date_range(start_date, end_date))
            .ffill()
        )

        assets = [anda.Asset("MSFT", Decimal(1.0), msft_vals)]

        strategy = anda.Strategy(
            start_date,
            end_date,
            self.starting_balance,
            assets,
            self.contribution_dates,
            self.contribution_amount,
            self.rebalancing_dates,
        )
        self.assertAlmostEqual(
            anda.sortino_ratio(strategy, risk_free_vals), Decimal("1.34"), delta=0.1
        )

    def test_sortino_ratio_multi_asset(self):
        start_date = date(1989, 12, 29)
        end_date = date(2000, 12, 29)

        msft_vals = self.msft_vals.reindex(pd.date_range(start_date, end_date)).ffill()
        berkshire_vals = self.berkshire_vals.reindex(
            pd.date_range(start_date, end_date)
        ).ffill()
        risk_free_vals = (
            self.risk_free_vals.dropna()["Close"]
            .reindex(pd.date_range(start_date, end_date))
            .ffill()
        )

        assets = [
            anda.Asset("MSFT", Decimal(0.6), msft_vals),
            anda.Asset("BRK-A", Decimal(0.4), berkshire_vals),
        ]

        strategy = anda.Strategy(
            start_date,
            end_date,
            self.starting_balance,
            assets,
            self.contribution_dates,
            self.contribution_amount,
            self.rebalancing_dates,
        )
        self.assertAlmostEqual(
            anda.sortino_ratio(strategy, risk_free_vals), Decimal("1.56"), delta=0.2
        )


class TestBestWorstYear(TestCase):
    def setUp(self):
        self.starting_balance = Decimal("10000")
        self.contribution_dates = set()
        self.contribution_amount = None
        self.rebalancing_dates = set()

        self.msft_vals = read_asset("/test_data/MSFT.csv")
        self.berkshire_vals = read_asset("/test_data/BRK-A.csv")

    def test_simple(self):
        start_date = date(1989, 1, 4)
        end_date = date(2010, 1, 1)

        self.msft_vals = self.msft_vals.reindex(
            pd.date_range(start_date, end_date)
        ).ffill()

        assets = [
            anda.Asset("MSFT", Decimal("1.0"), self.msft_vals),
        ]

        strategy = anda.Strategy(
            start_date,
            end_date,
            self.starting_balance,
            assets,
            self.contribution_dates,
            self.contribution_amount,
            self.rebalancing_dates,
        )

        b = anda.best_year(strategy)
        w = anda.worst_year(strategy)

        self.assertAlmostEqual(b, Decimal("120"), delta=2)
        self.assertAlmostEqual(w, Decimal("-63"), delta=2)
        self.assertAlmostEqual(b, Decimal("122"), delta=Decimal("0.5"))
        self.assertAlmostEqual(w, Decimal("-63"), delta=Decimal("0.5"))

        b_year = anda.best_year_no(strategy)
        w_year = anda.worst_year_no(strategy)

        self.assertEqual(b_year, 1991)
        self.assertEqual(w_year, 2000)

    def test_short_time(self):
        start_date = date(1989, 1, 4)
        end_date = date(1989, 12, 31)

        self.msft_vals = self.msft_vals.reindex(
            pd.date_range(start_date, end_date)
        ).ffill()

        assets = [
            anda.Asset("MSFT", Decimal("1.0"), self.msft_vals),
        ]

        strategy = anda.Strategy(
            start_date,
            end_date,
            self.starting_balance,
            assets,
            self.contribution_dates,
            self.contribution_amount,
            self.rebalancing_dates,
        )

        self.assertRaises(anda.InsufficientTimeframe, lambda: anda.best_year(strategy))
        self.assertRaises(anda.InsufficientTimeframe, lambda: anda.worst_year(strategy))
        self.assertRaises(
            anda.InsufficientTimeframe, lambda: anda.best_year_no(strategy)
        )
        self.assertRaises(
            anda.InsufficientTimeframe, lambda: anda.worst_year_no(strategy)
        )


class TestDividends(TestCase):
    def setUp(self):
        self.starting_balance = Decimal("10000")
        self.contribution_dates = set()
        self.contribution_amount = None
        self.rebalancing_dates = set()

        self.msft_vals = read_asset("/test_data/MSFT.csv")
        self.msft_dividends = read_dividends("/test_data/MSFT_dividends.csv")
        self.aapl_vals = read_asset("/test_data/AAPL.csv")
        self.aapl_dividends = read_dividends("/test_data/AAPL_dividends.csv")

    def test_dividends_single_asset(self):
        start_date = date(1986, 12, 31)
        end_date = date(2019, 12, 31)

        msft_vals = self.msft_vals.reindex(pd.date_range(start_date, end_date)).ffill()
        msft_dividends = self.msft_dividends.reindex(
            pd.date_range(start_date, end_date)
        ).dropna()

        assets = [anda.Asset("MSFT", Decimal("1.0"), msft_vals, msft_dividends)]

        strategy = anda.Strategy(
            start_date,
            end_date,
            self.starting_balance,
            assets,
            self.contribution_dates,
            self.contribution_amount,
            self.rebalancing_dates,
        )
        self.assertAlmostEqual(
            anda.total_return(strategy)[end_date], Decimal("14599199.22"), delta=1
        )

    def test_dividends_multiple_assets(self):
        start_date = date(1986, 12, 31)
        end_date = date(2019, 12, 31)

        msft_vals = self.msft_vals.reindex(pd.date_range(start_date, end_date)).ffill()
        msft_dividends = self.msft_dividends.reindex(
            pd.date_range(start_date, end_date)
        ).dropna()
        aapl_vals = self.aapl_vals.reindex(pd.date_range(start_date, end_date)).ffill()
        aapl_dividends = self.aapl_dividends.reindex(
            pd.date_range(start_date, end_date)
        ).dropna()

        assets = [
            anda.Asset("MSFT", Decimal("0.5"), msft_vals, msft_dividends),
            anda.Asset("AAPL", Decimal("0.5"), aapl_vals, aapl_dividends),
        ]

        strategy = anda.Strategy(
            start_date,
            end_date,
            self.starting_balance,
            assets,
            self.contribution_dates,
            self.contribution_amount,
            self.rebalancing_dates,
        )
        self.assertAlmostEqual(
            anda.total_return(strategy)[end_date], Decimal("9856511.60"), delta=1
        )


class TestCurrencyConversion(TestCase):
    def gen_random_usd_vals(self, start_date, end_date):
        cur_date = start_date
        dates, usd_vals = [], []
        while cur_date < end_date:
            dates.append(cur_date)
            usd_vals.append(Decimal(random.random() * 1000000).quantize(anda.PENNY))
            cur_date += timedelta(days=random.randint(1, 1000))
        return pd.Series(usd_vals, dates)

    def setUp(self):
        self.start_date = date(1998, 1, 1)
        self.end_date = date(2020, 1, 1)
        self.forex_vals = read_asset("/test_data/USDJPY.csv")
        self.forex_vals = self.forex_vals.reindex(
            pd.date_range(self.start_date, self.end_date)
        ).ffill()
        self.usd_vals = self.gen_random_usd_vals(self.start_date, self.end_date)

    def test_currency_conversion_single_value(self):
        self.assertAlmostEqual(
            anda.convert_usd(
                self.forex_vals, pd.Series([Decimal("100.0")], [self.start_date]),
            ).at[self.start_date],
            Decimal(13047.9996).quantize(anda.PENNY),
            1,
        )

    def test_currency_conversion_series(self):
        self.assertListEqual(
            [
                self.forex_vals.at[idx, "Close"] * val
                for idx, val in self.usd_vals.iteritems()
            ],
            list(anda.convert_usd(self.forex_vals, self.usd_vals).values),
        )


class TestYearlyReturns(TestCase):
    def setUp(self):
        self.starting_balance = Decimal("10000")
        self.contribution_dates = set()
        self.contribution_amount = None
        self.rebalancing_dates = set()

        self.msft_vals = read_asset("/test_data/MSFT.csv")
        self.msft_dividends = read_dividends("/test_data/MSFT_dividends.csv")

    def test_msft(self):
        start_date = date(1986, 3, 13)
        end_date = date(2019, 1, 1)
        msft_vals = self.msft_vals.reindex(pd.date_range(start_date, end_date)).ffill()
        msft_dividends = self.msft_dividends.reindex(
            pd.date_range(start_date, end_date)
        ).dropna()

        assets = [anda.Asset("MSFT", Decimal("1.0"), msft_vals, msft_dividends)]

        strategy = anda.Strategy(
            start_date,
            end_date,
            self.starting_balance,
            assets,
            self.contribution_dates,
            self.contribution_amount,
            self.rebalancing_dates,
        )
        annual_returns = anda.relative_yearly_returns(strategy)
        expected = [
            #   (year, change)
            (1987, Decimal("125")),
            (1988, Decimal("-2")),
            (2000, Decimal("-63")),
            (2001, Decimal("53")),
            (2002, Decimal("-22")),
            (2003, Decimal("7")),
            (2017, Decimal("41")),
            (2018, Decimal("21")),
        ]
        for year, change in expected:
            self.assertAlmostEqual(
                annual_returns.at[date(year, 1, 1)], change, delta=Decimal("0.5")
            )


class TestDrawdowns(TestCase):
    def test_degenerate_case(self):
        returns = pd.Series([], dtype=object)
        drawdowns = anda.drawdowns(returns)
        self.assertTrue(drawdowns.equals(pd.Series([], dtype=float)))
        summary = anda.drawdown_summary(drawdowns)
        self.assertTrue(
            summary.equals(
                pd.DataFrame(
                    [],
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
            )
        )

    def test_months_of_year(self):
        returns = pd.Series(
            map(
                Decimal,
                [  # Drawdowns from MSFT in 1990 - modified for testing more general stuff.
                    38342,
                    40933,
                    45907,
                    48083,
                    60518,
                    63005,
                    55130,
                    50984,
                    52228,
                    52850,
                    63896,  # modified value
                    62383,
                ],
            ),
            index=pd.date_range(date(1990, 1, 1), date(1990, 12, 1), freq="MS"),
        )
        drawdowns = anda.drawdowns(returns)
        expected_drawdowns = [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            -12.5,
            -19.1,
            -17.1,
            -16.1,
            0.0,
            -2.4,
        ]
        for real, expected in zip(drawdowns.array, expected_drawdowns):
            self.assertAlmostEqual(real, expected, delta=0.05)

    def test_summary_table(self):
        drawdowns = pd.Series(
            # Made up data.
            [
                0.0,
                -4.86,
                -3.30,
                0.0,
                0.0,
                0.0,
                0.0,
                -17.4,
                -20.0,
                -35.0,
                -62.0,
                -37.6,
                -7.4,
                0.0,
                0.0,
            ],
            index=pd.date_range(date(2005, 1, 1), date(2006, 3, 1), freq="MS"),
        )
        summary = anda.drawdown_summary(drawdowns)
        expected_summary = pd.DataFrame(
            [
                [
                    -62.0,
                    pd.to_datetime(date(2005, 8, 1)),
                    pd.to_datetime(date(2005, 11, 1)),
                    pd.to_datetime(date(2006, 2, 1)),
                    timedelta(days=31 + 30 + 31),
                    timedelta(days=30 + 31 + 31),
                    timedelta(days=31 + 30 + 31 + 30 + 31 + 31),
                ],
                [
                    -4.86,
                    pd.to_datetime(date(2005, 2, 1)),
                    pd.to_datetime(date(2005, 2, 1)),
                    pd.to_datetime(date(2005, 4, 1)),
                    timedelta(days=0),
                    timedelta(days=28 + 31),
                    timedelta(28 + 31),
                ],
            ],
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

        self.assertTrue(summary.equals(expected_summary))


if __name__ == "__main__":
    unittest.main()
