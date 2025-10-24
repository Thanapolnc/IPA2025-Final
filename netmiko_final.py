from netmiko import ConnectHandler
from pprint import pprint
from textfsm import TextFSM
import re
import os
import io

username = "admin"
password = "cisco"


def gigabit_status(router_ip):
    device_params = {
        "device_type": "cisco_ios",
        "ip": router_ip,
        "username": username,
        "password": password,
    }
    
    ans = ""
    interface_list = []
    with ConnectHandler(**device_params) as ssh:
        up = 0
        down = 0
        admin_down = 0
        result = ssh.send_command("show ip interface brief", use_textfsm=True)
        
        # Debug: print first item to see the keys
        if result and len(result) > 0:
            print("Available keys:", result[0].keys() if isinstance(result[0], dict) else "Not a dict")
        
        for interface in result:
            # Try different possible key names
            interface_name = interface.get("intf") or interface.get("interface") or interface.get("name") or ""
            status = interface.get("status") or interface.get("proto") or ""
            
            if interface_name.startswith("GigabitEthernet"):
                interface_list.append(f"{interface_name} {status}")
                if status == "up":
                    up += 1
                elif status == "down":
                    down += 1
                elif status == "administratively down":
                    admin_down += 1
        
        ans = ", ".join(interface_list) + f" -> {up} up, {down} down, {admin_down} administratively down"
        pprint(ans)
        return ans


def motd_read(router_ip):
    """
    Read MOTD banner from router using Netmiko + TextFSM
    
    Args:
        router_ip: IP address of the router
    
    Returns:
        MOTD banner text or error message
    """
    device_params = {
        "device_type": "cisco_ios",
        "ip": router_ip,
        "username": username,
        "password": password,
    }
    
    try:
        with ConnectHandler(**device_params) as ssh:
            # Get MOTD using 'show banner motd' command
            output = ssh.send_command("show banner motd")
            
            # Check if output exists
            if not output or not output.strip():
                return "No MOTD banner configured"
            
            # Use TextFSM to parse the MOTD
            template_path = os.path.join(os.path.dirname(__file__), 'cisco_ios_show_banner_motd.textfsm')
            
            # Check if template file exists
            if os.path.exists(template_path):
                with open(template_path) as template_file:
                    fsm = TextFSM(template_file)
                    result = fsm.ParseText(output)
                    
                    # Extract MOTD from parsed result
                    if result and len(result) > 0 and len(result[0]) > 0:
                        motd_text = result[0][0].strip()
                        if motd_text:
                            return motd_text
            else:
                # Fallback: if template doesn't exist, use simple text parsing
                print(f"TextFSM template not found at {template_path}, using fallback")
                motd_text = output.strip()
                # Clean up and preserve spaces between words
                motd_text = ' '.join(motd_text.split())
                if motd_text:
                    return motd_text
            
            # If TextFSM parsing fails, try fallback with running-config
            output = ssh.send_command("show running-config | section banner motd")
            
            if not output or "banner motd" not in output:
                return "No MOTD banner configured"
            
            # Parse MOTD content between delimiters using regex as fallback
            patterns = [
                r'banner motd\s+\^C(.*?)\^C',  # ^C delimiter
                r'banner motd\s+@(.*?)@',       # @ delimiter
                r'banner motd\s+\$(.*?)\$',     # $ delimiter
            ]
            
            for pattern in patterns:
                match = re.search(pattern, output, re.DOTALL)
                if match:
                    motd_text = match.group(1).strip()
                    motd_text = ' '.join(motd_text.split())
                    if motd_text:
                        return motd_text
            
            return "No MOTD banner configured"
            
    except Exception as e:
        print(f"Error reading MOTD: {e}")
        return f"Error: Failed to read MOTD from {router_ip}"
