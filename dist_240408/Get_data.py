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
# devopr / Nime1828!@
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
