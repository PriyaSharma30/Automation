import socket
import sys
import os
import warnings
import time
from ncclient import manager, operations
import string
from ncclient.operations import rpc
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.operations.rpc import RPCError
from ncclient.transport.errors import SessionCloseError
from ncclient.xml_ import to_ele
import paramiko
from paramiko.ssh_exception import NoValidConnectionsError
import xmltodict
import xml.dom.minidom
import STARTUP
from ncclient.transport import errors
import lxml.etree
import Config

OUT_LIST = []

def session_login(host, port, user, password):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent=False, look_for_keys=False) as m:

            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
            STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',OUTPUT_LIST=OUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
            STARTUP.STORE_DATA("\n\n######### STEP 1 TER NETCONF client establishes a connection using a user account with sudo privileges#########\n\n",OUTPUT_LIST=OUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
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
            STARTUP.STORE_DATA(STATUS,OUTPUT_LIST=OUT_LIST)
            for i in m.server_capabilities:
                STARTUP.STORE_DATA("\t", i,OUTPUT_LIST=OUT_LIST)

            try:
                cap = m.create_subscription()
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('>subscribe',OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
                dict_data = xmltodict.parse(str(cap))
                if dict_data['nc:rpc-reply']['nc:ok'] == None:
                    STARTUP.STORE_DATA('\nOk\n',OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA(
                    '\n> get --filter-xpath /o-ran-software-management:software-inventory',OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
                sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <software-inventory xmlns="urn:o-ran:software-management:1.0">
        </software-inventory>
        </filter>'''
                slot_names = m.get(sw_inv).data_xml
                s = xml.dom.minidom.parseString(slot_names)
                xml_pretty_str = s.toprettyxml()

                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
                slot_n = xmltodict.parse(str(slot_names))
                li = ['INVALID', 'EMPTY']
                slots_info1 = slot_n['data']['software-inventory']['software-slot']
                for SLOT in slots_info1:
                    if SLOT['status'] in li:
                        STARTUP.STORE_DATA(xml_pretty_str,OUTPUT_LIST=OUT_LIST)

                        return f'SW slot status is Invalid for {SLOT["name"]}...'

                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA(
                    '\t\tStep 1 : TER NETCONF Client sends <rpc><reset></rpc> to the O-RU NETCONF Server..',OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('\n> user-rpc\n',OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('******* Replace with below xml ********',OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
                xml_data3 = '''<reset xmlns="urn:o-ran:operations:1.0"></reset>'''
                STARTUP.STORE_DATA(xml_data3,OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
                d3 = m.dispatch(to_ele(xml_data3))
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('\t\tStep 2 : O-RU NETCONF Server responds with rpc-reply.',OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('{}'.format(d3),OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA(
                    '\t\tStep 3 : O-RU restarts with a new software version running matching the version activated.',OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
            except RPCError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                return [e.tag, e.type, e.severity, e.path, e.message, exc_tb.tb_lineno]

    except RPCError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        return [e.tag, e.type, e.severity, e.path, e.message, exc_tb.tb_lineno]

    except FileNotFoundError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA("*"*30+'FileNotFoundError'+"*"*30,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA("\t\t{}".format(e),OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        return f'No such file or directory : {e.filename}\nError occured in line number {exc_tb.tb_lineno}'
    
    except lxml.etree.XMLSyntaxError as e:
        
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA("*"*30+'XMLSyntaxError'+"*"*30,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA("\t\t{}".format(e),OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        return  f"{e} \nError occured in line number {exc_tb.tb_lineno}"
    
    except Exception as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA("\t\t{}".format(e),OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        return  f"{e} \nError occured in line number {exc_tb.tb_lineno}"


def get_config_detail(host, port, user, password):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent=False, look_for_keys=False) as m:

            sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <software-inventory xmlns="urn:o-ran:software-management:1.0">
                </software-inventory>
                </filter>'''

            slot_names = m.get(sw_inv).data_xml
            s = xml.dom.minidom.parseString(slot_names)
            xml_pretty_str = s.toprettyxml()
            dict_slots = xmltodict(str(slot_names))

            li = ['INVALID', 'EMPTY']
            SLOTS_INFO = dict_slots['data']['software-inventory']['software-slot']
            for i in SLOTS_INFO:
                if i['name'] in li:
                    STARTUP.STORE_DATA(xml_pretty_str,OUTPUT_LIST=OUT_LIST)
                    return f'{i["name"]} status is not correct....'

    except RPCError as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        return [e.tag, e.type, e.severity, e.path, e.message, exc_tb.tb_lineno]

    except FileNotFoundError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA("*"*30+'FileNotFoundError'+"*"*30,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA("\t\t{}".format(e),OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        return f'No such file or directory : {e.filename}\nError occured in line number {exc_tb.tb_lineno}'
    
    except lxml.etree.XMLSyntaxError as e:
        
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA("*"*30+'XMLSyntaxError'+"*"*30,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA("\t\t{}".format(e),OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        return  f"{e} \nError occured in line number {exc_tb.tb_lineno}"
    
    except Exception as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA("\t\t{}".format(e),OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        return  f"{e} \nError occured in line number {exc_tb.tb_lineno}"




def test_MAIN_FUNC_017():
   # give the input configuration in xml file format
   #xml_1 = open('o-ran-hardware.xml').read()
   # give the input in the format hostname, port, username, password
    try:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        USER_N = Config.details['SUDO_USER']
        PSWRD = Config.details['SUDO_PASS']
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        m = manager.call_home(host='', port=4334, hostkey_verify=False,
                              username=USER_N, password=PSWRD, allow_agent=False, look_for_keys=False)
        # ['ip_address', 'TCP_Port']
        li = m._session._transport.sock.getpeername()
        sid = m.session_id
        if m:
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
            STARTUP.kill_ssn(li[0], 830, USER_N, PSWRD, sid)
            time.sleep(10)
            RU_Details = STARTUP.demo(li[0], 830, USER_N, PSWRD)
            for key, val in RU_Details[1].items():
                if val[1] == 'true':
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
        * @file    M_CTC_ID_017_.txt
        * @brief    M PLANE O-RAN  Conformance
        * @credits Created based on Software Release for GIRU_revC-- v{val[2]}
                            
                            '''
                    STARTUP.STORE_DATA(CONFIDENTIAL,OUTPUT_LIST=OUT_LIST)

            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
            del RU_Details[1]['swRecoverySlot']
            time.sleep(10)
            res = session_login(li[0], 830, USER_N, PSWRD)
            time.sleep(5)

            if res == None:
                host = li[0]
                port = 22
                username = USER_N
                password = PSWRD
                command1 = f"cd {Config.details['SYSLOG_PATH']}; cat {Config.details['syslog_name']};"
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, port, username, password)

                stdin, stdout, stderr = ssh.exec_command(command1)
                lines1 = stdout.readlines()
                time.sleep(120)
                m1 = manager.call_home(host='', port=4334, hostkey_verify=False, username=USER_N,
                                       password=PSWRD, allow_agent=False, look_for_keys=False, timeout=60)
                # ['ip_address', 'TCP_Port']
                li = m1._session._transport.sock.getpeername()
                if m1:
                    # For Capturing the logs

                    ssid = m1.session_id

                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                    STARTUP.kill_ssn(li[0], 830, USER_N, PSWRD, ssid)
                    time.sleep(10)
                    # For getting software inventory
                    slot_s = get_config_detail(li[0], 830, USER_N, PSWRD)
                    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
                    STARTUP.STORE_DATA('\t\t\t\tSYSTEM LOGS',OUTPUT_LIST=OUT_LIST)
                    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
                    command = f"cd {Config.details['SYSLOG_PATH']}; cat {Config.details['syslog_name']};"
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(host, port, username, password)

                    stdin, stdout, stderr = ssh.exec_command(command)
                    lines2 = stdout.readlines()
                    for i in lines1:
                        STARTUP.STORE_DATA('{}'.format(i),OUTPUT_LIST=OUT_LIST)
                    for i in lines2:
                        STARTUP.STORE_DATA('{}'.format(i),OUTPUT_LIST=OUT_LIST)
                    if slot_s:
                        if type(slot_s) == list:
                            STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                            STARTUP.STORE_DATA('*'*20, 'FAIL_REASON', '*'*20,OUTPUT_LIST=OUT_LIST)
                            STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                            Error_Info = '''ERROR\n\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tpath \t: \n{}\n\tDescription' \t: \t{}'''.format(
                                *map(str, res))
                            STARTUP.STORE_DATA(Error_Info,OUTPUT_LIST=OUT_LIST)
                            return Error_Info
                            # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)
                        else:
                            STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                            STARTUP.STORE_DATA(
                                f"{'activation-event-status' : <15}{'=' : ^20}{res : ^20}",OUTPUT_LIST=OUT_LIST)
                            STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                            # raise '\t\tFAIL-REASON\t\n activation-event-status :{}'.format(res)
                        STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                        STARTUP.STORE_DATA(f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",OUTPUT_LIST=OUT_LIST)
                        STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                        return res
                    else:

                        STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                        STARTUP.STORE_DATA(f"{'STATUS' : <50}{'=' : ^20}{'PASS' : ^20}",OUTPUT_LIST=OUT_LIST)
                        STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                        return True

            else:
                STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,OUT_LIST)
                if type(res) == list:
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                    STARTUP.STORE_DATA('*'*20, 'FAIL_REASON', '*'*20,OUTPUT_LIST=OUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                    Error_Info = '''ERROR\n\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tpath \t: \n{}\n\tDescription' \t: \t{}'''.format(
                        *map(str, res))
                    STARTUP.STORE_DATA(Error_Info,OUTPUT_LIST=OUT_LIST)
                    return Error_Info
                    # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)
                else:
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                    STARTUP.STORE_DATA(
                        f"{'activation-event-status' : <15}{'=' : ^20}{res : ^20}",OUTPUT_LIST=OUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                    # raise '\t\tFAIL-REASON\t\n activation-event-status :{}'.format(res)
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA(f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",OUTPUT_LIST=OUT_LIST)
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUT_LIST)
                return res

    except socket.timeout as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(
            e)
        STARTUP.STORE_DATA(Error,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUT_LIST)
        return Error
        # raise socket.timeout('{}: SSH Socket connection lost....'.format(e)) from None

    except errors.SSHError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        Error = '{} : SSH Socket connection lost....'.format(e)
        STARTUP.STORE_DATA(Error,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUT_LIST)
        return Error
        # raise errors.SSHError('{}: SSH Socket connection lost....'.format(e)) from None

    except errors.AuthenticationError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        Error = "{} : Invalid username/password........".format(e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUT_LIST)
        # raise f'{e} : Invalid username/password........'

    except NoValidConnectionsError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUT_LIST)
        Error = '{} : ...'.format(e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        return Error
        # raise e

    except TimeoutError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUT_LIST)
        Error = '{} : Call Home is not initiated, Timout Expired....'.format(e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        return Error
        # raise f'{e} : Call Home is not initiated, Timout Expired....'

    except SessionCloseError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUT_LIST)
        Error = "{} : Unexpected_Session_Closed....".format(e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        return Error
        # raise f'{e},Unexpected_Session_Closed....'

    except TimeoutExpiredError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUT_LIST)
        Error = "{} : TimeoutExpiredError....".format(e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        return Error
        # raise e

    except OSError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUT_LIST)
        Error = '{} : Call Home is not initiated, Please wait for sometime........'.format(
            e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        return Error
        # raise Exception('{} : Please wait for sometime........'.format(e)) from None

    except Exception as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA(e,OUTPUT_LIST=OUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUT_LIST)
        return e
        # raise Exception('{}'.format(e)) from None
        
    finally:
        STARTUP.CREATE_LOGS('M_CTC_ID_017',OUT_LIST)


if __name__ == "__main__":
    test_MAIN_FUNC_017()
