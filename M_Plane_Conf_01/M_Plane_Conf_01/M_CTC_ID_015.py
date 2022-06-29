import socket
import sys
import os
import warnings
import time
from ncclient import manager, operations
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
from ncclient.operations import rpc
from ncclient.operations.rpc import RPCError
from ncclient.xml_ import to_ele
import paramiko
import xmltodict
import xml.dom.minidom
import subprocess
from ncclient.transport import errors
import STARTUP
import lxml.etree
from paramiko.ssh_exception import NoValidConnectionsError
import Config

OUTPUT_LIST = []


def session_login(host, port, user, password, rmt, pswrd, slots):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent=False, look_for_keys=False) as m:

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
                    '''
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

            pub_k = subprocess.getoutput('cat /etc/ssh/ssh_host_rsa_key.pub')
            pk = pub_k.split()
            pub_key = pk[1]
            xml_data = open("Yang_xml/sw_download.xml").read()
            xml_data = xml_data.format(
                rmt_path=rmt, password=pswrd, public_key=pub_key)

            STARTUP.STORE_DATA('\n> user-rpc\n', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                '\t\t******* Replace with below xml ********', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(xml_data, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                '\t\tStep 1 : TER NETCONF Client triggers <rpc><software-download>', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)

            d = m.dispatch(to_ele(xml_data))
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('******* RPC Reply ********',
                               OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('{}'.format(d), OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                '\t\tStep 2 :  O-RU NETCONF Server sends <notification><download-event> with status COMPLETED to TER NETCONF Client', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
            while True:
                n = m.take_notification()
                if n == None:
                    break
                notify = n.notification_xml
                dict_n = xmltodict.parse(str(notify))
                try:
                    notf = dict_n['notification']['download-event']
                    if notf:
                        x = xml.dom.minidom.parseString(notify)
                        #xml = xml.dom.minidom.parseString(user_name)

                        xml_pretty_str = x.toprettyxml()

                        STARTUP.STORE_DATA(
                            xml_pretty_str, OUTPUT_LIST=OUTPUT_LIST)
                        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                        status = dict_n['notification']['download-event']['status']
                        if status != 'COMPLETED':
                            return status
                        break
                except:
                    pass

            # SW INSTALL
            STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA(
                '\t\tStep 3 : TER NETCONF Client triggers <rpc><software-install> Slot must have attributes active = FALSE, running = FALSE.', OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
            k = 1
            for key, val in slots.items():
                if val[0] == 'false' and val[1] == 'false':
                    STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)

                    STARTUP.STORE_DATA, OUTPUT_LIST = OUTPUT_LIST(
                        '\n> get --filter-xpath /o-ran-software-management:software-inventory')
                    STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                    sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <software-inventory xmlns="urn:o-ran:software-management:1.0">
            </software-inventory>
            </filter>'''
                    slot_names = m.get(sw_inv).data_xml
                    s = xml.dom.minidom.parseString(slot_names)
                    xml_pretty_str = s.toprettyxml()
                    STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)

                    ############ Checking The status, active and running value ##############
                    slot_n = xmltodict.parse(str(slot_names))
                    slots_info = slot_n['data']['software-inventory']['software-slot']
                    for i in slots_info:
                        if i['status'] == 'INVALID':
                            STARTUP.STORE_DATA(
                                xml_pretty_str, OUTPUT_LIST=OUTPUT_LIST)
                            return 'SW slot status is Invalid...'
                        if (i['active'] == 'false' and i['running'] == 'false') or (i['active'] == 'true' and i['running'] == 'true'):
                            pass
                        else:
                            return 'Slots Active and Running Status are diffrent...'
                    STARTUP.STORE_DATA(xml_pretty_str, OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)

                    xml_data1 = open("Yang_xml/sw_install.xml").read()
                    xml_data1 = xml_data1.format(slot_name=key)
                    STARTUP.STORE_DATA(
                        '\n> user-rpc\n', OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(
                        '\t\t******* Replace with below xml ********', OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(xml_data1, OUTPUT_LIST=OUTPUT_LIST)
                    d1 = m.dispatch(to_ele(xml_data1))
                    STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(
                        '******* RPC Reply ********', OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('{}'.format(d1), OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(
                        '\t\tStep 4 :  O-RU NETCONF Server sends <notification><install-event> with status INTEGRITY ERROR or FILE ERROR',OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                    while True:
                        n = m.take_notification(timeout=30)
                        if n == None:
                            break
                        notify = n.notification_xml
                        dict_n = xmltodict.parse(str(notify))
                        try:
                            notf = dict_n['notification']['install-event']
                            if notf:
                                x = xml.dom.minidom.parseString(notify)
                                xml_pretty_str = x.toprettyxml()

                                STARTUP.STORE_DATA(
                                    xml_pretty_str, OUTPUT_LIST=OUTPUT_LIST)
                                li = ['INTEGRITY_ERROR', 'FILE_ERROR']
                                STARTUP.STORE_DATA(
                                    '-'*100, OUTPUT_LIST=OUTPUT_LIST)
                                status = dict_n['notification']['install-event']['status']
                                if status not in li:
                                    return status

                                break
                        except:
                            pass

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


def test_MAIN_FUNC_015():
   # give the input configuration in xml file format
   #xml_1 = open('o-ran-hardware.xml').read()
   # give the input in the format hostname, port, username, password
    while True:
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        rmt = Config.details['remote_path']
        if not rmt:
            STARTUP.STORE_DATA('Invalid value... ', OUTPUT_LIST=OUTPUT_LIST)
        else:
            break

    while True:
        pswrd = Config.details['DU_PASS']
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        if not pswrd:
            STARTUP.STORE_DATA('Invalid value... ', OUTPUT_LIST=OUTPUT_LIST)
        else:
            break
    try:

        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        USER_N = Config.details['SUDO_USER']
        PSWRD = Config.details['SUDO_PASS']
        STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
        m = manager.call_home(host='', port=4334, hostkey_verify=False,
                              username=USER_N, password=PSWRD, allow_agent=False, look_for_keys=False)
        # ['ip_address', 'TCP_Port']
        li = m._session._transport.sock.getpeername()
        sid = m.session_id
        if m:
            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
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
        * @file    M_CTC_ID_015_.txt
        * @brief    M PLANE O-RAN  Conformance
        * @credits Created based on Software Release for GIRU_revC-- v{val[2]}
                            
                            '''
                    STARTUP.STORE_DATA(CONFIDENTIAL, OUTPUT_LIST=OUTPUT_LIST)

            STARTUP.STORE_DATA('-'*100, OUTPUT_LIST=OUTPUT_LIST)
            del RU_Details[1]['swRecoverySlot']
            res = session_login(li[0], 830, USER_N, PSWRD,
                                rmt, pswrd, RU_Details[1])
            STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,OUTPUT_LIST)
            if res:

                if type(res) == list:
                    STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*20, 'FAIL_REASON',
                                       '*'*20, OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                    Error_Info = '''ERROR\n\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tpath \t: \n{}\n\tDescription' \t: \t{}'''.format(
                        *map(str, res))
                    STARTUP.STORE_DATA(Error_Info, OUTPUT_LIST=OUTPUT_LIST)
                    return Error_Info
                    # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)
                else:
                    STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(
                        f"{'REJECT-REASON' : <15}{'=' : ^20}{res : ^20}", OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                    # raise '\t\tFAIL-REASON\t\n{}'.format(res)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(
                    f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}", OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                return res

            else:
                # For Capturing the logs
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(
                    f"{'STATUS' : <50}{'=' : ^20}{'PASS' : ^20}", OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100, OUTPUT_LIST=OUTPUT_LIST)
                return True

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
        STARTUP.CREATE_LOGS('M_CTC_ID_015', OUTPUT_LIST)


if __name__ == "__main__":
    test_MAIN_FUNC_015()
