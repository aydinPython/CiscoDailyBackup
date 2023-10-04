import smtplib
from email.mime.text import MIMEText
from netmiko import ConnectHandler
from datetime import datetime

# Define the path to your files
path = '/home/netadmin/cisco-inventory'
backup_path_switches = '/home/netadmin/HO-Backup/Cisco/Switches/'
backup_path_routers = '/home/netadmin/DR-Backup/Cisco/Routers/'


# Email parameters
sender_email = "sender@mail.com"
receiver_email = "receiver@mail.com"
smtp_server = "MAIL_SERVER_ADDRESS"
smtp_port = 25

# Define your device parameters
device_params = {
    'device_type': 'cisco_ios',
    'username': 'cisco',
    'password': 'cisco',
    'secret': 'cisco'
}

def send_email(ip_address):
    subject = "Network Backup Script Error"
    body = f"""
    The backup failed due to a TCP connection or device failure : {ip_address}.
    """
    msg = MIMEText(body)
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception as e:
        print(f"Error occurred while sending email: {str(e)}")

# Load IP addresses from text files
with open(path + '/switches_ip.txt', 'r') as f:
    switch_ips = f.read().splitlines()


with open(path + '/router_ip.txt', 'r') as f:
    router_ips = f.read().splitlines()


def backup_config(ip_list, device_type, backup_path):
    for ip in ip_list:
        try:
            device_params['ip'] = ip
            device_params['device_type'] = device_type
            connection = ConnectHandler(**device_params)
            connection.enable()  # Enter into enable mode
            output = connection.send_command('show running-config')
            
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d")
            
            with open(f"{backup_path}/{ip}_{timestamp}_backup.txt", 'w') as file:
                file.write(output)
                print(f'Backup completed : {ip}\n')
            connection.disconnect()
            
        except Exception as e:
            print(f"Error occurred for IP {ip}: {str(e)}")
            send_email(ip)  # Here, we are passing the IP address to the send_email function.

# Backup switches
backup_config(switch_ips, 'cisco_ios', backup_path_switches)  # for switches
backup_config(router_ips, 'cisco_ios', backup_path_routers)  # for routers
