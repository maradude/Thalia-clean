from Thalia.extensions import db
from Thalia.models import portfolio, user
import pytest
from analyse_data.analyse_data import Strategy, Asset
from datetime import date
from decimal import Decimal
import pandas as pd
import numpy
import sqlalchemy


def test_storing_retrieving_portfolio(client):
    # Dummy user setup
    usr = user.User()
    usr.set_password("password123")
    usr.id = 1337
    db.session.add(usr)
    db.session.commit()

    # Dummy strategy
    strat = Strategy(
        date(2011, 2, 1),
        date(2019, 12, 1),
        10000,
        [],
        [date(2019, 6, 1)],
        1000,
        [date(2019, 9, 1)],
    )
    strat.assets = [
        Asset("MSFT", Decimal("0.245"), pd.DataFrame()),
        Asset("AAPL", Decimal("0.755"), pd.DataFrame()),
    ]

    # Write test portfolio to DB
    porto = portfolio.Portfolio()
    porto.set_strategy(strat)
    porto.shared = False
    porto.name = "Dream portfolio"
    porto.owner = 1337

    db.session.add(porto)
    db.session.commit()

    # Retrieve portfolio and associated strategy
    stored_portfolio = portfolio.Portfolio.query.first()
    stored_portfolio.gen_uuid()
    retrieved_strat = stored_portfolio.get_strategy()

    assert retrieved_strat.dates[0] == strat.dates[0], "Matching start date"
    assert retrieved_strat.dates[-1] == strat.dates[-1], "Matching end date"
    assert (
        retrieved_strat.starting_balance == strat.starting_balance
    ), "Matching starting_balance"
    for i in range(len(retrieved_strat.assets)):
        assert (
            strat.assets[i].weight*100 - 0.01
            <= retrieved_strat.assets[i].weight
            <= strat.assets[i].weight*100 + 0.01
        )
    assert stored_portfolio.uuid is not None
