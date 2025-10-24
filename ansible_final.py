from netmiko import ConnectHandler
import os
import io
import subprocess
import glob
from textfsm import TextFSM

username = "admin"
password = "cisco"


def showrun(router_ip):
    """
    Use Ansible playbook to backup running-config from Cisco router
    
    Args:
        router_ip: IP address of the router
    
    Returns:
        Tuple of (status, backup_file_path)
    """
    try:
        # Create backups directory if not exists
        if not os.path.exists("backups"):
            os.makedirs("backups")
        
        # Run ansible-playbook command with limit to specific host
        result = subprocess.run(
            ['ansible-playbook', 'playbook.yaml', '-l', router_ip],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)) or '.'
        )
        
        # Check if ansible-playbook executed successfully
        if result.returncode == 0:
            print(f"Ansible playbook executed successfully")
            print(result.stdout)
            
            # Find the backup file created by Ansible
            # Pattern: backups/show_run_66070077_*.txt
            backup_pattern = "backups/show_run_66070077_*.txt"
            backup_files = glob.glob(backup_pattern)
            
            if backup_files:
                # Get the most recent backup file
                backup_file = max(backup_files, key=os.path.getctime)
                print(f"Successfully saved running-config to {backup_file}")
                return ('ok', backup_file)
            else:
                # Fallback: check for specific router IP
                backup_file = f"backups/show_run_66070077_{router_ip}.txt"
                if os.path.exists(backup_file):
                    print(f"Successfully saved running-config to {backup_file}")
                    return ('ok', backup_file)
                else:
                    print("Error: Backup file not found after Ansible execution")
                    return ('Error: Ansible - Backup file not created', None)
        else:
            print(f"Ansible playbook failed with return code {result.returncode}")
            print(f"Error output: {result.stderr}")
            return ('Error: Ansible', None)
            
    except FileNotFoundError:
        print("Error: ansible-playbook command not found. Make sure Ansible is installed.")
        return ('Error: Ansible not installed', None)
    except Exception as e:
        print(f"Error: {e}")
        return ('Error: Ansible', None)


def motd(router_ip, motd_message=None):
    """
    Configure or read MOTD banner on router using Ansible
    
    Args:
        router_ip: IP address of the router
        motd_message: Message to set as MOTD banner (None to read current MOTD)
    
    Returns:
        Success message or current MOTD text
    """
    try:
        # Build ansible-playbook command
        cmd = ['ansible-playbook', 'playbook_motd.yaml', '-l', router_ip]
        
        # Add extra vars if configuring MOTD
        if motd_message is not None:
            # Properly quote the message for shell
            # Replace single quotes with escaped version for YAML
            safe_message = motd_message.replace("'", "''")
            cmd.extend(['-e', f"motd_message='{safe_message}'"])
        
        # Run ansible-playbook command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)) or '.'
        )
        
        # Check if ansible-playbook executed successfully
        if result.returncode == 0:
            print(f"Ansible MOTD playbook executed successfully")
            print(result.stdout)
            
            if motd_message is None:
                # Parse MOTD from Ansible output
                output = result.stdout
                
                # Extract MOTD content from Ansible debug output
                if "banner motd" in output:
                    lines = output.split('\n')
                    banner_content = []
                    capture = False
                    
                    for line in lines:
                        if 'banner motd' in line:
                            # Check for single-line banner
                            if '^C' in line:
                                parts = line.split('^C')
                                if len(parts) >= 3:
                                    return parts[1].strip()
                                else:
                                    capture = True
                                    continue
                        elif capture:
                            if '^C' in line and line.strip() == '^C':
                                break
                            elif line.strip() and not line.strip().startswith('TASK') and not line.strip().startswith('PLAY'):
                                banner_content.append(line.strip())
                    
                    if banner_content:
                        # Clean up Ansible formatting
                        motd_text = '\n'.join(banner_content)
                        # Remove Ansible debug prefixes
                        motd_text = motd_text.replace('"msg":', '').replace('"', '').strip()
                        return motd_text if motd_text else "No MOTD banner configured"
                
                return "No MOTD banner configured"
            else:
                # MOTD was configured successfully
                return "Ok: success"
        else:
            print(f"Ansible MOTD playbook failed with return code {result.returncode}")
            print(f"Error output: {result.stderr}")
            return f"Error: Ansible failed"
            
    except FileNotFoundError:
        print("Error: ansible-playbook command not found. Make sure Ansible is installed.")
        return "Error: Ansible not installed"
    except Exception as e:
        print(f"Error with MOTD: {e}")
        if motd_message is None:
            return f"Error: Failed to read MOTD from {router_ip}"
        else:
            return f"Error: Failed to configure MOTD on {router_ip}"
