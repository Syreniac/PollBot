
import logging

import optparse
	
import sleekxmpp
import ssl

import time

import string

from os import listdir
from os.path import isfile, join

import redditLink

# Try to get the config. This is needed for admins and also an optional set of default commandline args.
# This is also the time to get any functionality modules.
import config

import random

from poker import *

from overlyComplex import *

def random_string(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))


def jid2nick(jid):
	return str(jid).split("/")[1]
	
def nick2jid(nick):
	return config.channel+"/"+nick

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
		self.pimpamspamPreparing=None
		self.bossstubsMemorial=True
		
		self.pimpamspam={}
		
		self.redditLink=redditLink.GenericRedditLink(self)
		
		self.pounces={}

		self.cakes=[ f for f in listdir("cakes/") if isfile(join("cakes/",f)) ]
		a=0
		while a<len(self.cakes):
			self.cakes[a]="cakes/"+self.cakes[a]
			a+=1
		print self.cakes
		
		self.pokerBot=PokerBot(self)
		
		self.Nichya="Nichya"
		self.NichyaIgnored=True
		
		self.Ergoj="Ergoj Ormand"
		self.ErgojWatched=False
		
		self.jidList=[]
		self.polled=[]
		self.polling=0
		self.time=time.time()

		self.add_event_handler("session_start", self.start)
		self.add_event_handler("groupchat_presence", self.updateJIDs)
		self.add_event_handler("groupchat_message", self.msg_handler)
			
	def start(self, event):
		self.send_presence()
		r=self.get_roster()
		self.plugin['xep_0045'].joinMUC(self.channel, self.nick, wait=False)
		self.plugin['xep_0045'].joinMUC(self.channel, self.nick, wait=False)
		
	def updateJIDs(self,msg):
		code=getCode(msg)
		temp=self.jidList[:]
		spli=str(msg["from"]).split("/")
		m=spli[1]
		if m.lower() in self.excludedNames:
			return
		elif msg["type"]=="available":
			print "ADDING "+m+":"+str(msg["type"])
			if self.pounces.has_key(m):
				self.send_message(mto=self.channel, mbody=m+": "+self.pounces[m], mtype="groupchat")
				del self.pounces[m]
			if not m in self.jidList:
				self.jidList.append(m)
			if self.Nichya==None:
				self.Nichya=m
				print "Nichya Detected"
			if self.Ergoj==None:
				self.Ergoj=m
				print "Ergoj Detected"
				
			if self.polled.count(None)>0:
				self.polled[self.polled.index(None)]=m
		elif msg["type"]!="subscribe":
			# if "muc" in msg.keys():
				# if str(msg["muc"]["role"])=="none":
					# self.send_message(mto=self.channel,mbody="Mods are literally hitler! :godwin:",mtype="groupchat")
			print "REMOVING "+m+":"+str(msg["type"])
			if m==self.Nichya and code==303:
				self.Nichya=None
			elif m==self.Nichya:
				self.Nichya=="Nichya"
			elif m==self.Ergoj:
				self.Ergoj=None
			if code==307:
				self.send_message(mto=self.channel,mbody="mods are literally hitler :godwin:",mtype="groupchat")
			if m in self.jidList:
				self.jidList.remove(m)
			if m in self.polled:
				self.polled[self.polled.index(m)]=None
				print self.polled
		print "-------------------"
			
	def pollOver(self,b=None):
		print b
		if self.polling!=0 or b!=None:
			if b==None:
				self.send_message(mto=self.channel, mbody="The poll is over!", mtype="groupchat")
			self.polling=0
			
			c=0
			m=max(self.pollresults)
			for i in self.pollresults:
				if i==m:
					c+=1
			
			if c>1 and b==None:
				sendString="It's a tie!"
				self.polling=-1
				self.scheduler.add("Tiebreak",1.0,self.tiebreak,repeat=False)
			else:
				ind=self.pollresults.index(m)
				
				if b!=None:
					sendString=self.pollOptions[ind]+" is the winner through "+self.tiebreaker+"'s decision!"
				else:
					sendString=self.pollOptions[ind]+" is the winner with "+str(self.pollresults[ind])+" votes!"
			

				
			self.send_message(mto=self.channel, mbody=sendString, mtype="groupchat")
		
	def pollBreak(self):
		print "pollover"
		self.scheduler.remove("Poll")
		self.pollOver()

		
	def tiebreak(self):
		if self.tiebreaker=="eurobot":
			s=""
			a=0
			for i in self.pollOptions:
				if self.pollresults[a]==max(self.pollresults):
					s+=i+" or "
				a+=1
			s=s.rstrip(" or ")
			sendString="Eurobot: TIEBREAK: "+s+"?"
		else:
			sendString=self.tiebreaker+": "+self.pollOptions[0]+", c/d?"
		self.send_message(mto=self.channel, mbody=sendString, mtype="groupchat")
		
	def pimpamspamFunc(self,user):
		userNick=jid2nick(user)
		self.pimpamspam[userNick]+=1
		if self.pimpamspam[userNick]==60:
			self.pimpamspam[userNick]=None
			self.scheduler.remove(userNick+":Pimpamspam")
		self.send_message(mto=user, mbody="pim pam", mtype="chat")
		
	def bossStubsMemorial(self):
		self.bossstubsMemorial=True
		
	def jaffinatorS(self):
		self.send_message(mto=self.channel, mbody="/s", mtype="groupchat")
			
	def nichyaIgnorance(self):
		self.NichyaIgnored=True
		
	def ErgojWatching(self):
		self.ErgojWatched=False
		
	def ErgojFunc(self,mucnick):
		if mucnick==self.Ergoj:
			if self.ErgojWatched:
				self.punishing=True
				self.scheduler.add("punishment:"+mucnick,0.1,self.punishment,args=(mucnick,),repeat=True)
			self.ErgojWatched=True
			self.scheduler.add("Ergoj",10.0,self.ErgojWatching,repeat=False)
			
	def punishment(self,mucnick):
		if self.punishing:
			s=random_string(random.randint(1,32))
			self.send_message(mto=nick2jid(mucnick),mbody=s,mtype="chat")
			
	def msg_handler(self, msg):	

		if msg["mucnick"]==self.Nichya and self.NichyaIgnored:
			self.NichyaIgnored=False
			self.scheduler.add("nichya",10.0,self.nichyaIgnorance,repeat=False)
		elif msg["mucnick"]==self.Nichya and self.NichyaIgnored==False:
			return
			
		if msg["mucnick"]==self.Ergoj and self.ErgojWatched:
			return
	
		print msg["from"]
		
		if msg["body"].startswith("!fc"):
			self.send_message(mto=self.channel,mbody=self.FC(),mtype="groupchat")
			self.ErgojFunc(msg["mucnick"])
	
		# if msg["mucnick"]=="jaffinator":
			# self.scheduler.remove("Jaffinator")
			# self.scheduler.add("Jaffinator",3.0,self.jaffinatorS,repeat=False)
	
		#self.pokerBot(msg)
		self.redditLink(msg)
		
		if msg["body"].startswith("!help") and not msg["mucnick"].lower() in self.excludedNames:
			s="\n"
			s+="!koahi:\t\t\t\t\t\t\t\t\tgives you the Laws of Koahi"+"\n"
			#s+="!pounce [NAME]|[MESSAGE]:\t\t\t\t\tPings the named user with the message once they join the room"+"\n"
			s+="!help:\t\t\t\t\t\t\t\t\tshows the help text"+"\n"
			s+="!pimpamspam:\t \t\t\t\t\t\t[REDACTED]"+"\n"
			s+="!pm:\t\t\t\t\t\t\t\t\tNot much"+"\n"
			s+="!random:\t\t\t\t\t\t\t\tPings a random person on the channel"+"\n"
			s+="!timer [NAME] [TIME]:\t\t\t\t\t\tPings the person named after the time has elapsed"+"\n"
			s+="!shakespeare:\t\t\t\t\t\t\tMakes you a more cultured person"+"\n"
			s+="!die:\t\t\t\t\t\t\t\t\tIf pollbot likes you enough, it will close"+"\n"
			s+="!poll [OPTION] or [OPTION] ... or [OPTION]:\tStarts a poll with the entered options"+"\n"
			s+="!poker:\t\t\t\t\t\t\t\t\tAttempts to start a poker game. May get you modissar'd."+"\n"
			s+="There are also easter eggs for certain users."
			self.send_message(mto=msg["from"], mbody=s,mtype="chat")
		
		elif self.pimpamspamPreparing==msg["from"]:
			if msg["body"].startswith("confirmed"):
				self.pimpamspam[msg["mucnick"]]=0
				self.scheduler.add(msg["mucnick"]+":Pimpamspam",0.1,self.pimpamspamFunc,args=(self.pimpamspamPreparing,),repeat=True)
				self.pimpamspamPreparing=None
				
	
		elif msg["mucnick"].lower()=="plexasaideron" and "terrible coding" in msg["body"].lower():
			self.send_message(mto=self.channel, mbody=":argh:", mtype="groupchat")
			
		elif msg["mucnick"].lower()=="migui" and msg["body"].lower().startswith("http://") and (msg["body"].lower().endswith(".gif") or msg["body"].lower().endswith(".png") or msg["body"].lower().endswith(".jpg")):
			self.send_message(mto=self.channel,mbody=":frogsiren: Image linked by Migui, assume NSFW until proven otherwise :frogsiren:",mtype="groupchat")
			
		elif "dicks" in msg["body"] and self.bossstubsMemorial:
			self.bossstubsMemorial=False
			self.scheduler.add("bossstubs",10.0,self.bossStubsMemorial,repeat=False)
			l=self.jidList[:]
			a=0
			while a<len(l):
				l[a]=l[a].lower()
				a+=1
			if "dernarius" in l:
				self.send_message(mto=self.channel,mbody="Dernarius: ^",mtype="groupchat")
			
		elif msg["body"].startswith("!koahi") and not msg["mucnick"].lower() in self.excludedNames:
			self.send_message(mto=self.channel, mbody="\nDo:\n\tBe Cool\n\tHave Fun\nDon't\n\tBe Uncool\n\tGet Butthurt", mtype="groupchat")
			
		elif msg["body"].startswith("!pimpamspam") and not msg["mucnick"].lower() in self.excludedNames:
			print msg["mucnick"]+":"+str(config.admins)
			if msg["mucnick"] in config.admins:
				print "From an admin"
				try:
					n=msg["body"].split(":")[1]
					self.pimpamspam[n]=0
					self.scheduler.add(n+":Pimpamspam",0.1,self.pimpamspamFunc,args=(nick2jid(n),),repeat=True)
					self.pimpamspamPreparing=None
				except IndexError:
					self.send_message(mto=self.channel, mbody="Pimpamspam readied. Type confirmed to use. Please be warned that Syreniac is not responsible for any damages that may occur on use of this command", mtype="groupchat")
					self.pimpamspamPreparing=msg["from"]
			else:
				self.send_message(mto=self.channel, mbody="Pimpamspam readied. Type confirmed to use. Please be warned that Syreniac is not responsible for any damages that may occur on use of this command", mtype="groupchat")
				self.pimpamspamPreparing=msg["from"]
				
		elif msg["body"]==":order66:" and msg["mucnick"] in config.admins:
			for i in self.jidList:
				n=nick2jid(i)
				self.pimpamspam[i]=0
				self.pimpamspamPreparing=None
				self.scheduler.add(i+":Pimpamspam",0.1,self.pimpamspamFunc,args=(n,),repeat=True)
				
			
		elif "tele:ssh:" in msg["body"].lower():
			self.send_message(mto=self.channel, mbody="Don't worry Teledhil, I like your name", mtype="groupchat")
			
		elif msg["body"].startswith("!pm") and not msg["mucnick"].lower() in self.excludedNames:
			self.send_message(mto=msg["from"], mbody="What?",mtype="chat")
			
		elif msg["body"].startswith("!random") and not msg["mucnick"] in self.excludedNames:
			s=random.choice(self.jidList)
			self.send_message(mto=self.channel, mbody=s+":",mtype="groupchat")
			self.ErgojFunc(msg["mucnick"])
			
		elif msg["body"].startswith("!pounce") and not msg["mucnick"] in self.excludedNames:
			m=msg["body"].replace("!pounce ","")
			spli=m.split("|")
			self.pounces[spli[0]]=spli[1]
			print spli

			
		elif msg["body"].startswith("!timer"):
			m=msg["body"].replace("!timer","")
			m=m.split(" ")
			try:
				i=float(m[-1])
				n=""
				for s in m[1:-1]:
					n+=s+" "
				self.scheduler.add("Timer:"+msg["mucnick"],i,self.timering,args=(n),repeat=False)
			except ValueError:
				pass
		
		elif msg["body"].startswith("!shakespeare"):
			f=open("shakespeare/antony and cleopatra.txt","r")
			s=f.read()
			s=s.split("|")
			self.send_message(mto=self.channel, mbody=random.choice(s),mtype="groupchat")
			
		elif msg["body"].startswith("!cake"):
			fpath=random.choice(self.cakes)
			f=open(fpath,"r")
			s=f.read()
			self.send_message(mto=self.channel, mbody=s,mtype="groupchat")
			self.ErgojFunc(msg["mucnick"])
			
		elif msg["body"]=="they have suffered enough" and msg["mucnick"] in config.admins:
			print "punishment stopped"
			self.punishing=False
			self.scheduler.remove("punishment")
	
		elif msg["body"].lower().startswith("!die"):
			if msg["mucnick"] in config.admins:
				self.disconnect(wait=True)
		elif msg["body"].lower().startswith("!ohnoyoudon't"):
			if msg["mucnick"] in config.admins:
				self.pokerBot.analyze_hands()
		elif self.polling==1:
			if msg["mucnick"] in self.excludedNames:
				self.send_message(mto=self.channel, mbody="My parents told me not to talk to people like you, "+msg["mucnick"], mtype="groupchat")
			else:
				m=msg["body"].lower()
				if msg["mucnick"]==self.pollStart:
					if m.startswith("!pollover"):
						self.pollBreak()
				if m in self.pollkeys:
					if not msg["mucnick"] in self.polled:
						self.polled.append(msg["mucnick"])
						vote=ord(m[0]) - 97
						self.pollresults[vote]+=1
						print self.pollresults
						# if len(self.polled)==len(self.jidList):
							# self.scheduler.remove("Poll")
							# self.pollBreak()
					else:
						sendString="No cheating please, "+str(msg["mucnick"])
						self.send_message(mto=self.channel, mbody=sendString, mtype="groupchat")
		elif self.polling==-1:
			if msg["mucnick"]==self.tiebreaker:
				m=msg["body"].lower()
				if m in ["a","b"]:
					self.pollOver(m[0]=="a")
				else:
					self.polling=0
					self.send_message(mto=self.channel, mbody="Once again, Eurobot impresses me with its inability to make decisions",mtype="groupchat")
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
					
					self.pollresults=[]
					self.pollOptions=[]
					self.pollkeys=[]
					self.polled=[]
					a=0
					for i in m:
						
						sendString+="\n\t"+getLetter(a).upper()+": "+i
						self.pollOptions.append(i)
						self.pollresults.append(0)
						self.pollkeys.append(getLetter(a))
						a+=1
				
					
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
			
		self.send_message(mto=self.channel, mbody=name.rstrip(" ")+": time's up!", mtype="groupchat")
	def FC(self):
		commands=["Primary is %",
				  "Secondary is %",
				  "Don't shoot %",
				  "Shoot %",
				  "Burn towards %",
				  "Burn away from %",
				  "More bubbles on %",
				  "Get the bubbles off %",
				  "Flee for your lives from %",
				  "Oh god what even is $",
				  "Warp to %",
				  "Align to %",
				  "Web %",
				  "Tackle %",
				  "Scram %",
				  "Point %",
				  "Paint %",
				  "Damp %",
				  "Jam %",
				  "Stop DPS on %",
				  "More DPS on %",
				  "Scatter away from %",
				  "Starburst everywhere",
				  "Recite a terrible fanfic to %",
				  "Bump %",
				  "Don't bump %",
				  "Get reps on %",
				  "Stop reps on %",
				  "Reps aren't holding on %",
				  "Bring $",
				  "Don't bring $",
				  "Gate is Red",
				  "Gate is Green",
				  "Free burn",
				  "If you jump, you're dead",
				  "You jumped, didn't you?",
				  "Can I get my & to scout?",
				  "Time to commissar %",
				  "RABBLE RABBLE RABBLE",
				  "CHECK CHECK CHECK",
				  "SHUT THE FUCK UP",
				  "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
				  "Put gfs in local",
				  "Smack talk in local",
				  "Orbit $ at *",
				  "Keep at Range $ at *",
				  "We're standing down",
				  "Does anyone have a perch?",
				  'Log in to Kugu and post "YOU GOT DUNKED"',
				  'Log in to Kugu and whine about blobs',
				  'Log in to Kugu and shitpost',
				  'Log in to Kugu and blame Goons',
				  "Don't worry PL will save us",
				  "Wait, why are they shooting us?",
				  "Wait, they're blues?",
				  "Who bombed the blues?",
				  "It's awoxing time!",
				  "Who's alt just awoxed?",
				  "SPAIS!!!!!!",
				  "We need more spies!",
				  "We need more #",
				  "Why would we need more #",
				  "# are useless for this fleet",
				  "Anchor on me",
				  "Align to a random celestial",
				  "Hands are clean!",
				  "Blame & for this.",
				  "& is the primary",
				  "&, you're getting commissar'd",
				  "Cyno's up",
				  "Bridge, bridge, bridge",
				  "Jump, jump, jump",
				  "Diplos can deal with it",
				  "Hostile supers tackled :frogsiren:",
				  "Ha, jokes on you, it's actually a structure shoot",
				  "Well, I've been poached by PL, see you round!",
				  "Well, I've been poached by DYS0N, see you later!",
				  "Well, I've been poached by EMP, see you later!",
				  "Well, I've been poached by Goons, see you later!"
				  ]
				  
		targets=["Rifter",
				 "Burst",
				 "Slasher",
				 "Vigil",
				 "Breacher",
				 "Tristan",
				 "Incursus",
				 "Atron",
				 "Maulus",
				 "Navitas",
				 "Merlin",
				 "Kestrel",
				 "Condor",
				 "Griffin",
				 "Bantam",
				 "Punisher",
				 "Inquisitor",
				 "Executioner",
				 "Tormentor",
				 "Crucifier",
				 "@whatever &'s flying",
				 "Nyx",
				 "Aeon",
				 "Wyvern",
				 "Hel",
				 "SC",
				 "Erebus",
				 "Avatar",
				 "Ragnarok",
				 "Leviathan",
				 "Titan",
				 "Fucking Titan",
				 "Falcon",
				 "Blackbird",
				 "Scimitar",
				 "Scimi",
				 "Basi",
				 "Basilisk",
				 "Oneiros",
				 "Guardian",
				 "Armageddon",
				 "Apocalypse",
				 "Abaddon",
				 "Raven",
				 "Rokh",
				 "Scorpion",
				 "Dominix",
				 "Megathron",
				 "Hyperion",
				 "Typhoon",
				 "Tempest",
				 "Maelstrom",
				 "Drake",
				 "Hurricane",
				 "Myrmidon",
				 "Harbinger",
				 "Ferox",
				 "Cyclone",
				 "Prophecy",
				 "Brutix",
				 "Talos",
				 "Oracle",
				 "Naga",
				 "Tornado",
				 "Vindicator",
				 "Rattlesnake",
				 "Bhaalgorn",
				 "Machariel",
				 "Nightmare",
				 "Thorax",
				 "Rupture",
				 "Moa",
				 "Maller",
				 "Gate",
				 "POS",
				 "Station",
				 "Hulk",
				 "Orca",
				 "Proteus",
				 "Tengu",
				 "Legion",
				 "Loki",
				 "Velator",
				 "Goon"]
				 
		t=random.choice(targets)
		c=random.choice(commands)
		if not t.startswith("@"):
			c=c.replace("%","the "+t)
			if t.lower().startswith("a") or t.lower().startswith("e") or t.lower().startswith("i") or t.lower().startswith("o") or t.lower().startswith("u"):
				c=c.replace("$","an "+t)
			else:
				c=c.replace("$","a "+t)
		else:
			t=t.replace("@","")
			c=c.replace("%",t)
			c=c.replace("$",t)
		r=random.randint(1,6)*5
		c=c.replace("*",str(r))
		c=c.replace("&",t)
		c=c.replace("#",t+"s")
		c=c.replace("&",random.choice(self.jidList))
		return c
				
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

	
	logging.basicConfig(format='%(levelname)-8s %(message)s')
	
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