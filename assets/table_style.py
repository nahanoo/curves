style_table={'overflowX': 'auto'},
style_header={
    'backgroundColor': '#415a77',
    'fontWeight': 'bold',
    'color': '#f8f9fa',
    'textAlign': 'center',
    'border': '1px solid black'
},
style_cell={
    'backgroundColor': '#ecf0f1',
    'color': '#2c3e50',
    'textAlign': 'center',
    'border': '1px solid lightgrey',
    'fontFamily': 'Arial, sans-serif',
    'fontSize': '14px',
},
style_data_conditional=[
    {
        'if': {'row_index': 'odd'},
        'backgroundColor': '#f5f5f5',
    },
    {
        'if': {'row_index': 'even'},
        'backgroundColor': '#ffffff',
    },
    {
        'if': {
            'column_id': 'Temperature',
            'filter_query': '{Temperature} > 37'
        },
        'backgroundColor': '#e74c3c',
        'color': 'white',
    },
],
style_as_list_view=True,
style_cell_conditional=[
    {'if': {'column_id': 'Comments'},
    'textAlign': 'left'},
],
css=[{
    'selector': 'table',
    'rule': 'border-collapse: collapse; width: 100%;'
}]
