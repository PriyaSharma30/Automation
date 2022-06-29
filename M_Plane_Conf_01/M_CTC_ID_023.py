from getpass import getpass
from logging import exception
from socket import timeout, socket
import sys, os, warnings
import time
from ncclient import manager
from ncclient.transport import errors
from ncclient.operations.rpc import RPCError
from ncclient.transport import session
from ncclient.transport.errors import SSHError
from ncclient.transport.session import Session
import xmltodict
import xml.dom.minidom
import paramiko
from paramiko.ssh_exception import AuthenticationException
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import lxml.etree
import Config
import STARTUP, DHCP_CONF.Genrate_User_Pass as Genrate_User_Pass

OUTPUT_LIST = []


def Create_user(host, port, nam, pas1,USER_N, PSWRD):
    try:
        with manager.connect(host=host, port=port, username=USER_N, hostkey_verify=False, password=PSWRD, allow_agent = False , look_for_keys = False) as m:

            
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA("Step 1 and 2: The TER NETCONF Client establishes connection and creates an account for new user using o-ran-user9 mgmt.yang",OUTPUT_LIST=OUTPUT_LIST)
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

        
            snippet = f"""
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">
                        <user>
                            <name>{nam}</name>
                            <account-type>PASSWORD</account-type>
                            <password>{pas1}</password>
                            <enabled>true</enabled>
                        </user>
                    </users>
                    </config>"""

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
                n = m.take_notification(timeout=5)
                if n == None:
                    break
                notify=n.notification_xml
                s = xml.dom.minidom.parseString(notify)
                #xml = xml.dom.minidom.parseString(user_name)

                xml_pretty_str = s.toprettyxml()

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
            STARTUP.STORE_DATA("Step 3 and 4: The TER NETCONF Client retrieves a list of users",OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA("\n> get --filter-xpath /o-ran-usermgmt:users/user\n",OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            x = xml.dom.minidom.parseString(user_name)
            #xml = xml.dom.minidom.parseString(user_name)

            xml_pretty_str = x.toprettyxml()

            ########## Check whether users are merge ###########
            user_n = xmltodict.parse(str(user_name))
            USERs_info = user_n['data']['users']['user']
            User_list = []
            for user in USERs_info:
                User_list.append(user['name'])
            if  nam not in User_list:
                STARTUP.STORE_DATA(xml_pretty_str,OUTPUT_LIST=OUTPUT_LIST)
                return "Users didn't merge..."
            else:
                STARTUP.STORE_DATA(xml_pretty_str,OUTPUT_LIST=OUTPUT_LIST)

            
            ad_us = f'<user-name>{nam}</user-name>'
            nacm_file = open('Yang_xml/nacm_sudo.xml').read()
            nacm_file = nacm_file.format(add_sudo = ad_us)
            

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

 
            

def Call_Home(host,port,name,pas1):
    
        # rpc=m.create_subscription()
    # time.sleep(5)
    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
    STARTUP.STORE_DATA('Step 5 and 6: NETCONF Server establishes a TCP connection and performs the Call Home procedure to the TER NETCONF Client using the same IP and VLAN.\n\n',OUTPUT_LIST=OUTPUT_LIST)
    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
    m1 = manager.call_home(host = '', port=4334, hostkey_verify=False,username = name, password = pas1, timeout = 60, allow_agent = False , look_for_keys = False)
    li = m1._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
    LISTEN = f'''> listen --ssh --login {name}
    Waiting 60s for an SSH Call Home connection on port 4334...'''
    STARTUP.STORE_DATA(LISTEN,OUTPUT_LIST=OUTPUT_LIST)
    try:
        if m1:
            query = 'yes'
            Authenticity =f'''The authenticity of the host '::ffff:{li[0]}' cannot be established.
            ssh-rsa key fingerSTARTUP.STORE_DATA is 59:9e:90:48:f1:d7:6e:35:e8:d1:f6:1e:90:aa:a3:83:a0:6b:98:5a,OUTPUT_LIST=OUTPUT_LIST.
            Are you sure you want to continue connecting (yes/no)? yes'''
            STARTUP.STORE_DATA(Authenticity,OUTPUT_LIST=OUTPUT_LIST)
            if query == 'yes':
                STARTUP.STORE_DATA(f'''\n{name}@::ffff:{li[0]} password: \n''',OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA("Step 7: TER NETCONF Client and O-RU NETCONF Server exchange capabilities through the NETCONF <hello> messages",OUTPUT_LIST=OUTPUT_LIST)
                
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                STATUS = f'''
                    > status
                    Current NETCONF session:
                    ID          : {m1.session_id}
                    Host        : {li[0]}
                    Port        : {li[1]}
                    Transport   : SSH
                    Capabilities:
                    '''
                STARTUP.STORE_DATA(STATUS,OUTPUT_LIST=OUTPUT_LIST)
                for i in m1.server_capabilities:
                    STARTUP.STORE_DATA(i,OUTPUT_LIST=OUTPUT_LIST)
                return m1.session_id
        else:
            m1.close()

    except socket.timeout as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA(e,': Call Home is not initiated....',OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        return e

    except Exception as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA(e,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        return e 

        



def test_Main_Func_023():
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
        
        # STARTUP.STORE_DATA(m._session._transport.sock.close(),OUTPUT_LIST=OUTPUT_LIST)
        sid = m.session_id
        
        STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,sid)
        if m:
            
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                
                RU_Details = STARTUP.demo(li[0],830, USER_N, PSWRD)
                
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
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
        * @file    M_CTC_ID_023_.txt
        * @brief    M PLANE O-RAN  Conformance
        * @credits Created based on Software Release for GIRU_revC-- v{val[2]}
                            
                            '''
                        STARTUP.STORE_DATA(CONFIDENTIAL,OUTPUT_LIST=OUTPUT_LIST)


                
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                name = Genrate_User_Pass.genrate_username()
                pas1 = Genrate_User_Pass.genrate_password()
                STARTUP.STORE_DATA(pas1,OUTPUT_LIST=OUTPUT_LIST)
                time.sleep(5)
                res = Create_user(li[0],830,name,pas1,USER_N, PSWRD)
                time.sleep(5)
                
                if res == None: 
                    time.sleep(5)
                    ssid = Call_Home(li[0],li[1],name,pas1)
                    STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,ssid)
                    time.sleep(10)
                    STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,OUTPUT_LIST)
                    
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'STATUS' : <50}{'=' : ^20}{'PASS' : ^20}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    return True

                elif type(res) == list:
                    STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,OUTPUT_LIST)
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

                elif type(res) == str:
                    STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'FAIL_REASON' : <50}{'=' : ^20}{res : ^20}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    # raise '\t\tFAIL-REASON\t\n {}'.format(res)
                    return res
                    
                else:
                    STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'FAIL_REASON' : <50}{'=' : ^20}{res : ^20}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    # raise '\t\tFAIL-REASON\t\n {}'.format(res)
                    return res
                    
                    
                    
    # except socket.timeout as e:
    #     STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
    #     Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
    #         e)
    #     STARTUP.STORE_DATA(Error,OUTPUT_LIST=OUTPUT_LIST)
    #     STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
    #     return Error
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
        STARTUP.CREATE_LOGS('M_CTC_ID_023',OUTPUT_LIST)


if __name__ == "__main__":
    test_Main_Func_023()
