from flask_login import current_user
from Thalia.extensions import db
from Thalia.models.portfolio import Portfolio
import pandas as pd

from analyse_data.analyse_data import Strategy, Asset


def store_portfolio(start_date, end_date, starting_balance, name, table):
    strat = Strategy(start_date, end_date, starting_balance, [], [], None, [])

    strat.assets = [Asset(tkr, allocation, pd.DataFrame()) for tkr, allocation in table]

    if Portfolio.query.filter_by(name=name, owner=current_user.id).first() is not None:
        return False

    porto = Portfolio()
    porto.set_strategy(strat)
    porto.shared = False
    porto.name = name
    porto.owner = current_user.id

    db.session.add(porto)
    db.session.commit()

    return True


def get_own_portfolio(portfolio_id):
    portfolio, strategy = retrieve_portfolio(portfolio_id)
    if portfolio.owner != current_user.id:
        raise ValueError

    return portfolio, strategy


def retrieve_portfolio(portfolio_id):
    porto = Portfolio.query.get(portfolio_id)
    if porto:
        strat = porto.get_strategy()
    else:
        raise ValueError
    return porto, strat


def get_portfolios_list():
    portos = (
        Portfolio.query.filter_by(owner=current_user.id)
        .with_entities(Portfolio.id, Portfolio.name)
        .all()
    )
    return portos


def load_public_portfolio(uuid):
    try:
        porto = Portfolio.query.filter_by(uuid=uuid).one_or_none()
    except Exception as e:
        print(e)
        raise ValueError

    if porto and porto.shared:
        strat = porto.get_strategy()
        return porto, strat
    else:
        raise ValueError
