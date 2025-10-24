from ncclient import manager
import xmltodict


def create(router_ip):
    # Connect to the router
    m = manager.connect(
        host=router_ip,
        port=830,
        username="admin",
        password="cisco",
        hostkey_verify=False
    )
    
    netconf_config = """
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback66070077</name>
                <description>Loopback Interface 66070077</description>
                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
                <enabled>true</enabled>
                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                    <address>
                        <ip>172.0.77.1</ip>
                        <netmask>255.255.255.0</netmask>
                    </address>
                </ipv4>
            </interface>
        </interfaces>
    </config>
    """

    try:
        netconf_reply = m.edit_config(target="running", config=netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        m.close_session()
        if '<ok/>' in xml_data:
            return "Interface loopback 66070077 is created successfully using Netconf"
        else:
            return "Cannot create: Interface loopback 66070077 (checked by Netconf)"
    except Exception as e:
        print(f"Error: {e}")
        return "Cannot create: Interface loopback 66070077 (checked by Netconf)"


def delete(router_ip):
    # Connect to the router
    m = manager.connect(
        host=router_ip,
        port=830,
        username="admin",
        password="cisco",
        hostkey_verify=False
    )
    
    netconf_config = """
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface operation="delete">
                <name>Loopback66070077</name>
            </interface>
        </interfaces>
    </config>
    """

    try:
        netconf_reply = m.edit_config(target="running", config=netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        m.close_session()
        if '<ok/>' in xml_data:
            return "Interface loopback 66070077 is deleted successfully using Netconf"
        else:
            return "Cannot delete: Interface loopback 66070077 (checked by Netconf)"
    except Exception as e:
        print(f"Error: {e}")
        return "Cannot delete: Interface loopback 66070077 (checked by Netconf)"


def enable(router_ip):
    # Connect to the router
    m = manager.connect(
        host=router_ip,
        port=830,
        username="admin",
        password="cisco",
        hostkey_verify=False
    )
    
    netconf_config = """
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback66070077</name>
                <enabled>true</enabled>
            </interface>
        </interfaces>
    </config>
    """

    try:
        netconf_reply = m.edit_config(target="running", config=netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        m.close_session()
        if '<ok/>' in xml_data:
            return "Interface loopback 66070077 is enabled successfully using Netconf"
        else:
            return "Cannot enable: Interface loopback 66070077 (checked by Netconf)"
    except Exception as e:
        print(f"Error: {e}")
        return "Cannot enable: Interface loopback 66070077 (checked by Netconf)"


def disable(router_ip):
    # Connect to the router
    m = manager.connect(
        host=router_ip,
        port=830,
        username="admin",
        password="cisco",
        hostkey_verify=False
    )
    
    netconf_config = """
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback66070077</name>
                <enabled>false</enabled>
            </interface>
        </interfaces>
    </config>
    """

    try:
        netconf_reply = m.edit_config(target="running", config=netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        m.close_session()
        if '<ok/>' in xml_data:
            return "Interface loopback 66070077 is shutdowned successfully using Netconf"
        else:
            return "Cannot shutdown: Interface loopback 66070077 (checked by Netconf)"
    except Exception as e:
        print(f"Error: {e}")
        return "Cannot shutdown: Interface loopback 66070077 (checked by Netconf)"


def status(router_ip):
    # Connect to the router
    m = manager.connect(
        host=router_ip,
        port=830,
        username="admin",
        password="cisco",
        hostkey_verify=False
    )
    
    netconf_filter = """
    <filter>
        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback66070077</name>
            </interface>
        </interfaces-state>
    </filter>
    """

    try:
        # Use Netconf get operation to get interfaces-state information
        netconf_reply = m.get(filter=netconf_filter)
        print(netconf_reply)
        netconf_reply_dict = xmltodict.parse(netconf_reply.xml)
        m.close_session()

        # if there data return from netconf_reply_dict is not null, the operation-state of interface loopback is returned
        if netconf_reply_dict.get('rpc-reply', {}).get('data', {}).get('interfaces-state', {}).get('interface'):
            # extract admin_status and oper_status from netconf_reply_dict
            interface_data = netconf_reply_dict['rpc-reply']['data']['interfaces-state']['interface']
            admin_status = interface_data.get('admin-status', 'down')
            oper_status = interface_data.get('oper-status', 'down')
            
            if admin_status == 'up' and oper_status == 'up':
                return "Interface loopback 66070077 is enabled (checked by Netconf)"
            elif admin_status == 'down' and oper_status == 'down':
                return "Interface loopback 66070077 is disabled (checked by Netconf)"
        else: # no operation-state data
            return "No Interface loopback 66070077 (checked by Netconf)"
    except Exception as e:
        print(f"Error: {e}")
        return "No Interface loopback 66070077 (checked by Netconf)"
