# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 22:30:20 2020

@author: wyhys
"""

import pandas as pd
from pyecharts.charts import Graph
from pyecharts import options as opts
import jieba
import jieba.posseg as pseg

# 进行数据处理
def deal_data():
    with open("红楼梦.txt", encoding='gb18030') as f:
        lines = f.readlines()   # 依次读取每行
    jieba.load_userdict("people") # 添加自定义词典
    renwu_data = pd.read_csv("people", header=-1)
    mylist = [k[0].split(" ")[0] for k in renwu_data.values.tolist()]
    tmpNames = []  # 缓存变量，保存每一段文字分词后得到的人物名称
    names = {}     # 保存人物，键为人物名称，值为该人物在全文中出现的次数
    relationships = {}  # 保存人物关系的有向边，键为有向边的起点，值为字典edge(edge的键为有向边的终点，值为有向边的权值)
    
    for line in lines:
        # 替换人物的常见别称为词典中的名称
        line.replace("宝二爷", "宝玉")
        line.replace("宝哥哥", "宝玉")
        line.replace("宝兄弟", "宝玉")
        line.replace("老祖宗", "贾母")
        line.replace("老太太", "贾母")
        line.replace("颦儿", "黛玉")
        line.replace("林姑娘", "黛玉") 
        line.replace("林妹妹", "黛玉") 
        line.replace("二奶奶", "凤姐") 
        line.replace("王熙凤", "凤姐") 
        line.replace("凤辣子", "凤姐") 
        line.replace("凤丫头", "凤姐")
        line.replace("宝姑娘", "宝钗")  
        line.replace("宝丫头", "宝钗")
        line.replace("宝姐姐", "宝钗") 
        line.replace("二妹妹", "迎春")  
        line.replace("三妹妹", "探春") 
        line.replace("四妹妹", "惜春") 
        line.replace("英莲", "香菱")        
        line.replace("贾妃", "元春")
        line.replace("李宫裁", "李纨")
        line.replace("可卿", "秦氏")
       
                                                  
        poss = pseg.cut(line)  # 分词，返回词性
        tmpNames.append([])    # 为本段增加一个人物列表
        for w in poss:
            # 当分词词性不为人名（nr）或长度<2时判定该分词不为人名
            if w.flag != 'nr' or len(w.word) != 2 or w.word not in mylist:
                continue
            tmpNames[-1].append(w.word) #添加人物名称
            # 如果人物名称不属于自定义词典则忽略不计
            if names.get(w.word) is None:
                names[w.word] = 0
            relationships[w.word] = {}
            names[w.word] += 1
    print(relationships)
    print(tmpNames)
    # 输出人物出现次数统计结果
    for name, times in names.items():
        print(name, times)
    # 出现在同一段落中的人物即被认为关系紧密，同时出现一次即关系权值增加1
    for name in tmpNames:
        for name1 in name:
            for name2 in name:
                if name1 == name2:
                    continue
                if relationships[name1].get(name2) is None:
                    relationships[name1][name2] = 1
                else:
                    relationships[name1][name2] += 1
    print(relationships)
    # 将数据写入relationship.csv，NameNode.csv进行存储
    # relationship.csv：人物关系表，包括首先出现的人物、随后出现的人物以及一同出现的次数
    with open("relationship.csv", "w", encoding='utf-8') as f:
        f.write("Source,Target,Weight\n")
        for name, edges in relationships.items():
            for v, w in edges.items():
                f.write(name + "," + v + "," + str(w) + "\n")
    # NameNode.csv：人物权重表，包括人物出现总次数
    with open("NameNode.csv", "w", encoding='utf-8') as f:
        f.write("ID,Label,Weight\n")
        for name, times in names.items():
            f.write(name + "," + name + "," + str(times) + "\n")

# 使用pyecharts作图
def deal_graph():
    # 读取文件中的元素为list形式
    relationship_data = pd.read_csv('relationship.csv')
    namenode_data = pd.read_csv('NameNode.csv')
    relationship_data_list = relationship_data.values.tolist()
    namenode_data_list = namenode_data.values.tolist()
    # 设置节点
    nodes = []
    for node in namenode_data_list:
        # 由于"宝玉"节点权重过大，为方便展示进行缩放处理
        if node[0] == "宝玉":
            node[2] = node[2]/3
        nodes.append({"name": node[0], "symbolSize": node[2]/30})
    # 设置节点间连线
    links = []
    for link in relationship_data_list:
        links.append({"source": link[0], "target": link[1], "value": link[2]})

    g = (
        Graph()
        .add("", nodes, links, repulsion=8000)
        .set_global_opts(title_opts=opts.TitleOpts(title="红楼梦中的部分人物关系"))
    )
    return g


if __name__ == '__main__':
    deal_data()
    g = deal_graph()
    g.render()    # 生成xml文件