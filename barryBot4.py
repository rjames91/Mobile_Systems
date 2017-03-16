#### newbarryBot
# BarryBot client for COMP28512 - MobileSystems
# Orginially written by Andrew Leeming 2014
####

from socket import *
import select
import threading
import time,datetime
import re
import traceback
import sys
import random
import binascii

#####
# Updates
#	April/2015 : Added LAB variable to change the behaviour of barrybot (there is a slight difference between lab 4 and 5 versions, i.e. channel simulator)
#####


###
# Change this to reflect if you are running barryBot for lab 4 or 5
# STUDENT TODO: You need to do this from 2016 onwards.
###
LAB=4




############################################################
# YOU SHOULD NOT NEED TO CHANGE ANYTHING FROM HERE ONWARDS #
############################################################



BUFF = 4096
HOST = '127.0.0.1' #Default if no ip given as arg
SERVER_PORT = 9999 #Default if no port given as arg
CHANNEL_PORT = 9998

REPEAT_MSG="Sent by BarryBot, School of Computer Science, The University of Manchester"
KEY = 	   "1<AK8JNZBCHXUHCV1A?BYSE8PQW485M=XIK84MATON2NYYNU9KLWHBQO=PWPF<TE=L5SY601I1"
KEY_LEN=len(REPEAT_MSG)

SIG_PR=0.2	#This is the probability that the bot adds the signature instead of the fragment of text


#First paragraph from wikipedia about UoM - http://en.wikipedia.org/wiki/University_of_Manchester
TEXT_PIECE='''The University of Manchester is a large research university situated in the city of Manchester, England. Manchester University - as it is commonly known - is a public university formed in 2004 by the merger of the University of Manchester Institute of Science and Technology (est. 1824) and the Victoria University of Manchester (est. 1851). Manchester is a member of the worldwide Universities Research Association group, the Russell Group of British research universities and the N8 Group. The University of Manchester has been a "red brick university" since 1880 when Victoria University gained its royal charter.'''

def genRandStr (size):
	gen=""
	for i in xrange(size):		
		gen=gen+chr(random.randint(48,90))
	#end for
	return gen
#end genRandStr

def sxor (s1,s2):
	'''
	Basically an XOR but using char versions of 0 and 1
	'''
	xorstr=""
	#These strings should be '0' and '1' only
	for a,b in zip(s1,s2):
		xorstr = xorstr + str(int(a)^int(b))
	#end for

	return xorstr
#end sxor

#http://stackoverflow.com/questions/7396849/convert-binary-to-ascii-and-vice-versa-python
def str2bin (s):
	return bin(int(binascii.hexlify(s), 16))
#end str2bin
def bin2str (b):
	return binascii.unhexlify('%x' % int(b, 2))
#end bin2str

def encrypt (s):
	'''
	Encrypt (XOR) a string 's' using KEY.
	'''
	cipherstr=""

	#s and KEY should be same size
	if len(s) != len(KEY):
		print "ERROR string to encrypt not same length as key"
		

	for chars in zip(s,KEY):
		c=chr(ord(chars[0])^ord(chars[1]))
		cipherstr = cipherstr + c
	return cipherstr
#end encrypt


def padLeftZeros(s, multiple):
	'''
	Since 0's on the LHS are chopped off, stick them back in
	since we are treating s as a string not a number
	'''
	while len(s) % multiple != 0:
		s = '0'+s
	return s

def getRandText():
	starti = random.randint(0,len(TEXT_PIECE)-KEY_LEN)		
	return TEXT_PIECE[starti:starti+KEY_LEN]
#end getRandText

if __name__=='__main__':
	if len(sys.argv) == 2:
		HOST=sys.argv[1]

	socklst=[]
	#Set up socket connections
	svr=socket(AF_INET, SOCK_STREAM)
	svr.connect((HOST,SERVER_PORT))
	socklst.append(svr)
	
	if LAB==5:
		sim=socket(AF_INET, SOCK_STREAM)
		sim.connect((HOST,CHANNEL_PORT))
		socklst.append(sim)

	KEY=genRandStr(KEY_LEN)	#This would be used if you wanted a random key every time you run barryBot
								#else KEY is statically defined
	#print "KEY is ",KEY
	
	errorset=False

	#Register barrybot
	if LAB==4:
		svr.send("REGISTER BarryBot4")
	elif LAB==5:
		svr.send("REGISTER BarryBot5")
	else:
		print("Error: It looks like you did not set a valid value for LAB! Valid values are 4 or 5.");
		errorset=True
	
	try:
		while(not errorset):
			ready_socks,_,_ = select.select(socklst, [], [])
			for sock in ready_socks:
				#Grab the ip and port values of this socket (we do not know which one it is yet)
				iip,pport = sock.getpeername()#
				print iip,pport
				data = sock.recv(BUFF)
				#If Socket closed
				if not data: 
					sock.close()
					print "Socket connection lost - Exiting BarryBot"
					sys.exit()

				if pport == SERVER_PORT:
					print "SERVER PORT :",data

					if data[:6].upper() == "INVITE":
						print "Accepting invite :",data
						sock.send("ACCEPT "+data[7:]);
					elif data[:3].upper() == "MSG":	#Keeping MSG for debugging
						w=data[4:].split(' ',1)
						print "Msg on server port :",data
						sock.send("MSG "+w[0]+" I AM A ROBOT : "+w[1]);
					#else drop the message
			
				elif pport == CHANNEL_PORT:
					print "CHANNEL PORT :",data
					
					#Grab FROM
					fw = data.split(' ',1)
					fromwho = fw[0]
					data = fw[1]
					
					#This is a special command that the bot responds to. 
					if data[:7].upper() == "ENCRYPT":
						
						if random.random() < SIG_PR:	# chance of outputing the signature
							text = REPEAT_MSG
						else:
							#The rest of data is discarded now, grab random text
							text = getRandText()
						#Encrypt it
						print "Random text is :",text
						en = encrypt(text)
						print "Encrypted version is :",en

						#For the lab, encode into ascii-binary
						asciibin = str2bin(en)
						asciibin = padLeftZeros(asciibin[2:],8)	#make sure bin is multiple of 8bits
						print "ascii version is :",asciibin
					
						sock.send("0"+fromwho+" "+asciibin+"\n")
					else:
						sock.send("0"+fromwho+" "+data)
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

