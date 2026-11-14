#!/usr/bin/env python3
"""Escape Unseen: 5 cm grid approval and conservative shortcut search (Python 3.10+)."""
import argparse
import collections
import functools
import itertools
import json
import math
from pathlib import Path

STEP, EPS, TOL = .05, .005, 1e-8
RADIUS, HEIGHT = .30, 1.30


def merge(intervals):
    result = []
    for low, high in sorted(intervals):
        if high < low - TOL:
            continue
        if result and low <= result[-1][1] + TOL:
            result[-1] = (result[-1][0], max(high, result[-1][1]))
        else:
            result.append((low, high))
    return result


def intersect(a, b):
    return merge((max(x, u), min(y, v)) for x, y in a for u, v in b)


def subtract(parts, holes):
    for a, b in holes:
        nxt = []
        for x, y in parts:
            if a >= y - TOL or b <= x + TOL:
                nxt.append((x,y))
            else:
                if a > x + TOL: nxt.append((x,a))
                if b < y - TOL: nxt.append((b,y))
        parts = nxt
    return parts


def overlaps(a,b):
    return (a[0] < b[1]-TOL and a[1] > b[0]+TOL
            and a[2] < b[3]-TOL and a[3] > b[2]+TOL)


def on_grid(a,b):
    return range(math.ceil((a-TOL)/STEP), math.floor((b+TOL)/STEP)+1)


def grid_x(i):
    return round(i * STEP, 6)


def physical_x(x):
    return round(x, 6)


def shadow_slices(lamp, rects, lo, hi):
    """Endpoint union intersections. Between events both boundary functions are affine.

    Shadows cast by several rectangles may meet inside the target: test every topology
    interval, not just its four corners. Treat a rectangle with its finite thickness.
    """
    lx,lz=lamp
    levels={lo,hi}
    functions=[]
    for a,b,c,d in rects:
        for h in (c,d):
            if lo < h < hi: levels.add(h)
            if abs(lz-h) > TOL:
                for xx in (a,b):
                    slope=(xx-lx)/(lz-h)
                    functions.append((lx+slope*lz,-slope))
        functions.extend(((a,0),(b,0)))
    for i,(a,m) in enumerate(functions):
        for b,n in functions[:i]:
            if abs(m-n)>TOL:
                z=(b-a)/(m-n)
                if lo+TOL<z<hi-TOL: levels.add(z)
    critical=sorted(levels)
    # Exact boundary plus one-sided limits at discontinuities (top of a solid).
    sample=set(critical)
    for a,b in zip(critical,critical[1:]):
        if b-a>TOL:
            inset=min(1e-7,(b-a)/4)
            sample.update((a+inset,(a+b)/2,b-inset))
    return sorted(sample)


def shadow_at(lamp, rects, z):
    lx,lz=lamp
    if abs(z-lz)<TOL:
        # Horizontal rays are unusual; preserve valid input near a lamp-height shelf.
        output=[]
        for a,b,c,d in rects:
            if c-TOL<=z<=d+TOL:
                if b<lx: output.append((-1e9,b))
                elif a>lx: output.append((a,1e9))
                else: output.append((-1e9,1e9))
        return merge(output)
    out=[]
    for a,b,c,d in rects:
        if z<lz:
            if d < z-TOL or c>=lz-TOL: continue
            near,far=max(z,c),min(lz-1e-10,d)
        else:
            if c > z+TOL or d<=lz+TOL: continue
            near,far=max(lz+1e-10,c),min(d,z)
        # Rectangle at receiver height alone does not shade a point on its far side.
        xs=[lx+(x-lx)*(lz-z)/(lz-h) for x in (a,b) for h in (near,far)]
        out.append((min(xs),max(xs)))
    return merge(out)


def dark_band(lamp,rects,z0,z1,width):
    common=[(-1e8,1e8)]
    for z in shadow_slices(lamp,rects,z0,z1):
        here=[(a+EPS,b-width-EPS) for a,b in shadow_at(lamp,rects,z) if b-a>=width+2*EPS-TOL]
        common=intersect(common,here)
        if not common: break
    return common


def inside(x,intervals):
    return any(a-TOL <= x <= b+TOL for a,b in intervals)


def can_jump(a,b):
    # Expanded ledge contact, 0.4 B of coyote horizontal movement. Absolute apex
    # clipped at 1.30; do not substitute the reference designer's +1 cap.
    dz=b[2]-a[2]
    if dz>1.30+TOL: return False
    t=(6.5+math.sqrt(max(0,6.5**2-32*dz)))/16
    gap=max(0.,a[0]-b[1],b[0]-a[1])
    return gap<=4*t+.4+2*RADIUS+TOL


def support_faces(rects,width):
    levels=collections.defaultdict(list)
    for a,b,c,d in rects: levels[d].append((max(0,a),min(width,b)))
    out=[]
    for z,intervals in levels.items():
        if z< -TOL or z+HEIGHT>11.5+TOL: continue
        # Solid walls that penetrate the standing corridor split its walking surface.
        holes=[(a,b) for a,b,c,d in rects if c<z+HEIGHT-TOL and d>z+TOL]
        out.extend((a,b,z) for a,b in subtract(merge(intervals),holes) if b>a+TOL)
    return out


def platform_rect(p,t):
    x,z=p['start']; shift=t*p['travel']
    if p['axis'].upper()=='X': x+=shift
    else: z+=shift
    return (x-1,x+1,z-.15,z+.15)


def swept(p):
    a,b=platform_rect(p,0),platform_rect(p,1)
    return (min(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),max(a[3],b[3]))


def configurations(platforms):
    return [tuple(platform_rect(p,t) for p,t in zip(platforms,ts))
            for ts in itertools.product((0,1),repeat=len(platforms))]


def platform_path_nodes(p):
    # Vertical carrier is represented by both endpoints and the full continuum for
    # transfers. A free boarding/ride relaxation is deliberately generous to shortcut paths.
    a,b=platform_rect(p,0),platform_rect(p,1)
    return ((min(a[0],b[0]),max(a[1],b[1]),min(a[3],b[3]),max(a[3],b[3])))


def ride_jump(a,b):
    # For independently selectable launch/landing heights try the smallest difference
    # (largest flight time); this covers every intermediate carrier position.
    return can_jump((a[0],a[1],a[3]),(b[0],b[1],b[2]))


class Geometry:
    def __init__(self,data,removed=None):
        self.data=data
        self.width=data['width']
        self.solid=[tuple(o['box']) for o in data['solids']]
        if data.get('floor',True):
            self.solid.append((0,self.width,-1,0))
        self.flags=[tuple(o['box']) for o in data.get('flags',[])]
        self.platforms=[p for p in data.get('platforms',[]) if p['id']!=removed]
        self.occluders=[self.solid+self.flags+list(ps) for ps in configurations(self.platforms)]
        self.sweeps=[swept(p) for p in self.platforms]
        self.supports=support_faces(self.solid,self.width)
        self.bases=self._base_boxes()
        self.box_heights={physical_x(z+j) for _,z in self.bases for j in range(data['inventory']['pool'])}
        self.guard=[]  # Reachability must admit every placement that game geometry allows.

    def _base_boxes(self):
        result=set()
        for a,b,z in self.supports:
            for ix in on_grid(a,b-1):
                x=grid_x(ix)
                if self.free_box(x,z):result.add((ix,z))
        return sorted(result)

    def free_box(self,x,z):
        r=(x,x+1,z,z+1)
        return (x>=-TOL and x+1<=self.width+TOL and z+1<=11.5+TOL
                and not any(overlaps(r,o) for o in self.solid+self.sweeps))

    @functools.lru_cache(None)
    def approved_intervals(self,light,z):
        result=[(0,self.width-1)]
        for obstacles in self.occluders:
            result=intersect(result,dark_band((light,self.data['rail']['z']),obstacles,z-EPS,z+1+EPS,1))
            if not result:break
        return result

    def approved(self,light,ix,z):
        x=grid_x(ix)
        return inside(x,self.approved_intervals(light,z))

    def layouts(self,light,count):
        # Recursive assembly permits boxes bridging two adjacent lower boxes.
        # Geometry shared at equal height is joined before legal positions are sampled.
        starts=[(ix,z) for ix,z in self.bases if self.approved(light,ix,z)]
        for n in range(count+1):
            if n==0:
                yield ();continue
            if n==1:
                yield from ((v,) for v in starts);continue
            previous=set()
            def extend(layout):
                if len(layout)==n:
                    if layout not in previous:
                        previous.add(layout)
                        yield layout
                    return
                above=collections.defaultdict(list)
                for ix,z in layout: above[physical_x(z+1)].append((grid_x(ix),grid_x(ix)+1))
                extra=set()
                for z,spans in above.items():
                    spans+= [(a,b) for a,b,k in self.supports if abs(z-k)<TOL]
                    for a,b in merge(spans):
                        for ix in on_grid(a,b-1):
                            if self.free_box(grid_x(ix),z) and self.approved(light,ix,z):
                                extra.add((ix,z))
                for ix,z in itertools.chain(starts,sorted(extra-set(starts))):
                    if layout and (z,ix)<(layout[-1][1],layout[-1][0]):
                        continue
                    if any(abs(ix-jx)<20 and abs(z-h)<1-TOL for jx,h in layout):continue
                    yield from extend(layout+((ix,z),))
            yield from extend(())

    def _nodes(self,layout):
        rects=self.solid+[(grid_x(ix),grid_x(ix)+1,z,z+1) for ix,z in layout]
        nodes=[(a,b,z,z) for a,b,z in support_faces(rects,self.width)]
        nodes.extend(platform_path_nodes(p) for p in self.platforms)
        return nodes

    @staticmethod
    def components(nodes,start):
        a,b,z=start
        reached={i for i,n in enumerate(nodes) if n[2]-TOL<=z<=n[3]+TOL and max(a,n[0])<=min(b,n[1])+TOL}
        pending=list(reached)
        while pending:
            i=pending.pop()
            for j,n in enumerate(nodes):
                if j not in reached and ride_jump(nodes[i],n):
                    reached.add(j);pending.append(j)
        return reached

    @functools.lru_cache(maxsize=60000)
    def pose(self,layout,start):
        nodes=self._nodes(layout)
        reached=self.components(nodes,start)
        return tuple(nodes[i] for i in sorted(reached))

    @staticmethod
    def touches(reached,goal):
        a,b,z=goal
        return any(n[2]-TOL<=z<=n[3]+TOL and max(a,n[0])<=min(b,n[1])+TOL for n in reached)

    def fallen(self,ix,z,rest):
        x=grid_x(ix)
        levels=[h for a,b,h in self.supports if a-TOL<=x and x+1<=b+TOL and h<=z+TOL]
        levels.extend(h+1 for j,h in rest if j==ix and h+1<=z+TOL)
        return max(levels) if levels else None

    def push_moves(self,layout,reached):
        for idx,(ix,z) in enumerate(layout):
            rest=layout[:idx]+layout[idx+1:]
            for sign in (-1,1):
                left=grid_x(ix)
                px=left-RADIUS if sign==1 else left+1+RADIUS
                if not self.touches(reached,(px,px,z)):continue
                # The crate may stop anywhere on solid support. Once the leading edge
                # crosses a ledge, also allow intermediate overhang up to its trailing
                # edge and resolve gravity onto any lower full-width landing.
                for j in range(ix+sign, -1 if sign<0 else int(self.width/STEP),sign):
                    xx=grid_x(j);r=(xx,xx+1,z,z+1)
                    if not self.free_box(xx,z) or any(overlaps(r,(grid_x(k),grid_x(k)+1,h,h+1)) for k,h in rest):break
                    floor=self.fallen(j,z,rest)
                    anchor=xx-RADIUS if sign>0 else xx+1+RADIUS
                    back=(min(px,anchor),max(px,anchor),z,z+HEIGHT)
                    if any(overlaps(back,q) for q in self.solid):break
                    if floor is not None:
                        nxt=tuple(sorted(rest+((j,floor),),key=lambda p:(p[1],p[0])))
                        yield nxt,(anchor,anchor,z)
                    elif not any(a-TOL<=anchor<=b+TOL and abs(h-z)<TOL for a,b,h in self.supports):
                        break
                    if floor!=z and not any(a-TOL<=anchor<=b+TOL and abs(h-z)<TOL for a,b,h in self.supports):
                        break

    @functools.lru_cache(maxsize=180000)
    def possible(self,layout,start,end,push):
        if self.touches(self.pose(layout,start),end): return True
        if not push or not layout:return False
        queue=collections.deque([(layout,start)]);seen=set()
        while queue:
            poses,here=queue.popleft()
            reached=self.pose(poses,here)
            state=(poses,reached)
            if state in seen:continue
            seen.add(state)
            if self.touches(reached,end):return True
            for q,h in self.push_moves(poses,reached):
                if self.touches(self.pose(q,h),end):return True
                if (q,self.pose(q,h)) not in seen:queue.append((q,h))
        return False


class SingleReach:
    """Reverse reachability on (crate pose, connected region of the actor).

    No abstract re-positioning is allowed between consecutive pushes. The actor starts
    and ends at the touching side; after a fall the actor remains on the upper lip.
    """
    def __init__(self,g,start,goal):
        self.g,self.start,self.goal=g,start,goal
        self.empty=g.possible((),start,goal,False)
        self.poses=list(g.bases)
        self.can_static=set()
        self.can_push=set()
        self.can_static_pose=set()
        self._build()

    def _build(self):
        g=self.g
        reverse=collections.defaultdict(set)
        targets=set()
        starts={}
        full_labels={}
        for ix,z in self.poses:
            p=(ix,z); x=grid_x(ix)
            seeds={'S':self.start,'L':(x-RADIUS,x-RADIUS,z),'R':(x+1+RADIUS,x+1+RADIUS,z)}
            # Landing on a lower shelf after a fall can leave the pusher on any
            # originally higher support. Include such seeds, fixed in world space.
            for a,b,zt in g.supports:
                if zt<=z+TOL:continue
                for side,xx in [('L',x-RADIUS),('R',x+1+RADIUS)]:
                    if a-TOL<=xx<=b+TOL: seeds[(side,zt)]=(xx,xx,zt)
            reps={}
            for label,here in seeds.items():
                exposed=g.pose((p,),here)
                if not exposed:continue
                node=(p,exposed);reps[label]=node
                if g.touches(exposed,self.goal):targets.add(node)
            if 'S' in reps:
                starts[p]=reps['S']
                if starts[p] in targets:self.can_static.add(p)
            full_labels[p]=reps
        for p in self.poses:
            ix,z=p;x=grid_x(ix)
            reps=full_labels[p]
            for sign,label in [(1,'L'),(-1,'R')]:
                side=x-RADIUS if sign==1 else x+1+RADIUS
                predecessors={node for node in reps.values() if g.touches(node[1],(side,side,z))}
                if not predecessors:continue
                # One grid step on aligned support. Push overhangs advance until
                # reaching a lower full-support site, without requiring a midair push.
                for j in range(ix+sign,-1 if sign<0 else math.ceil(g.width/STEP),sign):
                    xx=grid_x(j)
                    if not g.free_box(xx,z):break
                    anchor=xx-RADIUS if sign>0 else xx+1+RADIUS
                    if any(overlaps((min(side,anchor),max(side,anchor),z,z+HEIGHT),r) for r in g.solid):break
                    floor=g.fallen(j,z,())
                    if floor is not None:
                        dest=(j,floor)
                        after_label=label if abs(z-floor)<TOL else (label,z)
                        tail=full_labels.get(dest,{}).get(after_label)
                        if tail:
                            reverse[tail].update(predecessors)
                        if abs(z-floor)<TOL:break
                    if not any(a-TOL<=anchor<=b+TOL and abs(h-z)<TOL for a,b,h in g.supports):
                        break
        queue=collections.deque(targets);reachable=set(targets)
        while queue:
            for prev in reverse.get(queue.popleft(),()):
                if prev not in reachable:reachable.add(prev);queue.append(prev)
        self.can_push={p for p,source in starts.items() if source in reachable}


def bands(points):
    intervals=[]
    for x in sorted(set(points)):
        if intervals and x<=intervals[-1][1]+STEP+TOL:
            intervals[-1][1]=x
        else: intervals.append([x,x])
    return intervals


def stats(points):
    return {'count':len(points),'intervals':bands(points)}


def serialize_pose(p):
    return [] if p is None else [grid_x(p[0]),p[1]]


class Scan:
    def __init__(self,data,removed=None,no_ride=False):
        self.g=Geometry(data,removed)
        g=self.g
        if no_ride:g.platforms=[] # retain optical geometry and excluded sweep volumes
        self.d=data
        sx,sz=data['spawn']
        s,m,e=(sx,sx,sz),tuple(data['mark']),tuple(data['exit'])
        self.journeys=[SingleReach(g,s,m),SingleReach(g,m,e),SingleReach(g,s,e)]

    def per_lamp(self,l):
        g=self.g;D=self.d
        ok=set()
        for ix,z in g.bases:
            if g.approved(l,ix,z):ok.add((ix,z))
        def side(j,budget,push=True):
            reach=self.journeys[j]
            result=ok & (reach.can_push if push else reach.can_static) if budget else set()
            if reach.empty: result=result|{None}
            return result
        A=side(0,D['inventory']['A'])
        B=side(1,D['inventory']['B'])
        no_push=bool(side(0,D['inventory']['A'],False)) and bool(side(1,D['inventory']['B'],False))
        no_cut=bool(side(2,D['inventory']['A']))
        minus=self.journeys[0].empty and self.journeys[1].empty
        return A,B,no_push,no_cut,minus


def family_bound(pairs):
    """A 0.50-diameter partition is a certificate of at most N families.

    A greedily picked >0.50-separated subset is a lower bound. If different,
    never describe the partition count as an exact minimum cover.
    """
    if not pairs:return {'lower':0,'upper':0,'pair_count':0,'cells':[]}
    def vec(p):
        return tuple(x for v in p for x in ((v[0],round(v[1]/STEP)) if v is not None else (-10000,-10000)))
    vectors=sorted((vec(pair),pair) for pair in pairs)
    cert=[];packing=[]
    for v,p in vectors:
        if all(max(abs(k-y) for k,y in zip(v,w))>10 for w in packing):packing.append(v)
        for cell in cert:
            lo,hi,qty=cell
            if all(max(b,vv)-min(a,vv)<=10 for a,b,vv in zip(lo,hi,v)):
                for k,vv in enumerate(v):lo[k]=min(lo[k],vv);hi[k]=max(hi[k],vv)
                cell[2]+=1;break
        else: cert.append([list(v),list(v),1])
    def coord(xs):return [None if x==-10000 else grid_x(x) for x in xs]
    return {'lower':len(packing),'upper':len(cert),'pair_count':len(pairs),
            'cells':[{'min_Ax_Az_Bx_Bz':coord(c[0]),'max_Ax_Az_Bx_Bz':coord(c[1]),'pairs':c[2]} for c in cert],
            'packing':[coord(x) for x in packing]}


def highest(data):
    items=[(o['box'][3],(o['box'][0]+o['box'][1])/2,o['id']) for o in data['solids']+data.get('flags',[])]
    for p in data.get('platforms',[]):
        r=swept(p)
        items.append((r[3],(r[0]+r[1])/2,p['id']))
    return [] if not items else [(x,name) for h,x,name in items if abs(h-max(i[0] for i in items))<TOL]


def reference_check(g,data):
    ref=data['reference'];l=ref['lamp'];result={}
    worst=None;max_rise=None
    for j in ref.get('jumps',[]):
        a,z=j['from'];b,h=j['to'];rise=h-z
        rad=6.5**2-32*rise
        if rad<0:margin=-1e6
        else:margin=4*(6.5+math.sqrt(rad))/16-abs(a-b)
        worst=margin if worst is None else min(worst,margin)
        max_rise=rise if max_rise is None else max(max_rise,rise)
    result['max_jump_rise']=max_rise
    result['min_horizontal_margin']=round(worst,4) if worst is not None else None
    result['jumps_pass']=max_rise is not None and max_rise<=1+TOL and worst>=.3-TOL
    for shot in ('A','B'):
        boxes=ref.get(shot,[])
        result[shot+'_whole_box']=all(inside(x,g.approved_intervals(l,z)) for x,z in boxes)
        # Verify incremental stability, including contiguous bottom blocks.
        placed=[];stable=True
        for x,z in sorted(boxes,key=lambda t:t[1]):
            supports=merge([(a,b) for a,b,h in g.supports if abs(z-h)<TOL]+[(xx,xx+1) for xx,zz in placed if abs(zz+1-z)<TOL])
            if not any(a-TOL<=x and x+1<=b+TOL for a,b in supports):stable=False
            r=(x,x+1,z,z+1)
            if (not g.free_box(x,z) or any(overlaps(r,s) for s in g.guard) or
                    any(overlaps(r,(xx,xx+1,zz,zz+1)) for xx,zz in placed)):stable=False
            placed.append((x,z))
        result[shot+'_support_clearance']=stable
    result['spawn_dark_all_endpoints']=all(all(inside(data['spawn'][0],dark_band((l,data['rail']['z']),r,data['spawn'][1]+h-EPS,data['spawn'][1]+h+EPS,0)) for h in (.85,1.2)) for r in g.occluders)
    return result


def solve(data):
    inventory=data['inventory']
    if not (0<=inventory['A']<=inventory['pool'] and 0<=inventory['B']<=inventory['pool']):
        raise ValueError('Per-shot inventory must be within the shared pool.')
    if not (0<data['width']<=24+TOL):
        raise ValueError('The specified room width is outside (0,24] B.')
    if data['rail']['start'] not in ('left','right'):
        raise ValueError('The rail start must be left or right.')
    if any(q[1]<q[0] for q in [data['mark'],data['exit']]):
        raise ValueError('The mark and exit must have increasing X endpoints.')
    if data['id']=='L02' and data['inventory']['pool']==3:
        import legacy_l02
        try:
            legacy_l02.recognized_geometry(data)
        except ValueError:
            pass
        else:
            return legacy_l02.solve(data)
    return solve_multiple(data)


def stable_order(layout):
    return tuple(sorted(layout, key=lambda p: (p[1], p[0])))


def canonical_pair(a, b):
    return (stable_order(a), stable_order(b))


def pair_bounds(pairs):
    """Cluster each inventory signature separately; IDs of indistinguishable boxes may swap."""
    by_size = collections.defaultdict(set)
    for a, b in pairs:
        by_size[len(a), len(b)].add(tuple(c for p in a+b for c in (p[0], round(p[1]/STEP))))
    cells, independent = [], []
    for sig, vs in sorted(by_size.items()):
        cover, packed = [], []
        # Fast exact rectangular cover for the frequent one-cell-per-group case.
        axes = list(zip(*vs))
        mins = [min(col) for col in axes]
        maxs = [max(col) for col in axes]
        if not vs:
            continue
        if all(h-l<=10 for l,h in zip(mins,maxs)):
            cover = [[mins, maxs, len(vs)]]
            packed = [min(vs)]
        else:
            for v in sorted(vs):
                if all(max((abs(k-y) for k,y in zip(v,w)), default=0)>10 for w in packed):
                    packed.append(v)
                for cell in cover:
                    lo,hi,_=cell
                    if all(max(b,vv)-min(a,vv)<=10 for a,b,vv in zip(lo,hi,v)):
                        for k,vv in enumerate(v):
                            lo[k]=min(lo[k],vv);hi[k]=max(hi[k],vv)
                        cell[2]+=1
                        break
                else:
                    cover.append([list(v),list(v),1])
        for lo,hi,count in cover:
            cells.append(dict(A_B_counts=sig, minimum=list(map(grid_x,lo)),maximum=list(map(grid_x,hi)),pairs=count))
        independent.extend(dict(A_B_counts=sig,vector=list(map(grid_x,v))) for v in packed)
    return dict(upper=len(cells),lower=len(independent),pair_count=len(pairs),cells=cells,packing=independent)


class RelaxedMotion:
    """Monotone over-approximation of actor and crate trajectories.

    A crate may slide once either side is reachable. We retain BOTH its old perch
    and every attainable new perch (including falling), waive the need to get the
    pusher to the correct SIDE at successive positions, and ignore travel times.
    On a single height, side walls of fixed scenery still stop a horizontal slide.
    Each composite node is the union of possible crate tops, not a simultaneous
    construction. These allowances can report possible false positives only.
    """
    def __init__(self,g):
        self.g=g
        self.fixed=[(a,b,z,z) for a,b,z in g.supports]
        self.mobile=[platform_path_nodes(p) for p in g.platforms]

    @functools.lru_cache(maxsize=50000)
    def edge(self,a,b):
        if not ride_jump(a,b):return False
        # A full-height intervening wall cannot be crossed underneath. Allow a
        # radius of contact at both ends and the entire physical jump apex.
        if a[1]<b[0]:left,right=a[1]+RADIUS,b[0]-RADIUS
        elif b[1]<a[0]:left,right=b[1]+RADIUS,a[0]-RADIUS
        else:return True
        for x,y,base,top in self.g.solid:
            if (min(right,y)>max(left,x)+TOL and base<=min(a[2],b[2])+TOL
                    and top>a[3]+6.5**2/32+TOL):
                return False
        return True

    @functools.lru_cache(maxsize=120000)
    def expanded(self,z,a,b):
        g=self.g
        # Begin with the slide corridor clear of vertical side walls. Keep an entire
        # unsupported gap up to the box width, even when the pusher could fall first.
        track=subtract([(0.,g.width)],[(x,y) for x,y,c,d in g.solid if c<z+1-TOL and d>z+TOL])
        out=[]
        for u,v in track:
            if b<u-TOL or a>v+TOL:continue
            supports=[(max(x,u),min(y,v)) for x,y,h in g.supports if abs(h-z)<TOL and x<=v and y>=u]
            segments=merge([(x-.5,y+.5) for x,y in supports]+[(a-.5,b+.5)])
            for x,y in segments:
                if max(a,x)<=min(b,y)+TOL:
                    out.append((max(x-.5,u),min(y+.5,v),z))
        return out

    def simulate(self,layout,start,goal,push):
        g=self.g
        # Extra parking / edge space is allowed in the ceiling, including during
        # movement; the constructive check below uses actual collision geometry.
        nodes=self.fixed+self.mobile+[(grid_x(i),grid_x(i)+1,h+1,h+1) for i,h in layout]
        sources=[(grid_x(i),grid_x(i)+1,h) for i,h in layout]
        def reach():
            l,r,z=start
            reached={i for i,n in enumerate(nodes) if n[2]-TOL<=z<=n[3]+TOL and max(l,n[0])<=min(r,n[1])+TOL}
            todo=list(reached)
            while todo:
                idx=todo.pop()
                for j,n in enumerate(nodes):
                    if j not in reached and self.edge(nodes[idx],n):
                        reached.add(j);todo.append(j)
            return [nodes[j] for j in reached]
        if not push:return Geometry.touches(reach(),goal)
        moving=set()
        # Crate occupancy ribbons carry their physical box identity. A carried
        # crate can land on another original or moved crate, never on its own
        # hypothetical past position. New overlaps are revisited after each pass.
        ribbons={i:{(a,b,h)} for i,(a,b,h) in enumerate(sources)}
        active_crates=set()
        landings={i:set() for i in range(len(sources))}
        while True:
            active=reach()
            if Geometry.touches(active,goal):return True
            changes=False
            for number,(a,b,z) in enumerate(sources):
                if not any(n[2]-TOL<=z+1 and z<=n[3]+HEIGHT+TOL and
                           (n[0]-.3-TOL<=a-RADIUS<=n[1]+.3+TOL or n[0]-.3-TOL<=b+RADIUS<=n[1]+.3+TOL)
                           for n in active):
                    continue
                active_crates.add(number)
                todo=[(a,b,z),*landings[number]]
                while todo:
                    left,right,h=todo.pop()
                    signature=(number,round(left,6),round(right,6),round(h,6))
                    if signature in moving:continue
                    moving.add(signature)
                    for x,y,k in self.expanded(h,left,right):
                        ribbons[number].add((x,y,k))
                        node=(x,y,k+1,k+1)
                        if node not in nodes:nodes.append(node);changes=True
                        for u,v,lower in g.supports:
                            if lower<k-TOL and max(u,x)-TOL<=min(y,v):
                                todo.append((max(u,x),min(y,v),lower))
                        for u,v,low,high in self.mobile:
                            if low<=k+TOL and max(u,x)-TOL<=min(y,v):
                                # A falling crate may hitch a ride even when the
                                # actual carrier would stop on contact.
                                node=(u,v,low+1,high+1)
                                if node not in nodes:nodes.append(node);changes=True
                                todo.append((u,v,high))
                        for other,(u,v,hh) in enumerate(sources):
                            if other!=number and abs(hh-(k+1))<TOL and max(u,left)<min(v,right)+TOL:
                                # Carry a supported upper crate with the lower box.
                                # Preserve its identity when creating a new position.
                                ride=(x,y,k+1)
                                if ride not in ribbons[other]:
                                    ribbons[other].add(ride);landings[other].add(ride)
                                    node=(x,y,k+2,k+2)
                                    if node not in nodes:nodes.append(node)
                                    changes=True
            # Descending onto a box may arrest a fall one block above the fixed
            # landing. Permit the most favorable phase and joint corridor for both
            # crates; demanding that these independent histories coincide would
            # discard genuine possibilities. Horizontal gains from an unsupported
            # shove are already included in expanded()'s extra overhang.
            for number in active_crates:
                for left,right,top in list(ribbons[number]):
                    for other,positions in ribbons.items():
                        if other==number:continue
                        for a,b,h in list(positions):
                            # Include only strict downward moves. Equal-height
                            # stacking support retains the original standing face.
                            if top<=h+1+TOL or max(left,a)>min(right,b)+TOL:continue
                            meet=(max(left,a),min(right,b),h+1)
                            if meet not in ribbons[number]:
                                ribbons[number].add(meet)
                                landings[number].add(meet)
                                node=(meet[0],meet[1],meet[2]+1,meet[2]+1)
                                if node not in nodes:nodes.append(node)
                                changes=True
            if not changes:return False

    @functools.lru_cache(maxsize=180000)
    def possible(self,layout,start,goal,push):
        return self.simulate(layout,start,goal,push)


def capsule_box_overlap(x,z,ix,h):
    """Distance between a vertical capsule axis segment and an axis-aligned crate."""
    left=grid_x(ix)
    dx=max(0.,left-x,x-left-1.)
    dz=max(0.,h-(z+HEIGHT-RADIUS),(z+RADIUS)-(h+1.))
    return dx*dx+dz*dz < RADIUS*RADIUS-TOL


def open_cut(segment,layout):
    a,b,z=segment
    holes=[]
    for ix,h in layout:
        dz=max(0.,h-(z+HEIGHT-RADIUS),(z+RADIUS)-(h+1.))
        if dz>=RADIUS:continue
        dx=math.sqrt(max(0.,RADIUS*RADIUS-dz*dz))
        x=grid_x(ix)
        holes.append((x-dx,x+1+dx))
    xs={a,b}
    for l,r in holes:
        if a<=l<=b:xs.add(l)
        if a<=r<=b:xs.add(r)
    return any(not any(l+TOL<x<r-TOL for l,r in holes) for x in xs)


class MultiScan:
    def __init__(self,data,removed=None,no_ride=False):
        self.g=Geometry(data,removed)
        self.data=data
        if no_ride:self.g.platforms=[]
        self.motion=RelaxedMotion(self.g)
        x,z=data['spawn']
        self.s=(x,x,z)
        self.m=tuple(data['mark'])
        self.e=tuple(data['exit'])

    def at(self,l):
        d=self.data; inv=d['inventory']
        faces=list(self.g.layouts(l,max(inv['A'],inv['B'])))
        def stage(start,end,qty,push=True):
            if start==self.s:
                fits=lambda p:all(not capsule_box_overlap(self.s[0],self.s[2],i,z) for i,z in p)
            else:
                fits=lambda p:open_cut(start,p)
            return {p for p in faces if len(p)<=qty and fits(p) and self.motion.possible(p,start,end,push)}
        A=stage(self.s,self.m,inv['A']);B=stage(self.m,self.e,inv['B'])
        minus=inv['pool']-1
        return dict(A=A,B=B,
                    no_push=bool(stage(self.s,self.m,inv['A'],False) and stage(self.m,self.e,inv['B'],False)),
                    no_cut=bool(stage(self.s,self.e,inv['A'])),
                    minus=any(len(p)<=minus for p in A) and any(len(p)<=minus for p in B))


def solve_multiple(data):
    scan=MultiScan(data)
    return make_report(data,scan)

def make_report(data,scan):
    g=scan.g
    width=data['width']
    lights=[grid_x(i) for i in on_grid(.6,width-.6)]
    memo={}
    def lamp(l):
        l=round(l,7)
        if l not in memo:memo[l]=scan.at(l)
        return memo[l]
    sets=collections.defaultdict(list)
    pairset=set();witness=[];budget=data['inventory']
    for l in lights:
        r=lamp(l);A=r['A'];B=r['B']
        for name in ('no_push','no_cut','minus'):
            if r[name]:sets[name].append(l)
        if not (A and B):continue
        sets['main'].append(l)
        pairs=set(itertools.product(A,B))
        pairset.update(pairs)
        collapse=lambda p:len({i for i,z in p})<=1
        if any(collapse(a) and collapse(b) for a,b in pairs):sets['single_column'].append(l)
        if A & B:sets['duplicate'].append(l)
        if any(collapse(a+b) for a,b in pairs):sets['world_column'].append(l)
        a,b=min(pairs)
        witness.append(dict(lamp=l,A=[[grid_x(i),z] for i,z in a],B=[[grid_x(i),z] for i,z in b],
                            A_options=len(A),B_options=len(B)))
    def modified(probe):
        return stats([l for l in lights if (v:=probe.at(l))['A'] and v['B']])
    no_ride=None;no_platform=None
    platforms=data.get('platforms',[])
    if platforms:
        no_ride=modified(MultiScan(data,no_ride=True))
        no_platform=modified(MultiScan(data,removed=data.get('primary_platform',platforms[0]['id'])))
    no_push,no_cut=stats(sets['no_push']),stats(sets['no_cut'])
    disabled={'push':no_push,'cut':no_cut,'platform':no_platform}.get(data['primary'])
    highest_tests=[]
    for x,name in highest(data):
        x=max(lights[0],min(lights[-1],x))
        p=lamp(x)
        test=dict(id=name,x=round(x,7),solved=bool(p['A'] and p['B']))
        horizontal=next((q for q in platforms if q['id']==name and q['axis'].upper()=='X'),None)
        if horizontal:
            u,v=sorted((horizontal['start'][0],horizontal['start'][0]+horizontal['travel']))
            points=sorted({u,v,x,*[l for l in lights if u<=l<=v]})
            hits=[l for l in points if (options:=lamp(l))['A'] and options['B']]
            test.update(swept_centres=[u,v],samples=len(points),possible_centres=hits,solved=bool(hits))
        highest_tests.append(test)
    start=lights[0] if data['rail']['start']=='left' else lights[-1]
    middle=lamp(width/2);points=sets['main'];intervals=bands(points)
    groups=pair_bounds(pairset)
    ref=reference_check(g,data)
    limit=.12 if data['id'][:3] in ('S07','S08') else (.5 if data['id'] in ('L02','L03') else .2)
    report=dict(id=data['id'],grid_step_B=STEP,model='relaxed_reachability_ceiling',lamp_samples=len(lights),count=len(points),
                ratio=round(len(points)/len(lights),8),intervals=intervals,start=start,start_solved=start in points,
                mid_solved=bool(middle['A'] and middle['B']),opposite_solved=round(width-start,6) in points,
                highest_tests=highest_tests,inventory_minus_one=stats(sets['minus']),disable_primary=disabled,no_push=no_push,no_cut=no_cut,
                no_ride=no_ride,remove_required_platform=no_platform,same_column_per_shot=stats(sets['single_column']),
                same_pose_both_shots=stats(sets['duplicate']),same_world_column_both_shots=stats(sets['world_column']),families=groups,
                reference=ref,witnesses=witness,
                checks={'ratio':len(points)/len(lights)<=limit,'width':any(b-a>=.3-TOL for a,b in intervals),
                        'displacement':bool(points) and all(abs((a+b)/2-start)>=3-TOL for a,b in intervals),
                        'start_impossible':start not in points,'tight_inventory':not sets['minus'],
                        'essential_primary':bool(disabled is not None and not disabled['count']),
                        'families_at_most_three':groups['upper']<=3,'reference_approved':all(ref[s+'_whole_box'] and ref[s+'_support_clearance'] for s in ('A','B'))})


    from route_certificate import populate
    populate(data,report,scan,lamp)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('level',type=Path)
    p.add_argument('-o','--output',type=Path)
    p.add_argument('--brief',action='store_true')
    opts=p.parse_args()
    data=json.loads(opts.level.read_text(encoding='utf-8-sig'))
    report=solve(data)
    if opts.output:
        opts.output.parent.mkdir(exist_ok=True,parents=True)
        opts.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    summary={k:v for k,v in report.items() if k not in ('witnesses','families','constructive')}
    if opts.brief and 'constructive' in report:
        summary['constructive']={k:v for k,v in report['constructive'].items() if k!='witnesses'}
    print(json.dumps(summary if opts.brief else report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
