import os
from database import UseDB as db
from concurrent.futures import ThreadPoolExecutor


# TODO: ups_mon
# Объявление асинхронных функций
def check_status(host):
    k = db.get_status(host)
    # Для AP
    if k[0] == 1:
        ap_status = k[1]
    # Для PC
    elif k[0] == 2:
        ap_status = k[2]
    
    

def ap_mon(host):
    k = db.get_status(host)
    resp = os.system(f'ping -c 1 {host}')
    if resp != 0 and k[host] == 3:
        db().update_status(host, 0)
        # TODO: отпрвка в телегу
    elif resp != 0:
        k += 1
    else:
        db().update_status(host, 1)
        k = 0


def pc_mon(host):
    resp = os.system(f'nmap {host}')
    if resp != 0:
        db().update_status(host, 0)
        # TODO: отправка в телегу
    else:
        db().update_status(host, 1)


def main():
    ips_list = {}
    ips_list['pc'], ips_list['ap'] = db().get_by_type(2), db().get_by_type(1)
    
    with ThreadPoolExecutor(4) as execut:
        results['pc'] = execut.map(pc_mon, ips_list['pc'])
        results['ap'] = execut.map(ap_mon, ips_list['ap'])
