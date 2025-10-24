#######################################################################################
# Yourname: Thanapol Wankhamgood
# Your student ID: 66070077
# Your GitHub Repo: https://github.com/Thanapolnc/IPA2024-Final

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import requests
import json
import time
import os
from dotenv import load_dotenv
import restconf_final
import netconf_final
import netmiko_final
import ansible_final
from requests_toolbelt.multipart.encoder import MultipartEncoder

# Load environment variables from .env file
load_dotenv()

#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.

ACCESS_TOKEN = os.environ.get("WEBEX_ACCESS_TOKEN")

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = os.environ.get("WEBEX_ROOM_ID")

# Variable to store selected method (restconf or netconf)
selected_method = None

while True:
    try:
        # always add 1 second of delay to the loop to not go over a rate limit of API calls
        time.sleep(1)

        # the Webex Teams GET parameters
        #  "roomId" is the ID of the selected room
        #  "max": 1  limits to get only the very last message in the room
        getParameters = {"roomId": roomIdToGetMessages, "max": 1}

        # the Webex Teams HTTP header, including the Authoriztion
        getHTTPHeader = {"Authorization": "Bearer " + ACCESS_TOKEN}

# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
        
        # Send a GET request to the Webex Teams messages API.
        # - Use the GetParameters to get only the latest message.
        # - Store the message in the "r" variable.
        r = requests.get(
            "https://webexapis.com/v1/messages",
            params=getParameters,
            headers=getHTTPHeader,
        )
        # verify if the retuned HTTP status code is 200/OK
        if not r.status_code == 200:
            print(f"Error getting messages. Status code: {r.status_code}")
            continue

        # get the JSON formatted returned data
        json_data = r.json()

        # check if there are any messages in the "items" array
        if len(json_data["items"]) == 0:
            continue

        # store the array of messages
        messages = json_data["items"]
        
        # store the text of the first message in the array
        message = messages[0]["text"]
        print("Received message: " + message)

        # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
        #  e.g.  "/66070077 restconf" or "/66070077 10.0.15.61 create"
        if message.startswith("/66070077"):

            # extract the command and IP with error handling
            try:
                parts = message.split()
                if len(parts) < 2:
                    responseMessage = "Error: No command specified. Please use format: /66070077 <method> or /66070077 <IP> <command>"
                # Check if selecting method (restconf/netconf)
                elif len(parts) == 2 and parts[1].lower() in ["restconf", "netconf"]:
                    selected_method = parts[1].lower()
                    responseMessage = f"Ok: {selected_method.capitalize()}"
                    print(f"Method selected: {selected_method}")
                elif len(parts) == 2:
                    # Only one argument and it's not restconf/netconf
                    # Check if method is selected first
                    if selected_method is None:
                        responseMessage = "Error: No method specified"
                    # Check if it's an IP address
                    elif parts[1].startswith("10.0.15."):
                        responseMessage = "Error: No command found."
                    else:
                        responseMessage = "Error: No IP specified"
                elif len(parts) < 3:
                    # Two arguments but still less than 3
                    if selected_method is None:
                        responseMessage = "Error: No method specified"
                    elif parts[1].startswith("10.0.15."):
                        responseMessage = "Error: No command found."
                    else:
                        responseMessage = "Error: No IP specified"
                else:
                    router_ip = parts[1]
                    command = parts[2]
                    
                    # Validate IP address (10.0.15.61-65)
                    valid_ips = [f"10.0.15.{i}" for i in range(61, 66)]
                    if router_ip not in valid_ips:
                        responseMessage = f"Error: Invalid IP. Valid IPs are 10.0.15.61 to 10.0.15.65"
                    else:
                        # Commands that don't require method selection
                        if command in ["gigabit_status", "showrun"]:
                            print(f"Router IP: {router_ip}, Command: {command} (no method required)")
                        # Commands that require method selection
                        elif selected_method is None:
                            responseMessage = "Error: No method specified"
                        else:
                            print(f"Router IP: {router_ip}, Command: {command}, Method: {selected_method}")

# 5. Complete the logic for each command

                        if command == "create":
                            if selected_method == "restconf":
                                responseMessage = restconf_final.create(router_ip)
                            else:  # netconf
                                responseMessage = netconf_final.create(router_ip)
                        elif command == "delete":
                            if selected_method == "restconf":
                                responseMessage = restconf_final.delete(router_ip)
                            else:  # netconf
                                responseMessage = netconf_final.delete(router_ip)
                        elif command == "enable":
                            if selected_method == "restconf":
                                responseMessage = restconf_final.enable(router_ip)
                            else:  # netconf
                                responseMessage = netconf_final.enable(router_ip)
                        elif command == "disable":
                            if selected_method == "restconf":
                                responseMessage = restconf_final.disable(router_ip)
                            else:  # netconf
                                responseMessage = netconf_final.disable(router_ip)
                        elif command == "status":
                            if selected_method == "restconf":
                                responseMessage = restconf_final.status(router_ip)
                            else:  # netconf
                                responseMessage = netconf_final.status(router_ip)
                        elif command == "gigabit_status":
                            responseMessage = netmiko_final.gigabit_status(router_ip)
                        elif command == "showrun":
                            responseMessage = ansible_final.showrun()
                        else:
                            responseMessage = "Error: Unknown command. Valid commands: create, delete, enable, disable, status, gigabit_status, showrun"
            except Exception as e:
                print(f"Error processing command: {e}")
                responseMessage = "Error: Failed to process command"
            
# 6. Complete the code to post the message to the Webex Teams room.

            try:
                # Check if responseMessage is a tuple (for showrun command with file)
                if isinstance(responseMessage, tuple) and len(responseMessage) == 2:
                    status, filepath = responseMessage
                    
                    if status == 'ok' and filepath and os.path.exists(filepath):
                        # Send message with file attachment
                        # Extract only filename without path
                        filename = os.path.basename(filepath)
                        
                        with open(filepath, 'rb') as fileobject:
                            postData = MultipartEncoder({
                                "roomId": roomIdToGetMessages,
                                "text": "show running config",
                                "files": (filename, fileobject, "text/plain")
                            })
                            HTTPHeaders = {
                                "Authorization": "Bearer " + ACCESS_TOKEN,
                                "Content-Type": postData.content_type
                            }
                            r = requests.post(
                                "https://webexapis.com/v1/messages",
                                data=postData,
                                headers=HTTPHeaders,
                            )
                    else:
                        # Send error message without file
                        postData = {"roomId": roomIdToGetMessages, "text": "Error: Ansible"}
                        postData = json.dumps(postData)
                        HTTPHeaders = {"Authorization": "Bearer " + ACCESS_TOKEN, "Content-Type": "application/json"}
                        r = requests.post(
                            "https://webexapis.com/v1/messages",
                            data=postData,
                            headers=HTTPHeaders,
                        )
                else:
                    # Send regular text message (for other commands)
                    postData = {"roomId": roomIdToGetMessages, "text": str(responseMessage)}
                    postData = json.dumps(postData)
                    HTTPHeaders = {"Authorization": "Bearer " + ACCESS_TOKEN, "Content-Type": "application/json"}   
                    r = requests.post(
                        "https://webexapis.com/v1/messages",
                        data=postData,
                        headers=HTTPHeaders,
                    )
                
                if not r.status_code == 200:
                    print(f"Error sending message to Webex. Status code: {r.status_code}")
                    print(f"Response: {r.text}")
            except Exception as e:
                print(f"Error sending message to Webex: {e}")
    
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
        break
    except Exception as e:
        print(f"Error in main loop: {e}")
        # Continue running even if there's an error
        time.sleep(1)
        continue
