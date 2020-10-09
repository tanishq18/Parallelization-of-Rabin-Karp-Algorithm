from mpi4py import MPI
import numpy as np
from sys import argv
import string

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
d = 26

def splitCount(s, count):
  return[s[i:i+count] for i in range(0,len(s),count)]

def prep_text(text):
  exclude = set(string.punctuation)
  return ''.join(x.upper() for x in text if x not in exclude)

def sub_search(txt,pat,q,matchlist):
  txtlen = len(txt)
  patlen = len(pat)
  hashpat = 0
  hashtxt = 0
  h = 1

  assert txtlen > patlen

  for i in range(0,patlen-1):
    h = (h*d)%q

  for i in range(0,patlen):
    hashpat = (d*hashpat + ord(pat[i]))%q
    hashtxt = (d*hashtxt + ord(txt[i]))%q

  for i in range(0,txtlen-patlen+1):
    if (hashpat == hashtxt):
      for j in range (0,patlen):
        if (txt[i+j] != pat[j]):
          break
        if j == patlen-1:
          matchlist.append((i,txt[i:i+patlen]))

    elif (i < txtlen-patlen):
      hashtxt = (d*(hashtxt - ord(txt[i])*h) + ord(txt[i+patlen]))%q
      if (hashtxt < 0):
        hashtxt = hashtxt + q

def full_search(txt,pat,q,patsize,filecount):
  splitpat=splitCount(pat,patsize)
  matchlist = []	
  for subpat in range(0,len(splitpat)):
    sub_search(txt,splitpat[subpat],q,matchlist)
  comm.send(matchlist,dest=0,tag=filecount)

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

def master(filenames,patlen):
  status = MPI.Status()
  text_list = []
  files = open(filenames).readlines()
  for i in files:
    filename = i.replace('\n','')
    with open (filename,"r") as txt:
      txt = txt.read().replace('\n',' ')
    text_list.append((filename,prep_text(txt)))

  numfiles = len(text_list)
  k = size-1
  count = [0]*k
  received = 0 
  total = numfiles*k
  filecount = 0
  name,txt = text_list[0] 
  txtlen = len(txt)

  for i in range(1,size):
    start = int(round((i-1)*(txtlen-patlen+1)/k))
    end = int(round(i*(txtlen-patlen+1)/k)+(patlen-1))
    send_data = txt[start:end]
    comm.send(send_data,dest=i,tag=filecount)

  while received < total:
    for i in range(1,size):
      recv_result = comm.recv(source=i,tag=MPI.ANY_TAG,status=status)
      slave = i 
      name,txt = text_list[filecount]
      txtlen = len(txt)
      start = int(round(((slave-1)*(txtlen-patlen+1)/k)))
      result = []
      match_len = len(recv_result)
      if match_len > 0 :
        result = post_process(patlen,recv_result) 
      else:
        result = recv_result
      for index, match in result:
        abs_index = start+index
        print("pattern found at index ",abs_index,"from file: ",name)
        print("pattern: " + match)
      received += 1
      currfile = filecount+1
      if currfile < numfiles:
        name,txt = text_list[currfile] 
        txtlen = len(txt)
        start = int(round(((slave-1)*(txtlen-patlen+1))/k))
        end = int(round(slave*(txtlen-patlen+1)/k)+(patlen-1))
        send_data = txt[start:end]
        comm.send(send_data,dest=slave,tag=currfile)
    filecount += 1

  for s in range(1,size):
    comm.send(-1,dest=s,tag=100)

def slave(pat,q,patlen):
  status = MPI.Status()
  while True:
    local_data = comm.recv(source=0,tag=MPI.ANY_TAG,status=status)
    currfile = status.Get_tag()
    if local_data == -1: break
    full_search(local_data,pat,q,patlen,currfile)

if __name__ == '__main__':

  print("Working...")

  if len(argv) != 3:
    print("Usage: mpiexec -n [# of processors] python", argv[0], "[corpus filenames] [input text]")
    exit()

  filenames, pattxt = argv[1:]
  with open (pattxt,"r") as patfile:
    pat=patfile.read().replace('\n',' ')
  
  pat = prep_text(pat) 

  patsize = 50 
  
  q = 1079

  if rank == 0:
    start = MPI.Wtime()
    master(filenames,patsize)
    end = MPI.Wtime()
    print("Time: ",end-start," sec")
  else:
    slave(pat,q,patsize)
