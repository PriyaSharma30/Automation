from logging import exception
import socket
import sys, os, warnings
#warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager
from lxml import etree
import string
import xmltodict
import xml.dom.minidom
from ncclient.transport.errors import SSHError
from ncclient.operations.rpc import RPCError
import paramiko
import re
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import lxml.etree
import Config, STARTUP, DHCP_CONF.Genrate_User_Pass as Genrate_User_Pass
import re

OUTPUT_LIST = []





def FETCH_MAC(host, port, user, password):
    with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent = False , look_for_keys = False) as m:
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
        
        return mac
    

def session_login(host, port, user, password,ru_mac,du_mac,ip_adr):
    try:
        with manager.connect(host=host, port=port, username=user, hostkey_verify=False, password=password, allow_agent = False , look_for_keys = False) as m:
                n = ip_adr[3]
                xml_data = open('Yang_xml/interface.xml').read()
                xml_data = xml_data.format(interface_name= ip_adr,mac = ru_mac, number= n)
                u1 =f'''
                        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        {xml_data}
                        </config>'''
                try:
                    Data = m.edit_config(u1, target='running')
                except RPCError as e:
                    STARTUP.STORE_DATA("\n",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA("*"*30+'RPCError'+"*"*30,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA("\t\t Not able to push interface xml {}".format(e),OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                    return '{}'.format(e)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                
                xml_data1 = open('Yang_xml/processing.xml').read()
                xml_data1 = xml_data1.format(int_name= ip_adr,ru_mac = ru_mac,du_mac = du_mac, element_name= 'element0')
                u2 =f'''
                        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                        {xml_data1}
                        </config>'''
                try:
                    Data = m.edit_config(u2, target='running')
                except RPCError as e:
                    STARTUP.STORE_DATA("\n",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA("*"*30+'RPCError'+"*"*30,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA("\t\t Not able to push processing xml {}".format(e),OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                    return '{}'.format(e)
                
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('\n\n\t\t********** Connect to the NETCONF Server ***********\n\n',OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            
                # rpc=m.create_subscription()
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
                STARTUP.STORE_DATA(STATUS,OUTPUT_LIST=OUTPUT_LIST)
                for i in m.server_capabilities:
                    STARTUP.STORE_DATA("\t",i,OUTPUT_LIST=OUTPUT_LIST)

                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                        

                STARTUP.STORE_DATA('\n>get --filter-xpath /o-ran-uplane-conf:user-plane-configuration',OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                    
                up ='''
                    <filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                    <user-plane-configuration xmlns="urn:o-ran:uplane-conf:1.0">
                    </user-plane-configuration>
                    </filter>
                    '''
                Cap = m.get(up).data_xml
                x = xml.dom.minidom.parseString(Cap)
                

                xml_pretty_str = x.toprettyxml()

                STARTUP.STORE_DATA(xml_pretty_str,OUTPUT_LIST=OUTPUT_LIST)

                
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA("\n\n######### STEP 1 TER NETCONF Client assigns eAxC_IDs to low-level-rx-endpoints. The same eAxC_ID is assigned to more than one low-level-tx-endpoint or/and more than one low-level-rx-endpoint.#########\n\n",OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                
                STARTUP.STORE_DATA('\n> edit-config  --target running --config --defop replace\n',OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('******* Replace with below xml ********',OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                
                
                xml_1 = open(Config.details['TC_27_xml']).read()
                xml_1 = xml_1.format(element_name= 'element0')
                snippet = f"""
                            <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                            {xml_1}
                            </config>"""
                
                STARTUP.STORE_DATA(snippet,OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                try:
                    data1 = m.edit_config(target="running", config=snippet, default_operation = 'replace')
                    dict_data1 = xmltodict.parse(str(data1))
                    STARTUP.STORE_DATA("\n",'-'*100,OUTPUT_LIST=OUTPUT_LIST)
                    if dict_data1['nc:rpc-reply']['nc:ok']== None:
                        STARTUP.STORE_DATA('\nOk\n',OUTPUT_LIST=OUTPUT_LIST)
                        return f'\t\t******COnfiguration are pushed********\n {data1}'

                except RPCError as e:
                    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA("\n\n######### STEP 2 The O-RU NETCONF Sever responds with the <rpc-reply> message indicating rejection of the requested procedure.#########\n\n",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('ERROR',OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'tag' :^20}{':' : ^10}{e.tag: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'type' : ^20}{':' : ^10}{e.type: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'severity' : ^20}{':' : ^10}{e.severity: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                    #STARTUP.STORE_DATA(f"{'info' : <20}{':' : ^10}{e: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'path' : ^20}{':' : ^10}{e.path: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'Description' : ^20}{':' : ^10}{e.message: ^10}",OUTPUT_LIST=OUTPUT_LIST)
                    #STARTUP.STORE_DATA(f"{'tag' : <20}{':' : ^10}{e.errlist: ^10}",OUTPUT_LIST=OUTPUT_LIST)
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



def test_Main_Func_027():
    #give the input configuration in xml file format
    #xml_1 = open('o-ran-hardware.xml').read()
    #give the input in the format hostname, port, username, password
    try:
        
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        USER_N = Config.details['SUDO_USER']
        PSWRD = Config.details['SUDO_PASS']
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD, allow_agent = False , look_for_keys = False)
        li = m._session._transport.sock.getpeername()
        sid = m.session_id
        if m:
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.kill_ssn(li[0],830, USER_N, PSWRD,sid)
            RU_Details = STARTUP.demo(li[0],830, USER_N, PSWRD)
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
        * @file    M_CTC_ID_027_.txt
        * @brief    M PLANE O-RAN  Conformance
        * @credits Created based on Software Release for GIRU_revC-- v{val[2]}
                            
                            '''
                        STARTUP.STORE_DATA(CONFIDENTIAL,OUTPUT_LIST=OUTPUT_LIST)
            
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            for i in range(5):
                du_mac = Config.details['DU_MAC']
                val = isValidMACAddress(du_mac)
                if val == True:
                    break
                else:
                    STARTUP.STORE_DATA('Please provide valid mac address :\n',OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            
            
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            macs = FETCH_MAC(li[0],830, USER_N, PSWRD)
            ip_a = 'eth0'
            mac = macs[ip_a]
            
            res = session_login(li[0],830,USER_N, PSWRD,mac,du_mac,ip_a)

            # For Capturing the logs  
            STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,OUTPUT_LIST)
            if res:  
                if type(res) == list:
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*20,'FAIL_REASON','*'*20,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    Error_Info = '''ERROR\n\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tpath \t: \t{}\n\tDescription' \t: \t{}'''.format(*map(str,res))
                    STARTUP.STORE_DATA(Error_Info,OUTPUT_LIST=OUTPUT_LIST)
                    return Error_Info
                    # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)
                else:
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f"{'REJECT-REASON' : <15}{'=' : ^20}{res : ^20}",OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    # raise '\t\tFAIL-REASON\t\n {}'.format(res)
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA(f"{'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}",OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('*'*100,OUTPUT_LIST=OUTPUT_LIST)
                return res
            else:
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
        STARTUP.CREATE_LOGS('M_CTC_ID_027',OUTPUT_LIST)


if __name__ == "__main__":
    test_Main_Func_027()
