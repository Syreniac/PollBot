import urllib
import urllib2

import eveapi

import json

class ZKBLink:
	def __init__(self,parent):
		self.parent=parent
		self.characters=[]
		
		self.api=eveapi.EVEAPIConnection()
		
		
	def __call__(self):
		for i in self.characters:
		
			url="https://zkillboard.com/api/kills/w-space/"
			data=urllib.urlencode({})
			headers={"User-Agent":"Syreniac",'Accept-Encoding':'gzip'}
			print url
			request=urllib2.Request(url,data,headers)
			for i in dir(request):
				thing=eval("request."+i)
				if hasattr(thing,"__call__"):
					try:
						new_thing=thing()
						thing=new_thing
					except TypeError:
						pass
				print i+":"+str(thing)
			downloaded_data=urllib2.urlopen(request)
			from_json=json.load(downloaded_data)
			print from_json

			
zkb=ZKBLink(None)
zkb.characters.append(268946627)
zkb()
			