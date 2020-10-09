import time
import string
from sys import argv
d = 26 

def splitCount(s, count):
	return[s[i:i+count] for i in range(0,len(s),count)]

def prep_text(text):
	exclude = set(string.punctuation)
	return ''.join(x.upper() for x in text if x not in exclude)

def sub_search(txt,pat,q,matchlist):

	patlen = len(pat)
	txtlen = len(txt)
	hashpat = 0
	hashpat2 = 0
	hashtxt = 0
	hashtxt2 = 0
	h = 1
	h2 = 1
	tuple_array = []

	for i in range(0,patlen-1):
		h = (h*d)%q
		h2 = (h2*d)%q2
	for i in range(0,patlen):
		hashpat = (d*hashpat + ord(pat[i]))%q
		hashpat2 = (d*hashpat2 + ord(pat[i]))%q2
		hashtxt = (d*hashtxt + ord(txt[i]))%q
		hashtxt2 = (d*hashtxt2 + ord(txt[i]))%q2

	for i in range(0,txtlen-patlen+1):
		if (hashpat == hashtxt):
			for j in range (0,patlen):
				if (txt[i+j] != pat[j]):
					break
				if j == patlen-1:
					matchlist.append((i,txt[i:i+patlen]))

		if (i < txtlen-patlen):
			hashtxt = (d*(hashtxt - ord(txt[i])*h) + ord(txt[i+patlen]))%q
			hashtxt2 = (d*(hashtxt2 - ord(txt[i])*h2) + ord(txt[i+patlen]))%q2
		if (hashtxt < 0):
			hashtxt = hashtxt + q
		if (hashtxt2 < 0):
			hashtxt2 = hashtxt2 + q2

def full_search(txt,pat,q,patsize):

	splitpat = splitCount(pat,patsize)
	matchlist = []

	for subpat in range(0,len(splitpat)):
		sub_search(txt,splitpat[subpat],q,matchlist)
	return matchlist

def post_process(patlen,recv_result):
	match_len = len(recv_result)
	result = []
	curr = 0
	offset = 1

	if match_len == 1:
		result.append(recv_result[curr])
		return result
	else:
		index,string = recv_result[curr]

	while  curr < match_len:
		nextcurr = curr+offset

		if nextcurr < match_len and index + offset*patlen == recv_result[nextcurr][0] :
			string = string + " " + recv_result[nextcurr][1]
			offset += 1			
		else:
			result.append((index,string))
			curr = nextcurr 
			if curr < match_len:
				index,string = recv_result[curr]	

	return result

if __name__ == '__main__':

	if len(argv) != 3:
		print("Usage: mpiexec -n [# of processors] python", argv[0], "[corpus filenames] [input text]")
		exit()
	q = 1079
	q2 = 1011
	patsize = 30;

	filenames, pattxt = argv[1:]
	with open (pattxt,"r") as patfile:
		pat=patfile.read().replace('\n',' ')

	pat = prep_text(pat)

	start = time.time()
	files = open(filenames).readlines()
	for i in files:
		filename = i.replace('\n','')
		with open (filename,"r") as txt:
			txt = txt.read().replace('\n',' ')
		
		txt = prep_text(txt)

		pre_results = full_search(txt,pat,q,patsize)
		
		if len(pre_results) == 0:
			results = pre_results
		else:	
			results = post_process(patsize,pre_results)

		for index,match in results:
			print("pattern found at index ", index," in text: ",filename)
			print("pattern: ",match)
		
	end = time.time()
	print("Time: ",end-start," sec")
