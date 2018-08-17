# ssh-user-enumeration
While reviewing the latest OpenSSH commits, we stumbled across:

https://github.com/openbsd/src/commit/779974d35b4859c07bc3cb8a12c74b43b0a7d1e0

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
