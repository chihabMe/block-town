"""Mesh-preserving knee/ankle rig and world-space foot solve for approved locomotion."""
import math
import bpy, bmesh
from mathutils import Vector, Matrix, Quaternion
import town

def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * u * (10 + u * (-15 + 6 * u))

def split_mesh(o, parent, cut, upper, name):
    """Clip in the original joint's coordinate system, preserving printed UVs."""
    n = o.copy()
    n.data = o.data.copy()
    town.COL.objects.link(n)
    for m in list(n.modifiers):
        n.modifiers.remove(m)
    bm = bmesh.new()
    bm.from_mesh(n.data)
    matrix = o.matrix_basis.copy()
    for v in bm.verts:
        v.co = matrix @ v.co
    edges = bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), dist=1e-05, plane_co=(0, 0, cut), plane_no=(0, 0, 1), clear_inner=upper, clear_outer=not upper)['geom_cut']
    border = [e for e in edges if isinstance(e, bmesh.types.BMEdge) and e.is_boundary]
    if border and len(n.data.polygons) > 1:
        bmesh.ops.holes_fill(bm, edges=border, sides=0)
    if not upper:
        for v in bm.verts:
            v.co.z -= cut
    bm.to_mesh(n.data)
    bm.free()
    n.parent = parent
    n.matrix_basis = Matrix.Identity(4)
    n.name = name
    if len(n.data.polygons) > 1:
        mod = n.modifiers.new('joint edge', 'BEVEL')
        mod.width = 0.025
        mod.segments = 2
    return n

def rig(c):
    result = {}
    for side in ('L', 'R'):
        hip = c['leg' + side]
        children = list(hip.children)
        knee = town.empty(c['name'] + '.knee' + side, (0, 0, -0.85), hip)
        ankle = town.empty(c['name'] + '.ankle' + side, (0, 0, -0.85), knee)
        for o in children:
            if o.location.z < -1.7:
                o.parent = ankle
                o.location.z += 1.7
            else:
                split_mesh(o, hip, -0.85, True, o.name + '.thigh')
                split_mesh(o, knee, -0.85, False, o.name + '.shin')
                bpy.data.objects.remove(o, do_unlink=True)
        result[side] = {'hip': hip, 'knee': knee, 'ankle': ankle}
    c['_walking_rig'] = result
    return result

def point_bone(o, end):
    bpy.context.view_layer.update()
    v = o.parent.matrix_world.inverted().to_3x3() @ (Vector(end) - o.matrix_world.translation)
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = v.to_track_quat('-Z', 'Y')

def solve(c, side, target, pitch):
    r = c['_walking_rig'][side]
    bpy.context.view_layer.update()
    H = r['hip'].matrix_world.translation.copy()
    A = Vector(target)
    v = A - H
    d = v.length
    length = 0.85 * c['scale']
    if d > 2 * length + 0.0001:
        raise ValueError(f'Unreachable {side} foot: {d:.4f}')
    direction = v.normalized()
    forward = c['root'].rotation_euler.to_quaternion() @ Vector((0, -1, 0))
    pole = (forward - direction * forward.dot(direction)).normalized()
    K = (H + A) * 0.5 + pole * math.sqrt(max(0.0, length * length - (d * 0.5) ** 2))
    point_bone(r['hip'], K)
    point_bone(r['knee'], A)
    bpy.context.view_layer.update()
    q = c['root'].rotation_euler.to_quaternion() @ Quaternion((1, 0, 0), pitch)
    r['ankle'].rotation_mode = 'QUATERNION'
    r['ankle'].rotation_quaternion = r['knee'].matrix_world.to_quaternion().inverted() @ q
