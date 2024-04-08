import pandas as pd
import networkx as nx
import pygraphviz as pgv
from networkx.drawing.nx_agraph import write_dot


df = pd.DataFrame(
    {'source': ('a', 'a', 'a', 'b', 'c', 'd'),
     'target': ('b', 'b', 'c', 'a', 'd', 'a'),
     'weight': (1, 2, 3, 4, 5, 6)})

G=nx.from_pandas_dataframe(df, 'source', 'target', ['weight'], create_using=nx.DiGraph())

# write_dot을 사용하기 전에 엣지 라벨을 설정합니다.
for u, v, data in G.edges(data=True):
    data['label'] = f"sessions: {data['sessions']}, recv_q: {data['recv_q']}, process: {data['process']}"

# DOT 파일로 그래프 저장
write_dot(G, "test240401.dot")

A = pgv.AGraph("test240401.dot")

# Graphviz 레이아웃을 사용하여 시각화 준비
A.layout(prog="dot")

# 그래프 그리기 (이미지 파일로 저장)
A.draw("test240401.png")