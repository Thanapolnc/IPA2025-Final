from netmiko import ConnectHandler
from pprint import pprint

device_ip = "10.0.15.65"
username = "admin"
password = "cisco"

device_params = {
    "device_type": "cisco_ios",
    "ip": device_ip,
    "username": username,
    "password": password,
}


def gigabit_status():
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
