
### for get netstat data and save graph.txt ###
# ========== For get netstat run command and save with graph.txt ========

# IPADDR=$(ifconfig eth0 |grep inet|awk '{print $2}')
# echo;echo \#$HOSTNAME; netstat -anpo |egrep -v LISTEN |egrep ^tcp|egrep "goodfys|java|beam|mongo|pips|redis|https|:(80|443|3011|3306|23011) " | awk '{print $5}' | sort -n |uniq -c |sort --key=1 -nr |head -3|awk '{print $2,$1}' |sed "s/^/$IPADDR /g"

# ===========================================================
# # 실행서버 호스트네임
# # 본인IP 연결많은IP:포트 연결카운트
# 1.2.3.4 1.2.3.4:1111 111
# 1.2.3.4 1.2.3.4:2222 22
# 1.2.3.4 1.2.3.4:3333 33

# v0.0.1 에 대한 개선필요사항
# 1. 노드명에 포트가 있고 없고 함에 따라 그림안에 노드수가 늘어남 ( 명칭이 같아야 하나의 노드에서 화살표가 뻗어나감 )
#   -> 콜론: 값을 가지고있는경우 = 서버[S] 노드로, 없는경우 = 클라이언트[C] 노드로 구분하여 노드를 생성하고 화살표를 그림
#   -> 서비스포트는 노드명이 아닌 화살표 숫자옆에 표시하자
#--------------------------------------------------------------
# 예)   1.2.3.4 1.2.3.4:1111 44
# 표시) [C]pc11 --db:22--> [S]search33
# 설명) 클라이언트pc11 이 서버db22 에 search33:44개 연결 되어있음
#     S,C 빼고 화살표를 받으면 서버, 보내면 클라이언트로 인식하자
#--------------------------------------------------------------

# v0.0.2 에 대한 개선필요사항
# 1. 그림옵션 숫자->이름 변경 설정 따로 빼기
# 2. recvQ
# 3. established, syn_sent 갯수 확인
#   - 초기에 ESTABLISHED 만 했다가 전부 다 추가한 이유는, Restful API 요청은 stateless 이기때문.
# 4. ssh 접속해서 체크 자동화 --> vpn접속후 테스트
# 5. SYN_SENT 에서 ESTABLISHED 로 바뀌는 시간 체크 --> 추후고민
#
# v0.0.3 
# 1. 그림옵션 별도 설정파일 분리
# 2. 체크시간 우측하단 표시

import networkx as nx
import matplotlib.pyplot as plt
import configparser
from datetime import datetime

CurrentTime = datetime.now().strftime('%y%m%d_%H%M')

# Create a graph with nodes and edges
G = nx.DiGraph()

# Create a new configparser object
config = configparser.ConfigParser()

# Read the configuration from the file
config.read('name_map.conf')

# 숫자를 이름으로 변경하기 위한 설정값 읽어 들인다.
# 포트번호 -> 서비스명, 아이피주소 -> 호스트명
port_service_map = {}
for port, service in config.items('port_service_map'):
    port_service_map[port] = service

dns_name_map = {}
for ip, name in config.items('dns_name_map'):
    dns_name_map[ip] = name

# 읽어들인 이름이 너무 길어서 줄바꿈을 한다.
for key, value in dns_name_map.items():
    dns_name_map[key] = value.replace('-', '\n', 1).replace('.', '\n', 2)

# 'instance_checklist' 섹션에서 인스턴스 목록 읽기
instance_map = {}
for ip, name in config.items('instance_map'):
    instance_map[ip] = name


# 결과를 저장할 리스트 초기화
filtered_lines = []
with open('netstat.log', 'r') as file:
#with open('netstat_240401.txt', 'r') as file:
    for line in file:
        # .strip()을 사용해 줄 앞뒤의 공백을 제거합니다.
        stripped_line = line.strip()

        # 줄이 비어있거나 '#'으로 시작하지 않는 경우에만 리스트에 추가합니다.
        if stripped_line and not stripped_line.startswith('#'):
            filtered_lines.append(stripped_line)


for line in filtered_lines:
    line = line.strip().split()
    ValueOne = line[0]
    ValueTwo = line[1]
    
    # SERVER have : string like IP:PORT
    if ":" in ValueOne:
        SERVER = ValueOne
        CLIENT = ValueTwo
    elif ":" in ValueTwo:
        SERVER = ValueTwo
        CLIENT = ValueOne
        
    # Separate the IP address and port number
    SERVER_IP, SERVER_PORT = SERVER.split(":")
    
    # Replace the IP addresses with the EC2 names
    for key, value in dns_name_map.items():
        SERVER_IP = SERVER_IP.replace(key, value)
        CLIENT = CLIENT.replace(key, value)

    # Replace the port numbers with the service names
    for key, value in port_service_map.items():
        SERVER_PORT = SERVER_PORT.replace(key, value)
        # print(f"SERVER_PORT: {SERVER_PORT}")

    CONN_CNT = int(line[2])

    G.add_edge(f"{SERVER_IP}", f"{CLIENT}", weight=CONN_CNT, label=f"{SERVER_PORT}:{CONN_CNT}")

# Reverse the direction of the graph ( CLIENT -> SERVER )
G_reversed = nx.reverse(G)

# Visualize the graph : 인스턴스=node, 연결선=edge
#pos = nx.spring_layout(G_reversed, k=3.5)
# pos = nx.spiral_layout(G_reversed, resolution=0.5)
#pos = nx.shell_layout(G_reversed)
# pos = nx.random_layout(G_reversed)
pos = nx.circular_layout(G_reversed)

#https://networkx.org/documentation/stable/reference/drawing.html#module-networkx.drawing.layout
# nx.draw(G_reversed, pos, with_labels=True, node_size=250, node_color="orange", font_size=3, font_color="black", font_weight="light", \
#     edge_color="green", width=0.3, style="dashed", alpha=0.9, arrowsize=5, arrowstyle="->", connectionstyle="arc,rad=0.001", \
#         min_source_margin=1, min_target_margin=1)
    
# 'draw_options' 섹션에서 옵션 읽기
options = dict(config['draw_options'])
    
# 옵션 값을 적절한 타입으로 변환
for key in options:
    if key in ['width', 'alpha']:  # float 타입으로 변환해야 하는 경우
        options[key] = float(options[key])
    elif options[key].isdigit():  # 정수 타입으로 변환
        options[key] = int(options[key])
    elif options[key] == 'True':  # 불리언 타입으로 변환 (True)
        options[key] = True
    elif options[key] == 'False':  # 불리언 타입으로 변환 (False)
        options[key] = False


# Draw edge labels : f"{SERVER_PORT}"
edge_labels = nx.get_edge_attributes(G_reversed, 'label')

# 그래프 시각화 설정 옵션을 사용하여 그래프 그리기
nx.draw(G_reversed, pos, **options)

# Visualize the graph with modified edge labels
nx.draw_networkx_edge_labels(G_reversed, pos, edge_labels=edge_labels, font_size=3, font_color="red")

# 파일을 열고 첫 번째 줄만 읽기 : 체크시간을 우측하단에 표시
with open('netstat.log', 'r') as file:
    CheckTime = file.readline().strip()  # .strip()을 사용하여 줄바꿈 문자 제거

#plt.title(subject, fontsize=5, fontweight='bold', color='blue', loc='center', pad=10)
#plt.text(1, 0, Subject, fontsize=5, horizontalalignment='right', verticalalignment='bottom', transform=plt.gca().transAxes)
plt.text(1, 0, CheckTime, fontsize=5, horizontalalignment='right', verticalalignment='bottom', transform=plt.gca().transAxes)

plt.savefig(f"netstat_{CurrentTime}.png", dpi=300)

#plt.show()
#----------------------------------------------#