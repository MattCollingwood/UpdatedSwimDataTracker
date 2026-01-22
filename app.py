# Imports
import dash
import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, html, dash_table, callback, State, clientside_callback
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go
import io
from datetime import datetime




# Loading Data
def load_data():
    data = pd.read_csv('assets/daily_swim_summary.csv')
    data["date"] = pd.to_datetime(data["date"])
    data["date_display"] = data["date"].dt.strftime("%Y-%m-%d")
    
    data["year"] = data["date"].dt.year

    return data


def load_aggregate_data():
    agg_data = pd.read_csv('assets/aggregated_swim_data.csv')
    agg_data["date"] = agg_data["date"]
    agg_data.set_index("date", inplace=True, drop=False)
    return agg_data


data = load_data()
agg_data = load_aggregate_data()


external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css"
]

# Create the Web Application
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server


# Sidebar navigation
sidebar = html.Div(
    [
        html.Div(
            [
                html.Img(
                    src="assets/Logo.svg",
                    style={
                        "width": "80px",
                        "height": "80px",
                        "backgroundColor": "#282a54",
                        "color": "#fff",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "fontSize": "18px",
                        "fontWeight": "bold",
                        "margin": "30px auto"
                    }
                )
            ]
        ),
        html.Hr(style={"borderColor": "#ddd"}),
        dbc.Nav(
            [
                dbc.NavLink(
                    "Overview",
                    id="nav-overview",
                    href="#",
                    active=True,
                    style={"fontSize": "16px", "padding": "15px 20px", "color": "#e0e1e5"}
                ),
                dbc.NavLink(
                    "All Records",
                    id="nav-table",
                    href="#",
                    active=False,
                    style={"fontSize": "16px", "padding": "15px 20px", "color": "#e0e1e5"}
                ),
                dbc.NavLink(
                    "Import/Export",
                    id="nav-export",
                    href="#",
                    active=False,
                    style={"fontSize": "16px", "padding": "15px 20px", "color": "#e0e1e5"}
                ),
            ],
            vertical=True,
            pills=True,
        ),
        html.Div(
            [
                html.Hr(style={"borderColor": "#ddd"}),
                dbc.Nav(
                    [
                        dbc.NavLink(
                            [html.I(className="bi bi-gear", style={"fontSize": "20px", "color": "#e0e1e5"})],
                            id="nav-settings",
                            href="#",
                            style={"padding": "0 15px", "textAlign": "center", "color": "#e0e1e5"}
                        ),
                        dbc.NavLink(
                            [html.I(className="bi bi-person", style={"fontSize": "20px"})],
                            id="nav-account",
                            href="#",
                            style={"padding": "0 15px", "textAlign": "center", "color": "#e0e1e5"}
                        ),
                    ],
                    vertical=False,
                    horizontal="end"
                )
            ],
            style={"position": "absolute", "bottom": "2px", "width": "100%"}
        )
    ],
    id="sidebar",
    style={
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "250px",
        "padding": "0",
        "backgroundColor": "#282a54",
        "height": "100vh"
    }
)


# Overview Content
overview_content = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Dropdown(
                        id="workout_filter",
                        options=[{"label": date, "value": date} for date in data["date_display"].unique()],
                        value=None,
                        placeholder="Select a Workout"
                    ),
                ], style={"border": "1px solid #375050", "borderRadius": "8px"})
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Span("🔆 Date:", style={"fontSize": "18px", "fontWeight": "bold", "marginRight": "10px", "color": "#e0e1e5"}),
                        html.Span(id="workout_date", style={"fontSize": "18px", "fontWeight": "bold", "color": "#e0e1e5"})
                    ], style={"display": "flex", "alignItems": "center"})
                ], style={"padding": "5px", "height": "40px"})
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Span("📈 Yardage: ", style={"fontSize": "18px", "fontWeight": "bold", "marginRight": "10px", "color": "#e0e1e5"}),
                        html.Span(id="workout_yardage", style={"fontSize": "18px", "fontWeight": "bold", "color": "#e0e1e5"})
                    ], style={"display": "flex", "alignItems": "center"})
                ], style={"padding": "5px", "height": "40px"})
            ])
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Span("⏱ Duration: ", style={"fontSize": "18px", "fontWeight": "bold", "marginRight": "10px", "color": "#e0e1e5"}),
                        html.Span(id="workout_duration", style={"fontSize": "18px", "fontWeight": "bold", "color": "#e0e1e5"})
                    ], style={"display": "flex", "alignItems": "center"})
                ], style={"padding": "5px", "height": "40px"})
            ])
        ], width=3),
    ], style={"marginBottom": "20px", "padding-top": "30px"}),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Yearly Average Time/Workout", style={"fontSize": "12px", "textAlign": "Center"}),
                    html.H4("--", id="avg_duration", style={"textAlign": "Center"})
                ], style={"padding": "5px"})
            ]) 
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Yearly Average Distance Swam/Workout", style={"fontSize": "12px", "textAlign": "Center"}),
                    html.H4("--", id="avg_distance", style={"textAlign": "Center"})
                ], style={"padding": "5px"})
            ])    
        ], width=6)  
    ], style={"marginBottom": "20px", "padding-top": "3px"}),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("📈 Yardage Overview", style={"marginBottom": "15px"}),
                    dcc.Graph(
                        id="yardage_overview_chart",
                        config={'displayModeBar': False}
                    )
                ], style={"padding": "15px"})
            ])
        ], width=8),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("📊 Breakdown by Stroke", style={"marginBottom": "15px"}),
                    dcc.Graph(id="swim_strokes", config={'displayModeBar': False})
                ], style={"padding": "15px"})
            ])
        ], width=4)
    ], style={"marginBottom": "20px"}),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6("🧮 Yearly Totals", style={"marginBottom": "15px"})
                        ], width=11),

                        dbc.Col([
                            dcc.Dropdown(
                                id="year_filter",
                                options=[{"label": "All Years", "value": "all"}] + 
                                        [{"label": str(year), "value": year} for year in sorted(data["year"].unique())],
                                value="all",
                                placeholder="Select a year",
                                style={"fontSize": "14px", "alignItems": "end", "marginRight": "15px", "border": "1px solid #375050", "borderRadius": "4px"}
                            )
                        ], width=1, style={"textAlign": "right"})
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.H6("Workouts", style={"fontSize": "12px", "textAlign": "Center"}),
                            html.H4(str(len(data)), id="yearly_workouts", style={"textAlign": "Center"})
                        ], width=4),
                        dbc.Col([
                            html.H6("Time Spent Swimming", style={"fontSize": "12px", "textAlign": "Center"}),
                            html.H4(f"{sum(data['total_elapsed_time']/ 3600):,.2f} hours", id="yearly_time", style={"textAlign": "Center"})
                        ], width=4),
                        dbc.Col([
                            html.H6("Distance", style={"fontSize": "12px", "textAlign": "Center"}),
                            html.H4(f"{sum(data['total_distance']/1650):,.2f} miles", id="yearly_distance", style={"textAlign": "Center"})
                        ], width=4)
                    ])
                    
                ], style={"padding": "15px"})
            ])
        ])
    ]),
], style={"height": "100vh"})
    



# Table Content
table_content = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("🏊‍♂️ Recent Workouts", style={"marginBottom": "15px"}),
                    dash_table.DataTable(
                        id="recent_workouts",
                        columns=[
                            {"name": "Date", "id": "date_display", "deletable": False, "selectable": True, "hideable": True},
                            {"name": "Total Distance", "id": "total_distance", "deletable": False, "selectable": True, "hideable": True, "type": "numeric", "format": {"specifier": ",.0f"}},
                            {"name": "Max Heart Rate", "id": "max_heart_rate", "deletable": False, "selectable": True, "hideable": True},
                            {"name": "Number of Lengths", "id": "num_lengths", "deletable": False, "selectable": True, "hideable": True},
                            {"name": "Stroke Type", "id": "swim_stroke", "deletable": False, "selectable": True, "hideable": True},
                            {"name": "Distance (Miles)", "id": "total_distance_miles", "deletable": False, "selectable": True, "hideable": True, "type": "numeric", "format": {"specifier": ".2f"}},
                            {"name": "Time (Minutes)", "id": "total_time_minutes", "deletable": False, "selectable": True, "hideable": True, "type": "numeric", "format": {"specifier": ".0f"}},
                        ] + [
                            {"name": i, "id": i, "deletable": True, "selectable": False}
                            for i in data.columns
                            if i not in ["date", "total_distance", "max_heart_rate", "num_lengths", "swim_stroke", "total_distance_miles", "total_time_minutes"]
                        ],
                        data=data.sort_values(by="date_display", ascending=False).to_dict("records"),
                        hidden_columns=["message_index", "event", "event_type", "start_time", "total_elapsed_time", "total_cycles", "avg_heart_rate", "avg_cadence", "max_cadence", "lap_trigger", "first_length_index", "avg_stroke_distance", "sport", "min_heart_rate", "enhanced_avg_speed", "time", "Unnamed: 0", "workout_id", "backstroke", "butterfly", "breaststroke", 'freestyle', "im", "mixed", "year", "date_display"],
                        sort_action="native",
                        selected_columns=[],
                        selected_rows=[],
                        page_size=25,
                        style_cell={"fontSize": "13px", "fontFamily": "Lexend Deca", "backgroundColor": "#e0e1e5"},
                        style_header={"fontWeight": "bold"},
                        style_cell_conditional=[
                            {"if": {"column_id": "date_display"}, "width": "120px", "minWidth": "120px", "maxWidth": "120px"},
                            {"if": {"column_id": "total_distance"}, "width": "130px", "minWidth": "130px", "maxWidth": "140px"},
                            {"if": {"column_id": "max_heart_rate"}, "width": "130px", "minWidth": "130px", "maxWidth": "140px"},
                            {"if": {"column_id": "num_lengths"}, "width": "130px", "minWidth": "130px", "maxWidth": "150px"},
                            {"if": {"column_id": "swim_stroke"}, "width": "210px", "minWidth": "180px", "maxWidth": "210px"},
                            {"if": {"column_id": "total_distance_miles"}, "width": "160px", "minWidth": "160px", "maxWidth": "160px"},
                            {"if": {"column_id": "total_time_minutes"}, "width": "150px", "minWidth": "150px", "maxWidth": "150px"},
                        ],
                        css=[{"selector": ".show-hide", "rule": "display: none"}]
                    )
                ])
            ])
        ], style={"marginTop": "30px"})
    ])
    
])


# Export Content
export_content = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("Export Data", style={"marginBottom": "20px"}),
            dbc.Card([
                dbc.CardBody([
                    html.H5("Download Options", style={"marginBottom": "20px", "color": "#e0e1e5"}),
                    html.P("Select the data you want to export:", style={"color": "#e0e1e5"}),
                    dbc.Button(
                        "Print Dashboard", 
                        color="primary", 
                        className="me-2 mb-2",
                        id="print_dashboard_btn"
                    ),
                    dbc.Button(
                        "Export All Data (Excel)", 
                        color="success", 
                        className="mb-2",
                        id="export_excel_btn"
                    ),
                    dcc.Download(id="download_excel"),
                    html.H5("Share Dashboard", style={"marginBottom": "20px", "marginTop": "30px", "color": "#e0e1e5"}),
                    html.P("Share your swim tracking dashboard with others:", style={"color": "#e0e1e5", "marginBottom": "15px"}),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                [
                                    html.I(className="bi bi-twitter-x", style={"marginRight": "8px"}),
                                    ""
                                ],
                                id="share_twitter_btn",
                                color="info",
                                className="mb-2 w-100",
                                style={"backgroundColor": "#1DA1F2", "borderColor": "#1DA1F2"}
                            )
                        ], width=2),
                        dbc.Col([
                            dbc.Button(
                                [
                                    html.I(className="bi bi-facebook", style={"marginRight": "8px"}),
                                    "Facebook"
                                ],
                                id="share_facebook_btn",
                                color="primary",
                                className="mb-2 w-100",
                                style={"backgroundColor": "#1877F2", "borderColor": "#1877F2"}
                            )
                        ], width=2),
                        dbc.Col([
                            dbc.Button(
                                [
                                    html.I(className="bi bi-instagram", style={"marginRight": "8px"}),
                                    "Instagram"
                                ],
                                id="share_instagram_btn",
                                color="danger",
                                className="mb-2 w-100",
                                style={"background": "linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%)", "borderColor": "#bc1888"}
                            )
                        ], width=2),
                        dbc.Col([
                            dbc.Button(
                                [
                                    html.I(className="bi bi-envelope", style={"marginRight": "8px"}),
                                    "Email"
                                ],
                                id="share_email_btn",
                                color="secondary",
                                className="mb-2 w-100"
                            )
                        ], width=2),
                        dbc.Col([
                            dbc.Button(
                                [
                                    html.I(className="bi bi-link-45deg", style={"marginRight": "8px"}),
                                    "Copy Link"
                                ],
                                id="copy_link_btn",
                                color="success",
                                className="mb-2 w-100"
                            )
                        ], width=2)
                    ]),
                    html.Div(id="copy_link_feedback", style={"marginTop": "10px", "color": "#28a745", "display": "none"})
                ], style={"padding": "10px"})
            ])
        ], style={"marginTop": "30px", "paddingLeft": "10px"})
    ])
])


# Settings Content
settings_content = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("Settings", style={"marginBottom": "30px"}),
            
            # Distance Units Setting
            dbc.Card([
                dbc.CardBody([
                    html.H5("Distance Units", style={"marginBottom": "15px"}),
                    html.P("Select your preferred measurement system:", style={"color": "#666", "fontSize": "14px"}),
                    dcc.RadioItems(
                        id="distance_units",
                        options=[
                            {"label": " Yards", "value": "yards"},
                            {"label": " Meters", "value": "meters"}
                        ],
                        value="yards",
                        inline=True,
                        style={"fontSize": "16px"}
                    )
                ])
            ], style={"marginBottom": "20px"}),
            
            # Auto Refresh Frequency Setting
            dbc.Card([
                dbc.CardBody([
                    html.H5("Auto Refresh Frequency", style={"marginBottom": "15px"}),
                    html.P("How often should the dashboard refresh data?", style={"color": "#666", "fontSize": "14px"}),
                    dcc.Dropdown(
                        id="refresh_frequency",
                        options=[
                            {"label": "Never", "value": "never"},
                            {"label": "Every 30 seconds", "value": "30"},
                            {"label": "Every minute", "value": "60"},
                            {"label": "Every 5 minutes", "value": "300"},
                            {"label": "Every 15 minutes", "value": "900"},
                            {"label": "Every hour", "value": "3600"}
                        ],
                        value="never",
                        placeholder="Select refresh frequency",
                        style={"fontSize": "14px"}
                    )
                ])
            ], style={"marginBottom": "20px"}),
            
            # Theme Setting
            dbc.Card([
                dbc.CardBody([
                    html.H5("Theme", style={"marginBottom": "15px"}),
                    html.P("Choose a color theme for your dashboard:", style={"color": "#666", "fontSize": "14px"}),
                    dcc.Dropdown(
                        id="theme_selector",
                        options=[
                            {"label": "🌙 Dark Blue (Default)", "value": "dark_blue"},
                            {"label": "🌊 Ocean Blue", "value": "ocean"},
                            {"label": "🌲 Forest Green", "value": "forest"},
                            {"label": "🌑 Midnight Black", "value": "midnight"},
                            {"label": "🌅 Sunset Orange", "value": "sunset"},
                            {"label": "💜 Purple Haze", "value": "purple"},
                            {"label": "☀️ Light Mode", "value": "light"}
                        ],
                        value="dark_blue",
                        placeholder="Select theme",
                        style={"fontSize": "14px"}
                    ),
                    html.Div([
                        html.P("Preview:", style={"marginTop": "15px", "marginBottom": "10px", "fontSize": "14px"}),
                        html.Div(
                            id="theme_preview",
                            style={
                                "height": "60px",
                                "backgroundColor": "#282a54",
                                "borderRadius": "8px",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "color": "#e0e1e5",
                                "fontWeight": "500"
                            },
                            children="Dark Blue Theme"
                        )
                    ])
                ])
            ], style={"marginBottom": "20px"}),
            
            # Save Button
            dbc.Button(
                "Save Settings",
                id="save_settings_btn",
                color="primary",
                size="lg",
                style={"marginTop": "20px"}
            ),
            
            html.Div(
                id="settings_saved_message",
                style={"marginTop": "15px", "color": "green", "display": "none"},
                children="✓ Settings saved successfully!"
            )
            
        ], width=8, style={"marginTop": "30px"})
    ])
])


# Account Content
account_content = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("Account", style={"marginBottom": "30px"}),
            
            # Profile Picture Section
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.Div(
                                    html.I(className="bi bi-person-circle", style={"fontSize": "80px", "color": "#666"}),
                                    style={
                                        "width": "100px",
                                        "height": "100px",
                                        "borderRadius": "50%",
                                        "backgroundColor": "#f0f0f0",
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "marginBottom": "15px"
                                    }
                                ),
                                dbc.Button("Upload Photo", size="sm", color="primary", style={"fontSize": "12px"})
                            ], style={"textAlign": "center"})
                        ], width=3),
                        dbc.Col([
                            html.H5("User Profile", style={"marginBottom": "10px"}),
                            html.Div([
                                html.I(className="bi bi-calendar-check", style={"marginRight": "8px", "color": "#666"}),
                                html.Span("User Since: ", style={"fontWeight": "500"}),
                                html.Span("January 15, 2024", style={"color": "#666"})
                            ], style={"marginBottom": "10px"}),
                            html.Div([
                                html.I(className="bi bi-clock-history", style={"marginRight": "8px", "color": "#666"}),
                                html.Span("Member for ", style={"color": "#666"}),
                                html.Span("1 year, 12 days", style={"fontWeight": "500"})
                            ])
                        ], width=9)
                    ])
                ])
            ], style={"marginBottom": "20px"}),
            
            # Email Section
            dbc.Card([
                dbc.CardBody([
                    html.H5("Email Address", style={"marginBottom": "15px"}),
                    dbc.Row([
                        dbc.Col([
                            dbc.Input(
                                id="email_input",
                                type="email",
                                placeholder="user@example.com",
                                value="user@example.com",
                                style={"fontSize": "14px"}
                            )
                        ], width=8),
                        dbc.Col([
                            dbc.Button("Update Email", color="primary", size="sm", id="update_email_btn")
                        ], width=4)
                    ])
                ])
            ], style={"marginBottom": "20px"}),
            
            # Password Section
            dbc.Card([
                dbc.CardBody([
                    html.H5("Password", style={"marginBottom": "15px"}),
                    dbc.Row([
                        dbc.Col([
                            dbc.Input(
                                id="current_password",
                                type="password",
                                placeholder="Current Password",
                                style={"fontSize": "14px", "marginBottom": "10px"}
                            ),
                            dbc.Input(
                                id="new_password",
                                type="password",
                                placeholder="New Password",
                                style={"fontSize": "14px", "marginBottom": "10px"}
                            ),
                            dbc.Input(
                                id="confirm_password",
                                type="password",
                                placeholder="Confirm New Password",
                                style={"fontSize": "14px"}
                            )
                        ], width=8)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button("Change Password", color="primary", size="sm", style={"marginTop": "10px", "marginRight": "10px"}),
                            dbc.Button("Reset Password", color="link", size="sm", style={"marginTop": "10px"})
                        ])
                    ])
                ])
            ], style={"marginBottom": "20px"}),
            
            # Subscription Plan Section
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="bi bi-star", style={"fontSize": "24px", "color": "#ffc107", "marginRight": "10px"}),
                        html.H5("Current Plan: Free", style={"display": "inline-block", "marginBottom": "0"})
                    ], style={"marginBottom": "15px"}),
                    html.P("You're currently on the free plan with basic features.", style={"color": "#666", "marginBottom": "10px"}),
                    html.Div([
                        html.I(className="bi bi-info-circle", style={"marginRight": "8px", "color": "#17a2b8"}),
                        html.Span("Paid plans with advanced analytics and unlimited storage coming soon!", 
                                style={"color": "#17a2b8", "fontStyle": "italic"})
                    ], style={
                        "padding": "10px",
                        "backgroundColor": "#d1ecf1",
                        "borderRadius": "5px",
                        "border": "1px solid #bee5eb"
                    })
                ])
            ], style={"marginBottom": "20px"}),
            
            # Danger Zone - Clear Data
            dbc.Card([
                dbc.CardBody([
                    html.H5("Danger Zone", style={"marginBottom": "15px", "color": "#dc3545"}),
                    html.P("Permanently delete all your workout data. This action cannot be undone.", 
                          style={"color": "#666", "fontSize": "14px", "marginBottom": "15px"}),
                    dbc.Button(
                        [html.I(className="bi bi-trash", style={"marginRight": "8px"}), "Clear All Data"],
                        color="danger",
                        outline=True,
                        id="clear_data_btn"
                    ),
                    dbc.Modal([
                        dbc.ModalHeader("Confirm Data Deletion"),
                        dbc.ModalBody([
                            html.P("Are you absolutely sure you want to delete all your data?", 
                                  style={"fontWeight": "500", "marginBottom": "10px"}),
                            html.P("This will permanently delete:", style={"marginBottom": "5px"}),
                            html.Ul([
                                html.Li("All workout records"),
                                html.Li("All personal settings"),
                                html.Li("All historical data")
                            ]),
                            html.P("This action cannot be undone!", 
                                  style={"color": "#dc3545", "fontWeight": "bold", "marginTop": "15px"}),
                            dbc.Input(
                                id="confirm_delete_input",
                                type="text",
                                placeholder="Type 'DELETE' to confirm",
                                style={"marginTop": "15px"}
                            )
                        ]),
                        dbc.ModalFooter([
                            dbc.Button("Cancel", id="cancel_delete_btn", className="me-2", color="secondary"),
                            dbc.Button("Delete All Data", id="confirm_delete_btn", color="danger", disabled=True)
                        ])
                    ], id="delete_modal", is_open=False)
                ])
            ], style={"marginBottom": "20px", "borderColor": "#dc3545"})
            
        ], width=8, style={"marginTop": "30px"})
    ])
])


# Main content area
content = html.Div(id="page-content", style={"marginLeft": "250px", "padding": "20px", "height": "100vh", "overflow": "hidden"})


# App Layout
app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        dcc.Store(id="print_trigger"),
        dcc.Store(id="workout_selection_store", data=None),
        dcc.Store(id="share_twitter_store"),
        dcc.Store(id="share_facebook_store"),
        dcc.Store(id="share_instagram_store"),
        dcc.Store(id="share_email_store"),
        sidebar,
        content
    ]
)


# Callbacks for navigation
@callback(
    Output("page-content", "children"),
    Output("nav-overview", "active"),
    Output("nav-table", "active"),
    Output("nav-export", "active"),
    Input("nav-overview", "n_clicks"),
    Input("nav-table", "n_clicks"),
    Input("nav-export", "n_clicks"),
    Input("nav-settings", "n_clicks"),
    Input("nav-account", "n_clicks"),
    prevent_initial_call=False
)
def render_page_content(overview_clicks, table_clicks, export_clicks, settings_clicks, account_clicks):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return overview_content, True, False, False
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "nav-table":
        return table_content, False, True, False
    elif button_id == "nav-export":
        return export_content, False, False, True
    elif button_id == "nav-settings":
        return settings_content, False, False, False
    elif button_id == "nav-account":
        return account_content, False, False, False
    else:
        return overview_content, True, False, False


# Callback to save workout selection to store
@callback(
    Output("workout_selection_store", "data"),
    Input("workout_filter", "value"),
    prevent_initial_call=False
)
def save_workout_selection(selected_workout):
    return selected_workout


# Callback to restore workout selection when Overview page is shown
@callback(
    Output("workout_filter", "value"),
    Input("nav-overview", "active"),
    State("workout_selection_store", "data"),
    prevent_initial_call=True
)
def restore_workout_selection(overview_active, stored_workout):
    # When Overview page becomes active, restore the stored workout selection
    if overview_active and stored_workout is not None:
        return stored_workout
    return dash.no_update


# Original callbacks for data

@callback(
    Output("yardage_overview_chart", "figure"),
    Input("url", "pathname")
)
def create_yardage_chart(pathname):
    fig = px.line(
        x="date",
        y="total_distance",
        data_frame=data,
        labels={
            "date": "Workout Date",
            "total_distance": "Total Distance (yards)"
        }
    )
    
    # Make background transparent
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e1e5'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)'
        )
    )
    
    return fig

@callback(
    Output('recent_workouts', "style_data_conditional"),
    Input("recent_workouts", 'selected_columns'),
    prevent_initial_call=True
)
def update_table_style(selected_columns):
    return [{
        "if": {"column_id": i},
        'background_color':'transparent',
        "font-family": "sans-serif"
    } for i in selected_columns]


@callback(
    Output('workout_date', "children"),
    Output('workout_yardage', "children"),
    Output('workout_duration', "children"),
    Input('workout_filter', 'value'),
    prevent_initial_call=True
)
def update_workout_filter(selected_date):
    if selected_date is None:
        return "Select a workout", "Select a workout", "Select a workout"

    filtered_df = data[data["date_display"] == selected_date]
    total_yardage = filtered_df["total_distance"].sum()
    total_duration = filtered_df["total_time_minutes"].sum()

    return selected_date, f"{(total_yardage):,.0f} yards", f"{(total_duration):,.0f} minutes"


@callback(
    Output("swim_strokes", "figure"),
    Input("workout_filter", "value")
)
def update_swim_pie(selected_date):
    if selected_date is None:
        filtered_df = agg_data.copy()
        title = ""
    else:
        try:
            date_obj = pd.to_datetime(selected_date)
            formatted_date = date_obj.strftime("%m/%d/%Y")
        except:
            formatted_date = selected_date
        
        filtered_df = agg_data[agg_data["date"] == formatted_date]
        title = f"Workout - {selected_date}"
        
    filtered_df = filtered_df[(filtered_df["swim_stroke"].notna()) & (filtered_df["total_distance"] > 0)]
    
    if filtered_df.empty:
        fig = px.pie(names=["No Data"], values=[1], title=title)
        fig.update_traces(textinfo='none')
        return fig
    
    stroke_summary = filtered_df.groupby("swim_stroke")["total_distance"].sum().reset_index()

    stroke_summary["swim_stroke"] = stroke_summary["swim_stroke"].str.title()

    fig = px.pie(stroke_summary, names="swim_stroke", values="total_distance", title=title)
    
    fig.update_traces(
        hoverinfo="skip",
        hovertemplate=None
    )


    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e0e1e5'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        margin=dict(b=80) 
    )

    return fig


@callback(
    Output("yearly_workouts", "children"),
    Output("yearly_time", "children"),
    Output("yearly_distance", "children"),
    Output("avg_duration", "children"),
    Output("avg_distance", "children"),
    Input("year_filter", "value"),
    prevent_initial_call=False
)
def update_yearly_totals(selected_year):
    if selected_year == "all" or selected_year is None:
        filtered_df = data.copy()
    else:
        filtered_df = data[data["year"] == int(selected_year)]
    
    num_workouts = len(filtered_df)
    total_time = filtered_df["total_elapsed_time"].sum() / 3600
    total_distance = filtered_df["total_distance"].sum() / 1650

    avg_duration_min = filtered_df["total_elapsed_time"].mean() / 60
    avg_distance_yards = filtered_df["total_distance"].mean()

    return (
        str(num_workouts),
        f"{total_time:,.2f} hours",
        f"{total_distance:,.2f} miles",
        f"{avg_duration_min:,.0f} min",
        f"{avg_distance_yards:,.0f} yards"
    )


@callback(
    Output("download_excel", "data"),
    Input("export_excel_btn", "n_clicks"),
    prevent_initial_call=True
)
def export_to_excel(n_clicks):
    if n_clicks is None:
        return dash.no_update
    
    
    output = io.BytesIO()
    
    # Create Excel writer object
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
     
        data.to_excel(writer, sheet_name='Daily Swim Summary', index=False)
        
       
        agg_data.to_excel(writer, sheet_name='Aggregated Swim Data', index=False)
    
    
    output.seek(0)
    file_content = output.read()
    
   
    filename = f"swim_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    
    return dcc.send_bytes(file_content, filename)


clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) {
            return {};
        }


        const overviewLink = document.getElementById("nav-overview");
        if (overviewLink) {
            overviewLink.click();
        }


        setTimeout(function() {
            window.print();
        }, 600);   // adjust if needed

        return {};
    }
    """,
    Output("print_trigger", "data"),
    Input("print_dashboard_btn", "n_clicks"),
    prevent_initial_call=True
)


# Social sharing callbacks
clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) {
            return null;
        }
        
        const url = encodeURIComponent(window.location.href);
        const text = encodeURIComponent("Check out my swim tracking dashboard!");
        const twitterUrl = "https://twitter.com/intent/tweet?url=" + url + "&text=" + text;
        window.open(twitterUrl, "_blank", "width=550,height=420");
        
        return null;
    }
    """,
    Output("share_twitter_store", "data"),
    Input("share_twitter_btn", "n_clicks"),
    prevent_initial_call=True
)

clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) {
            return null;
        }
        
        const url = encodeURIComponent(window.location.href);
        const facebookUrl = "https://www.facebook.com/sharer/sharer.php?u=" + url;
        window.open(facebookUrl, "_blank", "width=550,height=420");
        
        return null;
    }
    """,
    Output("share_facebook_store", "data"),
    Input("share_facebook_btn", "n_clicks"),
    prevent_initial_call=True
)

clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) {
            return null;
        }
        

        const url = window.location.href;
        
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(url).then(function() {
                alert("Link copied! Paste it in your Instagram post or story.");
            }).catch(function(err) {
                console.error("Failed to copy: ", err);
            });
        } else {

            const textArea = document.createElement("textarea");
            textArea.value = url;
            textArea.style.position = "fixed";
            textArea.style.left = "-999999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand("copy");
                alert("Link copied! Paste it in your Instagram post or story.");
            } catch (err) {
                console.error("Fallback copy failed: ", err);
            }
            document.body.removeChild(textArea);
        }
        
        return null;
    }
    """,
    Output("share_instagram_store", "data"),
    Input("share_instagram_btn", "n_clicks"),
    prevent_initial_call=True
)

clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) {
            return null;
        }
        
        const url = window.location.href;
        const subject = encodeURIComponent("My Swim Tracking Dashboard");
        const body = encodeURIComponent("Check out my swim tracking dashboard: " + url);
        const mailtoUrl = "mailto:?subject=" + subject + "&body=" + body;
        window.location.href = mailtoUrl;
        
        return null;
    }
    """,
    Output("share_email_store", "data"),
    Input("share_email_btn", "n_clicks"),
    prevent_initial_call=True
)

clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) {
            return {"display": "none"};
        }
        
        const url = window.location.href;
        

        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(url).then(function() {
                // Show feedback
                const feedback = document.getElementById("copy_link_feedback");
                if (feedback) {
                    feedback.textContent = "✓ Link copied to clipboard!";
                    feedback.style.display = "block";
                    setTimeout(function() {
                        feedback.style.display = "none";
                    }, 3000);
                }
            }).catch(function(err) {
                console.error("Failed to copy: ", err);
            });
        } else {

            const textArea = document.createElement("textarea");
            textArea.value = url;
            textArea.style.position = "fixed";
            textArea.style.left = "-999999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand("copy");
                const feedback = document.getElementById("copy_link_feedback");
                if (feedback) {
                    feedback.textContent = "✓ Link copied to clipboard!";
                    feedback.style.display = "block";
                    setTimeout(function() {
                        feedback.style.display = "none";
                    }, 3000);
                }
            } catch (err) {
                console.error("Fallback copy failed: ", err);
            }
            document.body.removeChild(textArea);
        }
        
        return {"display": "none"};
    }
    """,
    Output("copy_link_feedback", "style"),
    Input("copy_link_btn", "n_clicks"),
    prevent_initial_call=True
)


# Run the App
if __name__ == "__main__":
    app.run(debug=True)