import paramiko
import datetime
import csv
import time
import random

def readMkTemp(ip):
    ret = [ip]
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    out = []
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username="api", password="password", allow_agent=False)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("/system health print")
        out = ssh_stdout.readlines()
        ssh.close()
    except Exception:
        pass

    ret.extend("".join(out).split())
    ret.append(date_time)

    return ret

def save_to_csv(data, filename):
    try:
        with open(filename + '.csv', 'a') as f:
            wr = csv.writer(f)
            wr.writerow(data)
    except:
        with open(filename + '.csv', 'w') as f:
            wr = csv.writer(f)
            f.writerow(data)

def every(delay, task):
    next_time = time.time() + delay
    while True:
        time.sleep(max(0, next_time - time.time()))
        try:
            task()
        except Exception:
            pass
        next_time += (time.time() - next_time) // delay * delay + delay

def read():
    data = readMkTemp("172.16.10.6")
    save_to_csv(data, 'router_health_data')

every(30, read)
# print(readMkTemp('172.16.10.6'))
