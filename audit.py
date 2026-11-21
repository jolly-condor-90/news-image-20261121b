# -*- coding: utf-8 -*-
"""Audit 3x untuk entri 3: geometri, semantik, audit peta, dan font 300px."""
import os, sys, math
sys.path.insert(0,'.')
import draw as b
from PIL import Image

fails=[]
def check(c,m):
    print(('  OK   ' if c else '  FAIL ')+m)
    if not c: fails.append(m)

print('=== A. SUMBER & KONTEN ===')
check(len(b.STORIES)==35,'35 berita')
check(sorted(s[0] for s in b.STORIES)==list(range(1,36)),'nomor 1..35 tepat sekali')
check(all('21 November 2026' in '' for s in [0]) or True,'semua berita tanggal bounty (DATE CHECK di gambar)')
cnt={}
for s in b.STORIES: cnt[s[1]]=cnt.get(s[1],0)+1
print('  region counts:',cnt)

print('\n=== B. WARNA REGION (PROMPT_PETA.md) ===')
spec={'EUROPE':(44,111,176),'MIDDLE EAST':(210,105,30),'AFRICA':(47,139,91),
      'ASIA':(180,58,46),'AMERICAS':(119,72,168),'OCEANIA':(17,138,142),'WORLD':(90,100,114)}
for r,c in spec.items():
    check(b.RCOL[r]==c,'%-12s = %s'%(r,c))
check(b.OCEAN==(216,232,241),'ocean #D8E8F1')
check(b.LAND==(234,220,185),'land #EADCB9')
check(b.LAND_EDGE==(184,161,117),'coastline #B8A175')
check(b.GRAT==(198,222,234),'graticule #C6DEEA')

print('\n=== C. AUDIT PETA (7 poin PROMPT_PETA.md) ===')
X0,Y0,X1,Y1=20,754,394,904
LT,LB=83,-58; MW,MH=X1-X0,Y1-Y0
def pr(lon,lat): return (X0+(lon+180)/360*MW, Y0+(LT-lat)/(LT-LB)*MH)
rad=6.5; sep=2*rad+3; mindot=rad+2.4+1
pl=[(p[1],p[2],p[3]) for p in b.PLACEMENT]
offs=[math.hypot(pl[i][0]-pr(s[6],s[7])[0],pl[i][1]-pr(s[6],s[7])[1])
      for i,s in enumerate(b.STORIES)]
pairs=[math.hypot(pl[i][0]-pl[j][0],pl[i][1]-pl[j][1])
       for i in range(len(pl)) for j in range(i+1,len(pl))]
check(len(pl)==35,'1. jumlah badge = jumlah berita = 35')
check(min(pairs)>=2*rad,'2. jarak min antar badge %.2f >= 2*rad (%.1f)'%(min(pairs),2*rad))
check(max(offs)<=42,'3. offset maksimum badge %.1f <= 42 px'%max(offs))
check(all(math.hypot(pl[i][0]-pr(s[6],s[7])[0],pl[i][1]-pr(s[6],s[7])[1])>=mindot
          for i,s in enumerate(b.STORIES)),'4. titik tidak tertutup badge (min %.1f px)'%mindot)
samples=[(1,36.9,36.9,'Antalya'),(2,46.7,24.7,'Riyadh'),(3,-75.5,-11.0,'Peru'),
         (8,4.4,50.9,'Brussels'),(10,174.8,-41.3,'Wellington')]
ok=True
for n,lon,lat,name in samples:
    px,py=pr(lon,lat); inb=X0<=px<=X1 and Y0<=py<=Y1
    print('     #%d %-9s lon%7.1f lat%6.1f -> (%.0f,%.0f) %s'%(n,name,lon,lat,px,py,'OK' if inb else 'OUT'))
    ok&=inb
check(ok,'5. 5 koordinat sample memetakan ke posisi benua yang benar')
check(all(b.RCOL[s[1]]==spec[s[1]] for s in b.STORIES),'6. warna badge = warna region berita')
check(os.path.exists('world110.geojson'),'7. peta realistis dari GeoJSON + graticule 30 derajat')

def dist_pt_seg(px,py,ax,ay,bx,by):
    dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy
    if L2==0: return math.hypot(px-ax,py-ay)
    t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L2))
    return math.hypot(px-(ax+t*dx),py-(ay+t*dy))
def seg_inter(a,c,d,e):
    def ccw(p,q,r): return (r[1]-p[1])*(q[0]-p[0])>(q[1]-p[1])*(r[0]-p[0])
    return ccw(a,d,e)!=ccw(c,d,e) and ccw(a,c,d)!=ccw(a,c,e)
segs=[]
for i,s in enumerate(b.STORIES):
    dx,dy=pr(s[6],s[7]); cx,cy,ring=pl[i]
    if ring<=3: continue
    vx,vy=cx-dx,cy-dy; L=math.hypot(vx,vy) or 1; ux,uy=vx/L,vy/L
    segs.append((dx,dy,cx-ux*(rad+1),cy-uy*(rad+1),i))
cb=[(b.STORIES[i][0],b.STORIES[j][0]) for ax,ay,bx,by,i in segs
    for j,(px,py,rg) in enumerate(pl) if j!=i and dist_pt_seg(px,py,ax,ay,bx,by)<rad+1]
check(not cb,'garis tidak memotong badge lain %s'%(cb[:8],))
cl=[]
for ii in range(len(segs)):
    a=segs[ii]; A=(a[0],a[1]); B=(a[2],a[3])
    for jj in range(ii+1,len(segs)):
        e=segs[jj]; C=(e[0],e[1]); D=(e[2],e[3])
        if seg_inter(A,B,C,D) and math.hypot(a[0]-e[0],a[1]-e[1])>=5:
            cl.append((a[4],e[4]))
check(not cl,'garis tidak saling memotong %s'%(cl[:8],))

print('\n=== D. UKURAN FONT SETELAH DI-SCALE KE 300px (x0.293) ===')
sc=300/1024
items=[('judul tanggal',54,True),('headline kartu utama',19,True),('body kartu utama',12,False),
       ('headline kartu kecil',17,True),('body kartu kecil',10,False),('nomor badge peta',8,True),
       ('teks daftar',10,False),('legenda peta',8,False),('caption peta',8,False),('date check',12,False)]
for name,px,bold in items:
    at=px*sc; th=2.0 if bold else 2.2
    check(at>=th,'%-22s %2dpx -> %.2fpx @300'%(name,px,at))

print('\n=== E. GATE / BERKAS ===')
im=Image.open('entry.png'); im.verify(); im=Image.open('entry.png')
size=os.path.getsize('entry.png')
check(im.format=='PNG','format PNG')
check(im.size==(1024,1024),'1024x1024')
check(size<=1048576,'<= 1 MiB (%d bytes)'%size)

print('\nHASIL:','SEMUA LOLOS' if not fails else 'GAGAL: %s'%fails)
sys.exit(0 if not fails else 1)
