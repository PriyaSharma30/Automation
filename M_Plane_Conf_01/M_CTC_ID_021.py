from logging import exception
import re
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
import lxml.etree
import Config
import STARTUP
import re

OUTPUT_LIST = []


def FETCH_DATA(host, port, user, password):
    with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent=False, look_for_keys=False) as m:

        # Fetching all the users
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
        # STARTUP.STORE_DATA(Interfaces,OUTPUT_LIST=OUTPUT_LIST)
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


def session_login(host, port, user, password, ru_mac, du_mac, nam, ip_adr):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent=False, look_for_keys=False) as m:

            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                '\n\n\t\t********** Connect to the NETCONF Server ***********\n\n', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                "\n\n######### STEP 1 TER NETCONF client establishes a connection using a user account with fm-pm privileges#########\n\n", OUTPUT_LIST=OUTPUT_LIST)
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
                "\n\n###########Step 2 TER NETCONF client attempts to get the configuration of the o-ran-processing.yang model#####################\n\n", OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)

            STARTUP.STORE_DATA(
                '\n> edit-config  --target running --config --defop replace\n', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                '******* Replace with below xml ********', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)

            xml_file = open('Yang_xml/processing.xml').read()
            xml_file = xml_file.format(
                int_name=ip_adr, ru_mac=ru_mac, du_mac=du_mac, element_name=nam)

            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(xml_file, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            pro = f'''
            <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                {xml_file}
            </config>
            '''

            try:
                data3 = m.edit_config(
                    target="running", config=pro, default_operation='replace')
                dict_data1 = xmltodict.parse(str(data3))
                STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(
                    '''\n\n######### RPC Reply #########\n\n''', OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                if dict_data1['nc:rpc-reply']['nc:ok'] == None:
                    return 'o-ran-processing configuration is complete...'
            except RPCError as e:
                if e.tag == 'access-denied':
                    STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(
                        "\n\n###########Step 3 NETCONF server replies rejecting the protocol operation with an 'access-denied' error#####################\n\n", OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('ERROR', OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(
                        f"\t{'error-tag' : ^20}{':' : ^10}{e.tag: ^10}", OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(
                        f"\t{'error-type' : ^20}{':' : ^10}{e.type: ^10}", OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(
                        f"\t{'error-severity' : ^20}{':' : ^10}{e.severity: ^10}", OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(
                        f"\t{'path' : ^20}{':' : ^10}{e.path: ^10}", OUTPUT_LIST=OUTPUT_LIST)
                #STARTUP.STORE_DATA(f"{'info' : <20}{':' : ^10}{e: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(
                        f"\t{'Description' : ^20}{':' : ^10}{e.message: ^10}", OUTPUT_LIST=OUTPUT_LIST)
                #STARTUP.STORE_DATA(f"{'tag' : <20}{':' : ^10}{e.errlist: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                else:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    return [e.tag, e.type, e.severity, e.path, e.message, exc_tb.tb_lineno]

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




def isValidMACAddress(str):

    # Regex to check valid MAC address
    regex = ("^([0-9A-Fa-f]{2}[:-])" +
             "{5}([0-9A-Fa-f]{2})|" +
             "([0-9a-fA-F]{4}\\." +
             "[0-9a-fA-F]{4}\\." +
             "[0-9a-fA-F]{4})$")

    # Compile the ReGex
    p = re.compile(regex)

    # If the string is empty
    # return false
    if (str == None):
        return False

    # Return if the string
    # matched the ReGex
    if(re.search(p, str)):
        return True
    else:
        return False


def test_Main_Func_021():
    # give the input configuration in xml file format
    #xml_1 = open('o-ran-hardware.xml').read()
    # give the input in the format hostname, port, username, password
    try:

        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        USER_SUDO = Config.details['SUDO_USER']
        PSWRD_SUDO = Config.details['SUDO_PASS']
        USER_N = Config.details['FM_PM_USER']
        PSWRD = Config.details['FM_PM_PASS']
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        m = manager.call_home(host='', port=4334, hostkey_verify=False,
                              username=USER_N, password=PSWRD, allow_agent=False, look_for_keys=False)
        # ['ip_address', 'TCP_Port']
        li = m._session._transport.sock.getpeername()
        sid = m.session_id
        if m:
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.kill_ssn(li[0], 830, USER_SUDO, PSWRD_SUDO, sid)
            RU_Deatil = STARTUP.demo(li[0], 830, USER_SUDO, PSWRD_SUDO)

            for key, val in RU_Deatil[1].items():
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
        * @file    M_CTC_ID_021_.txt
        * @brief    M PLANE O-RAN  Conformance
        * @credits Created based on Software Release for GIRU_revC-- v{val[2]}
                            
                            '''
                    STARTUP.STORE_DATA(CONFIDENTIAL, OUTPUT_LIST=OUTPUT_LIST)

            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            for i in range(5):
                du_mac = Config.details['DU_MAC']
                val = isValidMACAddress(du_mac)
                if val == True:
                    break
                else:
                    STARTUP.STORE_DATA(
                        'Please provide valid mac address :\n', OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)

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
            macs, get_filter = FETCH_DATA(li[0], 830, USER_SUDO, PSWRD_SUDO)
            STARTUP.STORE_DATA(get_filter, OUTPUT_LIST=OUTPUT_LIST)
            ip_a = 'eth0'
            mac = macs[ip_a]
            time.sleep(10)
            res = session_login(li[0], 830, USER_N, PSWRD,
                                mac, du_mac, 'element0', ip_a)
            time.sleep(5)
            STARTUP.GET_SYSTEM_LOGS(li[0], USER_N, PSWRD,OUTPUT_LIST)
            if res == None:
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(
                    f"{'STATUS' : <50}{'=' : ^20}{'PASS' : ^20}", OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                return True

            elif type(res) == list:

                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('ERROR', OUTPUT_LIST=OUTPUT_LIST)
                Error_Info = '''ERROR\n\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tpath \t: \t{}\n\tDescription' \t: \t{}'''.format(
                    *map(str, res))
                STARTUP.STORE_DATA(Error_Info, OUTPUT_LIST=OUTPUT_LIST)
                # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(
                    f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}", OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                # raise '\t\tFAIL-REASON\t\n {}'.format(res)
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
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(
                    f"{'FAIL_REASON' : <50}{'=' : ^20}{res : ^20}", OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(
                    f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}", OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                # raise '\t\tFAIL-REASON\t\n {}'.format(res)
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
        STARTUP.CREATE_LOGS('M_CTC_ID_021', OUTPUT_LIST)


if __name__ == "__main__":
    test_Main_Func_021()
