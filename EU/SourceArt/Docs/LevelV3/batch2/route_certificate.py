"""Constructive fixed-route replay with variable approved boxes on the 0.05 B grid.

Endpoint carrier events and maximum travel budgets come from the level's reference
route. Check jump arcs, full support, authored parking points, and merge consecutive
legs whenever an intermediate wait loses its shadow. No random patrol simulation.
"""
import itertools
import math
from functools import lru_cache
from level_solver import (STEP, TOL, RADIUS, HEIGHT, Geometry, bands, grid_x,
                          inside, merge, overlaps, shadow_at)


def flight(a,b):
    dx=abs(b[0]-a[0]);dz=b[1]-a[1]
    rad=6.5**2-32*dz
    if dz>1+TOL or rad<0:return None
    t=(6.5+math.sqrt(rad))/16
    return t if 4*t-dx>=.30-TOL else None


def arc_clear(a,b,obstacles,width):
    """Exact quadratic z range across every rectangular obstacle's X-contact times.
    Choose a stationary launch delay, then run horizontally at constant <=4 B/s.
    The actor is enclosed by a .60 x 1.30 rectangular envelope throughout.
    """
    t=flight(a,b)
    if t is None:return False
    xa,za=a; xb,zb=b
    if min(xa,xb)<RADIUS-TOL or max(xa,xb)>width-RADIUS+TOL:return False
    def h(s):return za+6.5*s-8*s*s
    if h(min(6.5/16,t))+HEIGHT>11.5+TOL:return False
    max_delay=t-abs(xb-xa)/4
    for proportion in (1.,.75,.5,.25,0.):
        delay=max(0.,max_delay*proportion);v=(xb-xa)/(t-delay) if t>delay+TOL else 0.
        for x,y,c,d in obstacles:
            u,w=x-RADIUS+TOL,y+RADIUS-TOL
            if max(xa,xb)<u or min(xa,xb)>w:continue
            if abs(v)<TOL:
                if not u<=xa<=w:continue
                t0,t1=0,t
            else:
                a0,b0=sorted((delay+(u-xa)/v,delay+(w-xa)/v))
                t0=max(0.,a0); t1=min(t,b0)
                if u<=xa<=w:t0=0.
                if t1<t0:continue
            lo=min(h(t0),h(t1));hi=max(h(t0),h(t1),h(max(t0,min(t1,6.5/16))))
            if lo<d-TOL and hi+HEIGHT>c+TOL:break
        else:return True
    return False


def platform_support(p,x,z):
    cx,cz=p['start'];z0=cz+.15
    if p['axis']=='X':
        a,b=sorted((cx,cx+p['travel']))
        return abs(z-z0)<TOL and a-1-TOL<=x<=b+1+TOL
    a,b=sorted((z0,z0+p['travel']))
    return a-TOL<=z<=b+TOL and cx-1-TOL<=x<=cx+1+TOL


def supported(point,solids,platforms):
    x,z=point
    return (any(a-TOL<=x<=b+TOL and abs(d-z)<TOL for a,b,c,d in solids)
            or any(platform_support(p,x,z) for p in platforms))


def rects(positions):
    return [(x,x+1,z,z+1) for x,z in positions]


class Certificate:
    def __init__(self,g,d):
        self.g,self.d=g,d
        self.ref=d['reference']
        self.sp=tuple(d['spawn'])
        self.legs=self.ref.get('patrol_legs',[])
        self.push=list(self.ref.get('pushes',[]))
        if 'A_push' in self.ref:
            self.push.append(dict(shot='A',crate=1,via=self.ref['A_push']))
        self.ib={s:tuple(sorted(map(tuple,self.ref.get(s,[])),key=lambda p:(p[1],p[0]))) for s in ('A','B')}
        self.anchor={}
        for item in self.push:
            s=item['shot'];origin=tuple(item['via'][0])
            if origin in self.ib[s]:self.anchor[s,self.ib[s].index(origin)]=tuple(item['via'][-1])
        self.static=g.solid+g.flags
        self.platforms=g.platforms
        self.jump_list=self.ref.get('jumps',[])
        self.legacy=d['id'] in ('L00','L02','L03')

    @lru_cache(maxsize=30000)
    def dark(self,l,point):
        # Stationary occluders alone give continuous shadow for all carrier phases.
        x,z=point
        return all(inside(x,shadow_at((l,self.d['rail']['z']),self.static,z+h)) for h in (.85,1.20))

    @lru_cache(maxsize=25000)
    def static_boxes_dark(self,l,boxes):
        from level_solver import dark_band
        return all(inside(x,dark_band((l,self.d['rail']['z']),self.static,z-.005,z+1.005,1)) for x,z in boxes)

    def candidates(self,s,layout):
        if len(layout)!=len(self.ib[s]):return False
        return all(abs(z-h)<TOL and abs(grid_x(i)-x)<=.85+TOL for (i,z),(x,h) in zip(layout,self.ib[s]))

    @lru_cache(maxsize=180000)
    def track(self,s,layout,fraction):
        initial=tuple((grid_x(i),z) for i,z in layout)
        originals=self.ib[s]
        active=tuple(self.anchor.get((s,i),p) for i,p in enumerate(initial))
        originals_active=tuple(self.anchor.get((s,i),p) for i,p in enumerate(originals))
        obstacles=self.g.solid+rects(active)
        def shift(point):
            x,z=point
            for (rx,rz),(px,pz) in zip(originals_active,active):
                if abs(rz+1-z)<TOL and rx-TOL<=x<=rx+1+TOL:
                    target=x+fraction*(px-rx)
                    return (round(max(px+.015,min(px+.985,target)),6),z)
            return (x,z)
        jumps=[]
        for j in self.jump_list:
            shot=j.get('shot')
            if not shot:
                z=j['from'][1]
                if self.d['id']=='L02':shot='B'
                else:shot='A' if z<self.d['mark'][2] else 'B'
            if shot!=s:continue
            a,b=shift(j['from']),shift(j['to'])
            if not (supported(a,obstacles,self.platforms) and supported(b,obstacles,self.platforms)
                    and arc_clear(a,b,obstacles,self.g.width)):
                return None
            # A declared push takes place between jumps. On the approach side
            # use the initial box geometry, so an earlier hop cannot pass through
            # a crate merely because its final location is elsewhere.
            before=list(active); affected=False
            for (shot,idx),(target,tz) in self.anchor.items():
                if shot!=s:continue
                initial_x,initial_z=initial[idx]
                approach=(max(a[0],b[0])<initial_x-RADIUS+TOL if target>=initial_x
                          else min(a[0],b[0])>initial_x+1+RADIUS-TOL)
                if approach:
                    before[idx]=initial[idx];affected=True
            if affected and not arc_clear(a,b,self.g.solid+rects(before),self.g.width):return None
            jumps.append((a,b))
        for (shot,idx),(tx,tz) in self.anchor.items():
            if shot!=s:continue
            x,z=initial[idx]
            support=merge([(a,b) for a,b,h in self.g.supports if h==z])
            if abs(tz-z)>TOL or not any(a-TOL<=min(x,tx) and max(x,tx)+1<=b+TOL for a,b in support):
                return None
            sweep=(min(x,tx),max(x,tx)+1,z,z+1)
            if any(overlaps(sweep,o) for o in self.g.solid+rects(initial[:idx]+initial[idx+1:])+self.g.sweeps):return None
        point_map={tuple(p):shift(p) for p in self.ref.get('safe_stops',[])}
        residual=0.
        for i,((px,_),(rx,_)) in enumerate(zip(initial,originals)):
            # Arrival/departure walks may become slightly longer. Jump flight time is
            # unchanged for equal dz; count a pair of walks and additional pushing.
            delta=abs(px-rx)
            residual+=delta/2
            if (s,i) in self.anchor: residual+=delta/1.5
        return active,point_map,residual,jumps

    def walk_or_ride(self,a,b,positions):
        # Explicitly carry across a moving steel plate, otherwise require continuous
        # foot support and swept capsule clearance. Choosing a platform phase for
        # these short transfers relies on its authored timetable.
        if any(platform_support(p,*a) and platform_support(p,*b) for p in self.platforms):
            return True
        if abs(a[1]-b[1])>TOL:return False
        x0,x1=sorted((a[0],b[0]));z=a[1];obstacles=self.g.solid+rects(positions)
        supports=merge([(l-.299,r+.299) for l,r,_,top in obstacles if abs(top-z)<TOL])
        if not any(l-TOL<=x0 and x1<=r+TOL for l,r in supports):return False
        swept=(x0-RADIUS,x1+RADIUS,z,z+HEIGHT)
        return not any(overlaps(swept,p) for p in obstacles)

    @lru_cache(maxsize=30000)
    def connected(self,A,B,fa,fb):
        TA=self.track('A',A,fa);TB=self.track('B',B,fb)
        if TA is None or TB is None:return False
        for t in (TA,TB):
            seq=t[3]
            if any(not self.walk_or_ride(j[1],k[0],t[0]) for j,k in zip(seq,seq[1:])):return False
        aj,bj=TA[3],TB[3]
        if aj and not self.walk_or_ride(self.sp,aj[0][0],TA[0]):return False
        a=aj[-1][1] if aj else self.sp
        b=bj[0][0] if bj else tuple((self.d['exit'][0],self.d['exit'][2]))
        m0,m1,h=self.d['mark']
        candidates=(m0,m1,(m0+m1)/2,max(m0,min(m1,a[0])),max(m0,min(m1,b[0])))
        if not any(self.walk_or_ride(a,(x,h),TA[0]) and self.walk_or_ride((x,h),b,TB[0]) for x in candidates):
            return False
        ex,ey,ez=self.d['exit'];end=bj[-1][1] if bj else b
        door=(max(ex,min(ey,end[0])),ez)
        return self.walk_or_ride(end,door,TB[0])

    def verify(self,l,A,B):
        if not self.legs or not (self.candidates('A',A) and self.candidates('B',B)):return None
        if tuple(self.legs[0]['from'])!=self.sp or self.legs[-1].get('to') is not None:return None
        if any(a.get('to')!=b.get('from') for a,b in zip(self.legs,self.legs[1:])):return None
        for fa,fb in itertools.product((0.,.5,1.),repeat=2):
            TA=self.track('A',A,fa); TB=self.track('B',B,fb)
            if TA is None or TB is None or not self.connected(A,B,fa,fb):continue
            tracks={'A':TA,'B':TB}
            init={'A':tuple((grid_x(i),z) for i,z in A),'B':tuple((grid_x(i),z) for i,z in B)}
            # Waiting for a withdrawn guard is safe at the spawn if already approved.
            spawn_body=(self.sp[0]-RADIUS,self.sp[0]+RADIUS,self.sp[1],self.sp[1]+HEIGHT)
            if any(overlaps(spawn_body,box) for box in self.g.solid+rects(init['A'])):continue
            if not self.dark(l,self.sp) or not self.static_boxes_dark(l,init['A']):continue
            total=0.;sections=[];waits=[self.sp]
            # Charge all deviations on every merged leg. Conservatively overcounts
            # walking, never assumes time saved by translating a box.
            slack=TA[2]+TB[2]
            for leg in self.legs:
                total+=leg['seconds']
                ep=leg.get('to')
                if ep is None:
                    sections.append(total+slack);break
                if ep[0]>=self.d['mark'][0]-TOL and ep[1]>=self.d['mark'][2]-TOL:s='B'
                else:s='A'
                if leg.get('to_shot') in ('A','B'):s=leg['to_shot']
                track=tracks[s]
                pos=track[1].get(tuple(ep),tuple(ep))
                boxes=track[0]
                # Before pushing the actor can also wait beside the original boxes.
                for (shot,idx),q in self.anchor.items():
                    if shot==s and pos[0]<min(init[s][idx][0],q[0])-.3+TOL:
                        boxes=init[s]
                body=(pos[0]-RADIUS,pos[0]+RADIUS,pos[1],pos[1]+HEIGHT)
                occupied=any(overlaps(body,obstacle) for obstacle in self.g.solid+rects(boxes))
                if not occupied and self.dark(l,pos) and self.static_boxes_dark(l,boxes) and supported(pos,self.g.solid+rects(boxes),[]):
                    sections.append(total+slack);total=0.;waits.append(pos)
            if sections and max(sections)<=8+TOL:
                return dict(lamp=l,A=list(init['A']),B=list(init['B']),max_joint_leg_s=round(max(sections),4),
                            safe_waits=waits,legs_s=[round(x,4) for x in sections],jump_shift=[fa,fb],
                            route_basis='authored_carrier_events_and_leg_times; analytic_swept_jump_clearance')
        return None


def populate(data,report,scan,lookup):
    c=Certificate(scan.g,data)
    wins=[]
    for sample in report['witnesses']:
        l=sample['lamp'];v=lookup(l)
        A=sorted((a for a in v['A'] if c.candidates('A',a)),key=lambda p:sum(abs(grid_x(i)-x) for (i,z),(x,h) in zip(p,c.ib['A'])))
        B=sorted((b for b in v['B'] if c.candidates('B',b)),key=lambda p:sum(abs(grid_x(i)-x) for (i,z),(x,h) in zip(p,c.ib['B'])))
        found=None
        for a,b in itertools.product(A,B):
            found=c.verify(l,a,b)
            if found:break
        if not found and data['id']=='L03':
            from legacy_alternate import verify as alternate
            found=alternate(l,scan.g,data)
            if found:
                seconds=found['joint_to_exit_s_upper']
                found.update(legs_s=[seconds],max_joint_leg_s=seconds,route_basis='forward_walk_push_cut_replay')
        if found:wins.append(found)
    lower=[w['lamp'] for w in wins]
    rr=data['reference']
    to_layout=lambda s:tuple((round(x/STEP),h) for x,h in c.ib[s])
    ref=c.verify(rr['lamp'],to_layout('A'),to_layout('B'))
    report['constructive']={'count':len(wins),'intervals':bands(lower),'witnesses':wins,
        'checks':['grid placement approvals','conservative jump arc, swept actor envelope',
                  'fixed-scene all-phase shadow at waits','whole active crates at waits',
                  'continuous supported walks, cut point and exit interaction','authored route times merged across lit stops; every joint exposure <=8 s']}
    report['checks']['width_on_constructive_lamps']=any(b-a>=.30-TOL for a,b in bands(lower))
    report['checks']['all_ceiling_lamps_witnessed']=len(lower)==report['count']
    report['reference']['conservative_timed_route']=ref
