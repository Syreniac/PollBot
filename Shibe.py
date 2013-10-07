import random
import config

IGNORED_PHRASES=["",
				 "\t",
				 "\n"]

class Shibe:
	def __init__(self,parent):
		self.parent=parent
		
	def __call__(self,msg):
		if msg["body"].startswith("!shibe ") and not msg["mucnick"] in config.excluded:
			
			spli=msg["body"].split(" ")
			
			del spli[0]
			if spli[0].lower()=="everyone" and msg["type"]=="chat":
				spli=self.parent.jidList.keys()
				
			a=0
			while a<len(spli):
				if spli[a] in IGNORED_PHRASES or spli.count(spli[a])>1:
					del spli[a]
				else:
					a+=1
			
			random.shuffle(spli)
			
			l=["very",
			   "so",
			   "much",
			   "such"]
			   
			l2=[None]
			
			maxLength=min(8,len(spli))
			wowCount=0
			dWowCount=random.randint(int(len(spli)**0.5),int(len(spli)))
			wows=[]
			for i in range(dWowCount):
				r=random.randint(0,len(spli)+dWowCount-2)
				while r in wows and r-1 in wows and r+1 in wows:
					r=random.randint(0,len(spli)+dWowCount-2) 
				wows.append(r)
			   
			sA=""
			runCount=0
			while len(spli)>0:
				if len(l2)>maxLength:
					del l2[random.randint(1,len(l2)-1)]
				r=None
				while r in l2:
					r=random.randint(0,8)+2
				l2.append(r)
				s=""
				for j in range(r):
					s+="\t"
				if not runCount in wows:
					sA+="\n"+s+random.choice(l)+" "+spli.pop(0)
				else:
					sA+="\n"+s+"wow"
				runCount+=1
					
				
			if msg["type"]=="groupchat":
				self.parent.send_message(mto=self.parent.channel,mbody=sA,mtype="groupchat")
			else:
				self.parent.send_message(mto=msg["from"],mbody=sA,mtype="chat")
				
			
			
				