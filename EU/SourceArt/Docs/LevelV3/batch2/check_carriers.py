#!/usr/bin/env python3
"""Recheck timed rides in S05/S07/S08 from the final scene and solver-report JSONs.

Usage: python check_carriers.py [--root DIR] [--output FILE] [--scene S08]
Only the Python standard library is required. Coordinates are room-relative in B.
At local carrier time zero the platform starts the 0.60 s origin dwell. A clock
advances continuously from phase*period at load, including cuts and retakes.
The constructive route may wait for a visual dock event at a permanent dark stop.
"""
import argparse
import json
import math
from pathlib import Path

TOL=1e-8
DWELL=.6
RADIUS=.30
HEIGHT=1.30
WALK=4.


def intersects(a,b):
    return a[0]<b[1]-TOL and b[0]<a[1]-TOL and a[2]<b[3]-TOL and b[2]<a[3]-TOL


def bounding(rects):
    return min(r[0] for r in rects),max(r[1] for r in rects),min(r[2] for r in rects),max(r[3] for r in rects)


def face(x,z):
    return x-RADIUS,x+RADIUS,z,z+HEIGHT


def crate_box(p):
    x,z=p
    return x,x+1,z,z+1


class Carrier:
    def __init__(self,p):
        self.name=p['id']
        self.axis=p['axis']
        self.start=p['start']
        self.distance=p['travel']
        self.leg=abs(self.distance)/p['speed']
        self.period=2*(self.leg+DWELL)
        self.phase=p['phase']

    def fraction(self,t):
        t=t%self.period
        if t<=DWELL:return 0.
        if t<=DWELL+self.leg:return (1-math.cos(math.pi*(t-DWELL)/self.leg))*.5
        if t<=2*DWELL+self.leg:return 1.
        return (1+math.cos(math.pi*(t-2*DWELL-self.leg)/self.leg))*.5

    def center(self,t):
        dx=self.distance*self.fraction(t)
        x,z=self.start
        return (x+dx,z) if self.axis=='X' else (x,z+dx)

    def plate(self,t):
        x,z=self.center(t)
        return x-1,x+1,z-.15,z+.15

    def sweep(self,t0,t1):
        times=[t0,t1]
        for k in range(math.floor(t0/self.period)-1,math.floor(t1/self.period)+1):
            for f in (0,DWELL,DWELL+self.leg,2*DWELL+self.leg):
                event=k*self.period+f
                if t0<event<t1:times.append(event)
        return bounding([self.plate(t) for t in times])

    def outbound_time(self,fraction):
        if not -TOL<=fraction<=1+TOL:raise ValueError('Launch outside travel')
        return DWELL+self.leg*math.acos(1-2*max(0,min(1,fraction)))/math.pi


def ray_blocked(lamp,point,rect):
    lo,hi=0.,1.
    for start,finish,low,high in zip(lamp,point,rect[::2],rect[1::2]):
        if abs(start-finish)<TOL:
            if not low-TOL<=start<=high+TOL:return False
        else:
            a,b=sorted(((low-start)/(finish-start),(high-start)/(finish-start)))
            lo=max(lo,a)
            hi=min(hi,b)
    return lo<=hi+TOL


def dark(p,lamp,scenery):
    x,z=p
    return all(any(ray_blocked(lamp,(x,z+offset),r) for r in scenery) for offset in (.85,1.2))


def on_top(p,rects):
    x,z=p
    return any(r[0]+TOL<=x<=r[1]-TOL and abs(z-r[3])<.00001 for r in rects)


def duration(j):
    dz=j['to'][1]-j['from'][1]
    return (6.5+math.sqrt(6.5**2-32*dz))/16


def timing(scene,mover,jin,jout):
    """Three authored dock signals. Locations and travel are read from the level."""
    if mover.axis=='Z':
        board=-.15 # 0.15 s before the start of the low-end dwell
        rise=jout['from'][1]-(mover.start[1]+.15)
        leave=mover.outbound_time(rise/mover.distance)
    elif scene=='S05':
        board=.20 # first third of the 0.60 s west dwell
        leave=DWELL+mover.leg # the east-end dwell begins
    else:
        board=DWELL # the west dwell ends; board an accelerating ferry
        target_center=jout['from'][0]-.75
        leave=mover.outbound_time((target_center-mover.start[0])/mover.distance)
    return board,leave


def certify_arc(jump,mover,tstart,surfaces,unknown_sweeps,dt):
    """Each subinterval covers the entire parabolic/linear player envelope and
    entire sinusoidal plate envelope. AABB separation certifies an interval,
    rather than treating a finite list of frame snapshots as a continuous proof.
    """
    a,z=jump['from']
    b,h=jump['to']
    T=duration(jump)
    dx=abs(b-a)
    if h-z>1+TOL or WALK*T-dx<.30-TOL:raise ValueError('Jump margin')
    line=1 if b>=a else -1
    def zz(t):return z+6.5*t-8*t*t
    count=math.ceil(T/dt)
    for d in range(21):
        wait=(T-dx/WALK)*d/20
        def xx(t):return a+line*min(dx,max(0,t-wait)*WALK)
        accepted=True
        for i in range(count):
            u,v=T*i/count,T*(i+1)/count
            xs=sorted((xx(u),xx(v)))
            heights=[zz(u),zz(v)]
            if u<6.5/16<v:heights.append(zz(6.5/16))
            envelope=(xs[0]-RADIUS,xs[1]+RADIUS,min(heights),max(heights)+HEIGHT)
            # At a rising-platform takeoff independent AABBs overlap at the
            # separating contact. Certify this interval instead by relative
            # vertical speed: v_player >= 6.5-16*v, v_plate <= its peak.
            peak=abs(mover.distance)*math.pi/(2*mover.leg) if mover.axis=='Z' else 0.
            separating=(on_top(jump['from'],[mover.plate(tstart)]) and 6.5-16*v>=peak)
            plates=[] if separating else [mover.sweep(tstart+u,tstart+v)]
            if any(intersects(envelope,r) for r in surfaces+unknown_sweeps+plates):
                accepted=False
                break
        if accepted:return {'delayed_horizontal_input_s':round(wait,6),'flight_s':round(T,6),'intervals':count}
    raise ValueError(f'No collision-free input delay found: {jump}')


def ride_witness(scene,level,witness,platform,jin,jout,other,dt):
    shot=jin['shot']
    boxes=[crate_box(p) for p in witness[shot]]
    fixed=[o['box'] for o in level['solids']]
    flags=[o['box'] for o in level['flags']]
    surfaces=fixed+boxes
    unknown=[p.sweep(0,p.period) for p in other]
    lamp=(witness['lamp'],level['rail']['z'])
    begin,end=timing(scene,platform,jin,jout)
    boarded=begin+duration(jin)
    landed=end+duration(jout)
    if not (begin<boarded<end<landed):raise ValueError('Ride event ordering')
    if not (on_top(jin['from'],surfaces) and on_top(jout['to'],surfaces)):
        raise ValueError('No fixed takeoff/landing support')
    if not (on_top(jin['to'],[platform.plate(boarded)]) and on_top(jout['from'],[platform.plate(end)])):
        raise ValueError('No moving takeoff/landing support')
    if not all(dark(p,lamp,fixed+flags) for p in [jin['from'],jout['to']]):
        raise ValueError('Uncovered transfer stop')
    if any(intersects(platform.sweep(0,platform.period),s) for s in surfaces+unknown):
        raise ValueError('Plate swept volume can collide or stall on this layout')
    arc_in=certify_arc(jin,platform,begin,surfaces,unknown,dt)
    arc_out=certify_arc(jout,platform,end,surfaces,unknown,dt)
    left=jin['to'][0]-platform.center(boarded)[0]
    right=jout['from'][0]-platform.center(end)[0]
    relative_speed=abs(right-left)/(end-boarded)
    if max(abs(left),abs(right))>1+TOL or relative_speed>WALK+TOL:raise ValueError('Rider cannot reposition on deck')
    # Both center and offset are monotone on each slice. Independent bounds on
    # their sum cover every intermediate rider pose, including a stationary plate.
    n_steps=math.ceil((end-boarded)/dt)
    for i in range(n_steps):
        u,v=i/n_steps,(i+1)/n_steps
        deck=platform.sweep(boarded+u*(end-boarded),boarded+v*(end-boarded))
        d0,d1=sorted((left+(right-left)*u,left+(right-left)*v))
        rider=(deck[0]+1+d0-RADIUS,deck[1]-1+d1+RADIUS,deck[2]+.3,deck[3]+HEIGHT)
        if any(intersects(rider,r) for r in surfaces+unknown):raise ValueError('Rider strikes fixed scene or another carrier')
    if (landed-begin)>8+TOL:raise ValueError('Joint transfer is longer than 8 seconds')
    period=platform.period
    elapsed=landed-begin
    if scene=='S05':
        # A bad departure lies in [5s warning + 1.5s inspection]. W<P means
        # each bad departure needs a separate inspection. No 3 can be bad if
        # 2*minimum guard period exceeds 2*P plus the forbidden window width.
        W=6.5
        guard_min=11.5
        if not (elapsed+.20<=5 and W<period and 2*guard_min>2*period+W):raise ValueError('No deterministic three-call waiting policy')
        guard={'policy':'take first west call without warning or active inspection',
               'at_most_calls':3,'warning_and_inspection_s':W,'min_guard_cycle_s':guard_min,
               'action_plus_allowance_s':round(elapsed+.20,6),'guaranteed_notice_s':5.}
    else:
        # Use an entire period as an upper bound on the delay until the NEXT
        # departure from arbitrary phase. The visible-action time ends at the
        # permanently dark first landing point, not at completion of the cut.
        guard_bound=period+elapsed
        if guard_bound>=10-TOL:raise ValueError(f'Not protected by a full post-retraction interval ({guard_bound})')
        guard={'policy':'at full guard retraction take the next authored dock signal',
               'arbitrary_phase_to_dark_bound_s':round(guard_bound,6),'earliest_inspection_s':10.,
               'remaining_slack_s':round(10-guard_bound,6)}
    return {'platform':platform.name,'shot':shot,'period_s':round(period,6),
            'initial_phase_fraction':platform.phase,'first_signal_from_load_s':round((begin-platform.phase*period)%period,6),
            'local_board_signal_s':round(begin,6),'local_board_contact_s':round(boarded,6),
            'local_disembark_signal_s':round(end,6),'local_fixed_dark_landing_s':round(landed,6),
            'actor_endpoints':[jin['from'],jin['to'],jout['from'],jout['to']],
            'max_deck_relative_speed_B_per_s':round(relative_speed,6),'board_arc':arc_in,'depart_arc':arc_out,
            'deck_intervals':n_steps,'complete_exposure_ceiling_s':round(elapsed,6),'patrol':guard}


def audit(root,scene,dt):
    paths=list((root/'levels').glob(scene+'*.json'))
    if len(paths)!=1:raise ValueError(f'Expected one {scene} scene JSON')
    level=json.loads(paths[0].read_text())
    report=json.loads((root/'reports'/(scene+'.json')).read_text())
    rides={'S05':[('Camera Dolly',5,6)],'S07':[('Lift',1,2)],'S08':[('Lift',1,2),('Ferry',3,4)]}[scene]
    movers={p['id']:Carrier(p) for p in level['platforms']}
    jumps=level['reference']['jumps']
    expected={round(start+i*.05,6) for start,stop in report['intervals'] for i in range(round((stop-start)/.05)+1)}
    witnesses=report['constructive']['witnesses']
    found={w['lamp'] for w in witnesses}
    if expected!=found or len(witnesses)!=len(expected):raise ValueError(f'{scene}: constructive lamp witnesses do not cover ceiling intervals')
    results=[]
    for w in witnesses:
        route=[]
        for name,i,j in rides:
            route.append(ride_witness(scene,level,w,movers[name],jumps[i],jumps[j],[p for key,p in movers.items() if key!=name],dt))
        results.append({'lamp':w['lamp'],'A':w['A'],'B':w['B'],'rides':route})
    return {'scene':scene,'lamp_count':len(results),'intervals':report['intervals'],'witnesses':results}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--output',type=Path)
    p.add_argument('--scene',action='append',choices=['S05','S07','S08'])
    p.add_argument('--interval-s',type=float,default=.002,help='maximum width of a continuous bounding time interval')
    args=p.parse_args()
    if not 0<args.interval_s<=.05:p.error('interval width must be >0 and <=0.05s')
    data={'format':1,'maximum_interval_s':args.interval_s,
          'input':'shipped scene JSON and constructive per-lamp crate layouts in matching reports, reproduced by level_solver.py',
          'scope':'independent timed carrier-transfer geometry and patrol schedule; non-carrier jumps, crate approval and rest of route are in the main solver',
          'clock':'time advances through cuts/retakes; choose next dock event from a dark wait, independent of load phase',
          'collision':'floating-point continuous interval enclosure, 1e-8 B strict-overlap tolerance; moving plate sinusoid extrema and parabolic apex included; touching a face is legal',
          'assumptions':['4 B/s controllable world-horizontal air speed with a 0–4 B/s input (choose zero or four); each arc begins at the listed foot position with vertical impulse 6.5 B/s, no added carrier impulse',
                         'standing rider is transported by deck and may walk on it; other independently phased plates are represented by their full swept volumes',
                         'guard entirely absent for at least 10 s after full retraction, or sends 5 s notice before inspection; boarding signals observed in play'],
          'scenes':[audit(args.root,s,args.interval_s) for s in args.scene or ['S05','S07','S08']]}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(' '.join(f"{s['scene']}={s['lamp_count']} lamps / {sum(len(w['rides']) for w in s['witnesses'])} rides" for s in data['scenes']))


if __name__=='__main__':main()
