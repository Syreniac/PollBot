
import optparse
	
import sleekxmpp
import ssl

import time

import string

# Try to get the config. This is needed for admins and also an optional set of default commandline args.
# This is also the time to get any functionality modules.
import config

import random

def getLetter(a,b=None):
	if b!=None:
		l=[]
		for i in string.lowercase[a:b]:
			l.append(i)
		return l
	else:
		return string.lowercase[a]
	

class PollBot(sleekxmpp.ClientXMPP):
	def __init__(self, jid, password, nick, channel, excludedNames, tiebreaker):
		self.excludedNames=excludedNames
		self.tiebreaker=tiebreaker
		sleekxmpp.ClientXMPP.__init__(self, jid, password)
		self.jid = jid
		self.password = password
		self.nick = nick
		self.channel = channel
		
		self.recentUsers=[]

		
		self.jidList=[]
		self.polled=[]
		self.polling=0
		self.time=time.time()

		self.add_event_handler("session_start", self.start)
		self.add_event_handler("groupchat_presence", self.updateJIDs)
		self.add_event_handler("message", self.msg_handler)

	def start(self, event):
		self.send_presence()
		r=self.get_roster()
		self.plugin['xep_0045'].joinMUC(self.channel, self.nick, wait=False)
		
	def updateJIDs(self,msg):
		m=str(msg["from"]).split("/")[1]
		print m
		if m.lower() in self.excludedNames:
			return
		elif msg["type"]=="available":
			if not msg["from"] in self.jidList:
				self.jidList.append(msg["from"])
		elif msg["type"]!="subscribe":
			if msg["from"] in self.jidList:
				self.jidList.remove(msg["from"])
		for i in self.jidList:
			print i
			
	def pollOver(self,b=None):
		print b
		if self.polling!=0 or b!=None:
			if b==None:
				self.send_message(mto=self.channel, mbody="The poll is over!", mtype="groupchat")
			self.polling=0
			if self.pollresults[0]>self.pollresults[1] or b==True:
				if b!=None:
					sendString=self.pollOptions[0]+" is the winner through "+self.tiebreaker+"'s decision!"
				else:
					sendString=self.pollOptions[0]+" is the winner with "+str(self.pollresults[0])+" votes to "+str(self.pollresults[1])+"!"
			elif self.pollresults[1]>self.pollresults[0] or b==False:
				if b!=None:
					sendString=self.pollOptions[1]+" is the winner through "+self.tiebreaker+"'s decision!"
				else:
					sendString=self.pollOptions[1]+" is the winner with "+str(self.pollresults[1])+" votes to "+str(self.pollresults[0])+"!"
			else:
				sendString="It's a tie!"
				self.polling=-1
				self.scheduler.add("Tiebreak",1.0,self.tiebreak,repeat=False)

				
			self.send_message(mto=self.channel, mbody=sendString, mtype="groupchat")
		
	def pollBreak(self):
		print "pollover"
		self.scheduler.remove("Poll")
		self.pollOver()

		
	def tiebreak(self):
		if self.tiebreaker=="Eurobot":
			sendString="Eurobot: "+self.pollOptions[0]+", c/d?"
		else:
			sendString=self.tiebreaker+": "+self.pollOptions[0]+", c/d?"
		self.send_message(mto=self.channel, mbody=sendString, mtype="groupchat")
			
	def msg_handler(self, msg):	
	
		if msg["mucnick"]=="plexasaideron" and "terrible coding" in msg["body"].lower():
			self.send_message(mto=self.channel, mbody=":argh:", mtype="groupchat")
			
		if "tele:ssh:" in msg["body"]:
			self.send_message(mto=self.channel, mbody="Teledhil:", mtype="groupchat")
			
		if msg["body"].startswith("!random") and not msg["mucnick"] in self.excludedNames:
			s=random.choice(self.jidList)
			print s
			self.send_message(mto=self.channel, mbody=str(s).split("/")[1],mtype="groupchat")
			
		if msg["body"].startswith("!timer"):
			print "!timer"
			m=msg["body"].replace("!timer","")
			m=m.split(" ")
			try:
				i=float(m[2])
				n=m[1]
				self.scheduler.add("Timer:"+msg["mucnick"],i,self.timering,args=(n,),repeat=False)
			except ValueError:
				pass
	
		if msg["body"].lower().startswith("!die"):
			if msg["from"].bare in config.admins:
				self.disconnect(wait=True)
		elif self.polling==1:
			if msg["mucnick"] in self.excludedNames:
				self.send_message(mto=self.channel, mbody="My parents told me not to talk to people like you, "+msg["mucnick"], mtype="groupchat")
			else:
				m=msg["body"].lower()
				if msg["mucnick"]==self.pollStart:
					print "pollStart"
					if m.startswith("!pollover"):
						self.pollBreak()
				if m in ["a","b"]:
					if not msg["from"] in self.polled:
						self.polled.append(msg["from"])
						vote=ord(m[0]) - 97
						print vote
						self.pollresults[vote]+=1
						if len(self.polled)==len(self.jidList):
							self.scheduler.remove("Poll")
							self.pollBreak()
					else:
						sendString="No cheating please, "+str(msg["mucnick"])
						self.send_message(mto=self.channel, mbody=sendString, mtype="groupchat")
		elif self.polling==-1:
			print msg["mucnick"]==self.tiebreaker
			if msg["mucnick"]==self.tiebreaker:
				self.pollOver(msg["body"].lower()=="c")
		elif self.polling==0:
			if msg["body"].startswith("!poll") and not msg["mucnick"] in self.excludedNames and not msg["mucnick"] in self.recentUsers and not msg["body"].startswith("!pollover"):
				
				self.recentUsers.append(msg["mucnick"])
				
				m=msg["body"].lstrip("!poll")
				m=m.rstrip("?")
				if m[0]==" ":
					m=m[1:]
				
				m=m.split(" or ")
				
				if len(m)>1:
				
				
					sendString="Poll noted."
					
					self.pollresults=[0,0]
					self.pollOptions=[m[0],m[1]]
					self.polled=[]
					sendString+="\n\t"+"A"+": "+m[0]
					sendString+="\n\t"+"B"+": "+m[1]
					
					sendString+="\nPlease enter your choices using the relevant letters."
						
					self.polling=1
					
					self.pollStart=msg["mucnick"]
					
					self.scheduler.add("Poll",30.0,self.pollFunc,repeat=False)
					try:
						self.scheduler.remove("Countout"+msg["mucnick"])
					except KeyError:
						pass
					self.scheduler.add("Countout"+msg["mucnick"],60.0,self.removeRecentness,args=(msg["mucnick"],),repeat=False)
			
					self.send_message(mto=self.channel, mbody=sendString, mtype="groupchat")
				else:
					self.send_message(mto=self.channel, mbody="That poll is terrible, and I don't like it", mtype="groupchat")

	def pollFunc(self):
		self.pollOver()
		
	def removeRecentness(self,name):
		self.recentUsers.remove(name)
		
	def timering(self,name):
		self.send_message(mto=self.channel, mbody=name+": time's up!", mtype="groupchat")
				
if __name__ == "__main__":

	# Object to parse and hold options for server and MUCs.
	optionParser = optparse.OptionParser()

	optionParser.add_option("-j", "--jid", help="JID to connect with.", dest="jid")
	optionParser.add_option("-p", "--password", help="Password to connect with.", dest="password")
	optionParser.add_option("-n", "--nick", help="Nick to use in channels.", dest="nick")
	optionParser.add_option("-c", "--channel", help="Channel to work in.", dest="channel")
	optionParser.add_option("-e", "--excluded", help="Names that cannot vote.", dest="excluded")
	optionParser.add_option("-t", "--tiebreaker", help="The deciding vote.", dest="tiebreaker")
	optionParser.add_option("-s", "--server", help="Which server.", dest="server")

	options, args = optionParser.parse_args()

	# Ensure we grabbed all the required options. If we didn't, check to see if we have one in the config.
	if options.jid is None:
		try:
			options.jid = config.jid
		except NameError:
			print "I require a JID."
			exit()
	if options.password is None:
		try:
			options.password = config.password
		except NameError:
			print "I require a password."
			exit()
	if options.nick is None:
		try:
			options.nick = config.nick
		except NameError:
			print "I require a nick."
			exit()
	if options.channel is None:
		try:
			options.channel = config.channel
		except NameError:
			print "I require a channel to join."
			exit()
			
	if options.excluded is None:
		try:
			options.excluded = config.excluded
		except NameError:
			pass
			
	if options.tiebreaker is None:
		try:
			options.tiebreaker = config.tiebreaker
		except NameError:
			pass
			
	if options.server is None:
		try:
			options.server = config.server
		except NameError:
			print "I require a server to join."
			exit()


	# Instantiate the bot and load the required plugins.
	bot = PollBot(options.jid, options.password, options.nick, options.channel, options.excluded, options.tiebreaker)
	bot.register_plugin('xep_0030')	 # Service discovery.
	bot.register_plugin('xep_0045')	 # MUC support.
	bot.register_plugin('xep_0199')	 # XMPP Ping
	bot.ssl_version = ssl.PROTOCOL_SSLv3

	if bot.connect((options.server,5222)):
		bot.process(block=True)
	else:
		print "Failed to connect."
		exit()