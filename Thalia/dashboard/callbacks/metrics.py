from analyse_data import analyse_data as anda


def get_table_data(strat, total_return, portfolio_name):
    """
    Return a list of key metrics and their values
    """
    returns = total_return
    table = [
        {"Metric": "Initial Balance", portfolio_name: returns[strat.dates[0]]},
        {"Metric": "Final Balance", portfolio_name: returns[strat.dates[-1]]},
    ]
    try:
        # We can't use append here because we want the table
        # unaltered if anything goes wrong.
        table = table + [
            {"Metric": "Best Year", portfolio_name: round(anda.best_year(strat), 2)},
            {"Metric": "Worst Year", portfolio_name: round(anda.worst_year(strat), 2)},
            {
                "Metric": "Max Drawdown",
                portfolio_name: round(anda.max_drawdown(strat), 2),
            },
        ]
        table = table + [{"Metric": "CAGR", portfolio_name: round(anda.cagr(strat), 2)}]
        table = table + [
            {
                "Metric": "Sortino Ratio",
                portfolio_name: round(anda.sortino_ratio(strat, None), 2),
            },
            {
                "Metric": "Sharpe Ratio",
                portfolio_name: round(anda.sharpe_ratio(strat, None), 2),
            },
        ]
    except anda.InsufficientTimeframe:
        print("Not enough enough data for best/worst year")
    except Exception:
        print("Could not calculate Sharpe/Sortino ratios")

    return table


def combine_cols(table1, table2):
    """
    Combines two lists of dictionaries,
    takes care if empty
    """
    to_return = []
    length = max(len(table1), len(table2))
    if not table1:
        table1 = [{} for _ in range(length)]
    if not table2:
        table2 = [{} for _ in range(length)]
    for i in range(length):
        temp = {**table1[i], **table2[i]}
        to_return.append(temp)
    return to_return
