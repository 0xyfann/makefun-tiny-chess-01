import json,os
from urllib.request import Request,urlopen
# Mailbox: 255 border, rights and EP
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
 pos=bytearray([255])*120
 for s,p in zip(UCI,''.join(ranks.split('/')[::-1])):
  pos[s]=PIECE.index(p.lower())+8*p.islower()
 mask=sum(1<<i for i,c in enumerate('KQkq') if c in rights)
 ep=next((s for s in UCI if UCI[s]==ep),0)
 return bytes(pos)+bytes((16+mask,ep))
def checked(pos,side,k=0):
 k=k or pos.index(6+8*side)
 for d in RAYS+JUMP:
  y=k+d
  while not pos[y] and d in RAYS:
   y+=d
  t=pos[y]-8*(1-side)
  if 1<t<7 and d in STEPS[t] and (t!=6 or y==k+d) or t==1 and y-k in (9-20*side,11-20*side):
   return True
 return False
def moves(pos,side,caps=False):
 f=10-20*side
 for x in UCI:
  if not (p:=pos[x]) or p//8!=side:
   continue
  t=p%8
  if t==1:
   j=x+f
   for y in (j,j-1,j+1):
    z=pos[y]
    if not z if y==j else y==pos[-1] or z and z//8==1-side:
     if y//10 in (2,9):
      for promo in (5,4,3,2):
       yield x,y,promo
     elif not caps or y!=j:
      yield x,y,0
   if not caps and x//10==3+5*side and not (pos[j] or pos[j+f]):
    yield x,j+f,0
  else:
   for d in STEPS[t]:
    y=x+d
    while not pos[y] or pos[y]//8==1-side:
     if pos[y] or not caps:
      yield x,y,0
     if pos[y] or t in (2,6):
      break
     y+=d
 k=25+70*side
 rights=pos[-2]>>2*side&3
 if rights and not caps and not checked(pos,side):
  for bit,d,gaps in ((1,1,pos[k+1:k+3]),(2,-1,pos[k-3:k])):
   if rights&bit and not any(gaps) and not checked(pos,side,k+d):
    yield k,k+2*d,0
def push(pos,m,side):
 x,y,promo=m
 c=bytearray(pos)
 p=pos[x]
 c[x],c[y]=0,promo+8*side if promo else p
 c[-2]&=~(MASK.get(x,0)|MASK.get(y,0))
 c[-1]=0
 if p%8==1:
  if y==pos[-1]:
   c[y-10+20*side]=0
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
def term(s,p):
 g,t=divmod(p,8)
 r=(s//10-2)^(7*g)
 q=abs(2*(s%10)-9)+abs(2*r-7)
 return (1-2*g)*(VAL[t]+(0,5*r,35-4*q,35-2*q,12*(r==6),0,-12*r,0)[t])
PST={s:[term(s,p) for p in range(15)] for s in UCI}
def score(pos,side):
 v=sum(PST[s][pos[s]] for s in UCI)+30*((pos.count(3)>1)-(pos.count(11)>1))
 return -v if side else v
def play(text,legal):
 tt,kill={},{}
 nodes=0
 def search(pos,side,depth,alpha,beta,ply):
  nonlocal nodes
  nodes+=1
  if nodes>30000:
   raise TimeoutError
  check=checked(pos,side)
  caps=depth<=0 and not check
  best=score(pos,side) if caps or depth<-7 else -31000
  if best>=beta or depth<-7:
   return best
  key=pos,ply
  def order(m):
   x,y,promo=m
   z=pos[y]%8 or (y==pos[-1] and pos[x]%8==1)
   if z or promo:
    return 16*VAL[z]+VAL[promo]-VAL[pos[x]%8]
   return 2 if m==tt.get(key) else m==kill.get(ply)
  for m in sorted(moves(pos,side,caps),key=order,reverse=True):
   c=push(pos,m,side)
   if checked(c,side):
    continue
   v=-search(c,1-side,depth-1,-beta,-max(alpha,best),ply+1)
   if v>best:
    best,tt[key]=v,m
   if best>=beta:
    if order(m)<3:
     kill[ply]=m
    break
  return best if best!=-31000 else -30000+ply if check else 0
 root=fen(text),int(text.split()[1]=='b')
 pick=legal[0]
 try:
  for depth in range(1,64):
   v=search(*root,depth,-31000,31000,0)
   pick=uci(tt[root[0],0])
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
