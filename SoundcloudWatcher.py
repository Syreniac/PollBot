class SoundcloudWatcher:
	def __init__(self,parent):
		self.parent=parent
		
		self.list=[]
		
	def __call__(self,msg):
		if msg["mucnick"]=="Berach" or msg["mucnick"]=="El Presidente Berach" or msg["type"]=="chat":
			if msg["body"].startswith("https://soundcloud.com") and not "Nichya" in self.parent.jidList:
				self.list.append(msg["body"])
				
		if msg["mucnick"]=="Nichya":
			if len(self.list)!=0:
				self.parent.send_message(mto="eurosquad@chat.eurosquad.co.uk/Nichya",mbody="Berach has sent you the following soundcloud links",mtype="chat")
				while len(self.list)>0:
					p=self.list.pop(0)
					self.parent.send_message(mto="eurosquad@chat.eurosquad.co.uk/Nichya",mbody=p,mtype="chat")