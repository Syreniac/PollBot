f=open("input.txt","r")
f2=file("output.txt","w")

def stringIsCapital(s):
	b=True
	for i in s:
		b=b and i.isupper()
	return b

s=""
writing=False
for i in f:
	i=i.replace("|","")
	i2=i.split("\t")
	a=i2[0].replace(".","")
	if not "]" in i and not "[" in i and not "ACT" in i and not "SCENE" in i:
		if stringIsCapital(a) and len(a)>1:
			if writing:
				s=s.rstrip("\n")
				f2.write(s+"|\n")
				s=""
			else:
				writing=True
		if writing and i!="\n":
			s+=i