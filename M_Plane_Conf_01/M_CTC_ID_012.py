import socket
import sys, os, warnings
from time import time
#warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager
import string
from ncclient.operations.rpc import RPCError
from ncclient.transport.errors import SSHError
import xmltodict
import paramiko
import xml.dom.minidom  
from ncclient.transport import errors
import STARTUP
from calnexRest import calnexInit, calnexGet, calnexSet, calnexCreate, calnexDel,calnexGetVal
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import lxml.etree
import Config

OUTPUT_LIST = []


#xml_1 = open('o-ran-interfaces.xml').read()
def session_login(host, port, user, password):
    
    with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent = False , look_for_keys = False) as m:
        try:
            
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
            STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
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
            STARTUP.STORE_DATA(STATUS,OUTPUT_LIST)
            for i in m.server_capabilities:
                STARTUP.STORE_DATA("\t",i,OUTPUT_LIST)

            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
            # STARTUP.STORE_DATA("\n\n########### Initial Get#####################\n\n",OUTPUT_LIST)
            # STARTUP.STORE_DATA('-'*100,,OUTPUT_LIST)
            # STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
            # STARTUP.STORE_DATA('\n>get --filter-xpath /o-ran-sync:sync',OUTPUT_LIST)
            # STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
            # SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            #     <sync xmlns="urn:o-ran:sync:1.0">
            #     </sync>
            #     </filter>
            #     '''
            # data  = m.get(SYNC).data_xml
            # dict_Sync = xmltodict.parse(str(data))
            # x = xml.dom.minidom.parseString(data)
            

            # xml_pretty_str = x.toprettyxml()

            # STARTUP.STORE_DATA(xml_pretty_str,OUTPUT_LIST)
            # STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)


            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
            STARTUP.STORE_DATA("\n\n###########Step 1 The TER NETCONF Client periodically tests O-RU’s sync-status until the LOCKED state is reached.#####################\n\n",OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100)   ,OUTPUT_LIST 
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
            STARTUP.STORE_DATA('\n>get --filter-xpath /o-ran-sync:sync',OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
            start_time = time() + 1200
            while time() < start_time:
                SYNC = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <sync xmlns="urn:o-ran:sync:1.0">
                </sync>
                </filter>
                '''
                data  = m.get(SYNC).data_xml
                dict_Sync = xmltodict.parse(str(data))
                state = dict_Sync['data']['sync']['sync-status']['sync-state']
                if state == 'LOCKED':

                    x = xml.dom.minidom.parseString(data)
                    

                    xml_pretty_str = x.toprettyxml()

                    STARTUP.STORE_DATA(xml_pretty_str,OUTPUT_LIST)
                    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
                    break
            calnexSet(f"app/mse/master/Master{Config.details['PORT']}/stop")
            calnexSet(f"app/generation/synce/esmc/Port{Config.details['PORT']}/stop")
            rpc=m.create_subscription()
            while True:
                n = m.take_notification(timeout=30)
                if n == None:
                    return 1
                notify=n.notification_xml
                dict_n = xmltodict.parse(str(notify))
                try:
                    notf = dict_n['notification']['alarm-notif']['fault-id']
                    type(notf)
                    if notf == '17':
                        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
                        STARTUP.STORE_DATA("\n\n###########Step 3 After a while (time depends on implementation) the O-RU NETCONF SERVER sends a notification for  alarm 17: No external sync source”#####################\n\n",OUTPUT_LIST)
                        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
                        x = xml.dom.minidom.parseString(notify)
                        #xml = xml.dom.minidom.parseString(user_name)

                        xml_pretty_str = x.toprettyxml()
                        STARTUP.STORE_DATA(xml_pretty_str,OUTPUT_LIST)
                        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
                        break
                    else:
                        x = xml.dom.minidom.parseString(notify)
                        #xml = xml.dom.minidom.parseString(user_name)

                        xml_pretty_str = x.toprettyxml()
                        STARTUP.STORE_DATA(xml_pretty_str,OUTPUT_LIST)
                        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
                        return dict_n['notification']['alarm-notif']['fault-text']
                except:
                    pass
            


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
    

def test_MAIN_FUNC_012():
    #give the input configuration in xml file format
    #xml_1 = open('o-ran-hardware.xml').read()
    #give the input in the format hostname, port, username, password
    try:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        USER_N = Config.details['SUDO_USER']
        PSWRD = Config.details['SUDO_PASS']
        P_NEO_IP = Config.details['IPADDR_PARAGON']
        P_NEO_PORT = Config.details['PORT']
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        sys.path.append(f'//{P_NEO_IP}/calnex100g/RemoteControl/')
        calnexInit(f"{P_NEO_IP}")
        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD, allow_agent = False , look_for_keys = False)
        li = m._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
        sid = m.session_id
        if m:
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
            STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,sid)
            RU_DETAILS = STARTUP.demo(li[0], 830, USER_N, PSWRD)
            calnexSet(f"app/mse/master/Master{P_NEO_PORT}/start")
            calnexSet(f"app/generation/synce/esmc/Port{P_NEO_PORT}/start")
            for key, val in RU_DETAILS[1].items():
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
        * @file    M_CTC_ID_012_.txt
        * @brief    M PLANE O-RAN  Conformance
        * @credits Created based on Software Release for GIRU_revC-- v{val[2]}
                            
                            '''
                        STARTUP.STORE_DATA(CONFIDENTIAL,OUTPUT_LIST)

            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
            
            
            res = session_login(li[0],830,USER_N, PSWRD)
            STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,OUTPUT_LIST)
            if res:
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST)
                if type(res) == list:
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*20,'FAIL_REASON','*'*20,OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST)
                    Error_Info = '''ERROR\n\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tpath \t: \n{}\n\tDescription' \t: \t{}'''.format(*map(str,res))
                    STARTUP.STORE_DATA(Error_Info,OUTPUT_LIST)
                    return Error_Info
                    # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)
                else:
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'FAIL_REASON' : <15}{'=' : ^20}{res : ^20}",OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST)
                    # raise '\t\tFAIL-REASON\t\n{}'.format(res)
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST)
                STARTUP.STORE_DATA(f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST)
                return res
            else:
                # For Capturing the logs
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST)
                STARTUP.STORE_DATA(f"{'STATUS' : <50}{'=' : ^20}{'PASS' : ^20}",OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST)
                return True
                
            
    except socket.timeout as e:
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
            Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(e)
            STARTUP.STORE_DATA(Error,OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST)
            return Error
            # raise socket.timeout('{}: SSH Socket connection lost....'.format(e)) from None


    except errors.SSHError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        Error = '{} : SSH Socket connection lost....'.format(e)
        STARTUP.STORE_DATA(Error,OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST)
        return Error
        # raise errors.SSHError('{}: SSH Socket connection lost....'.format(e)) from None


    except errors.AuthenticationError as e:
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
            Error = "{} : Invalid username/password........".format(e)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST)
            # raise f'{e} : Invalid username/password........'

    except NoValidConnectionsError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST)
        Error = '{} : ...'.format(e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        return Error
        # raise e

    except TimeoutError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST)
        Error = '{} : Call Home is not initiated, Timout Expired....'.format(e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        return Error
        # raise f'{e} : Call Home is not initiated, Timout Expired....'

    except SessionCloseError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST)
        Error = "{} : Unexpected_Session_Closed....".format(e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        return Error
        # raise f'{e},Unexpected_Session_Closed....'

    except TimeoutExpiredError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST)
        Error = "{} : TimeoutExpiredError....".format(e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        return Error
        # raise e

    except OSError as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST)
        Error ='{} : Call Home is not initiated, Please wait for sometime........'.format(e)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        return Error
        # raise Exception('{} : Please wait for sometime........'.format(e)) from None


    except Exception as e:
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        STARTUP.STORE_DATA(e,OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST)
        return e
        # raise Exception('{}'.format(e)) from None

    finally:
        STARTUP.CREATE_LOGS('M_CTC_ID_012',OUTPUT_LIST)


if __name__ == "__main__":
    test_MAIN_FUNC_012()