
# ssh-user-enumeration

OpenSSH through 7.7 is prone to a user enumeration vulnerability due to not delaying bailout for an invalid authenticating user until after the packet containing the request has been fully parsed, related to auth2-gss.c, auth2-hostbased.c, and auth2-pubkey.c.

CVE: CVE-2018-15473

#### Write up from https://www.openwall.com/lists/oss-security/2018/08/15/5

Date:   Tue Jul 31 03:10:27 2018 +0000
    delay bailout for invalid authenticating user until after the packet
    containing the request has been fully parsed. Reported by Dariusz Tytko
    and Michal Sajdak; ok deraadt

We realized that without this patch, a remote attacker can easily test
whether a certain user exists or not (username enumeration) on a target
OpenSSH server:
```c
  87 static int
  88 userauth_pubkey(struct ssh *ssh)
  89 {
 ...
 101         if (!authctxt->valid) {
 102                 debug2("%s: disabled because of invalid user", __func__);
 103                 return 0;
 104         }
 105         if ((r = sshpkt_get_u8(ssh, &have_sig)) != 0 ||
 106             (r = sshpkt_get_cstring(ssh, &pkalg, NULL)) != 0 ||
 107             (r = sshpkt_get_string(ssh, &pkblob, &blen)) != 0)
 108                 fatal("%s: parse request failed: %s", __func__, ssh_err(r));
```
The attacker can try to authenticate a user with a malformed packet (for
example, a truncated packet), and:

- if the user is invalid (it does not exist), then userauth_pubkey()
  returns immediately, and the server sends an SSH2_MSG_USERAUTH_FAILURE
  to the attacker;

- if the user is valid (it exists), then sshpkt_get_u8() fails, and the
  server calls fatal() and closes its connection to the attacker.
  

## Updates

The original code using Paramiko library has been updated to use the `ssh2-python` library for better compatibility and to avoid issues with Paramiko updates.

## Dependencies

Before running the updated code, you need to install the `ssh2-python` library:

``` pip install ssh2-python ```

## Usage

``` usage: ssh-check-username.py [-h] [-t HOSTNAME] [-p PORT] [-u USERNAME] [-w WORDLIST]

options:
  -h, --help   show this help message and exit
  -t HOSTNAME  Single target
  -p PORT      port to connect on: Default port is 22
  -u USERNAME  username you want to enumerate
  -w WORDLIST  enumerate multiple users
  ```


## Disclaimer

Please use this script responsibly and only on systems where you have permission to access. Unauthorized access to a system can lead to severe legal consequences.



