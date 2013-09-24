import random

def from2room(f):
	return str(f).split("/")[0]

class PokerBot:
	def __init__(self,parent):
		self.parent=parent
		
		self.active=False
		self.mode=""
	
		self.players=[]
		self.currentPlayer=None
		self.currentPlayerCommand=None
		self.playersHands={}
		self.playerWealth={}
		self.playerAllIn={}
		self.pot={}
		self.playersGone=0
		
		self.roundLength=0
		self.maxRoundLength=0
		self.rounds=0
		
		self.cards=[]
		for suit in ["H","S","C","D"]:
			for number in range(2,15):
				self.cards.append(suit+str(number))
				
		self.cardsLocked=tuple(self.cards)
		
		self.channel="koahi_is_a_faggot@chat.eurosquad.co.uk"
				
				
				
	def activate(self):
		if not self.active:
			self.mode="assessing_interest"
			self.active=True
			
			self.roundLength=0
			self.maxRoundLength=0
			self.rounds=0
			self.currentPlayer=None
			self.currentPlayerCommand=None
			self.playersHands={}
			self.playerWealth={}
			self.playerAllIn={}
			self.pot={}
			self.tableCards=[]
			
			self.parent.send_message(mto=self.parent.channel,mbody=self.jid2nick(self.players[0])+" wants to play poker! X up to play!",mtype="groupchat")
			
			self.parent.scheduler.add("assessing_interest",60.0,self.startPlay,repeat=False)
			
	def __call__(self,msg):
		if self.active:
			if self.mode=="assessing_interest":
				if msg["body"].lower().startswith("x"):
					self.players.append(msg["from"])
			if self.mode=="play_loop":
				if msg["from"]==self.currentPlayer:
					self.currentPlayerCommand=msg["body"]
		else:
			if msg["body"].startswith("!poker"):
				self.players=[msg["from"]]
				self.activate()
				
	def jid2nick(self,jid):
		return str(jid).split("/")[1]
		
	def card2str(self,card):
		suit=card[0]
		
		if suit=="D":
			suit="of :d:"
		elif suit=="S":
			suit="of :s:"
		elif suit=="C":
			suit="of :c:"
		elif suit=="H":
			suit="of :h:"
		
		number=int(card[1:])
		
		if number==11:
			number="Jack"
		elif number==12:
			number="Queen"
		elif number==13:
			number="King"
		elif number==14:
			number="Ace"
		else:
			number=str(number)
		
		return number+" "+suit
				
	def startPlay(self):
		if len(self.players)>1:
			self.mode="dealing_hand"
			self.cards=list(self.cardsLocked)
			random.shuffle(self.cards)
			self.numPlayers=len(self.players)
			for i in self.players:
				self.deal_hand(i)
			self.mode="play_loop"
			self.playersGone=0
			self.parent.send_message(mto=self.parent.channel,mbody="To play poker, when it's you're turn, type check, fold or raise. When using raise, follow raise with the amount you with to bet.",mtype="groupchat")
			self.parent.scheduler.add("play_loop",0.1,self.play_loop,repeat=True)
		else:
			self.active=False
			self.parent.send_message(mto=self.parent.channel, mbody="Seems no one wants to play with you, "+self.jid2nick(self.players[0])+" :(", mtype="groupchat")
			
	def deal_hand(self,player):
		self.playersHands[player]=[]
		self.playerWealth[player]=190
		self.playerAllIn[player]=0
		self.pot[player]=10
		s="You have been dealt:"
		for i in range(2):
			card=self.cards.pop(0)
			self.playersHands[player].append(card)
			s+="\n"+self.card2str(card)
		self.parent.send_message(mto=player,mbody=s,mtype="chat")
		self.parent.send_message(mto=player,mbody="You have automatically added 10 chips to the pot.",mtype="chat")
		self.update_player_wealth(player)
		
	def update_player_wealth(self,player):
		self.parent.send_message(mto=player,mbody="You currently have "+str(self.playerWealth[player])+" chips.",mtype="chat")
		
	def deal_card(self):
		card=self.cards.pop(0)
		self.tableCards.append(card)
		self.parent.send_message(mto=self.parent.channel,mbody="The dealer drew the "+self.card2str(card),mtype="groupchat")
		
		
	def potMaximum(self):
		a=0
		for i in self.pot.keys():
			if i!="Extra":
				if self.pot[i]>a: a=self.pot[i]
		return a
		
	def potTotal(self,player):
		a=0
		for i in self.pot.keys():
			a+=self.pot[i]
		if self.playerAllIn[player]!=0:
			a=min(a,len(self.pot.keys())*self.playerAllIn[player])
		return a
		
	def roundOver(self):
		b=True
		pm=self.potMaximum()
		if self.currentPlayer!=None:
			extra=[self.currentPlayer]
		else:
			extra=[]
		for i in self.players+extra:
			if self.playerAllIn[i]==0 and self.pot[i]!=pm:
				b=False
		b=b and self.playersGone==self.numPlayers
		return b
		
	def analyze_hands(self):
		results={}
		if self.currentPlayer!=None:
			extra=[self.currentPlayer]
		else:
			extra=[]
		for i in self.players+extra:
			results[i]=self.analyze_hand(i)
			
		currentWinner=self.players[0]
		currentMaximum=results[currentWinner][0]
		for i in self.players[1:]:
			if results[i][0]>currentMaximum:
				currentWinner=i
			elif results[i][0]==currentMaximum:
				winnerTemp=list(results[currentWinner])
				challengeTemp=list(results[i])
				winnerTemp.reverse()
				challengeTemp.reverse()
				
				a=0
				while a<len(challengeTemp):
					if winnerTemp[a]<challengeTemp[a]:
						currentWinner=i
						break
					elif winnerTemp[a]>challengeTemp[a]:
						break
					else:
						a+=1
						

		self.parent.send_message(mto=self.parent.channel, mbody=self.jid2nick(currentWinner)+" has won "+str(self.potTotal(currentWinner))+"!", mtype="groupchat")
		
		self.mode=""
		self.active=False
		self.parent.scheduler.remove("play_loop")
			
		
	def analyze_hand(self,player):
		highCard=self.high_card(player)
		highPair=self.high_pair(player)
		dualPair=self.dual_pair(player)
		highTriple=self.high_triple(player)
		straight=self.straight(player)
		flush=self.flush(player)
		fullHouse=self.full_house(player)
		highFour=self.high_four(player)
		straightFlush=self.straight_flush(player)
		
		results=(highCard,highPair,dualPair,highTriple,straight,flush,fullHouse,highFour,straightFlush)
		
		maximum=0
		a=0
		for i in results:
			if i!=0:
				maximum=a
			a+=1
			
		return (maximum,highCard,highPair,dualPair,highTriple,straight,flush,fullHouse,highFour,straightFlush)
		
	def high_card(self,player):
		hc=0
		for i in self.playersHands[player]:
			v=int(i[1:])
			if v>hc:
				hc=v
		return hc
		
	def high_pair(self,player):
		hp=0
		for i in self.playersHands[player]:
			v1=int(i[1:])
			l=self.search_table(player," "+i[1:],[i])
			if len(l)>=1:
				hp=v1
		return hp
		
	def dual_pair(self,player):
		dp=0
		for i in self.playersHands[player]:
			v1=int(i[1:])
			l=self.search_table(player," "+i[1:],[i])
			if l!=[]:
				l2=self.playersHands[player]+self.tableCards
				for j in l2:
					l3=self.search_table(player," "+j[1:],[j,i]+l)
					if len(l3)>0:
						dp=max(int(l[0][1:]),int(l3[0][1:]))
		return dp
		
	def high_triple(self,player):
		ht=0
		for i in self.playersHands[player]:
			v1=int(i[1:])
			l=self.search_table(player," "+i[1:],[i])
			if len(l)>=2:
				ht=v1
		return ht
		
	def straight(self,player):
		s=0
		for i in self.playersHands[player]+self.tableCards:
			v1=int(i[1:])
			l=[i]
			oldl=l[:]
			a=1
			while l!=[]:
				card=" "+str(int(l[0][1:])+1)
				oldl=l
				l=self.search_table(player,card)
				a+=1
			b=0
			l2=[" -1"]
			oldl2=l2[:]
			if v1==14:
				# This is to catch when aces are low
				while l2!=[]:
					v=int(l2[0][1:])
					card=" "+str(v+1)
					oldl2=l2
					l2=self.search_table(player,card)
					b+=1
			if a==5 or b==5:
				s=max(int(oldl[0][1:]),int(oldl2[0][1:]))
		return s
		
	def flush(self,player):
		f=0
		for i in self.playersHands[player]+self.tableCards:
			v1=int(i[1:])
			suit=i[0]
			l=[i]
			a=1
			exclude=[i]
			while l!=[]:
				card=suit+" "
				l=self.search_table(player,card,exclude)
				exclude.extend(l)
				a+=1
			if a==5:
				f=int(l[0][1:])
		return f
		
	def full_house(self,player):
		three=0
		for i in self.playersHands[player]:
			v1=int(i[1:])
			l=self.search_table(player," "+i[1:],[i])
			if len(l)>=2:
				three=v1
		
		two=0
		for i in self.playersHands[player]:
			v1=int(i[1:])
			l=self.search_table(player," "+i[1:],[i])
			if len(l)>=1:
				two=v1
				
		
		if three!=0 and two!=0:
			return three
		else:
			return 0
			
	def high_four(self,player):
		hf=0
		for i in self.playersHands[player]:
			v1=int(i[1:])
			l=self.search_table(player," "+i[1:],[i])
			if len(l)>=3:
				hf=v1
		return hf
		
	def straight_flush(self,player):
		sf=0
		for i in self.playersHands[player]+self.tableCards:
			v1=int(i[1:])
			l=[i]
			a=1
			suit=i[0]
			while l!=[]:
				v=int(l[0][1:])
				card=suit+str(v+1)
				l=self.search_table(player,card)
				a+=1
			b=1
			if v1==14:
				# This is to catch when aces are low
				l=[suit+"-1"]
				while l!=[]:
					v=int(l[0][1:])
					card=suit+str(v+1)
					l=self.search_table(player,card)
					b+=1
				
				
			if a==5 or b==5:
				s=int(l[0][1:])
		return sf
		
		
	def search_table(self,player,searchCard,exclusion=[]):
		return self.search_hand(player,searchCard,exclusion)+self.search_hand("",searchCard,exclusion)
				
	def search_hand(self,player,searchCard,exclusion=[]):
		if player=="":
			searchList=self.tableCards[:]
		else:
			searchList=self.playersHands[player]
		results=[]
		if searchCard[0]==" ":
			for card in searchList:
				if card[1:]==searchCard[1:]:
					results.append(card)
		elif searchCard[1]==" ":
			for card in searchList:
				if card[0]==searchCard[0]:
					results.append(card)
		else:
			for card in searchList:
				if card==searchCard:
					results.append(card)
		
		for i in exclusion:
			if i in results:
				results.remove(i)
				
		return results
					
			
			
		
	def play_loop(self):
	
		if self.currentPlayer==None:
			if len(self.players)==1:
				self.analyze_hands()
			else:
				self.currentPlayer=self.players.pop(0)
				self.parent.send_message(mto=self.parent.channel,mbody="It is "+self.jid2nick(self.currentPlayer)+"'s turn to play.",mtype="groupchat")
		
		
		if self.roundOver() and self.active:
			self.rounds+=1
			if self.rounds==1:
				self.deal_card()
				self.deal_card()
				self.deal_card()
			elif self.rounds==2:
				self.deal_card()
			elif self.rounds==3:
				self.deal_card()
			elif self.rounds==4:
				self.analyze_hands()
			self.playersGone=0
				
				
		elif self.currentPlayer!=None and self.active:
			print self.currentPlayer
			print self.currentPlayerCommand
			if self.playerWealth[self.currentPlayer]>0:
				if self.currentPlayerCommand!=None:
						if self.currentPlayerCommand.startswith("raise"):
							spli=self.currentPlayerCommand.split(" ")
							try:
								amount=int(spli[1])
								amount+=self.potMaximum()-self.pot[self.currentPlayer]
								if amount>=self.playerWealth[self.currentPlayer]:
									amount=min(self.playerWealth[self.currentPlayer],amount)
									if self.playerAllIn[self.currentPlayer]==0:
										self.parent.send_message(mto=self.parent.channel, mbody=self.jid2nick(self.currentPlayer)+" has gone all in!", mtype="groupchat")
									self.pot[self.currentPlayer]+=amount
									self.playerWealth[self.currentPlayer]=0
									self.playerAllIn[self.currentPlayer]=self.pot[self.currentPlayer]
								else:
									self.pot[self.currentPlayer]+=amount
									self.playerWealth[self.currentPlayer]-=amount
									
								self.parent.send_message(mto=self.parent.channel, mbody=self.jid2nick(self.currentPlayer)+" raised the pot to "+str(self.pot[self.currentPlayer]), mtype="groupchat")
								if amount!=0:
									self.update_player_wealth(self.currentPlayer)
							
								self.players.append(self.currentPlayer)
								self.currentPlayer=None
								self.playersGone=min(self.playersGone+1,self.numPlayers)
								
							except ValueError:
								self.parent.send_message(mto=self.parent.channel, mbody="Could you repeat that please,"+self.jid2nick(self.currentPlayer)+"?", mtype="groupchat")
							except IndexError:
								self.parent.send_message(mto=self.parent.channel, mbody="Could you repeat that please,"+self.jid2nick(self.currentPlayer)+"?", mtype="groupchat")
							
						elif self.currentPlayerCommand.startswith("check"):
							amount=self.potMaximum()-self.pot[self.currentPlayer]
							
							if amount>=self.playerWealth[self.currentPlayer]:
								amount=min(self.playerWealth[self.currentPlayer],amount)
								if self.playerAllIn[self.currentPlayer]==0:
									self.parent.send_message(mto=self.parent.channel, mbody=self.jid2nick(self.currentPlayer)+" has gone all in!", mtype="groupchat")
								self.pot[self.currentPlayer]+=amount
								self.playerWealth[self.currentPlayer]=0
								self.playerAllIn[self.currentPlayer]=self.pot[self.currentPlayer]
								self.parent.send_message(mto=self.parent.channel, mbody=self.jid2nick(self.currentPlayer)+" matched the pot as much as possible to "+str(self.pot[self.currentPlayer]), mtype="groupchat")
							else:
								self.pot[self.currentPlayer]+=amount
								self.playerWealth[self.currentPlayer]-=amount
								
								self.parent.send_message(mto=self.parent.channel, mbody=self.jid2nick(self.currentPlayer)+" matched the pot at "+str(self.potMaximum()), mtype="groupchat")
							if amount!=0:
								self.update_player_wealth(self.currentPlayer)
							
							self.players.append(self.currentPlayer)
							self.currentPlayer=None
							self.playersGone=min(self.playersGone+1,self.numPlayers)
							
						elif self.currentPlayerCommand.startswith("fold"):
							self.parent.send_message(mto=self.parent.channel, mbody=self.jid2nick(self.currentPlayer)+" has folded!", mtype="groupchat")
							self.currentPlayer=None
							self.playersGone=min(self.playersGone+1,self.numPlayers)
						
						self.currentPlayerCommand=None
			else:
				print self.playerWealth[self.currentPlayer]
				self.parent.send_message(mto=self.parent.channel, mbody=self.jid2nick(self.currentPlayer)+" has no chips left!", mtype="groupchat")
				self.players.append(self.currentPlayer)
				self.currentPlayer=None
				self.playersGone=min(self.playersGone+1,self.numPlayers)