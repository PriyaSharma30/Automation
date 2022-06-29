import sys, os, warnings
import socket
from ncclient import manager
import xmltodict,Config
import paramiko
from datetime import datetime




def kill_ssn(host, port, user, password,sid):
    with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent = False , look_for_keys = False) as m:
        m.kill_session(session_id =sid)


def demo(host, port, user, password):
    with manager.connect(host=host, port=port, username=user , hostkey_verify=False, password=password, timeout = 60, allow_agent = False , look_for_keys = False) as m:
        


        # Fetching all the users
        u_name = '''
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <users xmlns="urn:o-ran:user-mgmt:1.0">	
            </users>
        </filter>'''


        get_u = m.get(u_name).data_xml
        dict_u = xmltodict.parse(str(get_u))
        try:
            users = dict_u['data']['users']['user']
            u = {}
            for i in users:
                name = i['name']                
                pswrd = i['password']
                if name:
                    u[name] = u.get(pswrd,0)
                
        except:
            pass

        sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-inventory xmlns="urn:o-ran:software-management:1.0">
            </software-inventory>
            </filter>'''
        s = {}
        slot_names = m.get(sw_inv).data_xml
        dict_slot = xmltodict.parse(str(slot_names))
        try:
            slots = dict_slot['data']['software-inventory']['software-slot']
            for k in slots:
                active_s = k['active']
                running_s = k['running']
                slot_name = k['name']
                sw_build = k['build-version']
                slot_status = k['status']
                s[slot_name] = [active_s,running_s,sw_build,slot_status]

        except:
            print("User doesn't have SUDO permission")


        # Fetching all the interface
        v_name1 = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                </interfaces>
                </filter>
        '''

        interface_name = m.get_config('running', v_name1).data_xml
        dict_interface = xmltodict.parse(str(interface_name))
        Interfaces = dict_interface['data']['interfaces']['interface']
        #STORE_DATA(Interfaces,OUTPUT_LIST)
        d = {}
        ma = {}

        
        for i in Interfaces:
            name = i['name']
            mac = i['mac-address']['#text']
            try:
                IP_ADD = i['ipv4']['address']['ip']
                if name:
                    d[name] = IP_ADD
                    ma[name] = mac
            except:
                pass


        
        host = host
        port = 22
        user1 = Config.details['SUPER_USER']
        pswrd = Config.details['SUPER_USER_PASS']

        command = "cd {}; rm -rf {};".format(Config.details['SYSLOG_PATH'],Config.details['syslog_name'])
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, user1, pswrd)

        stdin, stdout, stderr = ssh.exec_command(command)
        return [u, s, ma, d]


def GET_SYSTEM_LOGS(host,user, pswrd,OUTPUT_LIST):
    host = host
    port = 22
    username = user
    password = pswrd
    STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
    STORE_DATA('\t\t\t\tSYSTEM LOGS',OUTPUT_LIST=OUTPUT_LIST)
    STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)

    command = "cd {}; cat {};".format(Config.details['SYSLOG_PATH'],Config.details['syslog_name'])
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)

    stdin, stdout, stderr = ssh.exec_command(command)
    lines = stdout.readlines()
    for i in lines:
        STORE_DATA("{}".format(i),OUTPUT_LIST=OUTPUT_LIST)


def GET_LOGS_NAME(TC_Name):
    s = datetime.now()
    return f"{TC_Name}{s.hour}{s.minute}{s.second}{s.day}{s.month}_{s.year}"

######################## Use This when more then 2 args in STORE_DATA functio,OUTPUT_LISTn
def STORE_DATA(*data,OUTPUT_LIST):
    print(*data)
    # OUTPUT_LIST.append(*data)
    print(''.join([*data]))
    OUTPUT_LIST.append('{}\n'.format(''.join([*data])))
    return OUTPUT_LIST




def CREATE_LOGS(File_name,OUTPUT_LIST):
    LOG_NAME = GET_LOGS_NAME(File_name)
    local_DIR = os.path.dirname(__file__)
    ABS_Path = os.path.join(local_DIR,'LOGS')
    file1 = open(f"{ABS_Path}/{LOG_NAME}.txt","w+")
    # STORE_DATA(OUTPUT_LIST,OUTPUT_LIST)
    for datas in OUTPUT_LIST:
        file1.writelines(datas)
    file1.close()
