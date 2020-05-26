from analyse_data import analyse_data as anda

from . import user_csv, util


def get_strategy(
    tickers,
    proportions,
    handles,
    start_date,
    end_date,
    input_money,
    contribution_amount,
    contribution_dates,
    rebalancing_dates,
):
    """
    Initializes and returns strategy object
    """
    weights = [p for p in proportions if p is not None]
    normalise(weights)

    # Separate user-supplied data from Thalia-known data.
    user_assets = []
    thalia_tickers = []
    thalia_weights = []
    for ticker, weight, handle in zip(tickers, weights, handles):
        if handle is None:
            thalia_tickers.append(ticker)
            thalia_weights.append(weight)
        else:
            user_assets.append((ticker, weight, handle))

    thalia_data = get_assets(thalia_tickers, thalia_weights, start_date, end_date)

    if thalia_data is None:
        # raise error
        return None

    user_supplied_data = [
        anda.Asset(ticker, weight, user_csv.retrieve(handle))
        for ticker, weight, handle in user_assets
    ]
    all_asset_data = user_supplied_data + thalia_data

    real_start_date = max(asset.values.index[0] for asset in all_asset_data)
    real_end_date = min(asset.values.index[-1] for asset in all_asset_data)

    if real_end_date < real_start_date:
        # raise error
        return None

    strategy = anda.Strategy(
        real_start_date,
        real_end_date,
        input_money,
        all_asset_data,
        contribution_dates,
        contribution_amount,
        rebalancing_dates,
    )
    return strategy


def normalise(arr):
    """
    Changes arr in place, keeping the relative weights the same,
    but scaling it such that it totals to 1.
    """
    total = sum(arr)
    for i in range(len(arr)):
        arr[i] /= total


def get_assets(tickers, proportions, start_date, end_date):
    """
    Gets data for each ticker and puts it in an anda.Asset.
    Returns a list of all assets.
    """
    assert len(tickers) == len(proportions)
    data = util.get_data(tickers, start_date, end_date)
    data = data.rename(
        columns={"AOpen": "Open", "AClose": "Close", "ALow": "Low", "AHigh": "High"}
    )

    if data.empty:
        # raise error
        return None

    assets = []
    for tick, prop in zip(tickers, proportions):
        asset_data = data[(data.AssetTicker == tick)]
        only_market_data = asset_data[["ADate", "Open", "Close", "Low", "High"]]
        only_market_data.index = only_market_data["ADate"]
        assets.append(anda.Asset(tick, prop, only_market_data))
    return assets
