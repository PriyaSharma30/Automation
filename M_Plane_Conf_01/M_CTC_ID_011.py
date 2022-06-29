import socket
import sys, os, warnings
import time
#warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager
from ncclient.operations.rpc import RPC, RPCError
#from netconf_client.ncclient import RPCError
import xmltodict
import xml.dom.minidom
import paramiko
#xml_1 = open('o-ran-interfaces.xml').read()
from ncclient.transport import errors
import STARTUP
import lxml.etree
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import Config

OUTPUT_LIST = []


class M_ctc_id_10:
   
    # init method or constructor 
    def __init__(self,host, port,sid,user2, pswrd2):
        self.host = host
        self.port = port
        self.sid = sid
        self.user2 = user2
        self.pswrd2 = pswrd2
   
    def session_login(self):
    
        with manager.connect(host=self.host, port=self.port, username=self.user2, hostkey_verify=False, password=self.pswrd2, allow_agent = False , look_for_keys = False) as m:
        
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STATUS = f'''> connect --ssh --host {self.host} --port 830 --login {self.user2}
                    Interactive SSH Authentication
                    Type your password:
                    Password: 
                    > status
                    Current NETCONF session:
                    ID          : {m.session_id}
                    Host        : {self.host}
                    Port        : {self.port}
                    Transport   : SSH
                    Capabilities:
                    '''
            STARTUP.STORE_DATA(STATUS,OUTPUT_LIST=OUTPUT_LIST)
            for i in m.server_capabilities:
                STARTUP.STORE_DATA("\t",i,OUTPUT_LIST=OUTPUT_LIST)
            

            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('\n\n\t\t***********step 1 and 2 Retrival of ru information with filter **********\n\n',OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            try:
                STARTUP.STORE_DATA("get --filter-xpath /o-ran-usermgmt:users/user",OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                u_name = '''
                        <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        <users xmlns="urn:o-ran:user-mgmt:1.0">	
                            <user>                                                        
                                
                            </user>
                        </users>
                        </filter>
                '''
                
                user_name = m.get_config('running', u_name).data_xml

                x = xml.dom.minidom.parseString(user_name)
                #xml = xml.dom.minidom.parseString(user_name)

                xml_pretty_str = x.toprettyxml()

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
        
                

                

def test_MAIN_FUNC_011():
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
        obj = M_ctc_id_10(li[0],830,sid,USER_N,PSWRD)
        if m:
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,sid)
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
        * @file    M_CTC_ID_011_.txt
        * @brief    M PLANE O-RAN  Conformance
        * @credits Created based on Software Release for GIRU_revC-- v{val[2]}
                            
                            '''
                        STARTUP.STORE_DATA(CONFIDENTIAL,OUTPUT_LIST=OUTPUT_LIST)


            
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            
            time.sleep(5)
            res = obj.session_login()

            STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,OUTPUT_LIST)
            if res:
                if type(res) == list:
                    STARTUP.STORE_DATA('\n','*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*20,'FAIL_REASON','*'*20,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('\n','*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    Error_Info = '''ERROR\n\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tDescription' \t: \t{}'''.format(*map(str,res))
                    STARTUP.STORE_DATA(Error_Info,OUTPUT_LIST=OUTPUT_LIST)
                    return Error_Info
                    # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)
                else:
                    STARTUP.STORE_DATA('\n','*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'REJECT-REASON' : <15}{'=' : ^20}{res : ^20}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('\n','*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    # raise '\t\tFAIL-REASON\t\n{}'.format(res)
                STARTUP.STORE_DATA('\n','*'*100,OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('\n','*'*100,OUTPUT_LIST=OUTPUT_LIST)
                return res
            else:

                # For Capturing the logs
                STARTUP.STORE_DATA('\n','*'*100,OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(f"{'STATUS' : <50}{'=' : ^20}{'PASS' : ^20}",OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('\n','*'*100,OUTPUT_LIST=OUTPUT_LIST)
                return True
                     
    except socket.timeout as e:
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            Error = '{} : Call Home is not initiated, SSH Socket connection lost....'.format(e)
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
        Error ='{} : Call Home is not initiated, Please wait for sometime........'.format(e)
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
        STARTUP.CREATE_LOGS('M_CTC_ID_011',OUTPUT_LIST)


if __name__ == "__main__":
    test_MAIN_FUNC_011()