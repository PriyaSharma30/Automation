from getpass import getpass
from logging import exception
import re
import socket
import sys, os, warnings
#warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager
import string
from ncclient.operations.rpc import RPCError
from ncclient.transport.errors import SSHError
import paramiko
import xmltodict
import time
import xml.dom.minidom  
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import lxml.etree
import Config,STARTUP, DHCP_CONF.Genrate_User_Pass as Genrate_User_Pass
import re

OUTPUT_LIST = []

def FETCH_DATA(host, port, user, password):
    with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent = False , look_for_keys = False) as m:
        
        
        # Fetching all the users
        u_name = '''
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <users xmlns="urn:o-ran:user-mgmt:1.0">	
            </users>
        </filter>'''


        get_u = m.get(u_name).data_xml
        dict_u = xmltodict.parse(str(get_u))
        #STARTUP.STORE_DATA(user_name,OUTPUT_LIST=OUTPUT_LIST)
        s = xml.dom.minidom.parseString(get_u)
        #xml = xml.dom.minidom.parseString(user_name)

        xml_pretty_str = s.toprettyxml()

        
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
        #STARTUP.STORE_DATA(Interfaces,OUTPUT_LIST=OUTPUT_LIST)
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

        
        return ma, xml_pretty_str
        

def session_login(host,port,name,pas1,USER_N, PSWRD):
    try:
        with manager.connect(host=host, port=port, username=USER_N, hostkey_verify=False, password=PSWRD, allow_agent = False , look_for_keys = False) as m:    
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STATUS = f'''\n> connect --ssh --host {host} --port 830 --login {USER_N}
                    Interactive SSH Authentication
                    Type your password:
                    Password: 
                    > status
                    Current NETCONF session:
                    ID          : {m.session_id}
                    Host        : {host}
                    Port        : {port}
                    Transport   : SSH
                    Capabilities:
                    \n'''
            STARTUP.STORE_DATA(STATUS,OUTPUT_LIST=OUTPUT_LIST)
            for i in m.server_capabilities:
                STARTUP.STORE_DATA("\t",i,OUTPUT_LIST=OUTPUT_LIST)

            rpc=m.create_subscription()
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('subscribe',OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            dict_data1 = xmltodict.parse(str(rpc))
            if dict_data1['nc:rpc-reply']['nc:ok']== None:
                STARTUP.STORE_DATA('\nOk\n',OUTPUT_LIST=OUTPUT_LIST)
            
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            u_name = '''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">	
                    </users>
                    </filter>
                    '''

            
            user_name = m.get_config('running', u_name).data_xml
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA("\n\n######### Test Procedure/Test Configuration #########\n\n",OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA("\n> get --filter-xpath /o-ran-usermgmt:users/user\n",OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            x = xml.dom.minidom.parseString(user_name)
            #xml = xml.dom.minidom.parseString(user_name)

            xml_pretty_str = x.toprettyxml()

            STARTUP.STORE_DATA(xml_pretty_str,OUTPUT_LIST=OUTPUT_LIST)

            
            ad_us = f'<user-name>{name}</user-name>'
            nacm_file = open('Yang_xml/nacm_swm.xml').read()
            nacm_file = nacm_file.format(add_swm = ad_us)
            
            snippet = f"""
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">
                        <user>
                            <name>{name}</name>
                            <account-type>PASSWORD</account-type>
                            <password>{pas1}</password>
                            <enabled>true</enabled>
                        </user>
                    </users>
                    </config>"""

            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA("\n\n######### STEP 1 TER NETCONF client establishes a connection using a user account with swm privileges#########\n\n",OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('\n> edit-config  --target running --config --defop merge\n',OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('******* Replace with below xml ********',OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(snippet,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            
            data1 = m.edit_config(target="running" , config=snippet)
            dict_data1 = xmltodict.parse(str(data1))
            if dict_data1['nc:rpc-reply']['nc:ok']== None:
                STARTUP.STORE_DATA('\nOk\n',OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('******* NOTIFICATIONS ********',OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            while True:
                n = m.take_notification(timeout=3)
                if n == None:
                    break
                notify=n.notification_xml
                s = xml.dom.minidom.parseString(notify)
                #xml = xml.dom.minidom.parseString(user_name)

                xml_pretty_str = s.toprettyxml()

                STARTUP.STORE_DATA(xml_pretty_str,OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            

            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('\n> edit-config  --target running --config --defop merge\n',OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('******* Replace with below xml ********',OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            
            STARTUP.STORE_DATA(nacm_file,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        
            data2 = m.edit_config(target="running" , config=nacm_file, default_operation = 'merge')
            dict_data2 = xmltodict.parse(str(data2))
            if dict_data2['nc:rpc-reply']['nc:ok']== None:
                STARTUP.STORE_DATA('\nOk\n',OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            while True:
                
                n = m.take_notification(timeout=5)
                if n == None:
                    break
                notify = n.notification_xml
                dict_n = xmltodict.parse(str(notify))
                try:
                    sid = dict_n['notification']['netconf-config-change']['changed-by']['session-id']
                    # STARTUP.STORE_DATA(sid,OUTPUT_LIST=OUTPUT_LIST)
                    if sid == m.session_id:
                        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                        STARTUP.STORE_DATA("\n\t\t ******* NOTIFICATIONS *******\n",OUTPUT_LIST=OUTPUT_LIST)
                        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                        x = xml.dom.minidom.parseString(notify)
                        #xml = xml.dom.minidom.parseString(user_name)

                        xml_pretty_str = x.toprettyxml()

                        STARTUP.STORE_DATA(xml_pretty_str,OUTPUT_LIST=OUTPUT_LIST)
                        STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                        break
                except:
                    pass
            
            STARTUP.STORE_DATA("\n> get --filter-xpath /ietf-netconf-acm:nacm/groups\n",OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            u_name = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <nacm xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-acm">
                    <groups>
                    </groups>
                </nacm>
                </filter>
                '''
            user_name = m.get_config('running', u_name).data_xml
            #STARTUP.STORE_DATA(user_name,OUTPUT_LIST=OUTPUT_LIST)
            s = xml.dom.minidom.parseString(user_name)
            #xml = xml.dom.minidom.parseString(user_name)

            xml_pretty_str = s.toprettyxml()

            ################# Check whether users add in nacm or not #################
            # group_n = xmltodict.parse(str(user_name))
            # group_name = group_n['data']['nacm']['groups']['group']
            # for i in group_name:
            #     STARTUP.STORE_DATA(i['name'],OUTPUT_LIST=OUTPUT_LIST)
            #     if i['name'] == 'swm':
            #         if name not in i['user-name']:
            #             STARTUP.STORE_DATA(xml_pretty_str,OUTPUT_LIST=OUTPUT_LIST)
            #             return "User didn't merge in 'nms' privilege"
            #     else:
            #         return "User didn't merge in except these privilege ['sudo', 'fm-pm', 'nms', 'swm'] privilege"

            STARTUP.STORE_DATA(xml_pretty_str,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        
            u_name = '''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">	
                    </users>
                    </filter>
                    '''
            user_name = m.get_config('running', u_name).data_xml
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA("\n> get --filter-xpath /o-ran-usermgmt:users/user\n",OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            s = xml.dom.minidom.parseString(user_name)
            xml_pretty_str = s.toprettyxml()
            
            ########## Check whether users are merge ###########
            user_n = xmltodict.parse(str(user_name))
            USERs_info = user_n['data']['users']['user']
            User_list = []
            for user in USERs_info:
                User_list.append(user['name'])
            if  name not in User_list:
                STARTUP.STORE_DATA(xml_pretty_str,OUTPUT_LIST=OUTPUT_LIST)
                return "Users didn't merge..."
            else:
                STARTUP.STORE_DATA(xml_pretty_str,OUTPUT_LIST=OUTPUT_LIST)


    except RPCError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                return [e.tag, e.type, e.severity, e.path ,e.message,exc_tb.tb_lineno]

    except FileNotFoundError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA("*"*30+'FileNotFoundError'+"*"*30,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA("\t\t{}".format(e),OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        return f'No such file or directory : {e.filename}\nError occured in line number {exc_tb.tb_lineno}'
    
    except lxml.etree.XMLSyntaxError as e:
        
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA("*"*30+'XMLSyntaxError'+"*"*30,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA("\t\t{}".format(e),OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        return  f"{e} \nError occured in line number {exc_tb.tb_lineno}"
    
    except Exception as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA("\t\t{}".format(e),OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        return  f"{e} \nError occured in line number {exc_tb.tb_lineno}"

    

    try:
        with manager.connect(host=host, port=port, username=name, hostkey_verify=False, password=pas1, allow_agent = False , look_for_keys = False) as ms:
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('\n\n\t\t********** Connect with new user ***********\n\n',OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            cmd = f'''
            > connect --ssh --host {host} --port 830 --login {name}
            Interactive SSH Authentication
            Type your password:
            Password: 
            '''
            STARTUP.STORE_DATA(cmd,OUTPUT_LIST=OUTPUT_LIST)

            
            proc_xml = open('Yang_xml/sync.xml').read()
            
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA("\n\n###########Step 2 TER NETCONF client attempts to configure a new o-ran-sync.yang on the NETCONF server#####################\n\n",OUTPUT_LIST=OUTPUT_LIST)


            pro = f'''
            <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                {proc_xml}
            </config>
            '''

            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('\n> edit-config  --target running --config --defop replace\n',OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('******* Replace with below xml ********',OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)

            STARTUP.STORE_DATA(proc_xml,OUTPUT_LIST=OUTPUT_LIST)

            try:
                data3 = ms.edit_config(target="running" , config=pro, default_operation = 'replace')
                if data3:
                    return f'\t*******Configuration are pushed*******\n{data3}'
            except RPCError as e:
                if e.tag == 'access-denied':
                    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA("\n\n###########Step 3 NETCONF server replies rejecting the protocol operation with an 'access-denied' error#####################\n\n",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('ERROR',OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'tag' : ^20}{':' : ^10}{e.tag: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'type' : ^20}{':' : ^10}{e.type: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'severity' : ^20}{':' : ^10}{e.severity: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'path' : ^20}{':' : ^10}{e.path: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                #STARTUP.STORE_DATA(f"{'info' : <20}{':' : ^10}{e: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'Description' : ^20}{':' : ^10}{e.message: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                #STARTUP.STORE_DATA(f"{'tag' : <20}{':' : ^10}{e.errlist: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                else:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    return [e.tag, e.type, e.severity, e.path ,e.message,exc_tb.tb_lineno]

    except RPCError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                return [e.tag, e.type, e.severity, e.path ,e.message,exc_tb.tb_lineno]

    except FileNotFoundError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA("*"*30+'FileNotFoundError'+"*"*30,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA("\t\t{}".format(e),OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        return f'No such file or directory : {e.filename}\nError occured in line number {exc_tb.tb_lineno}'
    
    except lxml.etree.XMLSyntaxError as e:
        
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA("*"*30+'XMLSyntaxError'+"*"*30,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA("\t\t{}".format(e),OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        return  f"{e} \nError occured in line number {exc_tb.tb_lineno}"
    
    except Exception as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA("\t\t{}".format(e),OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        return  f"{e} \nError occured in line number {exc_tb.tb_lineno}"



def test_Main_Func_022():
    #give the input configuration in xml file format
    #xml_1 = open('o-ran-hardware.xml').read()
    #give the input in the format hostname, port, username, password
    try:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        USER_N = Config.details['SUDO_USER']
        PSWRD = Config.details['SUDO_PASS']
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD, allow_agent = False , look_for_keys = False)
        li = m._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
        sid = m.session_id
        if m:
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,sid)
            
            RU_Details = STARTUP.demo(li[0],830,  USER_N, PSWRD)
            
            for key, val in RU_Details[1].items():
                    if val[0] == 'true' and val[1] == 'true':
                        CONFIDENTIAL = f'''**
        * --------------------------------------------------------------------------------------------
        *              VVDN CONFIDENTIAL
        *  -----------------------------------------------------------------------------------------------
        * Copyright (c) 2016 - 2020 VVDN Technologies Pvt Ltd.
        * All rights reserved
        *
        * NOTICE:
        *  This software is confidential and proprietary to VVDN Technologies.
        *  No part of this software may be reproduced, stored, transmitted,
        *  disclosed or used in any form or by any means other than as expressly
        *  provided by the written Software License Agreement between
        *  VVDN Technologies and its license.
        *
        * PERMISSION:
        *  Permission is hereby granted to everyone in VVDN Technologies
        *  to use the software without restriction, including without limitation
        *  the rights to use, copy, modify, merge, with modifications.
        *
        * ------------------------------------------------------------------------------------------------
        * @file    M_CTC_ID_022_.txt
        * @brief    M PLANE O-RAN  Conformance
        * @credits Created based on Software Release for GIRU_revC-- v{val[2]}
                            
                            '''
                        STARTUP.STORE_DATA(CONFIDENTIAL,OUTPUT_LIST=OUTPUT_LIST)


            macs,get_filter = FETCH_DATA(li[0],830,  USER_N, PSWRD)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            name = Genrate_User_Pass.genrate_username()
            pas1 = Genrate_User_Pass.genrate_password()
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            time.sleep(5)
            res = session_login(li[0],830,name,pas1,USER_N, PSWRD)
            time.sleep(5)
            STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,OUTPUT_LIST)
            if res:
                host = li[0]
                port = 22
                username = USER_N
                password = PSWRD
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('\t\t\t\tSYSTEM LOGS',OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)

                command = "cd {}; cat {};".format(Config.details['SYSLOG_PATH'],Config.details['syslog_name'])
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, port, username, password)

                stdin, stdout, stderr = ssh.exec_command(command)
                lines = stdout.readlines()
                for i in lines:
                    STARTUP.STORE_DATA([i,'\n'],OUTPUT_LIST=OUTPUT_LIST)
                if type(res) == list:
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*20,'FAIL_REASON','*'*20,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    Error_Info = '''ERROR\n\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tDescription' \t: \t{}'''.format(*map(str,res))
                    STARTUP.STORE_DATA(Error_Info,OUTPUT_LIST=OUTPUT_LIST)
                    # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    return Error_Info
                else:
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'FAIL_REASON' : <50}{'=' : ^20}{res : ^20}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    return res
                    # raise '\t\tFAIL-REASON\t\n {}'.format(res)

                
            else:
                # For Capturing the logs                
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(f"{'STATUS' : <50}{'=' : ^20}{'PASS' : ^20}",OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                return True
                
            

    except socket.timeout as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
            e)
        STARTUP.STORE_DATA(Error,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
        return Error
        # raise socket.timeout('{}: SSH Socket connection lost....'.format(e)) from None

    except errors.SSHError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        Error = '{} : SSH Socket connection lost....'.format(e)
        STARTUP.STORE_DATA(Error,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
        return Error
        # raise errors.SSHError('{}: SSH Socket connection lost....'.format(e)) from None

    except errors.AuthenticationError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        Error = "{} : Invalid username/password........".format(e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
        # raise f'{e} : Invalid username/password........'

    except NoValidConnectionsError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
        Error = '{} : ...'.format(e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        return Error
        # raise e

    except TimeoutError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
        Error = '{} : Call Home is not initiated, Timout Expired....'.format(e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        return Error
        # raise f'{e} : Call Home is not initiated, Timout Expired....'

    except SessionCloseError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
        Error = "{} : Unexpected_Session_Closed....".format(e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        return Error
        # raise f'{e},Unexpected_Session_Closed....'

    except TimeoutExpiredError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
        Error = "{} : TimeoutExpiredError....".format(e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        return Error
        # raise e

    except OSError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
        Error = '{} : Call Home is not initiated, Please wait for sometime........'.format(
            e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        return Error
        # raise Exception('{} : Please wait for sometime........'.format(e)) from None

    except Exception as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA(e,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        return e
        # raise Exception('{}'.format(e)) from None

    finally:
        STARTUP.CREATE_LOGS('M_CTC_ID_022',OUTPUT_LIST)


if __name__ == "__main__":
    test_Main_Func_022()
