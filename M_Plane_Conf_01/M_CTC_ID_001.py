import socket
import sys, os, warnings
import time
from ncclient import manager, operations
import string
from ncclient.operations import rpc
from ncclient.operations.rpc import RPCError
from ncclient.xml_ import to_ele
import paramiko
import xmltodict
import subprocess
from ncclient.transport import errors
from paramiko.ssh_exception import NoValidConnectionsError
from ncclient.operations.errors import TimeoutExpiredError
from ncclient.transport.errors import SessionCloseError
import subprocess
import STARTUP, ifcfg, random, Config
import DHCP_CONF.ISC_DHCP_SERVER as ISC_DHCP_SERVER
import DHCP_CONF.DHCP_CONF_VLAN as DHCP_CONF_VLAN


OUTPUT_LIST = []

class M_CTC_id_001():

    def __init__(self,host, port, user, pswrd,sid):
        self.host = host
        self.port = port
        self.user = user
        self.pswrd = pswrd
        self.sid = sid
        


    

    # Check DHCP status----
    def DHCP_Status():
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('\t DHCP DISCOVER, OFFER, REQUEST, PACK Message\n\n',OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        st = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
        STARTUP.STORE_DATA(st,OUTPUT_LIST=OUTPUT_LIST)


    # For pinging vlan ip and perform call home feature
    def ping_ip(self):
        st = subprocess.getoutput(f'ping {self.host} -c 5')
        STARTUP.STORE_DATA(st,OUTPUT_LIST=OUTPUT_LIST)

    # Call Home initialization----
    def Call_Home(self):
    
        # rpc=m.create_subscription()
        # time.sleep(5)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('\tThe O-RU NETCONF Serve  establishes TCP connection and performs a Call Home procedure towards the NETCONF Client and establishes a SSH.\n\n',OUTPUT_LIST=OUTPUT_LIST)
        STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
        m1 = manager.call_home(host='', port=4334, username=self.user , hostkey_verify=False, password=self.pswrd, timeout = 60,allow_agent = False , look_for_keys = False)
        li = m1._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
        STARTUP.STORE_DATA(f'''> listen --ssh --login {self.user }\nWaiting 60s for an SSH Call Home connection on port 4334...''',OUTPUT_LIST=OUTPUT_LIST)
        try:
            if m1:
                query = 'yes'
                str_out = f'''The authenticity of the host '::ffff:{li[0]}' cannot be established.
                ssh-rsa key fingerSTARTUP.STORE_DATA is 59:9e:90:48:f1:d7:6e:35:e8:d1:f6:1e:90:aa:a3:83:a0:6b:98:5a,OUTPUT_LIST=OUTPUT_LIST.
                Are you sure you want to continue connecting (yes/no)? yes'''
                STARTUP.STORE_DATA(str_out,OUTPUT_LIST=OUTPUT_LIST)
                if query == 'yes':
                    STARTUP.STORE_DATA(f'''\n{self.user }@::ffff:{li[0]} password: \n''',OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA("\tTER NETCONF Client and O-RU NETCONF Server exchange capabilities through the NETCONF <hello> messages",OUTPUT_LIST=OUTPUT_LIST)
                    
                    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA(f'''> status\nCurrent NETCONF session:\nID\t: {m1.session_id}\nHost\t: {li[0]}\nPort\t: {li[1]}\nTransport\t: SSH\nCapabilities:''',OUTPUT_LIST=OUTPUT_LIST)
                    for i in m1.server_capabilities:
                        STARTUP.STORE_DATA(i,OUTPUT_LIST=OUTPUT_LIST)
                    return m1.session_id
            else:
                m1.close()
        
            
        except Exception as e:
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA("\t\t{}".format(e),OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            return  f"{e} \nError occured in line number {exc_tb.tb_lineno}"

       
    


def create_vlan(ip_a,v_id):
        time.sleep(10)
        obj = ISC_DHCP_SERVER.test_DHCP_CONF()
        obj.test_read(ip_a,v_id)
        obj1 = DHCP_CONF_VLAN.test_DHCP_CONF()
        IPADDR = obj1.test_read()
        
        d = os.system(f'sudo ip link add link {ip_a} name {ip_a}.{v_id} type vlan id {v_id}')
        d = os.system(f'sudo ifconfig {ip_a}.{v_id} {IPADDR} up')
        d = os.system('sudo /etc/init.d/isc-dhcp-server restart')
        st = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
        
        
def ethtool_linked(interface):
                # STARTUP.STORE_DATA(interface,OUTPUT_LIST=OUTPUT_LIST)
    cmd = "sudo ethtool " + interface
    # STARTUP.STORE_DATA(cmd,OUTPUT_LIST=OUTPUT_LIST)
    gp = os.popen(cmd)
    fat=gp.read().split('\n')
    for line in fat:
        # STARTUP.STORE_DATA(line,OUTPUT_LIST=OUTPUT_LIST)
        if "Speed" in line and ('25000' in line or '10000' in line):
            return interface

def linked_detected():
    inter = ifcfg.interfaces()
    Interface = list(inter.keys())
    for i in Interface:
        if '.' not in i:
            if ethtool_linked(i):
                s = ethtool_linked(i)
                return s


def test_MAIN_FUNC_001():
    STARTUP.STORE_DATA('Processing....',OUTPUT_LIST=OUTPUT_LIST)
    while True:
        interface_name = linked_detected()
        
        # STARTUP.STORE_DATA(interface_name,OUTPUT_LIST=OUTPUT_LIST)
        if interface_name != None:
            break
    out = interface_name
    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
    vlan_id = random.randint(10,20)
    # STARTUP.STORE_DATA(out,str(vlan_id),OUTPUT_LIST=OUTPUT_LIST)
    create_vlan(out,vlan_id)
    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
    STARTUP.STORE_DATA('Processing....',OUTPUT_LIST=OUTPUT_LIST)
    time.sleep(5)
    j = 20
    if vlan_id> j:
        j = vlan_id
    STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
       
    USER_N = Config.details['SUDO_USER'] 
    PSWRD = Config.details['SUDO_PASS'] 
    for i in range(j):
        try:
            m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD,timeout = 60,allow_agent = False , look_for_keys = False)
            li = m._session._transport.sock.getpeername()   #['ip_address', 'TCP_Port']
            # STARTUP.STORE_DATA(li,OUTPUT_LIST=OUTPUT_LIST)
            sid = m.session_id
            # STARTUP.STORE_DATA(sid,OUTPUT_LIST=OUTPUT_LIST)
            
            if m:
                
                obj = M_CTC_id_001(li[0],830,USER_N,PSWRD,sid)
                STARTUP.kill_ssn(li[0], 830, USER_N, PSWRD,sid)
                time.sleep(10)
                RU_Details = STARTUP.demo(li[0], 830, USER_N, PSWRD)
                
                for key, val in RU_Details[1].items():
                        if val[0] == 'true' and val[1] == 'true':
                            CONFIDENTIAL = (f'''**
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
            * @file    M_CTC_ID_001_.txt
            * @brief    M PLANE O-RAN  Conformance
            * @credits Created based on Software Release for GIRU_revC-- v{val[2]}
                                
                                ''')
                            STARTUP.STORE_DATA(CONFIDENTIAL,OUTPUT_LIST=OUTPUT_LIST)

                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA("\t Interfaces Present in DU Side",OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                ip_config = subprocess.getoutput('ifconfig')
                STARTUP.STORE_DATA(ip_config,OUTPUT_LIST=OUTPUT_LIST)



                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA("\t DHCP Status",OUTPUT_LIST=OUTPUT_LIST)
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                st = subprocess.getoutput('sudo /etc/init.d/isc-dhcp-server status')
                STARTUP.STORE_DATA(st,OUTPUT_LIST=OUTPUT_LIST)



                
                STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
                time.sleep(10)
                res = obj.Call_Home()
                time.sleep(10)

                if type(res) == list:
                    STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('\n','*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('*'*20,'FAIL-REASON','*'*20,OUTPUT_LIST=OUTPUT_LIST)
                    STARTUP.STORE_DATA('\n','*'*100,OUTPUT_LIST=OUTPUT_LIST)
                    Error_Info = '''\terror-tag \t: \t{}\n\terror-type \t: \t{}\n\terror-severity \t: \t{}\n\tDescription' \t: \t{}'''.format(*map(str,res))
                    STARTUP.STORE_DATA(Error_Info,OUTPUT_LIST=OUTPUT_LIST)
                    output = f'''''\n'{'*'*100}
                    {'STATUS' : <50}{'=' : ^20}{'FAIL' : ^20}
                    '\n'{'*'*100}'''
                    STARTUP.STORE_DATA(output,OUTPUT_LIST=OUTPUT_LIST)
                    return Error_Info
                    # raise '\t\tFAIL-REASON\t\n{}'.format(Error_Info)
                else:
                    # For Capturing the logs
                    STARTUP.kill_ssn(li[0], 830, USER_N, PSWRD,res)
                    STARTUP.GET_SYSTEM_LOGS(li[0],USER_N,PSWRD,OUTPUT_LIST=OUTPUT_LIST)

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
            # return Error
            # raise socket.timeout('{}: SSH Socket connection lost....'.format(e)) from None


        except errors.SSHError as e:
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            Error = '{} : SSH Socket connection lost....'.format(e)
            STARTUP.STORE_DATA(Error,OUTPUT_LIST=OUTPUT_LIST)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
            # return Error
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
            # return Error
            # raise e

        except TimeoutError as e:
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
            Error = '{} : Call Home is not initiated, Timout Expired....'.format(e)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            # return Error
            # raise f'{e} : Call Home is not initiated, Timout Expired....'

        except SessionCloseError as e:
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
            Error = "{} : Unexpected_Session_Closed....".format(e)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            # return Error
            # raise f'{e},Unexpected_Session_Closed....'

        except TimeoutExpiredError as e:
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
            Error = "{} : TimeoutExpiredError....".format(e)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            # return Error
            # raise e

        except OSError as e:
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            STARTUP.STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
            Error ='{} : Call Home is not initiated, Please wait for sometime........'.format(e)
            STARTUP.STORE_DATA('-'*100,OUTPUT_LIST=OUTPUT_LIST)
            # return Error
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
            time.sleep(80)
            STARTUP.CREATE_LOGS('M_CTC_ID_001',OUTPUT_LIST)

        
        
        # except:
        #         time.sleep(20)
        #         pass

if __name__ == '__main__':
    if test_MAIN_FUNC_001() == True:
        pass
    else:
        pass