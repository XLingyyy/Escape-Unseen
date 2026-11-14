"""Positive witness only: conservative free-fall for a up to 0.10s of coyote time.
PYTHONPATH=v3pack python legacy_coyote.py v3pack/levels/L02.json -o out.json
Ordinary jumps and standing waits are tested using the independent route checker.
The last jump spends coyote time after the centre reaches the edge of the top
crate, models gravity during that time, and lands with the centre beyond X=12.
"""
import argparse,itertools,json,math
from pathlib import Path
from legacy_alternate import clear_body,launch,rect
from level_solver import Geometry,bands,grid_x,on_grid,inside,dark_band,overlaps,TOL
from check_reference import check_arc

def solve(d,selected=None):
    g=Geometry(d);edge=next(obj['box'][0] for obj in d['solids'] if obj['id']=='Exit Ledge');fixed=g.solid;out=[]
    probes=on_grid(.60,d['width']-.6) if selected is None else [round(l/.05) for l in selected]
    for ix in probes:
        l=grid_x(ix);rat=(l,d['rail']['z'])
        def is_safe(x):return all(inside(x,dark_band(rat,g.solid+g.flags,z-.005,z+.005,0)) for z in [.85,1.2])
        staging=next((v for j in range(51)for v in [d['spawn'][0]-j*.02,d['spawn'][0]+j*.02] if .30<=v<=edge-.30 and is_safe(v)),None)
        if staging is None:continue
        from level_solver import shadow_at
        spawn_exact=all(inside(d['spawn'][0],shadow_at(rat,g.solid+g.flags,h)) for h in (.85,1.20))
        if not spawn_exact:continue
        prep=abs(staging-d['spawn'][0])/4
        F=[grid_x(i)for i,h in g.bases if h==0 and grid_x(i)<edge and g.approved(l,i,h)]
        U=[u for u in F if g.approved(l,round(u/.05),1)]
        if not F or not U:continue
        # Even ignoring face collisions and gravity during the grace period,
        # this farthest top cannot reach the exit.
        if max(U)+1+.40+4*(6.5+math.sqrt(6.5**2-32))/16<edge:continue
        for u,v in itertools.product(sorted(U,reverse=True), sorted(F,reverse=True)):
            if v+1>u-.04 or u+1+.4+2.43<edge+.015:continue
            boxes=fixed+[rect(v,0),rect(u,0),rect(u,1)]
            # Approach the lower box from a point on either side (provided both
            # the point and the entire floor walk from the cut clear all boxes).
            middles=[grid_x(i)for i in on_grid(d['mark'][0],d['mark'][1])]
            got=False
            for k in sorted(middles,key=lambda x:abs(x-v)):
                if not clear_body([k,0],boxes):continue
                for a in [v+1.35,v-.40]:
                    if not clear_body([a,0],boxes):continue
                    if any(overlaps((min(a,k)-.30,max(a,k)+.30,0,1.3),r)for r in boxes):continue
                    to1=[round(v+.50,4),1];to2=[round(u+.50,4),2];take=[round(a,4),0]
                    j1=launch(take,to1,boxes);j2=launch(to1,to2,boxes)
                    if not(j1 and j2):continue
                    # A full radius on the landing would discard the capsule's
                    # permitted lip contact; here the centre itself lands inside.
                    xe=u+1
                    for c in [.08,.085,.09,.095,.1]:
                        assert 16*c*c+(.30-8*c*c)**2>=.30**2 and 4*c>=.30
                        xs=xe+4*c;zs=2-8*c*c;tf=(6.5+math.sqrt(6.5**2-32*(3-zs)))/16
                        # Interior centre and body clearance at wall face must both hold.
                        if xs+4*tf<edge+.015:continue
                        # Model ".1 coyote" with strictly nonzero tolerance in the ceiling.
                        xdest=min(edge+.32,xs+4*tf-.001)
                        # During the 4 B/s edge run the foot sphere clears the
                        # original corner: (4t)^2 + (.30-8t^2)^2 >= .30^2.
                        # At launch x >= edge+.32 so the whole capsule has
                        # also left its former support. All other boxes stay.
                        if c*4<.30 or not check_arc([xs,zs],[xdest,3],boxes[:-1],11.5,tf,0,tf):continue
                        if not clear_body([xdest,3],boxes):continue
                        t=(abs(k-staging)+abs(k-a)+abs(xe-to2[0])+max(0,d['exit'][0]-xdest))/4+.22+.22+j1['seconds']+j2['seconds']+.2+c+tf+.35
                        if t>8:continue
                        out.append(dict(lamp=l,A_precondition='Select guard fully retracted at start if spawn is exposed; walk in empty A to the jointly dark staging point, wait 1.5s through its next inspection and leave after full retraction.',spawn_exact_dark=spawn_exact,staging_x=staging,staging_approach_s=prep,A=[],B=[[v,0],[u,0],[u,1]],cut_x=k,ground_takeoff=take,jumps=[j1,j2],
                                        last_ledge_takeoff=[xe,2],coyote_s=c,airborne_jump_starts=[xs,zs],land=[xdest,3],
                                        last_jump_flight=tf,last_control_speed=(xdest-xs)/tf,finish_x=max(xdest,d['exit'][0]),
                                        joint_to_exit_s_upper=math.ceil(t*100)/100,use_push=False));got=True;break
                    if got:break
                if got:break
            if got:break
    return dict(id=d['id'],intervals=bands([x['lamp']for x in out]),count=len(out),witnesses=out)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('level',type=Path);p.add_argument('-o',type=Path)
    a=p.parse_args();d=json.loads(a.level.read_text());result=solve(d);s=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if a.o:a.o.write_text(s)
    else:print(s)
