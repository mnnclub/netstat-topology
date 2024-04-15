# Compile Option for Mac
# pyinstaller --onefile --windowed --distpath=./dist_mac \
#  --icon=DALLE_hhji_20240408_Create_a_detailed_illustration_of_a_fully_connected.webp netstat_dev_v0.0.4.py

# Compile Option for Windows
# pyinstaller --onefile --console --distpath=./dist_win --icon=sample/DALLE_hhji_20240408_Create_a_detailed_illustration_of_a_fully_connected.webp netstat_dev_v0.0.4.py

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

# Read the instance list from the 'instance_checklist' section
instance_map = {}
for ip, name in config.items('instance_map'):
    instance_map[ip] = name


##### Main code for server verification starts here #####
CurrentTime = datetime.now().strftime('%Y-%m-%d %H:%M')
with open('netstat.conf', 'w') as file:
    file.write(f"## {CurrentTime} ##\n")
    

USER = input('Enter USER: ')
PW = getpass.getpass('Enter password: ')
PORT = 22

## Function to add server IP at the beginning of every line in netstat.conf, excluding comments and blank lines
filename = "netstat.log"
def add_ip_to_file_exclude_comments_and_blanks(filename, ip="127.0.0.1"):
    with open(filename, 'r') as file:  # Read Original File
        lines = file.readlines()

    # Append IP exclude # comment or blank line
    new_lines = []
    for line in lines:
        stripped_line = line.strip()
        if stripped_line and not stripped_line.startswith("#"):  # if not Blank line or # comment
            new_lines.append(f"{ip} {line}")
        else:
            new_lines.append(line)  # Keep Blank line or # comment

    with open(filename, 'w') as file:  # Write file with modified content
        file.writelines(new_lines)


# Test with only 2 upper line
#instance_map_subset = dict(list(instance_map.items())[:2])
#for name, ip in instance_map_subset.items():

for name, ip in instance_map.items():
    print(f"Checking {name} ({ip})...")
    HOST = ip
    ssh_manager = SSHManager()
    try:
        ssh_manager.create_ssh_client(HOST,PORT,USER,PW) # create session

        ssh_manager.send_file("netstat.sh", "netstat.sh")
        netstat_result = ssh_manager.send_command("chmod 700 netstat.sh; ./netstat.sh")
        ssh_manager.send_command("rm -f netstat.sh")
        ssh_manager.close_ssh_client()

#        print(netstat_result)
        
        # Append result to netstat.conf file
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
# # MyIP ManyConnIP:Port Count
# 1.2.3.4 1.2.3.4:1111 111
# 1.2.3.4 1.2.3.4:2222 22
# 1.2.3.4 1.2.3.4:3333 33

# v0.0.1 need to fix things
# 1. Depending on whether the node name has a port or not, the number of nodes in the graph increases (multiple arrows extend from one node if the names are the same)
#    - If the node name contains a colon ":" and has a value, it represents a server [S] node.
#    - If the node name does not contain a colon ":" or does not have a value, it represents a client [C] node.
#    - Create nodes accordingly and draw arrows.
#    - Display the service port next to the arrow instead of the node name.
#--------------------------------------------------------------
# Example:   1.2.3.4 1.2.3.4:1111 44
# Display: [C]pc11 --db:22--> [S]search33
# Explanation: Client pc11 is connected to server search33:44 on port db22
# Let's consider receiving arrows as servers and sending arrows as clients, excluding S and C
#--------------------------------------------------------------

# v0.0.2 improvements needed
# 1. Separate the graph options for number to name conversion
# 2. recvQ
# 3. Check the number of established and syn_sent connections
#    - Initially only checked for ESTABLISHED, but added all because Restful API requests are stateless.
# 4. Automate checking by connecting via SSH --> Test after connecting via VPN
# 5. Check the time it takes for SYN_SENT to transition to ESTABLISHED --> Consider later
#
# v0.0.3 
# 1. Separate the graph options into a separate configuration file
# 2. Display the check time in the bottom right corner

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

# Read the configuration values for converting numbers to names.
# Convert port numbers to service names and IP addresses to host names.
port_service_map = {}
for port, service in config.items('port_service_map'):
    port_service_map[port] = service

dns_name_map = {}
for ip, name in config.items('dns_name_map'):
    dns_name_map[ip] = name

# Split the long names into multiple lines for readability.
for key, value in dns_name_map.items():
    dns_name_map[key] = value.replace('-', '\n', 1).replace('.', '\n', 2)

# Read instance with 'instance_checklist' Section
instance_map = {}
for ip, name in config.items('instance_map'):
    instance_map[ip] = name


# Initialize list for result
filtered_lines = []
with open('netstat.conf', 'r') as file:
#with open('netstat_240401.txt', 'r') as file:
    for line in file:
        stripped_line = line.strip()

        # Append list only Blank line or not start with # comment
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

# Visualize the graph : Instance=node, ConnectLine=edge
#pos = nx.spring_layout(G_reversed, k=3.5)
# pos = nx.spiral_layout(G_reversed, resolution=0.5)
#pos = nx.shell_layout(G_reversed)
# pos = nx.random_layout(G_reversed)
pos = nx.circular_layout(G_reversed)

#https://networkx.org/documentation/stable/reference/drawing.html#module-networkx.drawing.layout
# nx.draw(G_reversed, pos, with_labels=True, node_size=250, node_color="orange", font_size=3, font_color="black", font_weight="light", \
#     edge_color="green", width=0.3, style="dashed", alpha=0.9, arrowsize=5, arrowstyle="->", connectionstyle="arc,rad=0.001", \
#         min_source_margin=1, min_target_margin=1)
    
# Read option with 'draw_options' Section
options = dict(config['draw_options'])
    
# Change proper type option value
for key in options:
    if key in ['width', 'alpha']:  
        options[key] = float(options[key])
    elif options[key].isdigit():  
        options[key] = int(options[key])
    elif options[key] == 'True':
        options[key] = True
    elif options[key] == 'False':
        options[key] = False


# Draw edge labels : f"{SERVER_PORT}"
edge_labels = nx.get_edge_attributes(G_reversed, 'label')

# Drawing graph with draw options
nx.draw(G_reversed, pos, **options)

# Visualize the graph with modified edge labels
nx.draw_networkx_edge_labels(G_reversed, pos, edge_labels=edge_labels, font_size=3, font_color="red")

# Open file and read only first line : show check time to right bottom
with open('netstat.conf', 'r') as file:
    CheckTime = file.readline().strip()  # use .strip() and move word

#plt.title(subject, fontsize=5, fontweight='bold', color='blue', loc='center', pad=10)
#plt.text(1, 0, Subject, fontsize=5, horizontalalignment='right', verticalalignment='bottom', transform=plt.gca().transAxes)
plt.text(1, 0, CheckTime, fontsize=5, horizontalalignment='right', verticalalignment='bottom', transform=plt.gca().transAxes)

plt.savefig(f"netstat_{CurrentTime}.png", dpi=300)

print(f"Completed: Saved as 'netstat_{CurrentTime}.png'")

#plt.show()
#----------------------------------------------#