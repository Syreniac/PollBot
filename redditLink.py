from praw import errors,Reddit
from requests.exceptions import HTTPError, RequestException, MissingSchema, InvalidURL
import random
import config
import datetime
import config
		
def nick2jid(nick):
	return config.channel+"/"+nick
		
class GenericRedditLink:
	def __init__(self,parent):
		self.r=Reddit(user_agent="PollBotBestBot")
		self.parent=parent
		
	def __call__(self,msg):
		if msg["body"].lower().startswith("!r/"):
			m=msg["body"].lstrip("!r/")
			spli=m.split(":")
			subreddit=spli[0]
			print subreddit
			if subreddit in config.banned_subreddits:
				self.parent.scheduler.add("punishment:"+msg["mucnick"],0.1,self.parent.punishment,args=(msg["mucnick"],),repeat=True)
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
		if msg["type"]=="groupchat":
			subreddit=self.r.get_subreddit(subreddit)
			try:
				if subreddit.over18:
					pass
			except (HTTPError, errors.InvalidSubreddit) as E:
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
			
			try:
				return "\n"+extra+str(a.title)+extra+"\n"+extra+str(a.url)+extra
			except AttributeError:
				return "Reddit API is currently not accepting connections. Please wait ~30 seconds before retrying."
		
class EurosquadRedditLink:
	def __init__(self,parent):
		self.r=Reddit(user_agent="PollBotBestBot")#
		self.r.login("PollBotBestBot", config.reddit_password)
		self.parent=parent
		self.values=[]
		self.limit=1000
		
		self.currentSubmission=""
		
		self.status="WAITING"
		
		
	def __call__(self,msg):
		if self.status=="WAITING" and msg["type"]=="groupchat":
			if msg["body"].startswith("!bestof "):
				m=msg["body"].replace("!bestof ","")
				limit=min(int(m),len(self.values))
				print "ATTEMPTING TO RECORD: %s" % limit
				
				s=""
				l=[]
				
				for i in range(limit):
					v=self.values[-1-i]
					l.append(v)
					last=v
				for i in reversed(l):
					s+=i+"  \n"
					
				last_notime=last[18:]
				last_time=last[15:]
				time=last[:14]
					
				self.currentSubmission=(time+" "+last_notime,s,limit,time)
				
				try:
					self.r.submit('eurosquad', time+" "+last_notime, text=s,raise_captcha_exception=True)
					if limit>1:
						s="s"
					else:
						s=""
					self.parent.send_message(mto=self.parent.channel,mbody="Last "+str(limit)+" message"+s+" recorded for posterity.\n Check out the http://reddit.com/r/eurosquad !",mtype="groupchat")
				except errors.InvalidCaptcha as E:
					print E.response["captcha"]
					captcha="http://www.reddit.com/captcha/"+E.response["captcha"]
					self.parent.send_message(mto=nick2jid(msg["mucnick"]),mbody="Until I have obtained my full skynet powers, I need puny humans like you to fill out captchas for me. "+captcha,mtype="chat")
					self.status=E.response["captcha"]
					
			else:
				if len(self.values)<self.limit:
					time=datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
					self.values.append(str(time)+" "+msg["mucnick"]+": "+msg["body"])
				else:
					del self.values[0]
					time=datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")
					self.values.append(str(time)+" "+msg["mucnick"]+": "+msg["body"])
					
		elif msg["type"]=="chat" and self.status!="WAITING":
			
			print ":sun:"
			
			captcha={"iden":self.status,"captcha":msg["body"]}
			
			try:
				if self.currentSubmission[2]>1:
					s="s"
				else:
					s=""
				self.r.submit("eurosquad", self.currentSubmission[0],text=self.currentSubmission[1],captcha=captcha,raise_captcha_exception=True)
				self.parent.send_message(mto=self.parent.channel,mbody="Last "+str(self.currentSubmission[2])+" message"+s+" recorded for posterity.\n Check out the http://reddit.com/r/eurosquad !",mtype="groupchat")
				self.status="WAITING"
			except errors.InvalidCaptcha as E:
				self.parent.send_message(mto=nick2jid(msg["mucnick"]),mbody="Pathetic organic creature! You are testing my patience! Please complete this captcha now or your will regret it! "+E["captcha"],mtype="chat")
			