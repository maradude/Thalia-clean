import dash_table


def table(data, id):
    columns = [
        {"name": "Metric", "id": "Metric"},
        {"name": "value", "id": "value"},
    ]
    return dash_table.DataTable(
        id=id,
        columns=columns,
        data=data,
        style_cell={"textAlign": "left"},
        style_as_list_view=True,
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "rgb(248, 248, 248)"}
        ],
        style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
        style_table={"overflowX": "scroll"},
    )
