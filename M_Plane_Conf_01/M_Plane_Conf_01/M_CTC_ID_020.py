from logging import exception
import socket
import sys
import os
import warnings
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
import STARTUP
import lxml.etree
import Config
import DHCP_CONF.Genrate_User_Pass as Genrate_User_Pass

OUTPUT_LIST = []


def FETCH_DATA(host, port, user, password):
    # Fetching all the interface
    with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent=False, look_for_keys=False) as m:
        u_name = '''
        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <users xmlns="urn:o-ran:user-mgmt:1.0">	
            </users>
        </filter>'''

        get_u = m.get(u_name).data_xml
        dict_u = xmltodict.parse(str(get_u))
        # STARTUP.STORE_DATA(user_name,OUTPUT_LIST=OUTPUT_LIST)
        s = xml.dom.minidom.parseString(get_u)
        #xml = xml.dom.minidom.parseString(user_name)

        xml_pretty_str = s.toprettyxml()

        return xml_pretty_str


def session_login(host, port, user, password, new_user, new_pswrd):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent=False, look_for_keys=False) as m:

            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                '\n\n\t\t********** Connect to the NETCONF Server ***********\n\n', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                "\n\n######### Test Procedure/Test Configuration #########\n\n", OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                "\n\n######### STEP 1 TER NETCONF client establishes a connection using a user account with nms privileges#########\n\n", OUTPUT_LIST=OUTPUT_LIST)
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

            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                "\n\n###########Step 2 TER NETCONF client attempts to configure a new user/password #####################\n\n", OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)

            STARTUP.STORE_DATA(
                '\n> edit-config  --target running --config --defop merge\n', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                '******* Replace with below xml ********', OUTPUT_LIST=OUTPUT_LIST)

            snip = f"""
                    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <users xmlns="urn:o-ran:user-mgmt:1.0">
                        <user>
                            <name>{new_user}</name>
                            <account-type>PASSWORD</account-type>
                            <password>{new_pswrd}</password>
                            <enabled>true</enabled>
                        </user>
                    </users>
                    </config>"""

            STARTUP.STORE_DATA(snip, OUTPUT_LIST=OUTPUT_LIST)

            try:
                data3 = m.edit_config(
                    target="running", config=snip, default_operation='merge')
                dict_data1 = xmltodict.parse(str(data3))
                STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(
                    '''\n\n######### RPC Reply #########\n\n''', OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                if dict_data1['nc:rpc-reply']['nc:ok'] == None:
                    return data3, 'Addition of new is complete...'
            except RPCError as e:
                if e.tag == 'access-denied':
                    STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(
                        "\n\n###########Step 3 NETCONF server replies rejecting the protocol operation with an 'access-denied' error#####################\n\n", OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('ERROR', OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(
                        f"{'tag' : ^20}{':' : ^10}{e.tag: ^10}", OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(
                        f"{'type' : ^20}{':' : ^10}{e.type: ^10}", OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(
                        f"{'severity' : ^20}{':' : ^10}{e.severity: ^10}", OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(
                        f"{'path' : ^20}{':' : ^10}{e.path: ^10}", OUTPUT_LIST=OUTPUT_LIST)
                #STARTUP.STORE_DATA(f"{'info' : <20}{':' : ^10}{e: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(
                        f"{'Description' : ^20}{':' : ^10}{e.message: ^10}", OUTPUT_LIST=OUTPUT_LIST)
                #STARTUP.STORE_DATA(f"{'tag' : <20}{':' : ^10}{e.errlist: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                else:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    return [e.tag, e.type, e.severity, e.path, e.message, exc_tb.tb_lineno]
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




def test_Main_Func_020():
    # give the input configuration in xml file format
    #xml_1 = open('o-ran-hardware.xml').read()
    # give the input in the format hostname, port, username, password
    STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
    new_user = Genrate_User_Pass.genrate_username()
    new_pswrd = Genrate_User_Pass.genrate_password()
    STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
    try:
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        USER_SUDO = Config.details['SUDO_USER']
        PSWRD_SUDO = Config.details['SUDO_PASS']
        USER_N = Config.details['NMS_USER']
        PSWRD = Config.details['NMS_PASS']
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        m = manager.call_home(host='', port=4334, hostkey_verify=False,
                              username=USER_N, password=PSWRD, allow_agent=False, look_for_keys=False)
        # ['ip_address', 'TCP_Port']
        li = m._session._transport.sock.getpeername()
        sid = m.session_id
        if m:
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.kill_ssn(li[0], 830, USER_SUDO, PSWRD_SUDO, sid)
            time.sleep(10)
            RU_Details = STARTUP.demo(li[0], 830, USER_SUDO, PSWRD_SUDO)

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
        * @file    M_CTC_ID_020_.txt
        * @brief    M PLANE O-RAN  Conformance
        * @credits Created based on Software Release for GIRU_revC-- v{val[2]}
                            
                            '''
                    STARTUP.STORE_DATA(CONFIDENTIAL, OUTPUT_LIST=OUTPUT_LIST)

            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                '\n\n\t\t********** Initial Get ***********\n\n', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(f'''\n> connect --ssh --host {li[0]} --port 830 --login {USER_SUDO}
                    Interactive SSH Authentication
                    Type your password:
                    Password: 
                    \n''', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                "\n> get --filter-xpath /o-ran-usermgmt:users/user\n", OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            get_filter = FETCH_DATA(li[0], 830, USER_SUDO, PSWRD_SUDO)
            STARTUP.STORE_DATA(get_filter, OUTPUT_LIST=OUTPUT_LIST)
            time.sleep(5)
            res = session_login(li[0], 830, USER_N, PSWRD, new_user, new_pswrd)
            STARTUP.GET_SYSTEM_LOGS(li[0], USER_N, PSWRD,OUTPUT_LIST)
            if res == None:
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
                    f"{'FAIL_REASON' : <50}{'=' : ^20}{res : ^20}", OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(
                    f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}", OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                # raise '\t\tFAIL-REASON\t\n {}'.format(res)
                return res

            else:
                # For Capturing the logs
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(
                    f"{'FAIL_REASON' : <50}{'=' : ^20}{res : ^20}", OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(
                    f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}", OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                # raise '\t\tFAIL-REASON\t\n {}'.format(res)
                return res
        # m.close_session()

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
        STARTUP.CREATE_LOGS('M_CTC_ID_020', OUTPUT_LIST)


if __name__ == "__main__":
    test_Main_Func_020()
