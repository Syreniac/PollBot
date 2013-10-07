from twitter import Api
import re

CONSUMER_KEY="GzdwGVOhtFkBopVz5cdlwg"
CONSUMER_SECRET="ncB8WRtNuhWfToDoWolRGb2q7pMfrV49uC1o7iWC9Y"
ACCESS_KEY="625637844-KgQRSLyNOSFRyYREwBtD41IKAsavNdmklxg4jSoo"
ACCESS_SECRET="2PlKswAKVYKT6VUxSkKKpgMgCIpTStvbPXjp9ocnQ"

def remove_hashtags(s):
	new_s=""
	b=True
	for i in s:
		if i=="#":
			b=False
		if b:
			new_s+=i
		elif not re.match("^[\w\d]*$",i) and i!="#":
			b=True
	return new_s
		

class TwitterLink:
	def __init__(self,parent,target,keywords=[],hashtagclear=False):
		self.parent=parent
		self.target=target
		self.keywords=keywords
		self.hashtagclear=hashtagclear
		
		
		try:
			self.f=file(target+".txt","r")
			r=self.f.read().split("\n")
			print r[-1]
			self.old_tweet=str(r[-1])
			self.f.close()
		except (IndexError, IOError) as E:
			self.old_tweet=""
			
		print "old_tweet:"+self.old_tweet
		
		self.f=file(target+".txt","a")
		
		self.api = Api(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET,
						access_token_key=ACCESS_KEY, access_token_secret=ACCESS_SECRET)

	def FetchTwitter(self,limit=1):
		statuses = self.api.GetUserTimeline(screen_name="@"+self.target, count=limit)
		s=str(statuses[limit-1].text)
		return s
			
	def __call__(self):
		
		limit=1
		try:
			new_tweet=self.FetchTwitter()
		except URLError:
			return
		if self.hashtagclear:
			new_tweet=remove_hashtags(new_tweet)
		write_tweet="\n"+new_tweet

		while str(self.old_tweet)!=str(new_tweet):
			limit+=1
			maybe_new_tweet=self.FetchTwitter(limit)
			
			if self.hashtagclear:
				maybe_new_tweet=remove_hashtags(maybe_new_tweet)
				
			b=True
			for i in self.keywords:
				if not i in maybe_new_tweet:
					b=False
					break
				
			if str(maybe_new_tweet)==str(self.old_tweet):
				break
			elif b:
				new_tweet=maybe_new_tweet
		
		if str(self.old_tweet)!=str(new_tweet):
			for i in self.keywords:
				if not i in new_tweet:
					return
			print write_tweet
			self.f.write(write_tweet)
			self.old_tweet=new_tweet
			self.parent.send_message(mto=self.parent.channel,mbody="@"+self.target+"\n\t"+new_tweet,mtype="groupchat")