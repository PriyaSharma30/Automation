import socket
import sys, os, warnings
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





def session_login(host, port, user, password,slots):
    try:
        with manager.connect(host=host, port=port, username=user,
         hostkey_verify=False, password=password, allow_agent = False , look_for_keys = False) as m:
        
            try:
                cap = m.create_subscription()
                print('-'*100)
                print('>subscribe')
                print('-'*100)
                dict_data = xmltodict.parse(str(cap))
                if dict_data['nc:rpc-reply']['nc:ok']== None:
                    print('\nOk\n')
                print('-'*100)
                print('*'*100)
                print('\n> get --filter-xpath /o-ran-software-management:software-inventory')
                print('-'*100)
                sw_inv = '''<filter xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <software-inventory xmlns="urn:o-ran:software-management:1.0">
        </software-inventory>
        </filter>'''
                slot_names = m.get(sw_inv).data_xml
                s = xml.dom.minidom.parseString(slot_names)
                xml_pretty_str = s.toprettyxml()

                print('-'*100)
                slot_n = xmltodict.parse(str(slot_names))
                li = ['INVALID', 'EMPTY']
                slots_info1 = slot_n['data']['software-inventory']['software-slot']
                for SLOT in slots_info1:
                    if SLOT['status'] in li:
                            print(xml_pretty_str)
                            
                            return f'SW slot status is Invalid for {SLOT["name"]}...'
                     
                

                print('*'*100)
                print('\t\tStep 1 : TER NETCONF Client sends <rpc><reset></rpc> to the O-RU NETCONF Server..')
                print('*'*100)
                print('-'*100)
                print('\n> user-rpc\n')
                print('-'*100)
                print('******* Replace with below xml ********')
                print('-'*100)
                xml_data3 = '''<reset xmlns="urn:o-ran:operations:1.0"></reset>'''
                print(xml_data3)
                print('-'*100)
                d3 = m.dispatch(to_ele(xml_data3))
                print('*'*100)
                print('\t\tStep 2 : O-RU NETCONF Server responds with rpc-reply.')
                print('*'*100)
                print(d3)
                print('*'*100)
                print('\t\tStep 3 : O-RU restarts with a new software version running matching the version activated.')
                print('*'*100)
            except RPCError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                return [e.tag, e.type, e.severity, e.path ,e.message,exc_tb.tb_lineno]


    except RPCError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                return [e.tag, e.type, e.severity, e.path ,e.message,exc_tb.tb_lineno]

    except FileNotFoundError as e:
        print('-'*100)
        print("*"*30+'FileNotFoundError'+"*"*30)
        print('-'*100)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('-'*100)
        print("\t\t",e)
        print('-'*100)
        return f'No such file or directory : {e.filename}\nError occured in line number {exc_tb.tb_lineno}'
    
    except lxml.etree.XMLSyntaxError as e:
        
        print('-'*100)
        print("*"*30+'XMLSyntaxError'+"*"*30)
        print('-'*100)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('-'*100)
        print("\t\t",e)
        print('-'*100)
        return  f"{e} \nError occured in line number {exc_tb.tb_lineno}"

    except Exception as e:
        print('-'*100)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('-'*100)
        print(e)
        print('-'*100)
        return  f"{e} \nError occured in line number {exc_tb.tb_lineno}"


print('-'*100)
USER_N = Config.details['SUDO_USER']
PSWRD = Config.details['SUDO_PASS']
print('-'*100)
m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = USER_N, password = PSWRD, allow_agent = False , look_for_keys = False)
li = m._session._transport.sock.getpeername()
if m:
    res = session_login(li[0],830,USER_N,PSWRD)
    time.sleep()