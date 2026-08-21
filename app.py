import sqlite3
import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc
from dash.dependencies import Input, Output


with sqlite3.connect("data/AdventureWorks.db") as conn:

    query_profability = """
    WITH LinearTransform AS (
    SELECT sod.SalesOrderID,
        sod.ProductID,
        p.Name AS Product,
        cat.Name AS Category,
        sod.OrderQty AS Quantity,
        sod.LineTotal AS GrossIncome,
        (sod.OrderQty * p.StandardCost) AS ProductionCost,
        (sod.LineTotal * 0.05) AS FregihtCost,
        (sod.LineTotal * 0.08) AS TaxCost
    FROM SalesOrderDetail sod
    JOIN Product p ON sod.ProductID = p.ProductID
    JOIN ProductCategory cat ON p.ProductCategoryID = cat.ProductCategoryID
    )
    SELECT Category,
    SUM(Quantity) AS TotalQuantity,
    ROUND(SUM(GrossIncome), 2) AS TotalGrossIncome,
    ROUND(SUM(ProductionCost), 2) AS TotalProductionCost,
    ROUND(SUM(FregihtCost), 2) AS TotalFregihtCost,
    ROUND(SUM(TaxCost), 2) AS TotalTaxCost,
    ROUND(SUM(GrossIncome - ProductionCost - FregihtCost - TaxCost), 2) AS TotalNetProfit,
    ROUND((SUM(GrossIncome - ProductionCost - FregihtCost - TaxCost) / SUM(GrossIncome)) * 100, 2) AS NetMarginPercentage
    FROM LinearTransform
    GROUP BY Category
    ORDER BY TotalNetProfit DESC;
    """

    df_profability = pd.read_sql_query(query_profability, conn)

    query_territory = """
    WITH TerritoryTransformation AS (
    SELECT
        CASE
            WHEN soh.SalesOrderID % 2 = 0 THEN 'E-Commerce'
            ELSE 'Retail Store'
        END AS SalesChannel,
        IFNULL(a.CountryRegion, 'United States') AS Country,
        soh.SubTotal AS Sales,
        (soh.Freight + soh.TaxAmt) AS MonthlyOperatingCosts
    FROM SalesOrderHeader soh
    LEFT JOIN Address a ON soh.ShipToAddressID = a.AddressID
    )
    SELECT SalesChannel,
    Country,
    COUNT(*) AS TotalOrders,
    ROUND(SUM(Sales), 2) AS MonthlySales,
    ROUND(SUM(MonthlyOperatingCosts), 2) AS MonthlyCosts,
    ROUND(SUM(Sales - MonthlyOperatingCosts), 2) AS NetProfit,
    ROUND((SUM(Sales - MonthlyOperatingCosts) / SUM(Sales)) * 100, 2) AS NetMarginPercentage
    FROM TerritoryTransformation
    GROUP BY SalesChannel, Country
    ORDER BY NetProfit DESC;    
    """

    df_territory = pd.read_sql_query(query_territory, conn)

    query_customers = """
    SELECT CustomerID,
    COUNT(SalesOrderID) AS TotalOrders,
    ROUND(SUM(SubTotal), 2) AS TotalSpend,
    ROUND(AVG(SubTotal), 2) AS AverageOrderValue,
    CASE
        WHEN SalesOrderID % 2 = 0 THEN 'E-Commerce'
        ELSE 'Retail Store'
    END AS SalesChannel
    FROM SalesOrderHeader
    GROUP BY CustomerID
    ORDER BY TotalSpend DESC
    LIMIT 10;
    """
    
    df_customers = pd.read_sql_query(query_customers, conn)

total_company_revenue = df_profability["TotalGrossIncome"].sum()
total_company_net_profit = df_profability["TotalNetProfit"].sum()
company_wide_net_margin_baseline = (total_company_net_profit / total_company_revenue) * 100

top_volume_row = df_profability.sort_values(by="TotalSales", ascending=False).iloc[0]
global_total_units = df_profability["TotalSales"].sum()
top_volume_market_share = (top_volume_row["TotalSales"] / global_total_units) * 100

top_revenue_row = df_profability.sort_values(by="TotalGrossIncome", ascending=False).iloc[0]

top_efficiency_row = df_profability.sort_values(by="NetMarginPercentage", ascending=False).iloc[0]

total_company_orders = df_territory["TotalOrders"].sum()
total_company_costs = df_territory["MonthlyCosts"].sum()
company_cost_per_order_baseline = total_company_costs / total_company_orders

top_regional_volume = df_territory.sort_values(by="TotalOrders", ascending=False).iloc

top_regional_profit = df_territory.sort_values(by="NetProfit", ascending=False)

df_territory["CostPerOrder"] = df_territory["MonthlyCosts"] / df_territory["TotalOrders"]
top_cost_efficiency = df_territory.sort_values(by="CostPerOrder", ascending=True).iloc

total_spend_global = df_customers["TotalSpend"].sum()
total_orders_global = df_customers["TotalOrders"].sum()
company_wide_aov_baseline = total_spend_global / total_orders_global

top_monetary_customer = df_customers.sort_values(by="TotalSpend", ascending=False).iloc[0]

top_frequency_customer = df_customers.sort_values(by="TotalOrders", ascending=False).iloc[0]

top_ticket_customer = df_customers.sort_values(by="AverageOrderValue", ascending=False).iloc[0]

app = dash.Dash(__name__)

app.layout = html.Div(id="body",children=[
    html.H1("AdventureWorks Analytics: Panel de control financiero y omnicanal de E-Commerce", className="e3_title", style={"margin-bottom":"50px"}),
    html.Div(id="dropdown_div", className="e3_dropdown_div", children=[
            dcc.Dropdown(id="dropdown", className="e3_dropdown",
                        options = [
                            {"label":"Categorías","value":"Category"},
                            {"label":"Canal de ventas","value":"SalesChannel"},
                            {"label":"Clientes","value":"CustomerID"}
                        ],
                        value="name",
                        multi=False,
                        clearable=False)
    ]),
    dcc.Graph(id="figure-1", figure={}),
    html.H2("Palancas de negocio", className="e3_title"),
    html.Div(className="e3_container", children=[
        html.Div(id="data_1", className="e3_children",style={"color":"blue"}, children=[
            html.H2("Categorías", style={"font-size":"1.15em","color":"blue","font-family":"sans-serif"}),
            html.P(f"Promedio (Margen Neto): {company_wide_net_margin_baseline}", className="e3_mean", style={"color":"blue"}),
            html.Ul(className="e3_ul", style={"color":"blue"}, children=[
                html.Li(f"Volumen de ventas ({top_volume_row["Category"]}): {top_volume_market_share["TotalSales"]}", className="e3_list"),
                html.Li(f"Ingresos brutos ({top_revenue_row["Category"]}): {top_revenue_row["TotalGrossIncome"]}$", className="e3_list"),
                html.Li(f"Margen Neto ({top_efficiency_row["Category"]}): {top_efficiency_row["NetMarginPercentage"]}", className="e3_list")
            ])
        ]),
        html.Div(id="data_2", className="e3_children", children=[
            html.H2("Territorios", style={"font-size":"1.15em","color":"red","font-family":"sans-serif"}),
            html.P(f"Promedio (CPO): {company_cost_per_order_baseline}", className="e3_mean", style={"color":"red"}),
            html.Ul(className="e3_ul", style={"color":"red"}, children=[
                html.Li(f"Volumen de órdenes ({top_regional_volume["SalesChannel"]}): {top_regional_volume["TotalOrders"]}", className="e3_list"),
                html.Li(f"Ganancia Neta ({top_regional_profit["SalesChannel"]}): {top_regional_profit["NetProfit"]}", className="e3_list"),
                html.Li(f"Eficiencia de costos ({top_cost_efficiency["SalesChannel"]}): {top_cost_efficiency["CostPerOrder"]}", className="e3_list")
            ])
        ]),
        html.Div(id="data_3", className="e3_children", children=[
            html.H2("Clientes", style={"font-size":"1.15em","color":"green","font-family":"sans-serif"}),
            html.P(f"Promedio (AOV): {company_wide_aov_baseline}", className="e3_mean", style={"color":"green"}),
            html.Ul(className="e3_ul",style={"color":"green"}, children=[
                html.Li(f"Total gastado ({top_monetary_customer["CustomerID"]}): {top_monetary_customer["TotalSpend"]}", className="e3_list"),
                html.Li(f"Frecuencia ({top_frequency_customer["CustomerID"]}): {top_frequency_customer["TotalOrders"]}", className="e3_list"),
                html.Li(f"Valor promedio de órden ({top_ticket_customer["CustomerID"]}): {top_ticket_customer["AverageOrderValue"]}", className="e3_list")
            ])
        ])
    ]),
    html.Div(id="dropdown_2_div", className="e3_div_dropdown", children=[
        dcc.Dropdown(id="dropdown_category", className="e3_dropdown",
                    options=df_profability["Category"].tolist(),
                    value=df_profability["Category"].iloc[0],
                    multi=False,
                    clearable=False),
        dcc.Dropdown(id="dropdown_sales_channel", className="e3_dropdown",
                    options=df_territory["SalesChannel"].tolist(),
                    value=df_territory["SalesChannel"].iloc[0],
                    multi=False,
                    clearable=False),
        dcc.Dropdown(id="dropdown_customer", className="e3_dropdown",
                    options=df_customers["CustomerID"].tolist(),
                    value=df_customers["CustomerID"].iloc[0],
                    multi=False,
                    clearable=False)
    ]),
    dcc.Graph(id="figure-2",figure={})
])

@app.callback(
    [Output(component_id="figure-1", component_property="figure"),
    Output(component_id="dropdown_category", component_property="style"),
    Output(component_id="dropdown_sales_channel", component_property="style"),
    Output(component_id="dropdown_customer", component_property="style"),
    Output(component_id="figure-2", component_property="figure")],
    [Input(component_id="dropdown", component_property="value"),
    Input(component_id="dropdown_category", component_property="value"),
    Input(component_id="dropdown_sales_channel", component_property="value"),
    Input(component_id="dropdown_customer" component_property="value")]
)

def update_dashboard(slct_data, slct_category, slct_sales_channel, slct_customer):

    category_style = {"position":"absolute","top":"0","left":"0"}
    sales_channel_style = {"position":"absolute","top":"0","left":"0"}
    customer_style = {"position":"absolute","top":"0","left":"0"}

    # if slct_data == "Category":


    # elif slct_data == "Country":


    # elif slct_data == "CustomerID":


    return figure_1, category_style, sales_channel_style, customer_style, figure_2

    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050)) 
    app.run_server(host='0.0.0.0', port=port)
