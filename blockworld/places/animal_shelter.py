"""A warm animal shelter, on the next outdoor plot at (4000, 0).

One reusable location with a real hinged entrance, rescue bell and open kennel area.
The kennel foreground stays clear for dog-and-puppy acting. Episodes supply animals.
"""
import math
import town as T
from roblox import rbox,disc,plastic
from places._outdoor import backdrop

GEO=('x','y')

def build(x=4000,y=0):
    backdrop(x,y,seed=181,trees=10,clear=65)
    root=T.empty('animal_shelter',(x,y,0));root['bt_root']=True
    cream=plastic('#F5ECDD',0.65);teal=plastic('#4E9B9B',0.45);navy=plastic('#24445E',0.4)
    rbox((30,29,0.5),(0,-2,0),plastic('#B8C6C3',0.7),root,bv=0.12)
    rbox((28,24,0.25),(0,0,0.3),plastic('#D8D3C6',0.6),root,bv=0.03)
    for xx in (-14,14):rbox((0.55,24,10),(xx,0,5.25),cream,root,bv=0.06)
    rbox((28,0.55,10),(0,12,5.25),cream,root,bv=0.06)
    # Entrance opening is a real gap between two wall pieces, not a door placed on a solid wall.
    for xx in (-8.6,8.6):rbox((10.8,0.6,7.0),(xx,-12,3.75),teal,root,bv=0.04)
    rbox((28,0.6,3.0),(0,-12,8.75),cream,root,bv=0.05)
    roof=rbox((29.5,25.5,0.6),(0,0,10.6),navy,root,bv=0.1);roof.visible_shadow=False
    # A compact two-line sign remains legible in a portrait entrance shot.
    rbox((11.2,0.5,3.4),(0,-12.5,8.7),navy,root,bv=0.15)
    for word,z in [('ANIMAL',9.35),('SHELTER',8.05)]:
        T.text(word,1.15,(0,-12.82,z),T.mat('#FFFFFF',emit=0.55,key='shelter.sign'),root,max_w=10.0)
    hinge=T.empty('shelter.door_hinge',(-3.2,-12,0.4),root);hinge['bt_shelter_door']=True
    rbox((6.4,0.4,6.3),(3.2,0,3.45),navy,hinge,bv=0.08)
    rbox((5.3,0.1,3.4),(3.2,-0.26,4.6),T.mat('#8FD8DD',emit=0.2,key='shelter.glass'),hinge,bv=0.03)
    rbox((0.28,0.6,1.1),(5.6,-0.3,3.3),plastic('#FFD06B',0.3),hinge,bv=0.06)
    # Bell plate is deliberately outside the sweep of the door.
    rbox((1.7,0.3,2.0),(5.2,-12.5,3.7),cream,root,bv=0.12)
    button=disc(0.48,0.2,(5.2,-12.8,3.5),plastic('#F4B440',0.25),root,bv=0.08,verts=24)
    button['bt_rescue_bell']=True
    T.text('RESCUE',0.29,(5.2,-12.75,4.35),navy,root,max_w=1.5)
    # Soft beds, a storage shelf and a few bars suggest a shelter without blocking the animals.
    for xx in (-8,8):
        rbox((8,6,0.5),(xx,7,0.7),teal,root,bv=0.2)
        rbox((7,5,0.35),(xx,7,1.0),plastic('#E1EFF0'),root,bv=0.2)
        for k in range(6):rbox((0.12,0.12,4.0),(xx-3.5+k*1.4,10,3.0),navy,root,bv=0.02)
    rbox((6.5,5.5,0.4),(-2,2,0.7),plastic('#87BDD1'),root,bv=0.25)
    rbox((6,5,0.3),(-2,2,1.0),plastic('#DCE9E5'),root,bv=0.25)
    for z in (1.8,4.0,6.2):rbox((5,1.5,0.25),(9,10.5,z),navy,root,bv=0.03)
    for i in range(6):rbox((1.0,0.9,1.6),(7.2+(i%3)*1.6,10.4,2.65+(i//3)*2.2),plastic(('#E0B76C','#E58E92','#8CB8D6')[i%3]),root,bv=0.08)
    for xx in (-8,8):
        rbox((4.5,0.08,2.8),(xx,11.65,6.4),T.mat('#FFE4B5',emit=0.3,key='shelter.window'),root,bv=0.03)
    return {'marks':{'door':(x,y-16,0.25,0),'bell':(x+5.0,y-14,0.25,180),
                    'keeper':(x,y-9,0.45,0),'max_inside':(x-4.5,y-3,0.45,0),
                    'zoe_inside':(x+3.8,y-2,0.45,0),'dog':(x-2.7,y+1.7,0.45,0),
                    'puppy':(x-0.7,y+0.9,0.45,0)},
            'cams':{'outside':((x-17,y-39,13),(x,y-9,5.0),55),
                    'door':((x+5,y-31,5.8),(x,y-12,3.9),48),
                    'inside':((x-7,y-8.5,6.8),(x-1.5,y+2,2.0),50),
                    'dogs':((x+0.5,y-7.5,4.3),(x-1.8,y+1.4,1.8),46)}}

def dress(p):
    import anim
    hinge=p.one('bt_shelter_door')
    button=p.one('bt_rescue_bell')
    base=button.location.copy()
    def reset(Tm):
        hinge.rotation_euler.z=0
        button.location=base
    anim.before_each_frame(reset)
    p['door_open']=lambda k:setattr(hinge.rotation_euler,'z',math.radians(95*max(0,min(1,k))))
    p['bell_press']=lambda k:setattr(button.location,'y',base.y+0.11*max(0,min(1,k)))
