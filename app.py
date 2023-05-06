# Example of using plotly via shinywidgets
#shiny run --reload

import plotly.graph_objs as go
from shiny import App, ui, render
from shinywidgets import output_widget, register_widget
import pandas

df = pandas.read_csv('playoff_on_ice_5623.csv')
app_ui = ui.page_fluid(
    ui.tags.style("td,div,h1,tr {color: white;}"),
ui.tags.style("div {background-color: #111111}"),
ui.tags.style("h1,h3 {text-align: center;}"),
    ui.tags.h1("Playoff On-Ice xG Rates", class_="app-heading"),
    ui.tags.h3("@StatsByZach", class_="app-heading"),
    ui.row(
        ui.column(2),
        ui.column(4,ui.tags.h5("Select a Team", class_="app-heading"),
            ui.input_select("x", "", {"All": "All", "NYI": "New York Islanders","CAR":"Carolina Hurricanes"
                                      ,"N.J":"New Jersey Devils","NYR":"New York Rangers","FLA":"Florida Panthers","BOS":"Boston Bruins"
                                      ,"EDM":"Edmonton Oilers","L.A":"Los Angeles Kings","T.B":"Tampa Bay Lightning","TOR":"Toronto Maple Leafs",
                                      "SEA":"Seattle Kraken","DAL":"Dallas Stars","COL":"Colorado Avalanche","VGK":"Vegas Golden Knights","WPG":"Winnipeg Jets"
                                      ,"MIN":"Minnesota Wild"}),
                                      ui.tags.h5("Minimum EV TOI", class_="app-heading"),
            ui.input_slider("toi", "", min=0, max=round(df['EV_TOI'].max(),0), value=round(df['EV_TOI'].quantile(.25),1)),
            ui.tags.h5("Sort Table by", class_="app-heading"),
            ui.input_select("y","",{"Player":"Player","Team":"Team","EV_TOI":"EV_TOI","xGF/60":"xGF/60","xGA/60":"xGA/60","xGF%":"xGF%"}),
            ui.input_radio_buttons(
        "z", "", {True: "High to Low", False: "Low to High"}
    ),
            ui.output_table("table")
            ),
        ui.column(6,output_widget("scatterplot"),
            ui.output_plot("scatter")),
    )
)
def server(input, output, session):
    @output
    @render.table
    def table():
        df = pandas.read_csv('playoff_on_ice_5623.csv')
        df = df[['Player','Team','EV_TOI','xGF/60','xGA/60','xGF%']].sort_values(by='Player',ascending=True)
        if (input.x() == "All"):
            df = df[df["EV_TOI"]>=input.toi()].sort_values(by=input.y(),ascending=input.z())
        else:
            df = df[(df['Team']==input.x())&(df['EV_TOI']>=input.toi())].sort_values(by=input.y(),ascending=input.z())
        return df
    
    @output
    @render.plot
    def scatter():
        team = input.x()
        if (team=='All'):
            data = df[df["EV_TOI"]>=input.toi()]
        else:
            data = df[(df['Team']==team)&(df['EV_TOI']>=input.toi())]
        scatterplot = go.FigureWidget(
            data=[
                go.Scatter(
                    x=data['xGF/60'],
                    y=data['xGA/60'],
                    mode='markers+text',
                    dy=-1,
                    marker=dict(
                        color=data['EV_TOI'],
                        size=10,
                        colorbar=dict(
                            title="EV TOI"
                        ),
                    ),
                    text=data['Player'],
                    textposition="top right"
                ),
            ],
        )
        scatterplot.update(layout_yaxis_range = [6,0.1])
        scatterplot.update(layout_xaxis_range  = [0.1,6])
        scatterplot.update_layout(width=1100)
        scatterplot.update_layout(height=1100)
        scatterplot.update_layout(template="plotly_dark", title=team+" Skaters On-Ice Expected Goal Rates<br>2022-23 Stanley Cup Playoffs<br><i>Strength: Even</i><br>")
        scatterplot.update_layout(margin=dict(t=115,l=50))
        scatterplot.update_layout(yaxis=dict(title_text="xGA/60",showgrid=False))
        scatterplot.update_layout(xaxis=dict(title_text="xGF/60",showgrid=False))
        scatterplot.add_annotation(
    text = ("Data: @StatsByZach on Twitter")
    , showarrow=False
    , x = .80
    , y = -.041
    , xref='paper'
    , yref='paper' 
    , xanchor='left'
    , yanchor='bottom'
    , xshift=-1
    , yshift=-5
    , font=dict(size=11, color="white")
    , align="left"
)
        register_widget("scatterplot", scatterplot)


app = App(app_ui, server)
