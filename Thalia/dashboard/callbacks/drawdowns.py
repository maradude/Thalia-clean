import humanize

from analyse_data import analyse_data as anda


def get_drawdowns_tables(portoflio_name, drawdowns):
    drawdowns_df = anda.drawdown_summary(drawdowns)
    drawdowns_formated = format_summary(drawdowns_df)
    no_records = 10 if 10 < len(drawdowns_df) else len(drawdowns_df)
    table_data = drawdowns_formated.to_dict("records")[:no_records]

    table_name = f"{portoflio_name} Top Drawdowns"
    table_visibility = {"display": "block"}

    return [table_name, table_data, table_visibility]


def format_summary(drawdowns):
    drawdowns = drawdowns.head(10)
    return drawdowns.apply(format_row, axis=1, result_type="broadcast")


def format_row(row):
    return [
        round(row["Drawdown"], 2),
        row["Start"].strftime("%d/%m/%Y"),
        row["End"].strftime("%d/%m/%Y"),
        row["Recovery"].strftime("%d/%m/%Y"),
        humanize.naturaldelta(row["Length"]),
        humanize.naturaldelta(row["Recovery Time"]),
        humanize.naturaldelta(row["Underwater Period"]),
    ]
