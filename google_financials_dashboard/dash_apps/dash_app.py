import yfinance as yf
from dash import dcc, html, Output, Input
import plotly.graph_objects as go
import pandas as pd
from datetime import date
from django_plotly_dash import DjangoDash

ticker = "GOOGL"
netflix = yf.Ticker(ticker)
financials = netflix.financials  # Income Statement
balance_sheet = netflix.balance_sheet
cashflow = netflix.cashflow
netflix_data = yf.download(ticker, start="2014-10-29", end="2024-10-29")
data = pd.DataFrame(netflix_data)
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.map(lambda x: x[0] if isinstance(x, tuple) else x)

data.reset_index(inplace=True)

financials = pd.DataFrame(financials.T)
cashflow = pd.DataFrame(cashflow.T)
result = financials.join(cashflow)[
    ["Total Revenue", "Free Cash Flow", "Cost Of Revenue"]
]
result.dropna(inplace=True)
x = [i.year for i in result.index]
result["year"] = [i.year for i in result.index]

cagr = (
    result[result["year"] == date.today().year - 1]["Total Revenue"].iloc[0]
    / result[result["year"] == date.today().year - 4]["Total Revenue"].iloc[0]
) ** (1 / 4) - 1
ltm_gm = (
    result[result["year"] == date.today().year - 1]["Total Revenue"].iloc[0]
    - result[result["year"] == date.today().year - 1]["Cost Of Revenue"].iloc[0]
) / result[result["year"] == date.today().year - 1]["Total Revenue"].iloc[0]
ltm_fcf = (
    result[result["year"] == date.today().year - 1]["Free Cash Flow"].iloc[0]
    / result[result["year"] == date.today().year - 1]["Total Revenue"].iloc[0]
)

stock = yf.Ticker(ticker)
forward_eps = stock.info.get("forwardEps")  # Forward EPS
forward_pe_ratio = stock.info.get("forwardPE")  # Forward P/E ratio
fair_value = forward_eps * forward_pe_ratio


def set_config(img_name):
    return {
        "displaylogo": False,
        "modeBarButtonsToRemove": [
            "zoom",
            "pan",
            "zoomIn",
            "zoomOut",
            "resetView",
            "autoScale",
            "resetScale",
            "lasso2d",
            "select2d",
        ],
        "toImageButtonOptions": {
            "format": "png",
            "filename": img_name,
            "height": 700,
            "width": 1300,
            "scale": 1,
        },
    }


external_scripts = [
    {"src": "https://cdn.tailwindcss.com"},
]
external_stylesheets = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
]
app = DjangoDash(
    'google_dashboard',
    external_scripts=external_scripts,
    external_stylesheets=external_stylesheets,
)
app.title = "Financial Google Dashboard"
app._favicon = "favicon.ico"
app.layout = html.Div(
    className="w-full flex flex-col justify-center items-center",
    children=[
        html.Div(
            children=[
                html.Img(
                    src="https://res.cloudinary.com/jhquihuiri7/image/upload/v1730828730/yvqikayetxicgufcre0c.png",
                    className="w-[300px]",
                )
            ]
        ),
        html.Div(
            children=[
                html.Div(className="flex-grow bg-black h-0.5"),
                html.Span("Keys Facts", className="mx-2 font-bold"),
                html.Div(className="flex-grow bg-black h-0.5"),
            ],
            className="flex items-center w-[80%]",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.I(
                            className="fa fa-line-chart fa-2x mr-2",
                            style={"color": "#db0000"},
                        ),
                        html.Div(
                            children=[
                                html.H2(
                                    f"{round(cagr*100,2)}%",
                                    className="text-white text-xl",
                                ),
                                html.H4(
                                    # TODO
                                    "4 year stock CARG",
                                    className="text-white text-[10px]",
                                ),
                            ]
                        ),
                    ],
                    className="my-4 bg-black rounded-lg flex flex-row py-2 px-4 items-center",
                ),
                html.Div(
                    children=[
                        html.I(
                            className="fa fa-pie-chart fa-2x mr-2",
                            style={"color": "#db0000"},
                        ),
                        html.Div(
                            children=[
                                html.H2(
                                    f"{round(ltm_gm * 100, 2)}%",
                                    className="text-white text-xl",
                                ),
                                html.H4(
                                    f"LMT Gross margin {date.today().year-1}",
                                    className="text-white text-[10px]",
                                ),
                            ]
                        ),
                    ],
                    className="my-4 bg-black rounded-lg flex flex-row py-2 px-4 items-center",
                ),
                html.Div(
                    children=[
                        html.I(
                            className="fa fa-usd fa-2x mr-2", style={"color": "#db0000"}
                        ),
                        html.Div(
                            children=[
                                html.H2(
                                    f"{round(ltm_fcf * 100, 2)}%",
                                    className="text-white text-xl",
                                ),
                                html.H4(
                                    f"LMT Free Cash Flow {date.today().year-1}",
                                    className="text-white text-[10px]",
                                ),
                            ]
                        ),
                    ],
                    className="my-4 bg-black rounded-lg flex flex-row py-2 px-4 items-center",
                ),
                html.Div(
                    children=[
                        html.I(
                            className="fa fa-balance-scale fa-2x mr-2",
                            style={"color": "#db0000"},
                        ),
                        html.Div(
                            children=[
                                html.H2(
                                    f"${round(fair_value,2)}",
                                    className="text-white text-xl",
                                ),
                                html.H4(
                                    "Est. Fair value", className="text-white text-[10px]"
                                ),
                            ]
                        ),
                    ],
                    className="my-4 bg-black rounded-lg flex flex-row py-2 px-4 items-center",
                ),
            ],
            className="flex flex-col sm:flex-row justify-evenly pb-[20px] w-[80%]",
        ),
        html.Div(className="w-[80%] bg-black h-0.5"),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H1("Revenue & FCF growth", className="font-bold text-3xl"),
                        dcc.Graph(id="revenue_fcf", config=set_config("revenue_fcf")),
                    ],
                    className="w-[40%] text-center",
                ),
                html.Div(
                    children=[
                        html.H1("Stock market value", className="font-bold text-3xl"),
                        dcc.Graph(
                            id="candle_stick", config=set_config("historical_data")
                        ),
                    ],
                    className="w-[40%] text-center",
                ),
            ],
            className="flex flex-row w-full my-5 justify-evenly",
        ),
        html.Div(className="w-[80%] bg-black h-0.5 my-6"),
        html.Div(
            children=[
                html.Div(
                    [
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.I(
                                            className="fa fa-bar-chart fa-2x",
                                            style={"color": "white"},
                                        ),
                                    ],
                                    className="w-12 h-12 rounded-full bg-black mr-6 flex items-center justify-center",
                                ),
                                html.P("Key Metrics", className="font-bold text-3xl"),
                            ],
                            className="flex flex-row my-1",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P(
                                            "Payed Memberships",
                                            className="font-bold italic",
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    html.Div(
                                                        className="w-[16.5%] h-6 bg-[#00ff00] rounded-xl"
                                                    ),
                                                    className="w-[70%] h-6 bg-slate-300 rounded-xl",
                                                ),
                                                html.P(
                                                    "+16.5%", className="ml-4 font-bold"
                                                ),
                                            ],
                                            className="flex flex-row",
                                        ),
                                    ],
                                    className="flex flex-col my-2",
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Streaming Revenue",
                                            className="font-bold italic",
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    html.Div(
                                                        className="w-[17%] h-6 bg-[#00ff00] rounded-xl"
                                                    ),
                                                    className="w-[70%] h-6 bg-slate-300 rounded-xl",
                                                ),
                                                html.P(
                                                    "+17%", className="ml-4 font-bold"
                                                ),
                                            ],
                                            className="flex flex-row",
                                        ),
                                    ],
                                    className="flex flex-col my-2",
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Return on capital",
                                            className="font-bold italic",
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    html.Div(
                                                        className="w-[22%] h-6 bg-[#00ff00] rounded-xl"
                                                    ),
                                                    className="w-[70%] h-6 bg-slate-300 rounded-xl",
                                                ),
                                                html.P(
                                                    "22%", className="ml-4 font-bold"
                                                ),
                                            ],
                                            className="flex flex-row",
                                        ),
                                    ],
                                    className="flex flex-col my-2",
                                ),
                            ],
                            className="flex flex-col",
                        ),
                    ],
                    className="w-[35%]",
                ),
                html.Div(
                    [
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.I(
                                            className="fa fa-diamond fa-2x",
                                            style={"color": "white"},
                                        ),
                                    ],
                                    className="w-12 h-12 rounded-full bg-black mr-6 flex items-center justify-center",
                                ),
                                html.P("Quality", className="font-bold text-3xl"),
                            ],
                            className="flex flex-row my-1",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P(
                                            "Management",
                                            className="font-bold italic",
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.I(
                                                            className="fa fa-star fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                        html.I(
                                                            className="fa fa-star fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                        html.I(
                                                            className="fa fa-star fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                        html.I(
                                                            className="fa fa-star fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                        html.I(
                                                            className="fa fa-star-half fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                    ],
                                                    className="flex flex-row w-[65%] pt-3",
                                                ),
                                                html.P(
                                                    "4.5", className="ml-4 font-bold"
                                                ),
                                            ],
                                            className="flex flex-row",
                                        ),
                                    ],
                                    className="flex flex-col my-2",
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Product",
                                            className="font-bold italic",
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.I(
                                                            className="fa fa-star fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                        html.I(
                                                            className="fa fa-star fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                        html.I(
                                                            className="fa fa-star fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                        html.I(
                                                            className="fa fa-star fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                        html.I(
                                                            className="fa fa-star-half fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                    ],
                                                    className="flex flex-row w-[65%] pt-3",
                                                ),
                                                html.P(
                                                    "4.8", className="ml-4 font-bold"
                                                ),
                                            ],
                                            className="flex flex-row",
                                        ),
                                    ],
                                    className="flex flex-col my-2",
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Employees",
                                            className="font-bold italic",
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.I(
                                                            className="fa fa-star fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                        html.I(
                                                            className="fa fa-star fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                        html.I(
                                                            className="fa fa-star fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                        html.I(
                                                            className="fa fa-star fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                    ],
                                                    className="flex flex-row w-[65%] pt-3",
                                                ),
                                                html.P(
                                                    "4.2", className="ml-4 font-bold"
                                                ),
                                            ],
                                            className="flex flex-row",
                                        ),
                                    ],
                                    className="flex flex-col my-2",
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Moat",
                                            className="font-bold italic",
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.I(
                                                            className="fa fa-star fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                        html.I(
                                                            className="fa fa-star fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                        html.I(
                                                            className="fa fa-star fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                        html.I(
                                                            className="fa fa-star-half fa-lg",
                                                            style={"color": "black"},
                                                        ),
                                                    ],
                                                    className="flex flex-row w-[65%] pt-3",
                                                ),
                                                html.P(
                                                    "3.5", className="ml-4 font-bold"
                                                ),
                                            ],
                                            className="flex flex-row",
                                        ),
                                    ],
                                    className="flex flex-col my-2",
                                ),
                            ],
                            className="flex flex-col",
                        ),
                    ],
                    className="w-[30%]",
                ),
                html.Div(
                    [
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.I(
                                            className="fa fa-usd fa-2x",
                                            style={"color": "white"},
                                        ),
                                    ],
                                    className="w-12 h-12 rounded-full bg-black mr-6 flex items-center justify-center",
                                ),
                                html.P("Financials", className="font-bold text-3xl"),
                            ],
                            className="flex flex-row my-1",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P(
                                            "Revenue growth",
                                            className="font-bold italic",
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    html.Div(
                                                        className="w-[16.8%] h-6 bg-[#00ff00] rounded-xl"
                                                    ),
                                                    className="w-[70%] h-6 bg-slate-300 rounded-xl",
                                                ),
                                                html.P(
                                                    "+16.8%", className="ml-4 font-bold"
                                                ),
                                            ],
                                            className="flex flex-row",
                                        ),
                                    ],
                                    className="flex flex-col my-2",
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Free cash flow growth",
                                            className="font-bold italic",
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    html.Div(
                                                        className="w-[9%] h-6 bg-[#db0000] rounded-xl"
                                                    ),
                                                    className="w-[70%] h-6 bg-slate-300 rounded-xl",
                                                ),
                                                html.P(
                                                    "-9%", className="ml-4 font-bold"
                                                ),
                                            ],
                                            className="flex flex-row",
                                        ),
                                    ],
                                    className="flex flex-col my-2",
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Net cash", className="font-bold italic"
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    html.Div(
                                                        className="w-[8%] h-6 bg-[#db0000] rounded-xl"
                                                    ),
                                                    className="w-[70%] h-6 bg-slate-300 rounded-xl",
                                                ),
                                                html.P(
                                                    "-8 bln", className="ml-4 font-bold"
                                                ),
                                            ],
                                            className="flex flex-row",
                                        ),
                                    ],
                                    className="flex flex-col my-2",
                                ),
                            ],
                            className="flex flex-col",
                        ),
                    ],
                    className="w-[35%]",
                ),
            ],
            className="w-[80%] flex flex-row",
        ),
        html.Div(className="w-[80%] bg-black h-0.5 my-6"),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.I(
                                            className="fa fa-retweet fa-2x",
                                            style={"color": "white"},
                                        ),
                                    ],
                                    className="w-12 h-12 rounded-full bg-black mr-6 flex items-center justify-center",
                                ),
                                html.P("Pros & Cons", className="font-bold text-3xl"),
                            ],
                            className="flex flex-row my-1",
                        ),
                        html.Ul(
                            children=[
                                html.Li(
                                    children=[
                                        html.Div(
                                            children=[
                                                html.I(
                                                    className="fa fa-check",
                                                    style={"color": "white"},
                                                ),
                                            ],
                                            className="w-6 h-6 rounded-xl bg-[#00ff00] mr-2",
                                        ),
                                        html.P("Strong Brand"),
                                    ],
                                    className="flex flex-row my-1",
                                ),
                                html.Li(
                                    children=[
                                        html.Div(
                                            children=[
                                                html.I(
                                                    className="fa fa-check",
                                                    style={"color": "white"},
                                                ),
                                            ],
                                            className="w-6 h-6 rounded-xl bg-[#00ff00] mr-2",
                                        ),
                                        html.P("Original Content leader"),
                                    ],
                                    className="flex flex-row my-1",
                                ),
                                html.Li(
                                    children=[
                                        html.Div(
                                            children=[
                                                html.I(
                                                    className="fa fa-times",
                                                    style={"color": "white"},
                                                ),
                                            ],
                                            className="w-6 h-6 rounded-xl bg-[#db0000] mr-2",
                                        ),
                                        html.P("Fierce competition"),
                                    ],
                                    className="flex flex-row my-1",
                                ),
                                html.Li(
                                    children=[
                                        html.Div(
                                            children=[
                                                html.I(
                                                    className="fa fa-times",
                                                    style={"color": "white"},
                                                ),
                                            ],
                                            className="w-6 h-6 rounded-xl bg-[#db0000] mr-2",
                                        ),
                                        html.P("High content costs"),
                                    ],
                                    className="flex flex-row my-1",
                                ),
                            ],
                            className="list-none",
                        ),
                    ],
                    className="w-[40%] text-center flex flex-col",
                ),
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.I(
                                            className="fa fa-balance-scale fa-2x",
                                            style={"color": "white"},
                                        ),
                                    ],
                                    className="w-12 h-12 rounded-full bg-black mr-6 flex items-center justify-center",
                                ),
                                html.P("Valuation", className="font-bold text-3xl"),
                            ],
                            className="flex flex-row my-1",
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.P(
                                            "Assumed FCF growth at current price ($702) and flat FCF margins.",
                                            className="text-justify italic",
                                        ),
                                        html.Ul(
                                            children=[
                                                html.Li(
                                                    [
                                                        html.Span("●   1-5 years:"),
                                                        html.Span("20%"),
                                                    ],
                                                    className="flex flex-row justify-between",
                                                ),
                                                html.Li(
                                                    [
                                                        html.Span("●   6-10 years:"),
                                                        html.Span("15%"),
                                                    ],
                                                    className="flex flex-row justify-between",
                                                ),
                                                html.Li(
                                                    [
                                                        html.Span(
                                                            "●   Terminal multiple:"
                                                        ),
                                                        html.Span("15x"),
                                                    ],
                                                    className="flex flex-row justify-between",
                                                ),
                                                html.Li(
                                                    [
                                                        html.Span("●   Discount rate:"),
                                                        html.Span("10%"),
                                                    ],
                                                    className="flex flex-row justify-between",
                                                ),
                                            ]
                                        ),
                                    ],
                                    className="w-[40%]",
                                ),
                                html.Div(
                                    children=[
                                        html.P(
                                            "Assuming a declining FCF growth and flat FCF margins.",
                                            className="text-justify italic",
                                        ),
                                        html.Ul(
                                            children=[
                                                html.Li(
                                                    [
                                                        html.Span("●   1-5 years:"),
                                                        html.Span("18%"),
                                                    ],
                                                    className="flex flex-row justify-between",
                                                ),
                                                html.Li(
                                                    [
                                                        html.Span("●   6-10 years:"),
                                                        html.Span("13%"),
                                                    ],
                                                    className="flex flex-row justify-between",
                                                ),
                                                html.Li(
                                                    [
                                                        html.Span(
                                                            "●   Terminal multiple:"
                                                        ),
                                                        html.Span("15x"),
                                                    ],
                                                    className="flex flex-row justify-between",
                                                ),
                                                html.Li(
                                                    [
                                                        html.Span("●   Discount rate:"),
                                                        html.Span("10%"),
                                                    ],
                                                    className="flex flex-row justify-between",
                                                ),
                                            ]
                                        ),
                                    ],
                                    className="w-[40%]",
                                ),
                            ],
                            className="flex flex-row justify-around",
                        ),
                    ],
                    className="w-[60%] text-center",
                ),
            ],
            className="flex flex-row w-[80%] mb-14",
        ),
        dcc.Store(id="dummy-store"),
    ],
)


@app.callback(
    [Output("revenue_fcf", "figure"), Output("candle_stick", "figure")],
    [Input("dummy-store", "data")],
)
def plot(data_dummy):
    fig1 = go.Figure()
    fig1.add_trace(
        go.Bar(
            x=x,
            y=result["Total Revenue"],
            marker_color="lightslategrey",
            base=0,
            name="Revenue",
        )
    )
    fig1.add_trace(
        go.Bar(
            x=x,
            y=result["Free Cash Flow"],
            base=[-100000000],
            marker_color="crimson",
            name="Free Cash Flow",
        )
    )
    fig1.update_layout(
        title="Values in Billions of Dollars",
        margin=dict(t=26, b=0, l=40, r=0),
        height=300,
        legend=dict(
            x=0.8,
            y=1.12,
            xanchor="center",
            yanchor="top",  # Anchor the legend at the bottom on the y-axis
            orientation="h",  # Horizontal orientation
        ),
    )
    fig2 = go.Figure(
        data=[
            go.Candlestick(
                x=data["Date"],
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
            )
        ]
    )
    fig2.update_layout(
        title="Values in Dollars", margin=dict(t=26, b=0, l=0, r=40), height=300
    )
    return fig1, fig2

