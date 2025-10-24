from netmiko import ConnectHandler
from pprint import pprint

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
