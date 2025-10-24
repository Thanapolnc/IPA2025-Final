from netmiko import ConnectHandler
import os

username = "admin"
password = "cisco"


def showrun(router_ip):
    device_params = {
        "device_type": "cisco_ios",
        "ip": router_ip,
        "username": username,
        "password": password,
    }
    
    try:
        # Connect to router using Netmiko
        with ConnectHandler(**device_params) as ssh:
            # Get hostname from router
            hostname_output = ssh.send_command("show running-config | include hostname")
            # Extract hostname (format: "hostname CSR1kv")
            hostname = hostname_output.split()[-1] if hostname_output else router_ip
            
            # Send show running-config command
            output = ssh.send_command("show running-config")
            
            # Create backups directory if not exists
            if not os.path.exists("backups"):
                os.makedirs("backups")
            
            # Save to file with format: show_run_[studentID]_[router_name].txt
            backup_file = f"backups/show_run_66070077_{hostname}.txt"
            with open(backup_file, "w") as f:
                f.write(output)
            
            print(f"Successfully saved running-config to {backup_file}")
            return ('ok', backup_file)
    except Exception as e:
        print(f"Error: {e}")
        return ('Error: Ansible', None)
