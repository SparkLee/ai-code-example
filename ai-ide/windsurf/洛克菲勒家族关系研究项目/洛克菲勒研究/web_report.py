"""
洛克菲勒家族关系研究项目 - Web报告
使用Dash创建交互式Web报告，展示洛克菲勒家族关系网络
"""

import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import networkx as nx
import pandas as pd
import json
import os
from pathlib import Path

# 确保目录存在
data_dir = Path('数据')
output_dir = Path('结果')
os.makedirs(data_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# 检查数据是否存在，如果不存在则运行数据分析
if not (output_dir / '家族网络数据.json').exists():
    print("数据不存在，正在运行数据分析...")
    try:
        import 数据分析
        # 运行数据分析
        数据分析.main()
    except Exception as e:
        print(f"运行数据分析时出错: {e}")
        print("尝试先运行数据收集...")
        import 数据收集
        import 数据分析
        数据分析.main()

# 加载数据
try:
    with open(output_dir / '家族网络数据.json', 'r', encoding='utf-8') as f:
        network_data = json.load(f)
    
    with open(data_dir / '洛克菲勒家族成员.json', 'r', encoding='utf-8') as f:
        members_data = json.load(f)
except FileNotFoundError:
    print("无法找到必要的数据文件，请先运行数据收集和数据分析脚本。")
    exit(1)

# 创建Dash应用
app = dash.Dash(__name__, 
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                title="洛克菲勒家族关系研究")

# 应用样式
app.layout = html.Div([
    html.Div([
        html.H1("洛克菲勒家族关系研究", className="header-title"),
        html.P("探索洛克菲勒家族的关系网络与历史影响", className="header-description"),
    ], className="header"),
    
    html.Div([
        html.Div([
            html.H2("家族网络图"),
            dcc.Graph(id="family-network-graph", style={"height": "700px"}),
            html.P("这个网络图展示了洛克菲勒家族主要成员之间的关系。点击节点可查看详细信息。", className="description"),
        ], className="card"),
        
        html.Div([
            html.H2("家族成员详情"),
            html.Div(id="member-details", children=[
                html.P("点击网络图中的节点查看成员详情", className="instruction")
            ]),
        ], className="card"),
    ], className="row"),
    
    html.Div([
        html.Div([
            html.H2("家族时间线"),
            dcc.Graph(id="family-timeline", style={"height": "400px"}),
            html.P("这个时间线展示了洛克菲勒家族主要成员的生平时间范围。", className="description"),
        ], className="card full-width"),
    ], className="row"),
    
    html.Div([
        html.H2("洛克菲勒家族背景"),
        html.Div([
            html.P([
                "洛克菲勒家族是美国最具影响力的家族之一，由约翰·戴维森·洛克菲勒(John D. Rockefeller)创立。",
                "约翰·D·洛克菲勒于19世纪创建了标准石油公司(Standard Oil)，成为美国历史上第一位亿万富翁。",
                "家族成员在商业、政治、慈善和艺术等领域产生了深远影响。洛克菲勒基金会是世界上最早的大型私人基金会之一，",
                "资助了医学研究、教育和国际事务等众多领域。"
            ]),
            html.P([
                "家族第二代中，约翰·D·洛克菲勒二世扩大了家族的慈善事业，资助了联合国总部的建设和洛克菲勒中心的开发。",
                "第三代成员在多个领域取得成就：纳尔逊·洛克菲勒担任纽约州州长和美国副总统；",
                "劳伦斯·洛克菲勒成为风险投资先驱和环保主义者；戴维·洛克菲勒领导大通曼哈顿银行并创建三边委员会。"
            ]),
        ], className="text-content"),
    ], className="card full-width"),
    
    html.Footer([
        html.P("洛克菲勒家族关系研究项目 - 数据分析报告"),
        html.P("© 2025 - 使用Python、Pandas、NetworkX和Dash创建")
    ])
], className="container")

# 添加CSS样式
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
                margin: 0;
                background-color: #f5f7fa;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background-color: #1c4587;
                color: white;
                border-radius: 8px;
            }
            .header-title {
                margin: 0;
                font-size: 2.5em;
            }
            .header-description {
                font-size: 1.2em;
                opacity: 0.9;
            }
            .row {
                display: flex;
                flex-wrap: wrap;
                margin: 0 -10px 20px;
            }
            .card {
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                padding: 20px;
                margin: 10px;
                flex: 1;
                min-width: 300px;
            }
            .full-width {
                flex-basis: 100%;
            }
            .text-content {
                line-height: 1.6;
            }
            .instruction {
                color: #666;
                font-style: italic;
            }
            .description {
                color: #666;
                font-size: 0.9em;
                margin-top: 10px;
            }
            footer {
                text-align: center;
                margin-top: 30px;
                padding: 20px;
                color: #666;
                font-size: 0.9em;
            }
            /* 成员详情样式 */
            .member-card {
                background-color: #f8f9fa;
                border-left: 5px solid #1c4587;
                padding: 15px;
                margin-top: 10px;
            }
            .member-name {
                font-size: 1.5em;
                margin: 0 0 5px 0;
                color: #1c4587;
            }
            .member-years {
                font-style: italic;
                color: #666;
            }
            .member-role {
                font-weight: bold;
                margin: 10px 0;
            }
            .member-bio {
                line-height: 1.5;
            }
            .member-achievements {
                background-color: #eaf0f7;
                padding: 10px;
                border-radius: 5px;
                margin-top: 10px;
            }
            .member-achievements-title {
                font-weight: bold;
                margin-bottom: 5px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# 回调函数：创建家族网络图
@app.callback(
    Output("family-network-graph", "figure"),
    Input("family-network-graph", "id")
)
def create_network_graph(_):
    # 创建网络图
    nodes = network_data["nodes"]
    links = network_data["links"]
    
    # 创建网络
    G = nx.DiGraph()
    
    # 添加节点
    for node in nodes:
        G.add_node(node["id"], **node)
    
    # 添加边
    for link in links:
        G.add_edge(link["source"], link["target"])
    
    # 使用spring布局
    pos = nx.spring_layout(G, seed=42)
    
    # 创建节点跟踪
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_data = G.nodes[node]
        node_text.append(f"{node_data['name']} ({node_data['birth_year']}-{node_data['death_year']})")
        
        # 节点大小基于角色重要性
        if "创始人" in node_data['role'] or "家族事业继承人" in node_data['role']:
            node_size.append(30)
            node_color.append("#1c4587")  # 深蓝色
        elif "政治家" in node_data['role'] or "银行家" in node_data['role'] or "州长" in node_data['role']:
            node_size.append(25)
            node_color.append("#4285f4")  # 蓝色
        else:
            node_size.append(20)
            node_color.append("#7baaf7")  # 浅蓝色
    
    # 创建边跟踪
    edge_x = []
    edge_y = []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    # 创建边跟踪对象
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # 创建节点跟踪对象
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        textfont=dict(
            family="Microsoft YaHei",
            size=10,
        ),
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            line=dict(width=2, color='white')
        ),
        customdata=[node for node in G.nodes()]
    )
    
    # 创建图形
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="洛克菲勒家族关系网络",
            titlefont=dict(size=16, family="Microsoft YaHei"),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            annotations=[
                dict(
                    text="家族关系：箭头方向表示从父母指向子女",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.01, y=-0.01,
                    font=dict(size=12, family="Microsoft YaHei")
                )
            ]
        )
    )
    
    return fig

# 回调函数：创建家族时间线
@app.callback(
    Output("family-timeline", "figure"),
    Input("family-timeline", "id")
)
def create_family_timeline(_):
    # 准备数据
    members = sorted(members_data, key=lambda x: x["birth_year"])
    
    # 创建时间线
    fig = go.Figure()
    
    # 添加每个成员的时间线
    for i, member in enumerate(members):
        fig.add_trace(go.Scatter(
            x=[member["birth_year"], member["death_year"]],
            y=[i, i],
            mode="lines+markers+text",
            line=dict(width=10, color="#4285f4"),
            text=[f"{member['name']} 出生", f"{member['name']} 逝世"],
            textposition=["bottom center", "bottom center"],
            textfont=dict(
                family="Microsoft YaHei",
                size=10,
            ),
            name=member["name"],
            hoverinfo="text",
            hovertext=f"{member['name']} ({member['birth_year']}-{member['death_year']})<br>{member['role']}"
        ))
    
    # 更新布局
    fig.update_layout(
        title="洛克菲勒家族成员时间线",
        xaxis=dict(
            title="年份",
            type="linear",
            showgrid=True,
            gridwidth=1,
            gridcolor="#eeeeee",
            range=[1830, 2030]
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=400,
        margin=dict(l=20, r=20, t=50, b=50),
        hovermode="closest"
    )
    
    return fig

# 回调函数：显示成员详情
@app.callback(
    Output("member-details", "children"),
    Input("family-network-graph", "clickData")
)
def display_member_details(clickData):
    if clickData is None:
        return [html.P("点击网络图中的节点查看成员详情", className="instruction")]
    
    # 获取点击的节点ID
    node_id = clickData["points"][0]["customdata"]
    
    # 查找成员信息
    member = None
    for m in members_data:
        if str(m["id"]) == str(node_id):
            member = m
            break
    
    if member is None:
        return [html.P("未找到成员信息", className="instruction")]
    
    # 生成成员详情
    return [
        html.Div([
            html.H3(f"{member['name']} ({member['english_name']})", className="member-name"),
            html.P(f"{member['birth_year']} - {member['death_year']}", className="member-years"),
            html.P(member['role'], className="member-role"),
            html.P(member['bio'], className="member-bio"),
            html.Div([
                html.P("主要成就:", className="member-achievements-title"),
                html.P(member['achievements'])
            ], className="member-achievements"),
            html.P(f"配偶: {member['spouse']}")
        ], className="member-card")
    ]

# 运行应用
if __name__ == '__main__':
    # 创建requirements文件
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write("dash==2.14.0\nplotly==5.18.0\nnetworkx==3.2.1\npandas==2.1.2\nnumpy==1.26.1")
    
    print("启动Web报告服务器，请在浏览器中访问 http://127.0.0.1:8050/")
    app.run_server(debug=True, port=8050)
