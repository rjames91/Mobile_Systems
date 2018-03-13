#----- ----- ----- ----- ----- ----- ----- ----
# BarryBot client for COMP28512 Mobile Systems
# Originally by Andrew Leeming 2014
# Modified by Danny Wood & Robert James 25/3/2017
# Thanks to Igor Wodiany for his corrections
# modified by Barry and Robert 03/18
#----- ----- ----- ----- ----- ----- ----- ----
from socket import *
import select
import threading
import time,datetime
import re
import traceback
import sys
import random
import binascii

BUFFSIZE = 4096
HOST = '127.0.0.1' #Default if no ip given as arg
SERVER_PORT = 9999 #Default if no port given as arg

REPEAT_MSG="Sent by BarryBot, School of Computer Science, The University of Manchester"
#Fixed key for testing:
KEY =      "1<ZK8JNZBCHXUHCV1A?BYSE8PQW485M=XIK84MATON2NYYNU9KLWHBQO=PWPF<TE=L5SY601I1"
KEY_LEN=len(REPEAT_MSG)

SIG_PR=0.2      #Probability of signature instead of a fragment of text

TEXT_PIECE = '''Standard 64-bit WEP uses a 40 bit key (also known as WEP-40), which is concatenated with a 24-bit initialization vector (IV) to form the RC4 key. At the time that the original WEP standard was drafted, the U.S. Government's export restrictions on cryptographic technology limited the key size. Once the restrictions were lifted, manufacturers of access points implemented an extended 128-bit WEP protocol using a 104-bit key size (WEP-104).'''

def genRandStr (size):
    '''
    Generate a random string of 8-bit ASCII chars
    '''
    gen=""
    for i in xrange(size):
        gen=gen+chr(random.randint(48,90))
    #end for
    return gen
#end of genRandStr method
#----- ----- ----- ----- ----- ----- ----- ----

def sxor (s1,s2):
    '''
    XOR of strings s1 & s2 using char versions of 0 and 1
    '''
    xorstr=""
    #Strings s1 & s2 should contain '0' and '1' chars only
    for a,b in zip(s1,s2):
        xorstr = xorstr + str(int(a)^int(b))
    #end for
    return xorstr
# End of sxor method
# --- --- --- --- --- --- --- --- --- --- --- ---

def str2bin (s):
    # Convert string s to binary form ????? 
    return bin(int(binascii.hexlify(s), 16))
#end of str2bin function
# --- --- --- --- --- --- --- --- --- --- --- ---

def bin2str (b):
    # Convert binary b to string form ????
    return binascii.unhexlify('%x' % int(b, 2))
#end of bin2str function
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
#stackoverflow/questions/7396849/convert-binary-to-ascii-&-vice-versa
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

def encrypt (s):
    '''
    Encrypt a string 's' using random text array KEY.
    '''
    cipherstr=""
    # s and KEY should be ASCII strings of same length
    if len(s) != len(KEY):
        print "ERROR in encrypt: strings s & KEY not of same length"
    for chars in zip(s,KEY):  # chars is 2 element list 
        c=chr(ord(chars[0])^ord(chars[1]))
        cipherstr = cipherstr + c
    return cipherstr
#end of encrypt function
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---

def padLeftZeros(s, multiple):
    '''
    Since 0's on the LHS are chopped off, stick them back in
    since we are treating s as a string not a number
    '''
    while len(s) % multiple != 0:
        s = '0'+s
    return s
#end of function

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
def getRandText():
    starti = random.randint(0,len(TEXT_PIECE)-KEY_LEN)
    return TEXT_PIECE[starti:starti+KEY_LEN]
#end of getRandText function

# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
# Start of main 
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
if __name__=='__main__':
    if len(sys.argv) == 2:
        HOST=sys.argv[1]

    socklst=[]
    #Set up socket connections
    svr=socket(AF_INET, SOCK_STREAM)
    svr.connect((HOST,SERVER_PORT))
    socklst.append(svr)

    KEY=genRandStr(KEY_LEN) #This would be used if you wanted a random key every time you run barryBot
                                                            #else KEY is statically defined
    #print "KEY is ",KEY

    errorset=False

    #Register barrybot
    svr.send("REGISTER BarryBot")

    try:
        while(not errorset):
            ready_socks,_,_ = select.select([svr], [], [])
            for sock in ready_socks:
                #Grab the ip and port values of this socket (we do not know which one it is yet)
                #iip,pport = sock.getpeername()#
                data = sock.recv(BUFFSIZE)
                #If Socket closed
                if not data:
                    sock.close()
                    print "Socket connection lost - Exiting BarryBot"
                    sys.exit()

                print "SERVER PORT :",data
                fw = data.split(" ", 1)
                fromwho = fw[0]

                if data[:6].upper() == "INVITE":
                    print "Accepting invite :",data
                    sock.send("ACCEPT "+data[7:]);
                elif data[:3].upper() == "MSG": #Keeping MSG for debugging
                    w=data[4:].split(' ',1)
                    print "Msg on server port :",data
                    msg = \
                    re.sub("[Bb]arry([Bb]ot5?)?",
                            w[0], w[1])
                    sock.send("MSG "+w[0]+" MY REPLY : " + msg);#+w[1] );


                elif data[0].isdigit():
                    data = data[1+len(fromwho):]
                    fromwho = fromwho[1:]
                    if "ENCRYPT" in data[:9].upper() and len(data) <=9:
                        if random.random() < SIG_PR:        # chance of outputing the signature
                            text = REPEAT_MSG
                        else:
                            #Rest of data discarded now, grab random text
                            text = getRandText()
                        #Encrypt it
                        print "Random text is :",text
                        en = encrypt(text)
                        print "Encrypted version is :",en

                        #For the lab, encode into ascii-binary
                        asciibin = str2bin(en)
                        asciibin = padLeftZeros(asciibin[2:],8)     
                        #make sure bin is multiple of 8bits
                        print "ascii version is :",asciibin
                        sock.send("0MSG "+fromwho+" "+asciibin+"\n")
                    else:
                        data = "BarryBot (via channel): " + data
                        sock.send( "0MSG "+fromwho+" "+data+"\n")
                #end if pport
            #end for all sock
        #end while
    except KeyboardInterrupt:
        print "Catching keyboard interrupt"

    #End of program, finish up
    #Close all sockets
    for sk in socklst:
        sk.close()
#end main

