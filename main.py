import json,os,urllib.request
V=[0,100,320,330,500,900,0];N=0;T={};H=set();G=None;C='';E='-'
Q=[1,16,15,17,-1,-16,-15,-17];J=[33,31,18,14,-14,-18,-31,-33]
def fen(f):
 global C,E
 a=f.split();C=a[2];E=a[3];b=[0]*128
 for r,w in enumerate(a[0].split('/')):
  x=0
  for c in w:
   if c.isdigit():x+=int(c)
   else:b[(7-r)*16+x]=' pnbrqk'.index(c.lower())+8*c.islower();x+=1
 return b
def key(b,s):return bytes(b),s,C or '-',E
def sq(s):return chr(97+(s&7))+str(1+(s>>4))
def ps(x):return [5,4,3,2] if x>>4 in (0,7) else [0]
def txt(m):return sq(m[0])+sq(m[1])+(' pnbrqk'[m[2]] if m[2] else '')
def atk(b,s,c):
 for d in (15,17):
  x=s+(d if c else -d)
  if not x&136 and b[x]==1+8*c:return 1
 for d in J:
  x=s+d
  if not x&136 and b[x]==2+8*c:return 1
 for d in Q:
  x=s+d
  while not x&136:
   p=b[x]
   if p:
    if p//8==c and (p%8==5 or p%8==6 and x==s+d or p%8==(4 if abs(d) in (1,16) else 3)):return 1
    break
   x+=d
 return 0
def gen(b,h,g=0):
 o=[]
 for s,p in enumerate(b):
  if not p or p//8!=h:continue
  t=p%8
  if t==1:
   f=16-32*h
   if not b[s+f] and not g:
    o.extend((s,y,u,0,0) for y in [s+f]+([s+2*f] if s>>4==1+5*h and not b[s+2*f] else []) for u in ps(y))
   for x in (s+f-1,s+f+1):
    if x&136:continue
    ep=E==sq(x)
    if b[x] and b[x]//8!=h or ep:o.extend((s,x,u,b[x],int(ep)) for u in ps(x))
   continue
  for d in J if t==2 else Q[2:4]+Q[6:] if t==3 else Q if t>4 else Q[:2]+Q[4:6]:
   x=s+d
   while not x&136:
    z=b[x]
    if z and z//8==h:break
    if not g or z:o.append((s,x,0,z,0))
    if z or t in (2,6):break
    x+=d
 B=112*h;k=B+4
 if not g and not atk(b,k,1-h):
  for ch,dx,r,cl in [('Kk',2,7,(5,6)),('Qq',-2,0,(1,2,3))]:
   if ch[h] in C and b[k]==6+8*h and b[B+r]==4+8*h and all(not b[B+d] for d in cl) and not atk(b,k+dx//2,1-h):o.append((k,k+dx,0,0,2 if dx>0 else 3))
 L=[]
 for m in o:
  S=do(b,m,h);ok=not atk(b,b.index(6+8*h),1-h);un(b,S)
  if ok:L.append(m)
 return L
def ev(b,h):
 v=0
 for s,p in enumerate(b):
  if p:
   c=p//8;t=p%8;r=(s>>4)^(7*c);f=s&7
   v+=(1-2*(c!=h))*(V[t]+(r*5 if t==1 else 5*(6-abs(3-f)-abs(3-r)) if t in (2,3,5) else 0))
 return v+30*((b.count(3+8*h)>1)-(b.count(11-8*h)>1))
def do(b,m,h):
 global C,E
 s,x,u,z,j=m;p=b[s];O=(b[:],C,E)
 if p%8==6:C=C.replace('k' if h else 'K','').replace('q' if h else 'Q','')
 for q,ch in ((0,'Q'),(7,'K'),(112,'q'),(119,'k')):
  if s==q or x==q:C=C.replace(ch,'')
 E=sq((s+x)//2) if p%8==1 and abs(x-s)==32 else '-';b[s]=0;b[x]=u+8*h if u else p
 if j==1:b[x-(16-32*h)]=0
 if j>1:
  a=(7 if j==2 else 0)+112*h;y=x-1 if j==2 else x+1;b[y]=b[a];b[a]=0
 return O
def un(b,S):
 global C,E
 b[:],C,E=S
def go(b,h,d,a,z,l,q=0):
 global N
 N+=1
 if N>12000:raise TimeoutError
 if q>5:return ev(b,h)
 k=key(b,h);e=T.get(k);A=a
 if d>0 and e and e[0]>=d:
  _,v,g,_=e
  if not g or g==1 and v>=z or g==-1 and v<=a:return v
 c=atk(b,b.index(6+8*h),1-h);i=ev(b,h);j=d<=0 and not c
 if j:
  if i>=z:return i
  a=max(a,i)
 M=gen(b,h,j);w=i if j else -99999;m0=None
 if not M:return -30000+l if c else i if j else 0
 M.sort(key=lambda m:(e and m==e[3],m[3]*100+m[2]*800),reverse=True)
 for m in M:
  S=do(b,m,h)
  try:v=-go(b,1-h,d-1,-z,-a,l+1,q+1 if d<=0 else 0)
  finally:un(b,S)
  if v>w:w=v;m0=m
  a=max(a,v)
  if a>=z:break
 if d>0:T[k]=(d,w,(w>=z)-(w<=A),m0)
 return w
def play(f,L):
 global N
 b=fen(f);h=int(f.split()[1]=='b');H.add(key(b,h));T.clear();N=0
 M=[m for m in gen(b,h) if txt(m) in L];P=M[0]
 for d in range(1,5):
  w=-99999
  try:
   for m in M:
    S=do(b,m,h)
    try:v=-go(b,1-h,d-1,-99999,99999,1)-1000*(key(b,1-h) in H)
    finally:un(b,S)
    if v>w:w=v;c=m
  except TimeoutError:break
  P=c;M.sort(key=lambda m:m!=P)
 do(b,P,h);H.add(key(b,1-h))
 return txt(P)
def post(p,o):
 r=urllib.request.Request(os.environ['MAKEFUN_ENV_URL']+p,data=json.dumps(o).encode(),headers={'content-type':'application/json'});return json.load(urllib.request.urlopen(r))
while 1:
 g=post('/game',{})
 if g.get('game')!=G:H.clear();G=g.get('game')
 if g['status']=='done':break
 while g['status']=='your_move':g=post('/move',{'game':g['game'],'move':play(g['fen'],g['legal_moves'])})
