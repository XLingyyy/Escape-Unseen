"""Certificates for the retained three-crate Hidden Stair. Standard library only.

A negative verdict is a necessary-condition proof. A positive verdict gives a
constructive no-push staircase with an optional modeled coyote launch. Where they differ, report both sets explicitly.
"""
import math
from level_solver import (EPS, TOL, Geometry, bands, grid_x, highest, inside,
                          on_grid, reference_check, stats, shadow_at)


def box_poses(geometry, light, z, edge):
    # Do not exclude the mark or spawn from this necessary upper bound.
    intervals = geometry.approved_intervals(light, z)
    return {index for index in on_grid(0, edge - 1)
            if inside(grid_x(index), intervals) and geometry.free_box(grid_x(index), z)}


def recognized_geometry(data):
    """Reject a changed topology until the inclusion lemma has been proved for it."""
    mark = data['mark']
    by_name = {obj['id']: obj['box'] for obj in data['solids']}
    exit_face = by_name.get('Exit Ledge')
    bar = by_name.get('Beam')
    if not (data.get('floor', True) and not data['platforms'] and
            set(by_name) == {'Exit Ledge', 'Beam'} and exit_face and bar and
            exit_face[2:] == [0, 3] and exit_face[1] == data['width'] and
            bar[2] > 4.30 and 0 < data['spawn'][0] < exit_face[0] and
            data['spawn'][1] == mark[2] == 0 and mark[1] < exit_face[0] and
            data['exit'][2] == 3 and exit_face[0] <= data['exit'][0] and
            data['exit'][1] <= exit_face[1] and data['inventory'] == {'pool':3,'A':0,'B':3}):
        raise ValueError('L02 proof requires flat entry, a 3 B exit and one overhead beam. '
                         'Re-derive the bound after changing this topology.')
    return exit_face[0]


def actor_dark(g, light, point):
    x,z = point
    return all(all(inside(x, shadow_at((light, g.data['rail']['z']), obstacles, z+h))
                   for h in (.85, 1.20)) for obstacles in g.occluders)


def staircase(g, light, foot, top, edge):
    """Place three approved crates; visit the low top then high top and the exit.

    The three jumps may rise vertically by 0.20 s before moving. The capsule
    then clears the near vertical face before its centre crosses that face.
    Ground walk starts at a free cut point; the dark spawn is a reset-safe wait.
    From spawn to door is timed as one leg to avoid assumptions about the patrol.
    """
    d=g.data
    if not actor_dark(g, light, d['spawn']):return None
    max_jump=(6.5+math.sqrt(6.5**2-32))/4
    # Closest legal door foot centre with physical side clearance.
    door_x=max(d['exit'][0],edge+.31)
    for upper in sorted(foot & top, reverse=True):
        u=grid_x(upper)
        if door_x-(u+.5)>max_jump-.30+TOL or door_x<=u+.5:continue
        # Candidate low step to the left of the two-high column.
        for low in sorted(foot,reverse=True):
            v=grid_x(low)
            if v+1>u+TOL or u-v>max_jump-.30+TOL:continue
            takeoff=v-.43
            cut=max(d['mark'][0],min(d['mark'][1],takeoff))
            if takeoff<cut-TOL or cut<d['spawn'][0]:continue
            # Choose delayed, constant-speed horizontal input on the ascent.
            tf=max_jump/4
            # First centre-side intersection with the target's near face must
            # occur with feet already above its top (rise > 1 B).
            crossings=[(takeoff,v+.50,v),(v+.50,u+.50,u),(u+.50,door_x,edge)]
            timing_ok=True
            for a,b,face in crossings:
                delta=b-a
                delay=min(.21,tf-delta/4)
                if delay<0:timing_ok=False;break
                t=delay+(face-.30-a)*(tf-delay)/delta
                if not 0<=t<=tf or 6.5*t-8*t*t<1-1e-7:timing_ok=False;break
            if not timing_ok:continue
            seconds=(takeoff-d['spawn'][0])/4+.25+3*(tf+.12)+.25
            if seconds>8:continue
            return {'lamp':light,'A':[],'B':[[v,0],[u,0],[u,1]],
                    'cut_x':round(cut,4),'takeoff_x':round(takeoff,4),
                    'landings':[[v+.5,1],[u+.5,2],[door_x,3]],
                    'joint_action_s':round(seconds,4)}
    return None


def solve(data):
    g=Geometry(data)
    edge=recognized_geometry(data)
    lights=[grid_x(i) for i in on_grid(.60,data['width']-.60)]
    # To reach the exit, an accessible crate top above 1 B is necessary.
    # Before the first arrival at the exit, no higher fixed support can be
    # reached to push a crate down. Horizontal pushes and falls cannot raise a
    # crate. Every initial qualifying upper crate therefore sits above the
    # floor on one base, or bridges two contiguous full-shadow approved bases.
    # In the latter case their union includes a full (virtual) aligned base:
    # evaluating that virtual box is still a necessary optical condition.
    def test(light):
        foot=box_poses(g,light,0,edge);top=box_poses(g,light,1,edge)
        return bool(foot & top), staircase(g,light,foot,top,edge)

    outcomes={l:test(l) for l in lights}
    from legacy_coyote import solve as ledge_routes
    unresolved_lights=[l for l,(possible,w) in outcomes.items() if possible and not w]
    extra=ledge_routes(data,unresolved_lights)
    for w in extra['witnesses']:
        outcomes[w['lamp']]=(True,w)
    hi=[l for l,(possible,_) in outcomes.items() if possible]
    lo=[l for l,(_,witness) in outcomes.items() if witness]
    start=lights[0] if data['rail']['start']=='left' else lights[-1]
    mid=data['width']/2
    other=round(data['width']-start,6)
    def result(l):
        h,w=outcomes[l] if l in outcomes else test(l)
        return 'witness' if w else ('open' if h else 'impossible')
    ref=reference_check(g,data)
    reference=data['reference']
    ref_light=reference['lamp']
    ref['spawn_actor_dark']=actor_dark(g,ref_light,data['spawn'])
    ref['patrol_legs']=reference.get('patrol_legs',[])
    ref['all_joint_legs_under_8']=all(p['seconds']<=8 for p in ref['patrol_legs'])
    def bound():
        return {**stats(hi),'kind':'upper_only','verified_count':0}
    uncertified=sorted(set(hi)-set(lo))
    return dict(id=data['id'],model='three_crate_optical_necessity_and_constructive_routes',
                grid_step_B=.05,lamp_samples=len(lights),start=start,
                count=len(hi),intervals=bands(hi),ratio=round(len(hi)/len(lights),7),
                certified={**stats(lo),'ratio':round(len(lo)/len(lights),7)},
                unresolved=stats(uncertified),start_solved=result(start)=='witness',
                mid_solved={'witness':True,'impossible':False,'open':None}[result(mid)],
                opposite_solved={'witness':True,'impossible':False,'open':None}[result(other)],
                special_status={'start':result(start),'mid':result(mid),'opposite':result(other)},
                highest_tests=[{'id':n,'x':x,'status':result(x),
                                'solved':{'witness':True,'impossible':False,'open':None}[result(x)]}
                               for x,n in highest(data)],
                inventory_minus_one=bound(),no_push={**stats(hi),'kind':'upper_with_witnesses','verified':stats(lo)},
                no_cut=stats([]),disable_primary=stats([]),no_ride=None,same_pose_both_shots=stats([]),
                same_column_per_shot=bound(),families=None,
                reference=ref,witnesses=[w for h,w in outcomes.values() if w],
                checks={'start_impossible':result(start)=='impossible','ratio':len(hi)/len(lights)<=.5,
                        'reference_approved':all(ref[s+'_whole_box'] and ref[s+'_support_clearance'] for s in ('A','B'))},
                notes={'upper':'At least one approved floor/top pair is necessary, including bridged supports; '
                               'the reported upper bound does not assume any spawn/mark exclusion.',
                       'inventory_and_same_column':'Live push behavior of an initially stacked column is left open. '
                       'Do not infer impossibility from absence of a static staircase.',
                       'uncertified':'Unresolved samples are included when proving the <=50% cap; all constructive witnesses obey a <=8 s joint patrol budget.'})
