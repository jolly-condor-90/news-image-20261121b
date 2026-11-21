# -*- coding: utf-8 -*-
"""Optimasi penempatan badge entri 2: 0 tabrakan, offset <=42px."""
import sys, math, json, random
sys.path.insert(0,'.')
import draw as d

# panel peta entri 3 (kanvas 1024): area gambar di dalam panel kiri-bawah
X0,Y0,X1,Y1 = 20, 754, 394, 904      # width 374, height 150
RAD=6.5; MINDOT=RAD+2.4+1.0; SEP=2*RAD+3
LT,LB=83,-58; MW,MH=X1-X0,Y1-Y0
def pr(lon,lat): return (X0+(lon+180)/360*MW, Y0+(LT-lat)/(LT-LB)*MH)
PTS={s[0]:pr(s[6],s[7]) for s in d.STORIES}
DENS={n:sum(1 for m,e in PTS.items() if m!=n and math.hypot(PTS[n][0]-e[0],PTS[n][1]-e[1])<45) for n in PTS}

def seg_inter(a,b,c,e):
    def ccw(p,q,r): return (r[1]-p[1])*(q[0]-p[0]) > (q[1]-p[1])*(r[0]-p[0])
    return ccw(a,c,e)!=ccw(b,c,e) and ccw(a,b,c)!=ccw(a,b,e)
def dist_pt_seg(px,py,ax,ay,bx,by):
    dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy
    if L2==0: return math.hypot(px-ax,py-ay)
    t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L2))
    return math.hypot(px-(ax+t*dx),py-(ay+t*dy))

def attempt(order,jit=0.0):
    placed=[]; segs=[]; fails=[]; rings={}; offs={}
    for s in order:
        n=s[0]; dx,dy=PTS[n]
        near=[PTS[m] for m in PTS if m!=n and math.hypot(PTS[m][0]-dx,PTS[m][1]-dy)<45]
        oa=math.atan2(dy-sum(p[1] for p in near)/len(near), dx-sum(p[0] for p in near)/len(near)) if near else None
        best=None
        for ring in (8,15,23,32,42):
            steps=max(18,int(ring*5))
            angles=[2*math.pi*k/steps+jit for k in range(steps)]
            if oa is not None: angles.sort(key=lambda a:abs(math.atan2(math.sin(a-oa),math.cos(a-oa))))
            for a in angles:
                cx=dx+ring*math.cos(a); cy=dy+ring*math.sin(a)*0.9
                if math.hypot(cx-dx,cy-dy)<MINDOT: continue
                if not(X0+9<=cx<=X1-9 and Y0+9<=cy<=Y1-9): continue
                if any((cx-px)**2+(cy-py)**2<SEP**2 for px,py in placed): continue
                vx,vy=cx-dx,cy-dy; L=math.hypot(vx,vy) or 1; ux,uy=vx/L,vy/L
                ex,ey=cx-ux*(RAD+1),cy-uy*(RAD+1); seg=(dx,dy,ex,ey)
                if any(dist_pt_seg(cx,cy,*sg)<RAD+1.0 for sg in segs): continue
                if any(dist_pt_seg(px,py,*seg)<RAD+1.0 for px,py in placed): continue
                bad=False
                for sg in segs:
                    if seg_inter((dx,dy),(ex,ey),(sg[0],sg[1]),(sg[2],sg[3])):
                        if math.hypot(dx-sg[0],dy-sg[1])<5: continue
                        bad=True;break
                if bad: continue
                best=(cx,cy,ring,seg);break
            if best:break
        if not best: fails.append(n); continue
        cx,cy,ring,seg=best
        placed.append((cx,cy)); segs.append(seg); rings[n]=ring; offs[n]=math.hypot(cx-dx,cy-dy)
    return fails,placed,segs,rings,offs

base=sorted(d.STORIES,key=lambda s:(-DENS[s[0]],s[0]))
best=None; random.seed(11)
for it in range(120):
    if it==0: order=list(base); jit=0.0
    elif it==1: order=list(reversed(base)); jit=0.0
    else:
        order=list(base); random.shuffle(order); jit=random.random()*0.35
    f,pl,sg,ri,of=attempt(order,jit)
    if best is None or len(f)<len(best[0]): best=(f,pl,sg,ri,of)
    if not f: break
f,pl,sg,ri,of=best
print('fails=%d maxoff=%.1f order_len=%d'%(len(f),max(of.values()) if of else 0,len(order)),f)
if not f:
    json.dump({str(n):{'cx':round(pl[i][0],2),'cy':round(pl[i][1],2),'ring':ri[n],'off':round(of[n],1)}
               for i,n in enumerate([s[0] for s in order])}, open('placement.json','w'))
    print('saved placement.json')
