"""
洛克菲勒家族数据收集模块
用于收集和整理洛克菲勒家族成员信息及关系
"""

import pandas as pd
import networkx as nx
import json
import os

# 创建数据目录
os.makedirs('数据', exist_ok=True)

# 洛克菲勒家族主要成员数据
rockefeller_members = [
    {
        "id": 1,
        "name": "约翰·戴维森·洛克菲勒",
        "english_name": "John Davison Rockefeller",
        "birth_year": 1839,
        "death_year": 1937,
        "role": "家族创始人，标准石油公司创始人",
        "parent_ids": [],
        "children_ids": [2, 3, 4, 5, 6],
        "spouse": "劳拉·斯佩尔曼·洛克菲勒 (Laura Spelman Rockefeller)",
        "achievements": "创建标准石油公司，成为美国历史上第一位亿万富翁，建立洛克菲勒基金会",
        "bio": "约翰·戴维森·洛克菲勒出生于纽约州里奇福德，他在石油业建立起了商业帝国，创办了标准石油公司。到19世纪末，他控制了美国90%以上的炼油业务。晚年致力于慈善事业。"
    },
    {
        "id": 2,
        "name": "伊丽莎白·洛克菲勒",
        "english_name": "Elizabeth Rockefeller",
        "birth_year": 1866,
        "death_year": 1906,
        "role": "约翰·D·洛克菲勒长女",
        "parent_ids": [1],
        "children_ids": [],
        "spouse": "Charles Augustus Strong",
        "achievements": "慈善家",
        "bio": "伊丽莎白是约翰·D·洛克菲勒的长女，早年接受教育后投身慈善事业。"
    },
    {
        "id": 3,
        "name": "艾达·洛克菲勒",
        "english_name": "Alta Rockefeller",
        "birth_year": 1871,
        "death_year": 1962,
        "role": "约翰·D·洛克菲勒次女",
        "parent_ids": [1],
        "children_ids": [],
        "spouse": "Ezra Parmalee Prentice",
        "achievements": "慈善家",
        "bio": "艾达是约翰·D·洛克菲勒的次女，她也积极参与家族的慈善事业。"
    },
    {
        "id": 4,
        "name": "约翰·戴维森·洛克菲勒二世",
        "english_name": "John Davison Rockefeller Jr.",
        "birth_year": 1874,
        "death_year": 1960,
        "role": "约翰·D·洛克菲勒独子，家族事业继承人",
        "parent_ids": [1],
        "children_ids": [7, 8, 9, 10, 11, 12],
        "spouse": "Abby Aldrich Rockefeller",
        "achievements": "扩大洛克菲勒基金会，资助联合国总部建设，建设洛克菲勒中心",
        "bio": "小约翰·D·洛克菲勒在父亲的遗产基础上扩大了家族的慈善事业，他帮助建立了纽约的洛克菲勒中心，并对联合国总部的建设提供了资金支持。"
    },
    {
        "id": 5,
        "name": "埃迪丝·洛克菲勒",
        "english_name": "Edith Rockefeller",
        "birth_year": 1872,
        "death_year": 1932,
        "role": "约翰·D·洛克菲勒三女",
        "parent_ids": [1],
        "children_ids": [],
        "spouse": "Harold Fowler McCormick",
        "achievements": "慈善家，芝加哥歌剧院资助人",
        "bio": "埃迪丝是洛克菲勒家族的一员，她嫁给了国际收割机公司(International Harvester)的继承人哈罗德·麦考密克。"
    },
    {
        "id": 6,
        "name": "威廉·洛克菲勒",
        "english_name": "William Rockefeller",
        "birth_year": 1841,
        "death_year": 1922,
        "role": "约翰·D·洛克菲勒的弟弟，合作伙伴",
        "parent_ids": [],
        "children_ids": [],
        "spouse": "Almira Geraldine Goodsell",
        "achievements": "与兄长共同创建标准石油公司",
        "bio": "威廉·洛克菲勒是约翰·D·洛克菲勒的弟弟，他与兄长一起创建了标准石油公司，并在公司担任重要角色。"
    },
    {
        "id": 7,
        "name": "约翰·戴维森·洛克菲勒三世",
        "english_name": "John Davison Rockefeller III",
        "birth_year": 1906,
        "death_year": 1978,
        "role": "约翰·D·洛克菲勒二世长子",
        "parent_ids": [4],
        "children_ids": [],
        "spouse": "Blanchette Ferry Hooker",
        "achievements": "创建亚洲协会，人口理事会和林肯中心",
        "bio": "约翰·D·洛克菲勒三世专注于艺术和慈善事业，他建立了林肯表演艺术中心，并创建了人口理事会。"
    },
    {
        "id": 8,
        "name": "纳尔逊·奥尔德里奇·洛克菲勒",
        "english_name": "Nelson Aldrich Rockefeller",
        "birth_year": 1908,
        "death_year": 1979,
        "role": "政治家，纽约州州长，美国副总统",
        "parent_ids": [4],
        "children_ids": [],
        "spouse": "Mary Todhunter Clark, Margaretta Large Fitler",
        "achievements": "担任纽约州州长(1959-1973)，美国副总统(1974-1977)",
        "bio": "纳尔逊·洛克菲勒是美国著名政治家，曾四次当选纽约州州长，并担任福特政府的副总统。他也是一位著名的艺术收藏家。"
    },
    {
        "id": 9,
        "name": "劳伦斯·洛克菲勒",
        "english_name": "Laurance Rockefeller",
        "birth_year": 1910,
        "death_year": 2004,
        "role": "风险投资家，环保主义者",
        "parent_ids": [4],
        "children_ids": [],
        "spouse": "Mary French",
        "achievements": "环保主义先驱，创建多个国家公园，风险投资先驱",
        "bio": "劳伦斯·洛克菲勒是一位风险投资家和环保主义者，他投资了许多科技企业，同时也致力于环境保护，帮助建立了多个国家公园。"
    },
    {
        "id": 10,
        "name": "温思罗普·洛克菲勒",
        "english_name": "Winthrop Rockefeller",
        "birth_year": 1912,
        "death_year": 1973,
        "role": "政治家，阿肯色州州长",
        "parent_ids": [4],
        "children_ids": [],
        "spouse": "Jievute Paulekiute, Jeannette Edris",
        "achievements": "担任阿肯色州州长(1967-1971)",
        "bio": "温思罗普·洛克菲勒移居阿肯色州后成为当地政治领袖，他是该州第一位共和党州长，推动了该州的经济发展和民权改革。"
    },
    {
        "id": 11,
        "name": "戴维·洛克菲勒",
        "english_name": "David Rockefeller",
        "birth_year": 1915,
        "death_year": 2017,
        "role": "银行家，大通曼哈顿银行董事长",
        "parent_ids": [4],
        "children_ids": [],
        "spouse": "Margaret McGrath",
        "achievements": "担任大通曼哈顿银行董事长，建立三边委员会，国际活动家",
        "bio": "戴维·洛克菲勒是洛克菲勒家族中最长寿的成员，他担任大通曼哈顿银行的董事长，积极参与国际政治和经济事务，创建了三边委员会。"
    },
    {
        "id": 12,
        "name": "艾比·洛克菲勒·莫兹",
        "english_name": "Abby Rockefeller Mauzé",
        "birth_year": 1903,
        "death_year": 1976,
        "role": "慈善家",
        "parent_ids": [4],
        "children_ids": [],
        "spouse": "David M. Milton, Jean Mauzé",
        "achievements": "活跃于慈善事业",
        "bio": "艾比是约翰·D·洛克菲勒二世的长女，她活跃于家族的慈善事业中。"
    }
]

# 将数据保存为JSON
with open('数据/洛克菲勒家族成员.json', 'w', encoding='utf-8') as f:
    json.dump(rockefeller_members, f, ensure_ascii=False, indent=4)

# 创建成员DataFrame
members_df = pd.DataFrame(rockefeller_members)
members_df.to_csv('数据/洛克菲勒家族成员.csv', index=False, encoding='utf-8')

print("洛克菲勒家族数据已保存。")

# 家族关系数据
relationships = []
for member in rockefeller_members:
    for child_id in member.get('children_ids', []):
        relationships.append({
            'source': member['id'],
            'target': child_id,
            'type': 'parent-child'
        })

# 将关系数据保存为CSV
relationships_df = pd.DataFrame(relationships)
relationships_df.to_csv('数据/洛克菲勒家族关系.csv', index=False, encoding='utf-8')

print("洛克菲勒家族关系数据已保存。")
