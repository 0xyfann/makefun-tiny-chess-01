import json,os
from urllib.request import Request,urlopen
PIECE=' pnbrqk'
VAL=(0,100,320,335,500,900,0,0)
AXES=(1,-1,10,-10)
DIAG=(9,11,-9,-11)
RAYS=AXES+DIAG
JUMP=(8,-8,12,-12,19,-19,21,-21)
STEPS=((),(),JUMP,DIAG,AXES,RAYS,RAYS)
UCI={10*r+f:chr(96+f)+str(r-1) for r in range(2,10) for f in range(1,9)}
MASK={21:2,25:3,28:1,91:8,95:12,98:4}
def fen(text):
 ranks,_,rights,ep=text.split()[:4]
 for n in range(1,9):
  ranks=ranks.replace(str(n),' '*n)
 b=bytearray([255])*120
 for s,p in zip(UCI,''.join(ranks.split('/')[::-1])):
  b[s]=PIECE.index(p.lower())+8*p.islower()
 mask=sum(1<<i for i,c in enumerate('KQkq') if c in rights)
 ep=next((s for s in UCI if UCI[s]==ep),0)
 return bytes(b)+bytes((16+mask,ep))
def checked(b,s,k=0):
 k=k or b.index(6+8*s)
 for d in RAYS+JUMP:
  y=k+d
  while not b[y] and d in RAYS:
   y+=d
  t=b[y]-8*(1-s)
  if 1<t<7 and d in STEPS[t] and (t!=6 or y==k+d) or t==1 and y-k in (9-20*s,11-20*s):
   return True
def moves(b,s,caps=False):
 f=10-20*s
 for x in UCI:
  if not (p:=b[x]) or p//8!=s:
   continue
  t=p%8
  if t==1:
   j=x+f
   for y in (j,j-1,j+1):
    z=b[y]
    if not z if y==j else y==b[-1] or z and z//8==1-s:
     if y//10 in (2,9):
      for promo in (5,4,3,2):
       yield x,y,promo
     elif not caps or y!=j:
      yield x,y,0
   if not caps and x//10==3+5*s and not (b[j] or b[j+f]):
    yield x,j+f,0
  else:
   for d in STEPS[t]:
    y=x+d
    while not b[y] or b[y]//8==1-s:
     if b[y] or not caps:
      yield x,y,0
     if b[y] or t in (2,6):
      break
     y+=d
 k=25+70*s
 rights=b[-2]>>2*s&3
 if rights and not caps and not checked(b,s):
  for bit,d,gaps in ((1,1,b[k+1:k+3]),(2,-1,b[k-3:k])):
   if rights&bit and not any(gaps) and not checked(b,s,k+d):
    yield k,k+2*d,0
def push(b,m,s):
 x,y,promo=m
 c=bytearray(b)
 p=b[x]
 c[x],c[y]=0,promo+8*s if promo else p
 c[-2]&=~(MASK.get(x,0)|MASK.get(y,0))
 c[-1]=0
 if p%8==1:
  if y==b[-1]:
   c[y-10+20*s]=0
  if abs(y-x)==20:
   c[-1]=(x+y)//2
 elif p%8==6 and abs(y-x)==2:
  d=(y-x)//2
  rook=x+3 if d>0 else x-4
  c[x+d],c[rook]=c[rook],0
 return bytes(c)
def uci(m):
 x,y,promo=m
 return UCI[x]+UCI[y]+PIECE[promo].strip()
def term(s,p,e):
 g,t=divmod(p,8)
 r=(s//10-2)^(7*g)
 q=abs(2*(s%10)-9)+abs(2*r-7)
 return (1-2*g)*(VAL[t]+(0,5*r+e*r*r,35-4*q,35-2*q,12*(r==6),0,32-4*q if e else -12*r,0)[t])
PST=[{s:[term(s,p,e) for p in range(15)] for s in UCI} for e in (0,1)]
def score(b,s):
 pst=PST[not (5 in b or 13 in b)]
 v=sum(pst[s][b[s]] for s in UCI)+30*((b.count(3)>1)-(b.count(11)>1))
 return -v if s else v
def play(text,legal):
 tt={}
 cnt=0
 def search(b,s,d,lo,hi,ply,nm=True):
  nonlocal cnt
  cnt+=1
  if cnt>150000:
   raise TimeoutError
  check=checked(b,s)
  caps=d<=0 and not check
  best=score(b,s) if caps or d<-6 else -31000
  if best>=hi or d<-6:
   return best
  if nm and d>2 and not check and abs(hi)<29000 and (4+8*s in b or 5+8*s in b):
   if -search(b[:-1]+b'\0',1-s,d-3,-hi,1-hi,ply+1,False)>=hi:
    return hi
  key=b,s
  n=0
  for m in sorted(moves(b,s,caps),key=lambda m:(m==tt.get(key),16*VAL[b[m[1]]%8]+VAL[m[2]]-VAL[b[m[0]]%8]),reverse=True):
   c=push(b,m,s)
   if checked(c,s):
    continue
   n+=1
   a=max(lo,best)
   r=d>2 and n>4 and not (check or b[m[1]] or m[1]==b[-1] or m[2] or checked(c,1-s))
   v=-search(c,1-s,d-1-r,-hi if n==1 else -a-1,-a,ply+1)
   if v>a and (r or n>1 and v<hi):
    v=-search(c,1-s,d-1,-hi,-a,ply+1)
   if v>best:
    best,tt[key]=v,m
   if best>=hi:
    break
  return best if n or caps else -30000+ply if check else 0
 root=fen(text),text.split()[1]=='b'
 pick=legal[0]
 try:
  for d in range(1,64):
   v=search(*root,d,-31000,31000,0)
   pick=uci(tt[root])
   if abs(v)>29000:
    break
 except TimeoutError:
  pass
 return pick
def post(path,data):
 req=Request(os.environ['MAKEFUN_ENV_URL']+path,json.dumps(data).encode(),{'content-type':'application/json'})
 return json.load(urlopen(req))
if __name__=='__main__':
 while (game:=post('/game',{}))['status']!='done':
  while game['status']=='your_move':
   game=post('/move',dict(game=game['game'],move=play(game['fen'],game['legal_moves'])))
