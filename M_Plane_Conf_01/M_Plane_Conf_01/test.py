from ncclient import manager
import socket,os,sys

OUTPUT_LIST = []

def STORE_DATA(*data,OUTPUT_LIST):
    print(*data)
    # OUTPUT_LIST.append(*data)
    OUTPUT_LIST.append('{}\n'.format(''.join([*data])))
    return OUTPUT_LIST
def test_acll():
     try:
          m = manager.call_home(host = '', port=4334, hostkey_verify=False,username = 'operator', password = 'admin123',timeout = 60,allow_agent = False , look_for_keys = False)
     except socket.timeout as e:
               STORE_DATA('-'*100,'\n',OUTPUT_LIST=OUTPUT_LIST)
               print(OUTPUT_LIST)
               STORE_DATA('{}: Call Home is not initiated, SSH Socket connection lost....'.format(e),OUTPUT_LIST=OUTPUT_LIST)
               STORE_DATA('-'*100,'\n',OUTPUT_LIST=OUTPUT_LIST)
               exc_type, exc_obj, exc_tb = sys.exc_info()
               STORE_DATA(f"Error occured in line number {exc_tb.tb_lineno}",OUTPUT_LIST=OUTPUT_LIST)
     except Exception as e:
          li = [1,2,3,4,5,6,7,8,9,10]
          STORE_DATA('-'*100,'\n',OUTPUT_LIST=OUTPUT_LIST)
          STORE_DATA(e,': Call Home is not initiated, Please wait for sometime........',OUTPUT_LIST=OUTPUT_LIST)
          STORE_DATA('-'*100,'\n',OUTPUT_LIST=OUTPUT_LIST)

     for i in OUTPUT_LIST:
          STORE_DATA(i,OUTPUT_LIST=OUTPUT_LIST)

test_acll()