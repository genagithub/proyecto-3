import sqlite3
import pandas as pd
import plotly.express as px
import dash
from dash import html, dcc
from dash.dependencies import Input, Output

with sqlite3.connect("northwind.db") as conn:

    first_queries = conn.cursor()

    first_queries.execute('''create view order_details_cash as
                         select OrderID, od.ProductID, Quantity, Price * Quantity as product_cash from OrderDetails od
                         join Products p on od.ProductID = p.ProductID;''')

    first_queries.execute('''create view products_revenue as
                         select p.ProductID, ProductName, sum(product_cash) as product_revenue, sum(Quantity) from order_details_cash odc
                         join Products p on p.ProductID = odc.ProductID
                         group by p.ProductID;''')

    first_queries.execute('''select * from products_revenue where product_revenue > (select avg(product_revenue) from products_revenue)
                         order by product_revenue desc''')

    df_products = pd.DataFrame(first_queries.fetchall())

    second_queries = conn.cursor()

    second_queries.execute('''create view orders_revenue as
                          select o.OrderID, sum(product_cash) as order_revenue, sum(Quantity) as total_quantity, EmployeeID from order_details_cash odc
                          join Orders o on o.OrderID = odc.OrderID
                          group by o.OrderID
                          order by order_revenue desc;''')

    second_queries.execute('select * from orders_revenue where order_revenue > (select avg(order_revenue) from orders_revenue)')

    df_orders = pd.DataFrame(second_queries.fetchall())

    third_queries = conn.cursor()

    third_queries.execute('''select e.EmployeeID, FirstName || " " || LastName, sum(order_revenue) as employee_revenue, sum(total_quantity) from Employees e
                         join orders_revenue o on o.EmployeeID = e.EmployeeID 
                         group by e.EmployeeID
                         order by employee_revenue''')


    df_employees = pd.DataFrame(third_queries.fetchall())

df_products.columns = ["product_id","product","product_revenue","total_quantity"]
df_orders.columns = ["order_id","order_revenue","total_quantity"]
df_orders.drop(3,axis=1,inplace=True)
df_orders["order_id"] = df_orders["order_id"].astype(str)
df_employees.columns = ["employee_id","name","employee_revenue","total_quantity"]

mean_products = df_products["product_revenue"].mean()
mean_orders = df_orders["order_revenue"].mean()
mean_employees = df_employees["employee_revenue"].mean()

best_product = df_products.iloc[0,:] 
best_order = df_orders.iloc[0,:] 
df_employees.sort_values(by="employee_revenue", ascending=False, inplace=True)
best_employee = df_employees.iloc[0,:] 

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(id="body",children=[
    html.Div(id="dropdown_div",className="e3_dropdown_div",children=[
            dcc.Dropdown(id="dropdown",className="e3_dropdown",
                        options = [
                            {"label":"Empleados","value":"name"},
                            {"label":"Productos","value":"product"},
                            {"label":"Órdenes","value":"order_id"}
                        ],
                        value="name",
                        multi=False,
                        clearable=False)
    ]),
    dcc.Graph(id="graph-1",figure={}),
    html.H1("Mayores ingresos",className="e3_title"),
    html.Div(className="e3_container",children=[
        html.Div(id="data_1",className="e3_children",style={"color":"blue"},children=[   
            html.H2("Productos",style={"font-size":"1.15em","color":"blue","font-family":"sans-serif"}),
            html.P(f"Promedio: {round(mean_products,1)}$",className="e3_mean",style={"color":"blue"}),         
            html.Ul(className="e3_ul",style={"color":"blue"},children=[
                html.Li(f"Producto: {best_product["product"]}",className="e3_list"),
                html.Li(f"Unidades vendidas: {best_product["total_quantity"]}",className="e3_list"),
                html.Li(f"Ingreso total: {best_product["product_revenue"]}$",className="e3_list")
            ])
        ]),
        html.Div(id="data_2",className="e3_children",children=[
            html.H2("Empleados",style={"font-size":"1.15em","color":"red","font-family":"sans-serif"}),
            html.P(f"Promedio: {round(mean_employees,1)}$",className="e3_mean",style={"color":"red"}),
            html.Ul(className="e3_ul",style={"color":"red"},children=[
                html.Li(f"Nombre: {best_employee["name"]}",className="e3_list"),
                html.Li(f"Unidades vendidas totales: {best_employee["total_quantity"]}",className="e3_list"),
                html.Li(f"Ingreso total: {best_employee["employee_revenue"]}$",className="e3_list")
            ])
        ]),
        html.Div(id="data_3",className="e3_children",children=[
            html.H2("Órdenes",style={"font-size":"1.15em","color":"green","font-family":"sans-serif"}),
            html.P(f"Promedio: {round(mean_orders,1)}$",className="e3_mean",style={"color":"green"}),
            html.Ul(className="e3_ul",style={"color":"green"},children=[
                html.Li(f"ID de órden: {best_order["order_id"]}",className="e3_list"),
                html.Li(f"Unidades vendidas totales: {best_order["total_quantity"]}",className="e3_list"),
                html.Li(f"Ingreso total: {best_order["order_revenue"]}$",className="e3_list")
            ])
        ]) 
    ]),
    html.Div(id="dropdown_2_div",className="e3_div_dropdown",children=[
        dcc.Dropdown(id="dropdown_employees",className="e3_dropdown",
                    options=df_employees["name"].tolist(),
                    value=df_employees["name"].iloc[0],
                    multi=False,
                    clearable=False),
        dcc.Dropdown(id="dropdown_products",className="e3_dropdown",
                    options=df_products["product"].tolist(),
                    value=df_products["product"].iloc[0],
                    multi=False,
                    clearable=False),
        dcc.Dropdown(id="dropdown_orders",className="e3_dropdown",
                    options=df_orders["order_id"].tolist(),
                    value=df_orders["order_id"].iloc[0],
                    multi=False,
                    clearable=False)
    ]),
    dcc.Graph(id="graph-2",figure={})
])

@app.callback(
    [Output(component_id="graph-1",component_property="figure"),
    Output(component_id="dropdown_employees",component_property="style"),
    Output(component_id="dropdown_products",component_property="style"),
    Output(component_id="dropdown_orders",component_property="style"),
    Output(component_id="graph-2",component_property="figure")],
    [Input(component_id="dropdown",component_property="value"),
    Input(component_id="dropdown_employees",component_property="value"),
    Input(component_id="dropdown_products",component_property="value"),
    Input(component_id="dropdown_orders",component_property="value")]
)

def update_graph(slct_data, slct_employee, slct_product, slct_order):
    
    employees_style = {"position":"absolute","top":"0","left":"0"}
    products_style = {"position":"absolute","top":"0","left":"0"}
    orders_style = {"position":"absolute","top":"0","left":"0"}
    
    if slct_data == "name":
        
        graph_1 = px.bar(df_employees, x=slct_data, y="employee_revenue", color_discrete_sequence=["red"], text_auto=".2s", title="Ingresos de empleados", labels=dict(name="Empleados", employee_revenue="Ingresos"))
        
        employees_style["zIndex"] = 5
        
        with sqlite3.connect("northwind.db") as conn:
            get_employee = conn.cursor()
            get_employee.execute(f'''select ProductName, sum(product_cash) from order_details_cash odc
                                 join Products p on p.ProductID = odc.ProductID
                                 join Orders o on o.OrderID = odc.OrderID join Employees e on o.EmployeeID = e.EmployeeID
                                 where e.EmployeeID = {employee}
                                 group by p.ProductID''')
            employee_products = pd.DataFrame(get_employee.fetchall())

        employee = df_employees.loc[df_employees["name"] == slct_employee, "employee_id"].values[0]
        employee_products.columns = ["product","revenue"]

        graph_2 = px.treemap(employee_products, path=["product"], values="revenue", color="revenue", color_continuous_scale="Viridis")
        graph_2.update_layout(title_text="Concentración de Ventas por Productos", coloraxis_colorbar_title_text="Ingresos")
                
    elif slct_data == "product":
        
        graph_1 = px.bar(df_products, x=slct_data, y="product_revenue", color_discrete_sequence=["blue"], text_auto=".2s", title="Ingresos de productos mayores al promedio", labels=dict(product="Productos", product_revenue="Ingresos"))
        graph_1.update_xaxes(tickangle=35, tickfont_size=8)
        
        products_style["zIndex"] = 5
        
        with sqlite3.connect("northwind.db") as conn:        
            get_product = conn.cursor()
            get_product.execute(f'''select OrderID,  sum(Quantity), sum(product_cash) from order_details_cash
                                where ProductID = {product}
                                group by OrderID''')
            product_orders = pd.DataFrame(get_product.fetchall())

        product = df_products.loc[df_products["product"] == slct_product, "product_id"].values[0]
        product_orders.columns = ["order_id","quantity","revenue"]

        graph_2 = px.treemap(product_orders, path=["order_id"], values="quantity", color="revenue", color_continuous_scale="Viridis")
        graph_2.update_layout(title_text="Distribución de Cantidad y Ingresos por Orden", coloraxis_colorbar_title_text="Ingresos")
        
    elif slct_data == "order_id":
        
        graph_1 = px.bar(df_orders, x=slct_data, y="order_revenue", color_discrete_sequence=["green"], title="Ingresos de órdenes mayores al promedio", labels=dict(order_id="Órdenes", order_revenue="Ingresos"))
        graph_1.update_xaxes(tickfont_size=9)
        
        orders_style["zIndex"] = 5
        
        with sqlite3.connect("northwind.db") as conn:        
            get_order = conn.cursor()
            get_order.execute(f'''select ProductName, sum(product_cash) from order_details_cash odc
                              join Products p on p.ProductID = odc.ProductID
                              where odc.OrderID = {order}
                              group by p.ProductID''')
            order_products = pd.DataFrame(get_order.fetchall())

        order = df_orders.loc[df_orders["order_id"] == slct_order, "order_id"].values[0]
        order_products.columns = ["product","revenue"]

        graph_2 = px.treemap(order_products, path=["product"], values="revenue", color="revenue", color_continuous_scale="Viridis")
        graph_2.update_layout(title_text="Concentración de Ventas por Productos", coloraxis_colorbar_title_text="Ingresos")
            
    return graph_1, employees_style, products_style, orders_style, graph_2    
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050)) 
    app.run_server(host='0.0.0.0', port=port)
