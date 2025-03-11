"""
洛克菲勒家族关系网络分析模块
用于分析洛克菲勒家族成员之间的关系和网络结构
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import json
import os
from pathlib import Path

# 确保数据目录存在
data_dir = Path('数据')
os.makedirs(data_dir, exist_ok=True)
output_dir = Path('结果')
os.makedirs(output_dir, exist_ok=True)

def load_family_data():
    """加载家族成员和关系数据"""
    # 检查文件是否存在，如果不存在则先运行数据收集脚本
    if not (data_dir / '洛克菲勒家族成员.json').exists():
        print("数据文件不存在，正在运行数据收集脚本...")
        import 数据收集
    
    # 加载成员数据
    with open(data_dir / '洛克菲勒家族成员.json', 'r', encoding='utf-8') as f:
        members = json.load(f)
    
    # 加载关系数据
    relationships_df = pd.read_csv(data_dir / '洛克菲勒家族关系.csv')
    
    return members, relationships_df

def create_family_network(members, relationships_df):
    """创建家族关系网络"""
    G = nx.DiGraph()
    
    # 添加节点
    for member in members:
        G.add_node(
            member['id'], 
            name=member['name'],
            english_name=member['english_name'],
            birth_year=member['birth_year'],
            death_year=member['death_year'],
            role=member['role']
        )
    
    # 添加边（关系）
    for _, rel in relationships_df.iterrows():
        G.add_edge(rel['source'], rel['target'], relationship_type='parent-child')
    
    return G

def analyze_network(G):
    """分析家族网络的特性"""
    results = {}
    
    # 计算基本网络指标
    results['节点数量'] = G.number_of_nodes()
    results['关系数量'] = G.number_of_edges()
    
    # 计算度中心性
    degree_centrality = nx.degree_centrality(G)
    # 将度中心性与成员名称对应
    degree_centrality_named = {}
    for node_id, centrality in degree_centrality.items():
        node_name = G.nodes[node_id]['name']
        degree_centrality_named[node_name] = centrality
    
    results['度中心性'] = degree_centrality_named
    
    # 计算中介中心性
    betweenness_centrality = nx.betweenness_centrality(G)
    betweenness_centrality_named = {}
    for node_id, centrality in betweenness_centrality.items():
        node_name = G.nodes[node_id]['name']
        betweenness_centrality_named[node_name] = centrality
    
    results['中介中心性'] = betweenness_centrality_named
    
    # 寻找最具影响力的家族成员（基于中心性）
    influential_members = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)
    results['最具影响力的成员'] = []
    for member_id, _ in influential_members[:3]:
        for member in members:
            if member['id'] == member_id:
                results['最具影响力的成员'].append({
                    'name': member['name'],
                    'role': member['role'],
                    'children_count': len(member.get('children_ids', []))
                })
    
    return results

def visualize_family_network(G, members):
    """可视化家族关系网络"""
    plt.figure(figsize=(12, 10))
    
    # 使用spring布局
    pos = nx.spring_layout(G, seed=42)
    
    # 创建节点标签
    labels = {}
    for member in members:
        member_id = member['id']
        labels[member_id] = f"{member['name']}\n({member['birth_year']}-{member['death_year']})"
    
    # 绘制网络
    nx.draw_networkx_nodes(G, pos, node_size=800, node_color='skyblue')
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_family='SimHei')
    
    plt.title("洛克菲勒家族关系网络", fontsize=16, fontfamily='SimHei')
    plt.axis('off')
    
    # 保存图像
    plt.savefig(output_dir / '洛克菲勒家族关系网络.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"关系网络图已保存到 {output_dir / '洛克菲勒家族关系网络.png'}")

def export_network_data(G):
    """导出网络数据为JSON格式，供Web可视化使用"""
    nodes = []
    for node in G.nodes(data=True):
        node_id, data = node
        nodes.append({
            'id': str(node_id),
            'name': data['name'],
            'english_name': data['english_name'],
            'birth_year': data['birth_year'],
            'death_year': data['death_year'],
            'role': data['role']
        })
    
    links = []
    for edge in G.edges():
        source, target = edge
        links.append({
            'source': str(source),
            'target': str(target)
        })
    
    network_data = {
        'nodes': nodes,
        'links': links
    }
    
    with open(output_dir / '家族网络数据.json', 'w', encoding='utf-8') as f:
        json.dump(network_data, f, ensure_ascii=False, indent=2)
    
    print(f"网络数据已导出到 {output_dir / '家族网络数据.json'}")

if __name__ == "__main__":
    # 加载数据
    members, relationships_df = load_family_data()
    
    # 创建网络
    G = create_family_network(members, relationships_df)
    
    # 分析网络
    analysis_results = analyze_network(G)
    
    # 保存分析结果
    with open(output_dir / '网络分析结果.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    
    print(f"网络分析结果已保存到 {output_dir / '网络分析结果.json'}")
    
    # 可视化网络
    visualize_family_network(G, members)
    
    # 导出网络数据
    export_network_data(G)
