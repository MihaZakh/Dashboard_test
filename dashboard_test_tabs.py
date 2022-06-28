from dash import Dash, html, dcc, Input, Output
import dash_auth
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

with open('login_password.txt') as auth_info:
    logins = auth_info.readlines()

VALID_USERNAME_PASSWORD_PAIRS = dict()
for login_pass in logins:
    VALID_USERNAME_PASSWORD_PAIRS.update({login_pass.split(':')[0]: login_pass.split(':')[1]})

app = Dash(__name__)
server = app.server
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

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

topics_df = pd.read_excel('data/mob_topics.xlsx', sheet_name="top_words_weekly")
topics_df['W_Rch(000)_rnd'] = topics_df['CumW_Rch(000)'].round(3)

week_dynamics_df = pd.read_excel('data/mob_topics.xlsx', sheet_name="weekly_dynamics")

app.layout = html.Div([
    html.H1('Тестовый дашборд', style={'color': "rgb(76,76,75)"}),
    html.H2("Несколько графиков, чтобы протестировать возможности библиотеки dash",
            style={'color': "rgb(76,76,75)"}),
    html.Label("Динамика тематик поисковых запросов", style={'text-align': 'center'}),
    html.Br(),
    html.Br(),
    dcc.Tabs(id='tabs-example-1', value='tab-1', children=[
        dcc.Tab(label='По дням', children=[
            html.Div([
                html.Div([
                    html.Br(),
                    dcc.Graph(id="graph")], style={'width': '80%'}),
                html.Div([
                    html.Br(),
                    html.Div([
                        dcc.Dropdown(
                            options=data.columns[2:],
                            value=data.columns[2],
                            id='yaxis-column')]),
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
            ], style={'display': "flex"})]),
        dcc.Tab(label='По неделям', children=[
            html.Div([
                html.Div([
                    html.Br(),
                    html.Label("Топ запросов", style={'color': "rgb(0,170,149)", 'font-size': "16px"}),
                    html.Table(id="top_ques")], style={'width': '30%', 'font-size': "14px"}),
                html.Div([
                    html.Div([
                        dcc.Graph(id="weekly_graph",
                                  hoverData={'points': [{'customdata': '11.04.2022 - 17.04.2022'}]})
                        ], style={'width': '80%'}),
                    html.Div([
                        html.Br(),
                        html.Br(),
                        html.Div([
                            dcc.RadioItems(
                                options=np.sort(data.TopicLevel1.unique()),
                                value='ковид',
                                id="topic_radio",
                                labelStyle={'display': 'block'}
                            )
                        ])
                    ], style={'font-size': "12px", 'width': "20%"})
                ], style={'width': '70%', 'display': 'flex'})
            ], style={'display': "flex"})
        ]),
    ])
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


@app.callback(
    Output("weekly_graph", "figure"),
    Input("topic_radio", "value"))
def display_line(topic_radio):
    data_week = week_dynamics_df.loc[week_dynamics_df['TopicLevel1'] == topic_radio]
    figure2 = go.Figure(data=go.Scatter(x=data_week["Week"], y=data_week['W_Rch(000)'], mode='lines+markers',
                        hovertemplate='%{y:.3f}'))
    figure2.update_yaxes(title="Взвешенный охват (тыс)", title_font={"size": 12}, tickfont=dict(size=10))
    figure2.update_xaxes(title="Неделя", tickangle=90, title_font={"size": 12},
                         tickfont=dict(family='Arial', size=9))
    figure2.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font_color="rgb(119,119,118)",
        showlegend=False
    )
    figure2.update_traces(marker_color="rgb(0,170,149)", marker_line_color="rgb(0,170,149)")
    return figure2


def table(max_rows, dataset):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in ['№', 'Текст запроса', 'Охват (тыс)']]),
            style={'border': '1px solid #ddd', 'border-collapse': 'collapse'}),
        html.Tbody([
            html.Tr([
                html.Td(dataset.sort_values('CumW_Rch(000)', ascending=False).iloc[i][col])
                for col in ['rank', 'QueryText', 'W_Rch(000)_rnd']
            ]) for i in range(0, max_rows)
        ], style={'padding': '15px'})
    ])


@app.callback(
    Output("top_ques", "children"),
    Input('weekly_graph', 'hoverData'),
    Input("topic_radio", "value"))
def generate_table(hover_data, topic_radio):
    if 'customdata' in hover_data['points'][0].keys():
        week = hover_data['points'][0]['customdata']
        topics_df_week = topics_df[(topics_df['TopicLevel1'] == topic_radio) & (topics_df['Week'] == week)]
        num_top_ques = len(topics_df_week)
        if num_top_ques >= 10:
            return table(10, topics_df_week)
        else:
            return table(num_top_ques, topics_df_week)
    else:
        week = hover_data['points'][0]['x']
        topics_df_week = topics_df[(topics_df['TopicLevel1'] == topic_radio) & (topics_df['Week'] == week)]
        num_top_ques = len(topics_df_week)
        if num_top_ques >= 10:
            return table(10, topics_df_week)
        else:
            return table(num_top_ques, topics_df_week)


if __name__ == '__main__':
    app.run_server(debug=True)
