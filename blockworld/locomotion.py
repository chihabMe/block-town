"""Approved ep18 locomotion: planted-foot walk and urgent seven-stud/second run.

Explicit opt-in: clone a cast member with make_runner(), then call move() per frame.
Existing episode helpers and cast geometry are unchanged. Gait phases and feet
are solved in world space; idle transforms must not modify the result afterward.
"""
import math
from mathutils import Vector,Quaternion
import bpy,town,life
import locomotion_rig as base
from roblox import rchar

PROFILES={
    'run':dict(speed=7.,cycle=.66,stance=.18,lift=.75,arm=31.,lean=9.),
    'walk':dict(speed=3.,cycle=.90,stance=.47,lift=.22,arm=20.,lean=2.5),
}

def make_runner(original,name):
    """Same appearance as the cast member, with local knee/ankle/elbow joints."""
    c=rchar(name,**dict(original['spec']))
    base.rig(c)
    elbows={}
    for side in ('L','R'):
        arm=c['arm'+side];children=list(arm.children)
        elbow=town.empty(name+'.elbow'+side,(0,0,-1),arm)
        for o in children:
            z=[(o.matrix_basis@v.co).z for v in o.data.vertices]
            if min(z)>=-1:continue
            if max(z)<=-1:
                o.parent=elbow;o.location.z+=1
            else:
                base.split_mesh(o,arm,-1,True,o.name+'.upper_arm')
                base.split_mesh(o,elbow,-1,False,o.name+'.forearm')
                bpy.data.objects.remove(o,do_unlink=True)
        elbows[side]=elbow
    c['_run_elbows']=elbows;c['_locomotion_active']=False
    return c

def foot(side,t,kind='run'):
    p=PROFILES[kind];speed,cycle,stance=p['speed'],p['cycle'],p['stance']
    offset=0 if side=='L' else cycle*.5
    n=math.floor((t-offset)/cycle);contact=n*cycle+offset;age=t-contact
    distance=speed*contact+speed*stance*.5
    height=0.;pitch=0.;support=age<=stance
    if not support:
        u=(age-stance)/(cycle-stance)
        distance+=speed*cycle*base.ease(u)
        height=p['lift']*math.sin(math.pi*u)**(1 if kind=='run' else 2)
        pitch=math.radians((24 if kind=='run' else 18)*math.sin(2*math.pi*u)*math.sin(math.pi*u))
    low=min(y*math.sin(pitch)+z*math.cos(pitch) for y in (-.62,.52) for z in (-.30,.06))
    return distance,height-low,pitch,support

def move(c,start,yaw,t,kind='run',face='determined',phase=0.):
    p=PROFILES[kind];scale=c['scale'];tt=t+phase
    rot=Quaternion((0,0,1),math.radians(yaw));forward=rot@Vector((0,-1,0))
    origin=Vector(start)-forward*(p['speed']*scale*phase)
    root=Vector(start)+forward*(p['speed']*scale*t)
    step=tt%(p['cycle']*.5);swing=math.cos(2*math.pi*tt/p['cycle'])
    if kind=='run':
        if step<=p['stance']:hip=1.84-.07*math.sin(math.pi*step/p['stance'])
        else:hip=1.84+.09*math.sin(math.pi*(step-p['stance'])/(p['cycle']*.5-p['stance']))
    else:hip=1.78+.08*math.sin(math.pi*step/(p['cycle']*.5))
    town.pose(c,root,yaw,face,armL=(-p['arm']*swing,7),armR=(p['arm']*swing,7),
              head=(0,6 if kind=='run' else 1),lean=-p['lean'])
    c['body'].location=(.025*math.sin(2*math.pi*tt/p['cycle']),0,hip)
    c['body'].rotation_euler.z=math.radians(-(3 if kind=='run' else 2)*swing)
    for side,sgn in (('L',-1),('R',1)):
        c['_run_elbows'][side].rotation_euler.x=math.radians((-70-4*sgn*swing) if kind=='run' else -10)
        distance,z,pitch,_=foot(side,tt,kind)
        target=origin+forward*(distance*scale)+rot@Vector((sgn*.5*scale,0,z*scale))
        base.solve(c,side,target,pitch)
    c['_locomotion_active']=True
    return root

def install_life_filter(runners):
    """Keep scene life/blinking; preserve solved feet and the selected shot camera."""
    original_characters=life._characters;original_camera=life._camera
    def characters(T,t):
        chars=town.CHARACTERS[:]
        town.CHARACTERS[:]=[c for c in chars if all(c is not r for r in runners)]
        try:original_characters(T,t)
        finally:town.CHARACTERS[:]=chars
        for c in runners:
            if c.get('_locomotion_active'):life._blink(c,T,t,life._ph(c['name']))
    def camera(T,t,d):
        if not any(c.get('_locomotion_active') for c in runners):original_camera(T,t,d)
    life._characters=characters;life._camera=camera
