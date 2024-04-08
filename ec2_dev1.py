import networkx as nx
from networkx.drawing.nx_agraph import write_dot

G = nx.DiGraph()

# 엣지 추가 및 속성 정의
G.add_edge("10.21.3.146:3306", "10.21.3.147:3306",
           sessions=300, state="ESTABLISHED",
           recv_q=0, send_q=0, pid=1234, process="nginx")


# write_dot을 사용하기 전에 엣지 라벨을 설정합니다.
for u, v, data in G.edges(data=True):
    data['label'] = f"sessions: {data['sessions']}, recv_q: {data['recv_q']}, process: {data['process']}"

# DOT 파일로 그래프 저장
write_dot(G, "network_with_labels.dot")

import pygraphviz as pgv

# DOT 파일에서 그래프를 읽기
A = pgv.AGraph("network_with_labels.dot")

# Graphviz 레이아웃을 사용하여 시각화 준비
A.layout(prog="dot")

# 그래프 그리기 (이미지 파일로 저장)
A.draw("network_with_labels.png")

