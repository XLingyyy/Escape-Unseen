"""Independent replay for alternate L03 lamps. Takes a level JSON as input.
Usage: python legacy_alternate.py path/to/L03.json -o alternate_L03.json
Place alongside level_solver.py and check_reference.py, or add their path to PYTHONPATH.
"""
import argparse
import itertools
import json
import math
from pathlib import Path

from check_reference import check_arc
from route_certificate import supported
from level_solver import Geometry, bands, grid_x, on_grid, overlaps, dark_band, inside

RADIUS = .30
HEIGHT = 1.30


def rect(x, z):
    return x, x+1, z, z+1


def clear_body(q, blocks):
    x, z = q
    return not any(overlaps((x-RADIUS,x+RADIUS,z,z+HEIGHT), b) for b in blocks)


def launch(start, goal, blocks):
    dx, dz = goal[0]-start[0], goal[1]-start[1]
    t = (6.5 + math.sqrt(6.5**2 - 32*dz)) / 16
    if dz > 1 or 4*t - abs(dx) < .30:
        return None
    available = t - abs(dx)/4
    for portion in (1., .75, .5, .25, 0.):
        delay = max(0.,available*portion)
        if check_arc(start,goal,blocks,11.5,t,delay,t-delay):
            return dict(action='jump',start=start,end=goal,seconds=t,
                        stationary_launch_delay=delay,
                        horizontal_speed=dx/(t-delay),settle=.10)
    return None


def verify(l,g,d):
    if d['id']!='L03':
        raise ValueError('The alternate route is defined for Match Cut.')
    orig=d['reference']
    if len(d['platforms']):return None
    light=(l,d['rail']['z'])
    fixed=g.solid; bodyshade = all(inside(d['spawn'][0],dark_band(light,fixed+g.flags,
                      d['spawn'][1]+k-.005,d['spawn'][1]+k+.005,0))for k in (.85,1.2))
    if not bodyshade:return None
    xA,zA=orig['A'][0]
    if not g.approved(l,round(xA/.05),zA):return None
    bs=[grid_x(i) for i,h in g.bases if h==2 and g.approved(l,i,h)]
    for xB in sorted(bs,reverse=True):
        left,right,z=d['mark'];endB=orig['B'][0][0]
        cut=min(7.5,round(xB-.4,2))
        if abs(z-2)>1e-7 or not left<=cut<=right or xB>endB:continue
        if not g.free_box(xA,zA) or not g.free_box(xB,2):continue
        A=rect(xA,zA);B=rect(xB,2)
        if not clear_body(d['spawn'],fixed+[A]) or not clear_body((cut,2),fixed+[B]):continue
        q=list(d['spawn']);actions=[];total=0.
        def walk(x,z,blocks,rate=4.,name='walk'):
            nonlocal q,total
            if abs(q[1]-z)>1e-7:return False
            y=q[0]
            if abs(x-y)<1e-7:return True
            sweep=(min(x,y)-RADIUS,max(x,y)+RADIUS,z,z+HEIGHT)
            if any(overlaps(sweep,b) for b in blocks):return False
            if not any(aa-1e-7<=min(x,y) and max(x,y)<=bb+1e-7 and abs(k-z)<1e-7 for aa,bb,k in g.supports):return False
            t=abs(x-y)/rate;actions.append(dict(action=name,start=q[:],end=[x,z],seconds=t));total+=t;q=[x,z];return True
        def j(to,blocks):
            nonlocal q,total
            if not (supported(q,blocks,[]) and supported(to,blocks,[])):return False
            k=launch(q,to,blocks)
            if k is None:return False
            actions.append(k);total+=k['seconds']+k['settle'];q=list(to);return True
        if not(j([5.,1],fixed+[A]) and j([6.40,2],fixed+[A]) and walk(cut,2,fixed+[A])):continue
        actions.append(dict(action='cut',at=q[:],seconds=.22));total+=.22
        touch=round(xB-RADIUS,4)
        if not walk(touch,2,fixed+[B]):continue
        p1,p2=rect(xB,2),rect(endB,2)
        sweep=(p1[0],p2[1],2,3)
        if any(overlaps(sweep,v)for v in fixed):continue
        if not any(a<=xB and endB+1<=b and abs(z-2)<1e-7 for a,b,z in g.supports):continue
        if not walk(endB-RADIUS,2,fixed,1.5,'push_right'):continue
        if endB>xB:actions[-1]['crate_from_to']=[[xB,2],[endB,2]]
        if not walk(8.70,2,fixed+[p2]):continue
        if not(j([10.,3],fixed+[p2]) and j([11.85,4],fixed+[p2])):continue
        if not (d['exit'][0]<=q[0]<=d['exit'][1] and q[1]==d['exit'][2]):continue
        actions.append(dict(action='exit',at=q[:],seconds=.22));total+=.22
        if total+.20>8:continue
        return dict(lamp=l,A=[[xA,zA]],B=[[xB,2]],wait_before_start_s=1.5,
                    start_condition='Wait at the shaded spawn with both boxes approved in their respective shots until the guard fully retracts.',
                    spawn_head_chest_expanded_dark=True,all_fixed_arcs_clear=True,
                    shot_B_cut_point=[cut,2],joint_to_exit_s_upper=math.ceil((total+.20)*100)/100,
                    actions=actions)
    return None


def run(d):
    g=Geometry(d)
    lights=(grid_x(i)for i in on_grid(.6,d['width']-.6))
    records=[q for l in lights if (q:=verify(l,g,d))]
    return dict(id=d['id'],grid=.05,intervals=bands([r['lamp']for r in records]),
                count=len(records),witnesses=records)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('level',type=Path)
    parser.add_argument('-o',type=Path)
    args=parser.parse_args()
    result=run(json.loads(args.level.read_text()))
    payload=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.o:args.o.write_text(payload)
    else:print(payload)
