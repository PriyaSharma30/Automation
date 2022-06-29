import socket
import sys
import os
import warnings
import time
from ncclient import manager
import string
from ncclient.operations.rpc import RPCError
from ncclient.transport.errors import SSHError
import paramiko
import xmltodict
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import lxml.etree
import xml.dom.minidom
from ncclient.transport import errors
import STARTUP
import Config
import DHCP_CONF.Genrate_User_Pass as Genrate_User_Pass


OUTPUT_LIST = []


def session_login(host, port, user, pswrd):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=pswrd, allow_agent=False, look_for_keys=False) as m:
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                "\n\n######### STEP 1. The TER NETCONF Client establishes a connection with the O-RU NETCONF Server. #########\n\n", OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                '\n\n\t\t********** Connect to the NETCONF Server ***********\n\n', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STATUS = f'''\n> connect --ssh --host {host} --port 830 --login {user}
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
            STARTUP.STORE_DATA(STATUS, OUTPUT_LIST=OUTPUT_LIST)
            for i in m.server_capabilities:
                STARTUP.STORE_DATA("\t", i, OUTPUT_LIST=OUTPUT_LIST)

            cap = m.create_subscription()
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('>subscribe', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            dict_data = xmltodict.parse(str(cap))
            if dict_data['nc:rpc-reply']['nc:ok'] == None:
                STARTUP.STORE_DATA('\nOk\n', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)

            u_name = '''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">	
                    </users>
                    </filter>
                    '''

            user_name = m.get_config('running', u_name).data_xml
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                "\n\n######### Test Procedure/Test Configuration #########\n\n", OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                "\n> get --filter-xpath /o-ran-usermgmt:users/user\n", OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            x = xml.dom.minidom.parseString(user_name)
            #xml = xml.dom.minidom.parseString(user_name)

            xml_pretty_str = x.toprettyxml()

            STARTUP.STORE_DATA(xml_pretty_str, OUTPUT_LIST=OUTPUT_LIST)

            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('''\n\n######### STEP 2. The TER NETCONF Client configures three new user accounts in addition to the default,OUTPUT_LIST=OUTPUT_LIST 
            sudo account already present and passwords these three accounts using o-ran-user.mgmt.yang#########\n\n''')
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            usrs = {}
            for i in range(1, 4):

                nam = Genrate_User_Pass.genrate_username()
                pas = Genrate_User_Pass.genrate_password()
                usrs[nam] = pas
            li = list(usrs.items())
            snippet = f"""
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">
                        <user>
                            <name>{li[0][0]}</name>
                            <account-type>PASSWORD</account-type>
                            <password>{li[0][1]}</password>
                            <enabled>true</enabled>
                        </user>
                        <user>
                            <name>{li[1][0]}</name>
                            <account-type>PASSWORD</account-type>
                            <password>{li[1][1]}</password>
                            <enabled>true</enabled>
                        </user>
                        <user>
                            <name>{li[2][0]}</name>
                            <account-type>PASSWORD</account-type>
                            <password>{li[2][1]}</password>
                            <enabled>true</enabled>
                        </user>
                    </users>
                    </config>"""

            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                '\n> edit-config  --target running --config --defop merge\n', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                '******* Replace with below xml ********', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(snippet, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)

            data1 = m.edit_config(target="running", config=snippet)
            dict_data1 = xmltodict.parse(str(data1))
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                '''\n\n######### RPC Reply #########\n\n''', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            if dict_data1['nc:rpc-reply']['nc:ok'] == None:
                STARTUP.STORE_DATA('\nOk\n', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
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
                        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                        STARTUP.STORE_DATA(
                            "\n\t\t NOTIFICATIONS \n", OUTPUT_LIST=OUTPUT_LIST)
                        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                        x = xml.dom.minidom.parseString(notify)
                        #xml = xml.dom.minidom.parseString(user_name)

                        xml_pretty_str = x.toprettyxml()

                        STARTUP.STORE_DATA(
                            xml_pretty_str, OUTPUT_LIST=OUTPUT_LIST)
                        STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                        break
                except:
                    pass

            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('''\n\n######### STEP 3. The TER NETCONF Client configures user account to group mappings for the three,OUTPUT_LIST=OUTPUT_LIST 
            new accounts using ietf-netconf-acm.yang respectively one with “nms”, one with “fm-pm” and one 
            with “swm” privilege. #########\n\n''')
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                '\n> edit-config  --target running --config --defop merge\n', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                '******* Replace with below xml ********', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)

            add_fm = f'<user-name>{li[0][0]}</user-name>'
            add_nms = f'<user-name>{li[1][0]}</user-name>'
            add_swm = f'<user-name>{li[2][0]}</user-name>'

            nacm_file = open('Yang_xml/M_CTC_ID_18.xml').read()
            nacm_file = nacm_file.format(
                add_swm=add_swm, add_fm=add_fm, add_nms=add_nms)
            STARTUP.STORE_DATA(nacm_file, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            data2 = m.edit_config(
                target="running", config=nacm_file, default_operation='merge')
            dict_data2 = xmltodict.parse(str(data2))
            STARTUP.STORE_DATA(
                '''\n\n######### STEP 4. The O-RU NETCONF Server confirms the operations for the above transactions #########\n\n''', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            if dict_data2['nc:rpc-reply']['nc:ok'] == None:
                STARTUP.STORE_DATA('\nOk\n', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
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
                        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                        STARTUP.STORE_DATA(
                            "\n\t\t NOTIFICATIONS \n", OUTPUT_LIST=OUTPUT_LIST)
                        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                        x = xml.dom.minidom.parseString(notify)
                        #xml = xml.dom.minidom.parseString(user_name)

                        xml_pretty_str = x.toprettyxml()

                        STARTUP.STORE_DATA(
                            xml_pretty_str, OUTPUT_LIST=OUTPUT_LIST)
                        STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                        break
                except:
                    pass

            STARTUP.STORE_DATA(
                "\n> get --filter-xpath /ietf-netconf-acm:nacm/groups\n", OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            u_name = '''
                <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <nacm xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-acm">
                    <groups>
                    </groups>
                </nacm>
                </filter>
                '''
            user_name = m.get_config('running', u_name).data_xml
            # STARTUP.STORE_DATA(user_name,OUTPUT_LIST=OUTPUT_LIST)
            s = xml.dom.minidom.parseString(user_name)
            xml_pretty_str = s.toprettyxml()

            ################# Check whether users add in nacm or not #################
            ADDED_USERS = list(usrs.keys())
            group_n = xmltodict.parse(str(user_name))
            group_name = group_n['data']['nacm']['groups']['group']
            j = 0
            for i in group_name:
                if i['name'] == 'sudo':
                    pass
                elif i['name'] in ['fm-pm', 'nms', 'swm']:
                    if ADDED_USERS[j] not in i['user-name']:
                        STARTUP.STORE_DATA(
                            xml_pretty_str, OUTPUT_LIST=OUTPUT_LIST)
                        return f"User didn't merge in {i['name']} privilege"
                    j += 1
                else:
                    STARTUP.STORE_DATA(xml_pretty_str, OUTPUT_LIST=OUTPUT_LIST)
                    return "User didn't merge in except these privilege ['sudo', 'fm-pm', 'nms', 'swm'] privilege"

            STARTUP.STORE_DATA(xml_pretty_str, OUTPUT_LIST=OUTPUT_LIST)

            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                '''\n\n######### STEP 5. The TER NETCONF Client retrieves a list of users from O-RU NETCONF Server. The newly created user accounts and mappings are validated. #########\n\n''', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            u_name = '''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">	
                    </users>
                    </filter>
                    '''
            user_name = m.get_config('running', u_name).data_xml

            STARTUP.STORE_DATA(
                "\n> get --filter-xpath /o-ran-usermgmt:users/user\n", OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            # STARTUP.STORE_DATA(user_name,OUTPUT_LIST=OUTPUT_LIST)
            s = xml.dom.minidom.parseString(user_name)
            #xml = xml.dom.minidom.parseString(user_name)

            xml_pretty_str = s.toprettyxml()

            ########## Check whether users are merge ###########
            user_n = xmltodict.parse(str(user_name))
            USERs_info = user_n['data']['users']['user']
            ADDED_USERS_R = ADDED_USERS[::-1]  # Reeverse of added_users
            LIST_User = []
            for _ in range(3):
                user1 = USERs_info.pop()
                LIST_User.append(user1['name'])

            if LIST_User != ADDED_USERS_R:
                STARTUP.STORE_DATA(xml_pretty_str, OUTPUT_LIST=OUTPUT_LIST)
                return "Users didn't merge..."
            else:
                STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(xml_pretty_str, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)

    except RPCError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        return [e.tag, e.type, e.severity, e.path, e.message, exc_tb.tb_lineno]

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




def test_MAIN_FUNC_018():
    try:
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        USER_N = Config.details['SUDO_USER']
        PSWRD = Config.details['SUDO_PASS']
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        m = manager.call_home(host='', port=4334, hostkey_verify=False,
                              username=USER_N, password=PSWRD, allow_agent=False, look_for_keys=False)
        li = m._session._transport.sock.getpeername()
        sid = m.session_id
        if m:
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.kill_ssn(li[0], 830, USER_N, PSWRD, sid)
            time.sleep(10)
            RU_Details = STARTUP.demo(li[0], 830, USER_N, PSWRD)

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
        * @file    M_CTC_ID_018_.txt
        * @brief    M PLANE O-RAN  Conformance
        * @credits Created based on Software Release for GIRU_revC-- v{val[2]}
                            
                            '''
                    STARTUP.STORE_DATA(CONFIDENTIAL, OUTPUT_LIST=OUTPUT_LIST)

            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            time.sleep(5)
            res = session_login(li[0], 830, USER_N, PSWRD)
            time.sleep(5)
            STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,OUTPUT_LIST)
            if res == None:
                # For Capturing the logs
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(
                    f"{'STATUS' : <50}{'=' : ^20}{'PASS' : ^20}", OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                return True

            elif type(res) == list:
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*20, 'FAIL_REASON',
                                   '*'*20, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                Error_Info = '''ERROR\n\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tDescription' \t: \t{}'''.format(
                    *map(str, res))
                STARTUP.STORE_DATA(Error_Info, OUTPUT_LIST=OUTPUT_LIST)
                # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(
                    f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}", OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                return Error_Info

            elif type(res) == str:
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(
                    f"{'FAIL_REASON' : <20}{':' : ^10}{res: ^10}", OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                # raise '\t\tFAIL-REASON\t\n {}'.format(res)
                STARTUP.STORE_DATA(
                    f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}", OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                return res

            else:
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(
                    f"{'FAIL_REASON' : <20}{':' : ^10}{res: ^10}", OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                # raise '\t\tFAIL-REASON\t\n {}'.format(res)
                STARTUP.STORE_DATA(
                    f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}", OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                return res

    except socket.timeout as e:
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
            e)
        STARTUP.STORE_DATA(Error, OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", OUTPUT_LIST=OUTPUT_LIST)
        return Error
        # raise socket.timeout('{}: SSH Socket connection lost....'.format(e)) from None

    except errors.SSHError as e:
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        Error = '{} : SSH Socket connection lost....'.format(e)
        STARTUP.STORE_DATA(Error, OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", OUTPUT_LIST=OUTPUT_LIST)
        return Error
        # raise errors.SSHError('{}: SSH Socket connection lost....'.format(e)) from None

    except errors.AuthenticationError as e:
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        Error = "{} : Invalid username/password........".format(e)
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", OUTPUT_LIST=OUTPUT_LIST)
        # raise f'{e} : Invalid username/password........'

    except NoValidConnectionsError as e:
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", OUTPUT_LIST=OUTPUT_LIST)
        Error = '{} : ...'.format(e)
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        return Error
        # raise e

    except TimeoutError as e:
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", OUTPUT_LIST=OUTPUT_LIST)
        Error = '{} : Call Home is not initiated, Timout Expired....'.format(e)
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        return Error
        # raise f'{e} : Call Home is not initiated, Timout Expired....'

    except SessionCloseError as e:
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", OUTPUT_LIST=OUTPUT_LIST)
        Error = "{} : Unexpected_Session_Closed....".format(e)
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        return Error
        # raise f'{e},Unexpected_Session_Closed....'

    except TimeoutExpiredError as e:
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", OUTPUT_LIST=OUTPUT_LIST)
        Error = "{} : TimeoutExpiredError....".format(e)
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        return Error
        # raise e

    except OSError as e:
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", OUTPUT_LIST=OUTPUT_LIST)
        Error = '{} : Call Home is not initiated, Please wait for sometime........'.format(
            e)
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        return Error
        # raise Exception('{} : Please wait for sometime........'.format(e)) from None

    except Exception as e:
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(
            f"Error occured in line number {exc_tb.tb_lineno}", OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA(e, OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        return e
        # raise Exception('{}'.format(e)) from None

    finally:
        STARTUP.CREATE_LOGS('M_CTC_ID_018', OUTPUT_LIST)


if __name__ == "__main__":
    test_MAIN_FUNC_018()
