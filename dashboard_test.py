from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

app = Dash(__name__)

data = pd.read_excel('data/mob_topics.xlsx', sheet_name="daily_dynamics")
n_days = data.ResearchDate.unique().size
first_date = np.sort(data.ResearchDate.unique())[0]
# делаем красивое написание
first_date_b = first_date.split('-')
first_date_b.reverse()
first_date_b = '.'.join(first_date_b)

last_date = np.sort(data.ResearchDate.unique())[-1]
# делаем красивое написание
last_date_b = last_date.split('-')
last_date_b.reverse()
last_date_b = '.'.join(last_date_b)

app.layout = html.Div([
    html.H1('Тестовый дашборд', style={'color': "rgb(76,76,75"}),
    html.H2("Несколько графиков, чтобы протестировать возможности библиотеки dash",
            style={'color': "rgb(76,76,75"}),
    html.Div([
            html.Div([
                html.Label("Динамика тематик поисковых запросов"),
                dcc.Graph(id="graph")
            ], style={'width': '80%'}),
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        options=data.columns[2:],
                        value=data.columns[2],
                        id='yaxis-column'
                    )]),
                html.Br(),
                html.Br(),
                html.Div([
                    dcc.RangeSlider(
                        0, n_days-1, value=[0, n_days-1],
                        marks={0: {'label': first_date_b},
                               n_days-1: {'label': last_date_b}
                               },
                        tooltip={"placement": "top"},
                        id="date-slider"
                    )
                ]),
                html.Br(),
                html.Div([
                    # html.Label('Темы', style={'font-weight': "bold", 'font-size': "14px"}),
                    dcc.Checklist(
                        id="topic",
                        options=np.flip(data.TopicLevel1.unique()),
                        value=np.flip(data.TopicLevel1.unique()),
                        labelStyle={'display': 'block'})
                ])
            ], style={'font-size': "12px", 'width': "20%"})
        ], style={'display': "flex"})
], style={'font-family': "Arial", 'color': "rgb(119,119,118)"})


@app.callback(
    Output("graph", "figure"),
    Input("topic", "value"),
    Input("yaxis-column", "value"),
    Input("date-slider", "value"))
def display_area(topics, y_axis_stats, dates):
    start_date = np.sort(data.ResearchDate.unique())[dates[0]]
    end_date = np.sort(data.ResearchDate.unique())[dates[1]]
    if isinstance(topics, list) is True:
        figure = px.area(
            data.loc[data['TopicLevel1'].isin(topics) & (data['ResearchDate'] >= start_date) &
                     (data['ResearchDate'] <= end_date)], x="ResearchDate", y=y_axis_stats,
            color='TopicLevel1')
    else:
        figure = px.area(
            data.loc[data['TopicLevel1'] == topics & (data['ResearchDate'] >= start_date) &
                     (data['ResearchDate'] <= end_date)], x="ResearchDate", y=y_axis_stats,
            color='TopicLevel1')
    figure.update_yaxes(title=y_axis_stats)
    figure.update_xaxes(title="Дата")
    figure.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font_color="rgb(119,119,118)",
        legend_traceorder="reversed"
    )
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
