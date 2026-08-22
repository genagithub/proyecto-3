import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import html, dcc
from dash.dependencies import Input, Output


with sqlite3.connect("data/AdventureWorks.db") as conn:

    query_category = """
    WITH LinearTransform AS (
    SELECT sod.SalesOrderID,
        sod.ProductID,
        p.Name AS Product,
        cat.Name AS Category,
        sod.OrderQty AS Quantity,
        sod.LineTotal AS GrossIncome,
        (sod.OrderQty * p.StandardCost) AS ProductionCost,
        (sod.LineTotal * 0.05) AS FreightCost,
        (sod.LineTotal * 0.08) AS TaxCost
    FROM SalesOrderDetail sod
    JOIN Product p ON sod.ProductID = p.ProductID
    JOIN ProductCategory cat ON p.ProductCategoryID = cat.ProductCategoryID
    )
    SELECT Category,
    SUM(Quantity) AS TotalQuantity,
    ROUND(SUM(GrossIncome), 2) AS TotalGrossIncome,
    ROUND(SUM(ProductionCost), 2) AS TotalProductionCost,
    ROUND(SUM(FregihtCost), 2) AS TotalFreightCost,
    ROUND(SUM(TaxCost), 2) AS TotalTaxCost,
    ROUND(SUM(GrossIncome - ProductionCost - FregihtCost - TaxCost), 2) AS TotalNetProfit,
    ROUND((SUM(GrossIncome - ProductionCost - FregihtCost - TaxCost) / SUM(GrossIncome)) * 100, 2) AS NetMarginPercentage
    FROM LinearTransform
    GROUP BY Category
    ORDER BY TotalNetProfit DESC;
    """

    df_category = pd.read_sql_query(query_category, conn)

    query_sales_channel = """
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

    df_sales_channel = pd.read_sql_query(query_sales_channel, conn)

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

total_company_revenue = df_category["TotalGrossIncome"].sum()
total_company_net_profit = df_category["TotalNetProfit"].sum()
company_wide_net_margin_baseline = (total_company_net_profit / total_company_revenue) * 100

top_volume_row = df_category.sort_values(by="TotalQuantity", ascending=False).iloc[0]
global_total_units = df_category["TotalQuantity"].sum()
top_volume_market_share = (top_volume_row["TotalQuantity"] / global_total_units) * 100
top_revenue_row = df_category.sort_values(by="TotalGrossIncome", ascending=False).iloc[0]
top_efficiency_row = df_category.sort_values(by="NetMarginPercentage", ascending=False).iloc[0]

total_company_orders = df_sales_channel["TotalOrders"].sum()
total_company_costs = df_sales_channel["MonthlyCosts"].sum()
company_cost_per_order_baseline = total_company_costs / total_company_orders

top_regional_volume = df_sales_channel.sort_values(by="TotalOrders", ascending=False).iloc[0]
top_regional_profit = df_sales_channel.sort_values(by="NetProfit", ascending=False).iloc[0]
df_sales_channel["CostPerOrder"] = df_sales_channel["MonthlyCosts"] / df_sales_channel["TotalOrders"]
top_cost_efficiency = df_sales_channel.sort_values(by="CostPerOrder", ascending=True).iloc[0]

total_spend_global = df_customers["TotalSpend"].sum()
total_orders_global = df_customers["TotalOrders"].sum()
company_wide_aov_baseline = total_spend_global / total_orders_global

top_monetary_customer = df_customers.sort_values(by="TotalSpend", ascending=False).iloc[0]
top_frequency_customer = df_customers.sort_values(by="TotalOrders", ascending=False).iloc[0]
top_ticket_customer = df_customers.sort_values(by="AverageOrderValue", ascending=False).iloc[0]

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(id="body", className="e3_body", children=[
    html.H1("Panel de control financiero mensual - AdventureWorks", className="e3_title", style={"margin-bottom":"50px"}),
    html.Div(id="dropdown_div", className="e3_div_dropdown", children=[
            dcc.Dropdown(id="dropdown", className="e3_dropdown", style={"position":"absolute","top":"0","left":"0"},
                        options = [
                            {"label":"Categorías","value":"Category"},
                            {"label":"Canal de ventas","value":"SalesChannel"},
                            {"label":"Clientes","value":"CustomerID"}
                        ],
                        value="name",
                        multi=False,
                        clearable=False)
    ]),
    dcc.Graph(id="figure-1", style={"width":"80%","margin-bottom":"25px"}, figure={}),
    html.H2("Palancas de negocio", className="e3_title"),
    html.Div(className="e3_container", children=[
        html.Div(id="data_1", className="e3_children", children=[
            html.H2("Categorías", className="e3_h2"),
            html.P(f"Promedio (Margen Neto): {round(company_wide_net_margin_baseline, 2)}%", className="e3_mean"),
            html.Ul(className="e3_ul", children=[
                html.Li(f"Volumen de ventas ({top_volume_row["Category"]}): {round(top_volume_market_share)}", className="e3_list"),
                html.Li(f"Ingresos Brutos ({top_revenue_row["Category"]}): ${top_revenue_row["TotalGrossIncome"]}", className="e3_list"),
                html.Li(f"Margen Neto ({top_efficiency_row["Category"]}): {top_efficiency_row["NetMarginPercentage"]}%", className="e3_list")
            ])
        ]),
        html.Div(id="data_2", className="e3_children", children=[
            html.H2("Canal de ventas", className="e3_h2"),
            html.P(f"Promedio (Costo por órden): ${round(company_cost_per_order_baseline, 2)}", className="e3_mean"),
            html.Ul(className="e3_ul", children=[
                html.Li(f"Volumen de órdenes ({top_regional_volume["SalesChannel"]}): {top_regional_volume["TotalOrders"]}", className="e3_list"),
                html.Li(f"Ganancia Neta ({top_regional_profit["SalesChannel"]}): ${top_regional_profit["NetProfit"]}", className="e3_list"),
                html.Li(f"Costo por órden ({top_cost_efficiency["SalesChannel"]}): ${round(top_cost_efficiency["CostPerOrder"], 2)}", className="e3_list")
            ])
        ]),
        html.Div(id="data_3", className="e3_children", children=[
            html.H2("Clientes", className="e3_h2"),
            html.P(f"Promedio (AOV): ${round(company_wide_aov_baseline, 2)}", className="e3_mean"),
            html.Ul(className="e3_ul", children=[
                html.Li(f"Gasto total ({top_monetary_customer["CustomerID"]}): ${top_monetary_customer["TotalSpend"]}", className="e3_list"),
                html.Li(f"Frecuencia ({top_frequency_customer["CustomerID"]}): {top_frequency_customer["TotalOrders"]}", className="e3_list"),
                html.Li(f"AOV ({top_ticket_customer["CustomerID"]}): ${top_ticket_customer["AverageOrderValue"]}", className="e3_list")
            ])
        ])
    ]),
    html.Div(id="dropdown_2_div", className="e3_div_dropdown", children=[
        dcc.Dropdown(id="dropdown_category", className="e3_dropdown",
                    options=df_category["Category"].tolist(),
                    value=df_category["Category"].iloc[0],
                    multi=False,
                    clearable=False),
        dcc.Dropdown(id="dropdown_sales_channel", className="e3_dropdown",
                    options=df_sales_channel["SalesChannel"].tolist(),
                    value=df_sales_channel["SalesChannel"].iloc[0],
                    multi=False,
                    clearable=False),
        dcc.Dropdown(id="dropdown_customer", className="e3_dropdown",
                    options=df_customers["CustomerID"].tolist(),
                    value=df_customers["CustomerID"].iloc[0],
                    multi=False,
                    clearable=False)
    ]),
    dcc.Graph(id="figure-2", style={"width":"80%","margin-bottom":"25px"}, figure={})
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
    Input(component_id="dropdown_customer", component_property="value")]
)


def update_dashboard(slct_data, slct_category, slct_sales_channel, slct_customer):

    category_style = {"position":"absolute","top":"0","left":"0"}
    sales_channel_style = {"position":"absolute","top":"0","left":"0"}
    customer_style = {"position":"absolute","top":"0","left":"0"}

    figure_1 = go.Figure()
    figure_2 = go.Figure()

    if slct_data == "Category":

        category_style["zIndex"] = 5

        figure_1 = px.bar(
            df_category,
            x="Category",
            y=["TotalGrossIncome", "TotalNetProfit"],
            barmode="group",
            title="Ingreso Bruto vs Ganancia Neta",
            labels={"TotalGrossIncome": "Ingreso Bruto ($)", "TotalNetProfit": "Ganancia Neta ($)", "Category": "Categoría"},
            template="plotly_dark"
        )

        df_filtered = df_category[df_category["Category"] == slct_category]
        row = df_filtered.iloc[0]

        figure_2 = px.pie(
              names=["Costo de Producción", "Costo de Flete", "Costo de Impuesto", "Ganancia Neta"],
              values=[row["TotalProductionCost"], row["TotalFreightCost"], row["TotalTaxCost"], row["TotalNetProfit"]],
              title=f"Descomposición Financiera: {slct_category} (Margen Neto de Junio: {row["NetMarginPercentage"]:.1f}%)",
              template="plotly_dark",
              hole=0.4,
              color_discrete_sequence=px.colors.qualitative.Pastel
        )

    elif slct_data == "SalesChannel":

        sales_channel_style["zIndex"] = 5

        figure_1 = px.bar(
            df_sales_channel,
            x="SalesChannel",
            y="MonthlySales",
            color="Country",
            barmode="group",
            title="Ventas del Mes por Canal y Territorio",
            labels={"MonthlySales": "Ingreso ($)", "SalesChannel": "Canal de Ventas"},
            template="plotly_dark"
        )

        df_filtered = df_sales_channel[df_sales_channel["SalesChannel"] == slct_sales_channel]

        figure_2 = px.bar(
            df_filtered,
            x="Country",
            y="NetMarginPercentage",
            title=f"Eficiencia del Margen Neto por País para el Canal: {slct_sales_channel}",
            labels={"NetMarginPercentage": "Margen Neto (%)", "Country": "País"},
            template="plotly_dark"
        ).update_traces(marker_color="#34d399")

    elif slct_data == "CustomerID":

        customer_style["zIndex"] = 5

        figure_1 = px.bar(
            df_customers,
            x="CustomerID",
            y="TotalSpend",
            color="SalesChannel",
            title="Top 10 Clientes VIP por Gasto Total Acumulado",
            labels={"TotalSpend": "Gasto Total ($)", "CustomerID": "ID"},
            template="plotly_dark"
        )

        df_filtered = df_customers[df_customers["CustomerID"] == int(slct_customer)]
        row = df_filtered.iloc[0]

        figure_2 = px.bar(
              x=["Gasto Total", "Valor de Ticket Promedio (AOV)"],
              y= [row["TotalSpend"], row["AverageOrderValue"]],
              title=f"Perfil Financiero Individual del Cliente ID: {slct_customer}",
              labels={"x": "Métrica Comercial", "y": "Valor ($)"},
              template="plotly_dark"
        ).update_traces(marker_color="#10b981")

    else:
        figure_2 = go.Figure()

    return figure_1, category_style, sales_channel_style, customer_style, figure_2

    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050)) 
    app.run_server(host='0.0.0.0', port=port)
