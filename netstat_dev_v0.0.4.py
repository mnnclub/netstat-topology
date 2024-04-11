# Compile Option for Mac
# pyinstaller --onefile --windowed --distpath=./dist_mac \
#  --icon=DALLE_hhji_20240408_Create_a_detailed_illustration_of_a_fully_connected.webp netstat_dev_v0.0.4.py

import paramiko
from scp import SCPClient, SCPException
import getpass
from datetime import datetime
import configparser

class SSHManager:
    """
    usage:
        >>> import SSHManager
        >>> ssh_manager = SSHManager()
        >>> ssh_manager.create_ssh_client(hostname, username, password)
        >>> ssh_manager.send_command("ls -al")
        >>> ssh_manager.send_file("/path/to/local_path", "/path/to/remote_path")
        >>> ssh_manager.get_file("/path/to/remote_path", "/path/to/local_path")
        ...
        >>> ssh_manager.close_ssh_client()
    """
    def __init__(self):
        self.ssh_client = None

    def create_ssh_client(self, hostname, port, username, password):
        """Create SSH client session to remote server"""
        if self.ssh_client is None:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(hostname, port, username=username, password=password, timeout=5)
        else:
            print("SSH client session exist.")

    def close_ssh_client(self):
        """Close SSH client session"""
        self.ssh_client.close()

    def send_file(self, local_path, remote_path):
        """Send a single file to remote path"""
        try:
            with SCPClient(self.ssh_client.get_transport()) as scp:
                scp.put(local_path, remote_path, preserve_times=True)
        except SCPException:
            raise SCPException.message

    def get_file(self, remote_path, local_path):
        """Get a single file from remote path"""
        try:
            with SCPClient(self.ssh_client.get_transport()) as scp:
                scp.get(remote_path, local_path)
        except SCPException:
            raise SCPException.message

    def send_command(self, command):
        """Send a single command"""
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        return stdout.readlines()


    def send_command2(self, command):
        """Send a single command"""
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        return stderr.readlines()


# Create a new configparser object
config = configparser.ConfigParser()

# Read the configuration from the file
config.read('name_map.conf')

# 'instance_checklist' 섹션에서 인스턴스 목록 읽기
instance_map = {}
for ip, name in config.items('instance_map'):
    instance_map[ip] = name


##### 서버 확인작업 메인코드 시작 #####
CurrentTime = datetime.now().strftime('%Y-%m-%d %H:%M')
with open('netstat.conf', 'w') as file:
    file.write(f"## {CurrentTime} ##\n")
    

USER = input('Enter USER: ')
PW = getpass.getpass('Enter password: ')
PORT = 22

## netstat.conf 주석공백 제외한 모든라인의 맨앞에 서버IP 추가해주는 함수
filename = "netstat.conf"
def add_ip_to_file_exclude_comments_and_blanks(filename, ip="127.0.0.1"):
    with open(filename, 'r') as file:  # 원본 파일 읽기
        lines = file.readlines()

    # 주석이나 공백 라인을 제외하고 IP 추가
    new_lines = []
    for line in lines:
        stripped_line = line.strip()  # 앞뒤 공백 제거
        if stripped_line and not stripped_line.startswith("#"):  # 공백 라인이 아니고 주석도 아닐 때
            new_lines.append(f"{ip} {line}")
        else:
            new_lines.append(line)  # 공백 라인이나 주석 라인은 그대로 유지

    with open(filename, 'w') as file:  # 수정된 내용을 파일에 쓰기
        file.writelines(new_lines)


# 맨위 2개 인스턴스만 테스트
instance_map_subset = dict(list(instance_map.items())[:2])

#for name, ip in instance_map_subset.items():
for name, ip in instance_map.items():
    print(f"Checking {name} ({ip})...")
    HOST = ip
    ssh_manager = SSHManager()
    try:
        ssh_manager.create_ssh_client(HOST,PORT,USER,PW) # 세션생성

        # 0. 운영체제 버전체크
        ssh_manager.send_file("netstat.sh", "netstat.sh") # 파일전송
        netstat_result = ssh_manager.send_command("chmod 700 netstat.sh; ./netstat.sh") # 결과받기
        ssh_manager.send_command("rm -f netstat.sh") # 파일삭제
        ssh_manager.close_ssh_client()      # 세선종료

#        print(netstat_result)

        
        # 결과를 파일에 추가
        with open('netstat.conf', 'a+') as file:
            for item in netstat_result:
                file.write(item.strip() + '\n')
        
                
    except Exception as e:
        print(f"Error: {e}")
        continue


#-----------------------------------------------------------------------#


### for get netstat data and save graph.txt ###
# ========== For get netstat run command and save with graph.txt ========

# IPADDR=$(ifconfig eth0 |grep inet|awk '{print $2}')
# echo;echo \#$HOSTNAME; netstat -anpo |egrep -v LISTEN |egrep ^tcp|egrep "goodfys|java|beam|mongo|pips|redis|https|:(80|443|3011|3306|23011) " | awk '{print $5}' | sort -n |uniq -c |sort --key=1 -nr |head -3|awk '{print $2,$1}' |sed "s/^/$IPADDR /g"

# ===========================================================
# # 실행서버 호스트네임
# # 본인IP 연결많은IP:포트 연결카운트
# 10.1.1.11 10.2.2.22:1122 111
# 10.1.1.11 10.2.2.22:2233 22
# 10.1.1.11 10.2.2.22:3344 33

# v0.0.1 에 대한 개선필요사항
# 1. 노드명에 포트가 있고 없고 함에 따라 그림안에 노드수가 늘어남 ( 명칭이 같아야 하나의 노드에서 화살표가 뻗어나감 )
#   -> 콜론: 값을 가지고있는경우 = 서버[S] 노드로, 없는경우 = 클라이언트[C] 노드로 구분하여 노드를 생성하고 화살표를 그림
#   -> 서비스포트는 노드명이 아닌 화살표 숫자옆에 표시하자
#--------------------------------------------------------------
# 예)   10.1.1.11 10.2.2.22:3333 44
# 표시) [C]client01 --redis--> [S]server01
# 설명) 클라이언트client01 이 서버server01 에 redis서비스:44개 연결 되어있음
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
with open('netstat.conf', 'r') as file:
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
with open('netstat.conf', 'r') as file:
    CheckTime = file.readline().strip()  # .strip()을 사용하여 줄바꿈 문자 제거

#plt.title(subject, fontsize=5, fontweight='bold', color='blue', loc='center', pad=10)
#plt.text(1, 0, Subject, fontsize=5, horizontalalignment='right', verticalalignment='bottom', transform=plt.gca().transAxes)
plt.text(1, 0, CheckTime, fontsize=5, horizontalalignment='right', verticalalignment='bottom', transform=plt.gca().transAxes)

plt.savefig(f"netstat_{CurrentTime}.png", dpi=300)

print(f"Completed: Saved as 'netstat_{CurrentTime}.png'")

#plt.show()
#----------------------------------------------#