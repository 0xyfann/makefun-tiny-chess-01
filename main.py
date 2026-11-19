import json,os
from functools import lru_cache as cache
from urllib.request import Request,urlopen
PIECE=' pnbrqk'
VAL=(0,100,320,335,500,900,0,0)
AX=(1,-1,10,-10)
DG=(9,11,-9,-11)
RY=AX+DG
JM=(8,-8,12,-12,19,-19,21,-21)
ST=(0,0,JM,DG,AX,RY,RY)
UCI={10*r+f:chr(96+f)+str(r-1) for r in range(2,10) for f in range(1,9)}
MK={21:2,25:3,28:1,91:8,95:12,98:4}
def fen(txt):
 rs,_,rt,ep,*_=txt.split()
 for n in range(1,9):rs=rs.replace(str(n),' '*n)
 b=bytearray([255])*120
 for s,p in zip(UCI,''.join(rs.split('/')[::-1])):
  b[s]=PIECE.index(p.lower())+8*p.islower()
 return bytes(b)+bytes((16+sum(2**i for i,c in enumerate('KQkq') if c in rt),next((x for x in UCI if UCI[x]==ep),0)))
def checked(b,s,k=0):
 k=k or b.index(6+8*s)
 o=8^8*s
 f=9-20*s
 if o+1 in (b[k+f],b[k+f+2]):return True
 for d in JM:
  if b[k+d]==o+2:return True
 for d in RY:
  y=k+d
  while b[y]==0:y+=d
  if b[y]-o in (5,4-(d in DG)) or y==k+d and b[y]==o+6:return True
def moves(b,s,caps=0):
 f=10-20*s
 o=1-s
 for x in UCI:
  if not (p:=b[x]) or p//8!=s:continue
  t=p&7
  if t==1:
   j=x+f
   for y in (j,j-1,j+1):
    z=b[y]
    if not z if y==j else y==b[-1] or z and z>>3==o:
     if y//10 in (2,9):
      for pr in (5,4,3,2):yield x,y,pr
     elif not caps or y!=j:yield x,y,0
   if not caps and x//10==3+5*s and not(b[j] or b[j+f]):yield x,j+f,0
  else:
   for d in ST[t]:
    y=x+d
    while not b[y] or b[y]>>3==o:
     if b[y] or not caps:yield x,y,0
     if b[y] or t in (2,6):break
     y+=d
 if not caps and (rt:=b[-2]>>2*s&3) and not checked(b,s):
  k=25+70*s
  for bit,d,gaps in ((1,1,b[k+1:k+3]),(2,-1,b[k-3:k])):
   if rt&bit and not any(gaps) and not checked(b,s,k+d):yield k,k+2*d,0
def push(b,m,s):
 x,y,pr=m
 c=bytearray(b)
 p=b[x]&7
 c[x],c[y]=0,(pr or p)+8*s
 c[-2]&=~(MK.get(x,0)|MK.get(y,0))
 c[-1]=0
 if p==1:
  if y==b[-1]:c[y-10+20*s]=0
  if abs(y-x)==20:c[-1]=(x+y)//2
 elif p==6 and abs(y-x)==2:
  d=(y-x)//2
  rook=x+3-7*(d<0)
  c[x+d],c[rook]=c[rook],0
 return bytes(c)
def uci(x,y,p):return (UCI[x]+UCI[y]+PIECE[p]).strip()
def ps(x,p,e):
 s,t=divmod(p,8)
 r=(x//10-2)^7*s
 f=abs(2*(x%10)-9)
 q=f+abs(2*r-7)
 return (1-2*s)*(VAL[t]+(0,8*r-3*f,38-5*q,30-2*q,0,0,40-5*q if e else 12*(f>=5)-14*r,0)[t])
PST=[[tuple(ps(x,p,e) for p in range(15)) for x in UCI] for e in (0,1)]
PA=bytes([0,1]+[0]*7+[9]+[0]*246)
@cache(4096)
def pawns(b):
 v=0
 for p,d,z in ((1,10,100),(9,-10,19)):
  x=b.find(p)
  while x>=0:
   y=x+d
   if 10-p not in b[y-1:z:d]+b[y:z:d]+b[y+1:z:d]:
    r=(x//10-2)^7*(p>1)
    v+=3*(r+1)**2*(1-2*(p>1))
   x=b.find(p,x+1)
 return v
def sc(b,s):
 e=not(5 in b or 13 in b)
 v=sum(map(tuple.__getitem__,PST[e],map(b.__getitem__,UCI)))
 v+=pawns(b[:-2].translate(PA))
 if not e:
  for p,d,r in ((6,9,30),(14,-11,80)):
   k=b.index(p)+d
   n=b[k:k+3].count(p-5)
   v+=(2-p//4)*(25*n-60*(n==3 and r<=k<r+10 and p^10 in b[r:r+10]))
 return -v if s else v
def play(txt,lg):
 tt={}
 i=0
 def go(b,s,d,a,h,p,nm=1):
  nonlocal i
  i+=1
  if i>90000:raise TimeoutError
  if p and (b,s)==rt:return 0
  ch=checked(b,s)
  caps=d<=0 and not ch
  g=sc(b,s) if caps or d<-6 else -31000
  if d<-6 or g>=h:return g
  if nm and d>2 and not ch and abs(h)<29000 and (4+8*s in b or 5+8*s in b):
   if -go(b[:-1]+b'\0',1-s,d-3,-h,1-h,p+1,0)>=h:return h
  key=b,s
  n,hm=0,tt.get(key)
  for m in sorted(moves(b,s,caps),key=lambda m:-9999*(m==hm)-16*VAL[b[m[1]]&7]-VAL[m[2]]+VAL[b[m[0]]&7]):
   c=push(b,m,s)
   if checked(c,s):continue
   n=1
   v=-go(c,1-s,d-1,-h,-max(a,g),p+1)
   if v>g:g,tt[key]=v,m
   if g>=h:break
  return g if n or caps else -30000+p if ch else 0
 rt=fen(txt),txt.split()[1]=='b'
 pick=lg[0]
 try:
  for d in range(1,64):
   v=go(*rt,d,-31000,31000,0)
   pick=uci(*tt[rt])
   if abs(v)>29000:break
 except TimeoutError:pass
 return pick
def post(p,d):return json.load(urlopen(Request(os.getenv('MAKEFUN_ENV_URL')+p,json.dumps(d).encode(),{'Content-Type':'application/json'})))
if __name__=='__main__':
 while (game:=post('/game',{}))['status']!='done':
  while game['status']=='your_move':
   game=post('/move',dict(game=game['game'],move=play(game['fen'],game['legal_moves'])))
