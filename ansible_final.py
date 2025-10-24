from netmiko import ConnectHandler
import os

device_ip = "10.0.15.65"
username = "admin"
password = "cisco"

device_params = {
    "device_type": "cisco_ios",
    "ip": device_ip,
    "username": username,
    "password": password,
}

def showrun():
    try:
        # Connect to router using Netmiko
        with ConnectHandler(**device_params) as ssh:
            # Get hostname from router
            hostname_output = ssh.send_command("show running-config | include hostname")
            # Extract hostname (format: "hostname CSR1kv")
            hostname = hostname_output.split()[-1] if hostname_output else device_ip
            
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
