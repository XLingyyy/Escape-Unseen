#!/usr/bin/env python3
"""Independent fixed-geometry collision and clearance audit for reference jumps.

Collision uses a circumscribing 0.60 x 1.30 rectangle. The vertical trajectory
is analytic. We enumerate start/end delays on the same jump, then test every
time interval delimited by the rectangle crossing a face. The check covers
all static solids and current visible crates. Moving carriers require the
arrival/departure schedule in the level card.
"""
import argparse
import json
import math
from pathlib import Path

EPS=1e-8
RADIUS=.30
HEIGHT=1.30


def intersects(a,b):
    return min(a[1],b[1])-max(a[0],b[0])>EPS and min(a[3],b[3])-max(a[2],b[2])>EPS


def check_arc(a,b,boxes,room,tmax,delay,move_time):
    start,z0=a
    end,z1=b
    vel=(end-start)/move_time if move_time else 0
    def pos(t):
        return start+vel*min(move_time,max(0,t-delay)), z0+6.5*t-8*t*t
    top=min(tmax,6.5/16)
    if pos(top)[1]+HEIGHT>room+EPS:return False
    events={0,tmax,delay,delay+move_time}
    for left,right,base,roof in boxes:
        for x in (left-RADIUS,right+RADIUS):
            if vel:
                t=delay+(x-start)/vel
                if delay<t<delay+move_time:events.add(t)
        for z in (base-HEIGHT,roof):
            rad=6.5**2-32*(z-z0)
            if rad<0:continue
            for t in ((6.5-math.sqrt(rad))/16,(6.5+math.sqrt(rad))/16):
                if 0<t<tmax:events.add(t)
    times=sorted(events)
    for u,v in zip(times,times[1:]):
        if v-u<EPS:continue
        x,z=pos((u+v)/2)
        if any(intersects((x-RADIUS,x+RADIUS,z,z+HEIGHT),o) for o in boxes):return False
    return True


def jump(a,b,boxes,h):
    rad=6.5**2-32*(b[1]-a[1])
    if rad<0:return None
    tf=(6.5+math.sqrt(rad))/16
    min_move=abs(a[0]-b[0])/4
    if min_move>tf+EPS:return None
    # Bounds are exact for each tried control. Delay/control grid supplies
    # positive witnesses only; failure is a request to revise the takeoff.
    for i in range(17):
        travel=min_move+(tf-min_move)*i/16
        for j in range(17):
            delay=(tf-travel)*j/16
            if check_arc(a,b,boxes,h,tf,delay,travel):
                return {'flight_s':round(tf,6),'horizontal_delay_s':round(delay,6),
                        'horizontal_time_s':round(travel,6),'horizontal_speed_Bps':
                         round((b[0]-a[0])/travel,6) if travel>EPS else 0}
    return None


def audit(d):
    r=d['reference'];zs=d['rail']['z'];fixed=[o['box'] for o in d['solids']]
    events=[*fixed,*[o['box'] for o in d['flags']]]
    for p in d['platforms']:
        x,z=p['start'];dx=p['travel'] if p['axis']=='X' else 0;dz=p['travel'] if p['axis']=='Z' else 0
        events.append([min(x,x+dx)-1,max(x,x+dx)+1,min(z,z+dz)-.15,max(z,z+dz)+.15])
    gap=min(max(0,q[2]-zs,zs-q[3]) for q in events)
    h=d.get('room_height',d.get('height',11.5))
    result=[]
    for i,j in enumerate(r['jumps']):
        shot=j.get('shot') or ('B' if d['id']=='L02' or i>=2 else 'A')
        boxes=[v[:] for v in r[shot]]
        pushes=r.get('pushes',[]) or ([{'shot':'A','crate':1,'via':r['A_push']}] if 'A_push' in r else [])
        for p in pushes:
            if p['shot']!=shot:continue
            # Use arrival position for jumps using the pushed step and later
            # jumps. Earlier approach jumps retain the original approved pose.
            src,end=p['via'][0],p['via'][-1]
            if d['id']=='L00' or max(j['from'][0],j['to'][0])>=max(src[0],end[0])-.35:
                boxes[p['crate']-1]=end
        static=fixed+[[x,x+1,z,z+1] for x,z in boxes]
        ctrl=jump(j['from'],j['to'],static,h)
        result.append({'shot':shot,'from':j['from'],'to':j['to'],'collision_free':bool(ctrl),'input':ctrl})
    return {'id':d['id'],'rail_clearance_B':round(gap,5),'rail_clear':gap>=.30-EPS,'jump_inputs':result,
            'all_fixed_arcs_clear':all(j['collision_free'] for j in result),
            'excludes':'moving steel plates during flight; inspect platform schedule in design document'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('files',nargs='+',type=Path)
    p.add_argument('-o',type=Path)
    args=p.parse_args()
    results=[audit(json.loads(f.read_text(encoding='utf-8-sig'))) for f in args.files]
    data=json.dumps(results,indent=2,ensure_ascii=False)+'\n'
    if args.o:args.o.write_text(data,encoding='utf-8')
    else:print(data)
