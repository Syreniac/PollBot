import praw
import random
import config

class AwwLink:
	def __init__(self,parent):
		self.r=praw.Reddit(user_agent="Syreniac")
		self.parent=parent
		
	def __call__(self,msg):
		if msg["body"].lower()=="!aww" or msg["body"].lower()=="!fluffy" or msg["body"].lower()=="!cute" or msg["body"].lower()=="!cuddly":
			self.parent.send_message(mto=self.parent.channel,mbody=self.get_aww_new(),mtype="groupchat")
			
	def get_aww_new(self):
		submissions=self.r.get_subreddit("kittens").get_hot(limit=10)
		a=None
		a1=None
		limit=random.randint(0,9)
		while limit>0:
			a1=a
			try:
				a=next(submissions)
			except StopIteration:
				a=a1
				break
			limit-=1
			
		return "\n"+str(a.title)+"\n\t"+str(a.url)
		
class GenericRedditLink:
	def __init__(self,parent):
		self.r=praw.Reddit(user_agent="Syreniac")
		self.parent=parent
		
	def __call__(self,msg):
		if msg["body"].lower().startswith("!r/"):
			m=msg["body"].lstrip("!r/")
			spli=m.split(":")
			subreddit=spli[0]
			print subreddit
			if subreddit in config.banned_subreddits:
				self.scheduler.add("punishment:"+mucnick,0.1,self.punishment,args=(mucnick,),repeat=True)
				self.parent.send_message(mto=self.parent.channel,mbody="Nope, not touching that.",mtype="groupchat")
				return
					
			body=self.get_hot(subreddit,msg)
			if body!=None:
				self.parent.send_message(mto=self.parent.channel,mbody=body,mtype="groupchat")
		
		if msg["body"].lower().startswith("!block ") and msg["mucnick"] in config.admins:
			m=m.spli(" ")
			subreddit=spli[1]
			config.banned_subreddits.append(subreddit)
			
	def get_hot(self,subreddit,msg):
		try:
			subreddit=self.r.get_subreddit(subreddit)
			if subreddit.over18:
				pass
		except InvalidSubReddit:
			self.parent.send_message(mto=self.parent.channel,mbody="Learn to Reddit please, "+msg["mucnick"],mtype="groupchat")
			return None
			
		if subreddit.over18:
			#self.parent.send_message(mto=self.parent.channel,mbody="NSFW content is currently blocked. Direct complaints to mods and admins.",mtype="groupchat")
			extra=" :nws: "
		else:
			extra=""
			
		submissions=subreddit.get_hot(limit=10)
		a=None
		a1=None
		limit=random.randint(0,9)
		while limit>0:
			a1=a
			print a1
			try:
				a=next(submissions)
			except StopIteration:
				a=a1
				break
			print a
			limit-=1
			
		return "\n"+extra+str(a.title)+extra+"\n"+extra+str(a.url)+extra
		
			