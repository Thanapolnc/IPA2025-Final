from netmiko import ConnectHandler
import os
import io
from textfsm import TextFSM

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


def motd(router_ip, motd_message=None):
    """
    Configure or read MOTD banner on router using Netmiko with TextFSM
    
    Args:
        router_ip: IP address of the router
        motd_message: Message to set as MOTD banner (None to read current MOTD)
    
    Returns:
        Success message or current MOTD text
    """
    device_params = {
        "device_type": "cisco_ios",
        "ip": router_ip,
        "username": username,
        "password": password,
    }
    
    try:
        # Connect to router using Netmiko
        with ConnectHandler(**device_params) as ssh:
            
            # If motd_message is None, read current MOTD using Netmiko with TextFSM
            if motd_message is None:
                # Get full running config
                output = ssh.send_command("show running-config")
                
                if not output or "banner motd" not in output:
                    return "No MOTD banner configured"
                
                # TextFSM template for parsing banner motd
                # This template extracts the MOTD message content
                textfsm_template = r"""Value MOTD_MESSAGE (.*?)

Start
  ^banner\s+motd\s+\^C -> GetMessage

GetMessage
  ^\^C -> End
  ^(.+) -> Continue.Record

End
"""
                
                try:
                    # Create TextFSM object with the template
                    fsm = TextFSM(io.StringIO(textfsm_template))
                    
                    # Parse the output using TextFSM
                    result = fsm.ParseText(output)
                    
                    # Extract MOTD message from parsed result
                    if result:
                        motd_lines = [row[0] for row in result if row[0].strip()]
                        if motd_lines:
                            motd_text = '\n'.join(motd_lines).strip()
                            print(f"TextFSM: Parsed MOTD successfully")
                            return motd_text
                    
                    # Fallback: manual parsing if TextFSM fails
                    print("TextFSM: Using fallback parsing method")
                    lines = output.split('\n')
                    banner_content = []
                    capture_banner = False
                    delimiter_found = False
                    
                    for line in lines:
                        if 'banner motd' in line:
                            # Check if single-line banner
                            if '^C' in line:
                                parts = line.split('^C')
                                if len(parts) >= 3:  # banner motd ^C message ^C
                                    # Single-line banner
                                    motd_text = parts[1].strip()
                                    return motd_text if motd_text else "No MOTD banner configured"
                                else:
                                    # Multi-line banner starts
                                    capture_banner = True
                                    continue
                        elif capture_banner:
                            if '^C' in line and line.strip() == '^C':
                                # End of banner
                                delimiter_found = True
                                break
                            else:
                                # Banner content line
                                banner_content.append(line)
                    
                    if delimiter_found and banner_content:
                        motd_text = '\n'.join(banner_content).strip()
                        return motd_text
                    elif not delimiter_found and banner_content:
                        motd_text = '\n'.join(banner_content).strip()
                        return motd_text
                    else:
                        return "No MOTD banner configured"
                        
                except Exception as e:
                    print(f"TextFSM parsing error: {e}, using fallback")
                    # Fallback parsing
                    lines = output.split('\n')
                    banner_content = []
                    capture_banner = False
                    
                    for line in lines:
                        if 'banner motd' in line:
                            if '^C' in line:
                                parts = line.split('^C')
                                if len(parts) >= 3:
                                    return parts[1].strip()
                                else:
                                    capture_banner = True
                                    continue
                        elif capture_banner:
                            if '^C' in line and line.strip() == '^C':
                                break
                            else:
                                banner_content.append(line)
                    
                    if banner_content:
                        return '\n'.join(banner_content).strip()
                    return "No MOTD banner configured"
            
            # If motd_message is provided, configure MOTD
            else:
                # Configure MOTD banner
                config_commands = [
                    f'banner motd #{motd_message}#'
                ]
                
                output = ssh.send_config_set(config_commands)
                print(f"MOTD configuration output:\n{output}")
                
                return "Ok: success"
                
    except Exception as e:
        print(f"Error with MOTD: {e}")
        if motd_message is None:
            return f"Error: Failed to read MOTD from {router_ip}"
        else:
            return f"Error: Failed to configure MOTD on {router_ip}"
