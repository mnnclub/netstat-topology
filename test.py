import networkx as nx
from networkx.drawing.nx_agraph import write_dot

G = nx.DiGraph()

# 엣지 추가 및 속성 정의
# svr_01
G.add_edge("svr_01-3.146", "10.21.3.147:3306", sessions=489, state="ESTABLISHED", recv_q=0, send_q=0, pid=1234, process="mysql", instance_name="")
G.add_edge("svr_01-3.146", "216.239.38.55:443", sessions=1260, state="TIME_WAIT", recv_q=0, send_q=0, pid=1234, process="https", instance_name="")

# nmas_01
G.add_edge("nmas_01-3.181", "10.21.5.149:3011", sessions=306, state="ESTABLISHED", recv_q=0, send_q=0, pid=1234, process="mongdb", instance_name="")
G.add_edge("nmas_01-3.181", "10.21.6.47:3011", sessions=299, state="ESTABLISHED", recv_q=0, send_q=0, pid=1234, process="mongdb", instance_name="")

# web_01
G.add_edge("web_01-3.208", "10.21.4.67:23010", sessions=365, state="ESTABLISHED", recv_q=0, send_q=0, pid=1234, process="mongdb", instance_name="web_01")

# mongodb_01_a
G.add_edge("mongodb_01_a-5.149", "10.21.6.47:3011", sessions=2, state="ESTABLISHED", recv_q=0, send_q=0, pid=1234, process="mongdb", instance_name="")
G.add_edge("mongodb_01_a-5.149", "10.21.6.47:23011", sessions=2, state="ESTABLISHED", recv_q=0, send_q=0, pid=1234, process="mongdb", instance_name="")
G.add_edge("mongodb_01_a-5.149", "10.21.5.233:23011", sessions=2, state="ESTABLISHED", recv_q=0, send_q=0, pid=1234, process="mongdb", instance_name="")


### 각 인스턴스별
# 10.21.3.146
svr_01 = """
   1260 216.239.38.55:443
    489 10.21.5.121:3306
    101 10.21.5.149:3011
"""

# 10.21.4.103
svc_02 = """
      3 52.95.195.121:443
      2 10.21.6.47:3011
      2 10.21.6.47:23011
"""

# 10.21.3.181
nmas_01 = """
    306 10.21.5.149:3011
    299 10.21.6.47:3011
     12 10.21.3.23:23010
"""

# 10.21.3.208
web_01 = """
    365 10.21.4.67:23010
     25 10.21.3.122:23010
     10 10.21.5.121:3306
"""

# 10.21.5.149
mongodb_01_a = """
      2 10.21.6.47:3011
      2 10.21.6.47:23011
      2 10.21.5.233:23011
"""



# write_dot을 사용하기 전에 엣지 라벨을 설정합니다.
for u, v, data in G.edges(data=True):
    # data['label'] = f"sessions: {data['sessions']}, recv_q: {data['recv_q']}, {data['instance_name']}: {data['process']}"
    data['label'] = f"{data['instance_name']}: {data['process']}, s:{data['sessions']}, rq:{data['recv_q']}"

# DOT 파일로 그래프 저장
write_dot(G, "network_with_labels.dot")

import pygraphviz as pgv

# DOT 파일에서 그래프를 읽기
A = pgv.AGraph("network_with_labels.dot")

# Graphviz 레이아웃을 사용하여 시각화 준비
A.layout(prog="dot")

# 그래프 그리기 (이미지 파일로 저장)
A.draw("network_with_labels.png")

