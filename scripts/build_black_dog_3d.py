"""Build editable, skinned black-dog assets with Blender's bundled Python.

Run: blender --background --factory-startup --python scripts/build_black_dog_3d.py
All paths are relative to this repository. No external packages or remote assets.
"""
from pathlib import Path
import json
import math
import random
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/models/black_dog'
QA = ROOT / 'docs/design/art/black_dog_3d'
OUT.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)
PALETTE = {'fur': '1B1716', 'warm': '3A2A24', 'iris': '5A3D2A',
           'reflection': '7FB6D8', 'cream': 'E9DDC9', 'ink': '0E0D0D'}
random.seed(41)


def linear(h):
    vals = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055)**2.4 for v in vals) + (1,)


def material(name, hex_color, roughness=.8, vertex=False):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = linear(hex_color)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = linear(hex_color)
    shader.inputs['Roughness'].default_value = roughness
    if vertex:
        attr = mat.node_tree.nodes.new('ShaderNodeVertexColor')
        attr.layer_name = 'Color'
        mat.node_tree.links.new(attr.outputs['Color'], shader.inputs['Base Color'])
    mat['srgb_hex'] = '#' + hex_color
    return mat


def active(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def smooth(obj):
    for face in obj.data.polygons:
        face.use_smooth = True


def ellipsoid(name, center, scale, mat=None, segments=20, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    smooth(obj)
    return obj


def tube(name, points, radii, mat, sides=10):
    """Parallel-frame tapered closed volume, used for ears, tail and fur locks."""
    points = [Vector(p) for p in points]
    verts, faces = [], []
    for i, (p, radius) in enumerate(zip(points, radii)):
        tangent = (points[min(i+1, len(points)-1)] - points[max(0, i-1)]).normalized()
        axis = Vector((1, 0, 0))
        if abs(tangent.dot(axis)) > .93:
            axis = Vector((0, 1, 0))
        u = (axis - tangent * tangent.dot(axis)).normalized()
        v = tangent.cross(u).normalized()
        rx, ry = radius if isinstance(radius, tuple) else (radius, radius)
        for j in range(sides):
            a = 2 * math.pi * j / sides
            verts.append(p + u * rx * math.cos(a) + v * ry * math.sin(a))
        if i:
            for j in range(sides):
                a = (i-1) * sides + j
                b = (i-1) * sides + (j+1) % sides
                faces.append((a, b, i*sides+(j+1)%sides, i*sides+j))
    faces.extend([tuple(reversed(range(sides))), tuple((len(points)-1)*sides+j for j in range(sides))])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    smooth(obj)
    return obj


def rigid(obj, bone):
    obj.vertex_groups.new(name=bone).add(list(range(len(obj.data.vertices))), 1., 'REPLACE')


def chain_weights(obj, names):
    # Each ring is assigned two neighboring bones; the tips follow their terminal bone.
    count = len(obj.data.vertices)
    groups = [obj.vertex_groups.new(name=name) for name in names]
    for vert in obj.data.vertices:
        t = vert.index / max(1, count-1) * (len(names)-1)
        lo = min(len(names)-1, int(t))
        hi = min(len(names)-1, lo+1)
        f = t-lo
        if hi == lo:
            groups[lo].add([vert.index], 1., 'REPLACE')
        else:
            groups[lo].add([vert.index], 1-f, 'REPLACE')
            if f > 0:
                groups[hi].add([vert.index], f, 'REPLACE')


def colorize(obj, callback):
    layer = obj.data.color_attributes.new(name='Color', type='FLOAT_COLOR', domain='POINT')
    obj.data.color_attributes.active_color = layer
    for v in obj.data.vertices:
        layer.data[v.index].color = callback(obj.matrix_world @ v.co)


def make_dog(stage):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)
    puppy = stage == 'puppy'
    mat = {k: material(k + '_' + stage, value, .17 if k in ('iris', 'ink') else .82)
           for k, value in PALETTE.items()}
    mat['coat'] = material('CoatVertexPalette', PALETTE['fur'], .9, True)
    if puppy:
        body_pos, body_scale = (0, .10, .34), (.205, .315, .225)
        head_pos, head_scale = (0, -.265, .615), (.235, .202, .213)
        hip_y, front_y, leg_x, joint_z, paw_z = .31, -.14, .135, .15, .055
    else:
        body_pos, body_scale = (0, .13, .63), (.265, .55, .295)
        head_pos, head_scale = (0, -.49, .96), (.262, .25, .247)
        hip_y, front_y, leg_x, joint_z, paw_z = .49, -.26, .177, .26, .073
    H, HS = Vector(head_pos), Vector(head_scale)
    B, BS = Vector(body_pos), Vector(body_scale)
    unit = HS.x / .235
    parts = [ellipsoid('Trunk', B, BS)]
    parts.append(ellipsoid('Chest', (0, front_y, B.z+.075), (BS.x*.94, BS.x*1.10, BS.z*1.16)))
    parts.append(ellipsoid('Neck', (0, H.y+.07, H.z-.13), (HS.x*.70, HS.y*.80, HS.z*.96)))
    parts.append(ellipsoid('Head', H, HS, segments=32, rings=24))
    muzzle = H + Vector((0, -HS.y*.78, -HS.z*.34))
    muzzle_scale = (.139*unit, (.122 if puppy else .20)*unit, .096*unit)
    parts.append(ellipsoid('Muzzle', muzzle, muzzle_scale))
    for sign in (-1, 1):
        parts.append(ellipsoid('Cheek', H + Vector((sign*HS.x*.54, -HS.y*.56, -HS.z*.20)),
                               (HS.x*.52, HS.y*.57, HS.z*.55)))
        for i in range(5):
            a = i/4
            p = H+Vector((sign*HS.x*(.73+.14*math.sin(a*math.pi)), -.035,
                          HS.z*(-.25-.44*a)))
            tuft = ellipsoid('SoftCheekFur', p, (.044*unit,.077*unit,.068*unit))
            tuft.rotation_euler.y = sign*-.35
            parts.append(tuft)
        for i in range(4):
            p = H+Vector((sign*HS.x*(.12+.16*i), .035, HS.z*(.95-.042*i*i)))
            parts.append(ellipsoid('SoftCrownFur',p,(.045*unit,.078*unit,.045*unit)))
    joints = {}
    for end, y in [('front', front_y), ('hind', hip_y)]:
        for side, sign in [('L', 1), ('R', -1)]:
            x = sign * leg_x
            shoulder = Vector((x, y, B.z + (.07 if end == 'front' else .02)))
            knee = Vector((x, y + (.038 if end == 'front' else -.085), joint_z+.065))
            ankle = Vector((x, y + (.014 if end == 'front' else .047), paw_z*1.6))
            toe = Vector((x, y-.055, paw_z))
            joints[end+'.'+side] = (shoulder, knee, ankle, toe)
            leg_r = (.080 if puppy else .092)
            parts.append(tube('LegVolume', [shoulder, shoulder.lerp(knee, .5), knee, ankle],
                              [leg_r*1.17, leg_r, leg_r*.75, leg_r*.64], mat['fur'], 16))
            parts.append(ellipsoid('PawVolume', toe, (leg_r*.94, leg_r*1.22, paw_z)))
    active(parts[0])
    for p in parts:
        p.select_set(True)
    bpy.ops.object.join()
    body = bpy.context.object
    body.name = 'BlackDog_' + stage + '_Mesh'
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    mod = body.modifiers.new('ContinuousSurface', 'REMESH')
    mod.mode = 'VOXEL'
    mod.voxel_size = .009 if puppy else .013
    mod.use_smooth_shade = True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mod = body.modifiers.new('RelaxSurface', 'SMOOTH')
    mod.factor, mod.iterations = 1.1, 5
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mod = body.modifiers.new('GameTopology', 'DECIMATE')
    mod.ratio = .24
    bpy.ops.object.modifier_apply(modifier=mod.name)
    body.data.materials.clear()
    body.data.materials.append(mat['coat'])
    smooth(body)

    def coat(p):
        # Markings are part of the skinned vertex colors, with no floating chest decal.
        chin = p.y < muzzle.y-.025*unit and abs(p.x) < .085*unit and muzzle.z-.09*unit < p.z < muzzle.z-.035*unit
        bib_top = H.z - HS.z*.73
        bib_bottom = B.z - BS.z*.44
        t = (p.z-bib_bottom) / max(.01, bib_top-bib_bottom)
        width = (.023 + .057*math.sin(math.pi*max(0., min(1., t))*.8)) * unit
        bib = 0 < t < 1 and abs(p.x) < width and p.y < front_y-.128*unit
        if chin or bib:
            return linear(PALETTE['cream'])
        base, high = linear(PALETTE['fur']), linear(PALETTE['warm'])
        noise = .12 + .035 * math.sin(p.z*115 + math.sin(p.x*93)*1.8 + p.y*18)
        return tuple(base[i]*(1-noise)+high[i]*noise for i in range(3)) + (1,)

    colorize(body, coat)
    armdata = bpy.data.armatures.new('BlackDogSkeleton')
    rig = bpy.data.objects.new('BlackDogRig', armdata)
    bpy.context.collection.objects.link(rig)
    rig.show_in_front = True
    active(rig)
    bpy.ops.object.mode_set(mode='EDIT')

    def bone(name, a, b, parent=None):
        eb = armdata.edit_bones.new(name)
        eb.head, eb.tail = a, b
        if parent:
            eb.parent = armdata.edit_bones[parent]
        return eb

    bone('root', (0, 0, 0), (0, 0, .10))
    bone('pelvis', (0, hip_y, B.z), (0, hip_y-.13, B.z+.025), 'root')
    bone('spine', (0, hip_y-.13, B.z+.025), (0, front_y+.1, B.z+.045), 'pelvis')
    bone('chest', (0, front_y+.1, B.z+.045), (0, front_y-.04, B.z+.12), 'spine')
    bone('neck', (0, front_y-.04, B.z+.12), H, 'chest')
    bone('head', H, H+Vector((0, -.16*unit, .01)), 'neck')
    bone('jaw', H+Vector((0, -.07*unit, -.085*unit)),
         muzzle+Vector((0, -.055*unit, -.06*unit)), 'head')
    for key, (a, b, c, d) in joints.items():
        bone(key+'.upper', a, b, 'chest' if key.startswith('front') else 'pelvis')
        bone(key+'.lower', b, c, key+'.upper')
        bone(key+'.paw', c, d, key+'.lower')
    ear_points = {}
    for side, sign in [('L', 1), ('R', -1)]:
        pts = [H + Vector((sign*HS.x*.77, -.015, HS.z*.57)),
               H + Vector((sign*HS.x*1.13, -.025, HS.z*.28)),
               H + Vector((sign*HS.x*1.24, -.075, -HS.z*.14)),
               H + Vector((sign*HS.x*1.10, -.10, -HS.z*.54))]
        ear_points[side] = pts
        bone('ear.'+side+'.base', pts[0], pts[1].lerp(pts[2], .3), 'head')
        bone('ear.'+side+'.tip', pts[1].lerp(pts[2], .3), pts[3], 'ear.'+side+'.base')
    tail_scale = 1. if puppy else 1.43
    tail_start = Vector((0, B.y+BS.y*.83, B.z+BS.z*.38))
    offsets = [(0,0,0), (0,.090,.045), (0,.165,.12), (0,.155,.245),
               (0,.063,.300), (0,-.020,.270), (0,-.037,.205)]
    tail_points = [tail_start+Vector(o)*tail_scale for o in offsets]
    for i in range(6):
        bone('tail.%02d'%i, tail_points[i], tail_points[i+1], 'pelvis' if i == 0 else 'tail.%02d'%(i-1))
    bpy.ops.object.mode_set(mode='OBJECT')
    # Heat weights are computed on a single continuous body volume.
    active(body)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    if not body.vertex_groups or any(not v.groups for v in body.data.vertices):
        raise RuntimeError('Automatic body skinning failed; refusing to export unweighted mesh')
    active(body)
    bpy.ops.object.vertex_group_limit_total(limit=4)
    bpy.ops.object.vertex_group_normalize_all(lock_active=False)
    extras = []
    for side, pts in ear_points.items():
        ear = tube('FloppyEar.'+side, pts, [(.060*unit,.035*unit),(.098*unit,.052*unit),
                   (.100*unit,.049*unit),(.025*unit,.026*unit)], mat['fur'], 16)
        chain_weights(ear, ['ear.'+side+'.base', 'ear.'+side+'.tip'])
        active(ear)
        sub = ear.modifiers.new('RoundedEar', 'SUBSURF')
        sub.levels = 2
        bpy.ops.object.modifier_apply(modifier=sub.name)
        extras.append(ear)
    tail = tube('CurledTail', tail_points, [v*tail_scale for v in (.077,.085,.080,.067,.052,.032,.004)], mat['fur'], 14)
    chain_weights(tail, ['tail.%02d'%i for i in range(6)])
    active(tail)
    sub = tail.modifiers.new('SoftCurledTail', 'SUBSURF')
    sub.levels = 2
    bpy.ops.object.modifier_apply(modifier=sub.name)
    extras.append(tail)
    # Eyes are recessed into the head with dark lids, small iris and corneal highlights.
    eye_z = H.z + HS.z*.045
    eye_y = H.y - HS.y*1.01
    eye_x = HS.x*.49
    eye_r = (.064 if puppy else .061)*unit
    for side, sign in [('L', 1), ('R', -1)]:
        center = Vector((sign*eye_x, eye_y, eye_z))
        for name, pos, scl, material_key in [
            ('EyeLid', center+Vector((0,.008,0)), (eye_r*1.22, eye_r*.70, eye_r*1.20), 'fur'),
            ('Eye', center+Vector((0,-.008,0)), (eye_r, eye_r*.64, eye_r*1.04), 'ink'),
            ('Iris', center+Vector((0,-eye_r*.59,0)), (eye_r*.75, eye_r*.16, eye_r*.85), 'iris'),
            ('Pupil', center+Vector((0,-eye_r*.74,0)), (eye_r*.59, eye_r*.075, eye_r*.74), 'ink'),
            ('Glint', center+Vector((-.017*unit,-eye_r*.90,.023*unit)), (eye_r*.17, eye_r*.055, eye_r*.18), 'cream'),
            ('Reflection', center+Vector((.017*unit,-eye_r*.87,-.022*unit)), (eye_r*.095, eye_r*.04, eye_r*.09), 'reflection')]:
            obj = ellipsoid(name+'.'+side, pos, scl, mat[material_key], 16, 12)
            rigid(obj, 'head')
            extras.append(obj)
    nose_pos = muzzle + Vector((0, -muzzle_scale[1]*.85, .017*unit))
    nose = ellipsoid('Nose', nose_pos, (.052*unit, .034*unit, .033*unit), mat['ink'])
    # A subtly tapered nose reads as canine rather than a sphere.
    for v in nose.data.vertices:
        v.co.x *= .80 + .22*(v.co.z/(.033*unit))
    rigid(nose, 'head')
    extras.append(nose)
    jaw = ellipsoid('LowerJaw', muzzle+Vector((0,-.005,-.058*unit)),
                    (.102*unit,.065*unit,.029*unit), mat['cream'])
    rigid(jaw, 'jaw')
    extras.append(jaw)
    # Sculpted locks give the silhouette soft fur without expensive hair particles.
    def lock(pos, direction, radius, length, bone_name, shade='fur'):
        p = Vector(pos)
        d = Vector(direction).normalized()
        # Short tapered rounded locks lie along the coat instead of forming spikes.
        length *= .70
        obj = tube('FurLock', [p, p+d*length*.20, p+d*length*.64, p+d*length],
                   [radius*.55, radius*.65, radius*.38, .0018], mat[shade], 7)
        rigid(obj, bone_name)
        active(obj)
        sub = obj.modifiers.new('RoundFur', 'SUBSURF')
        sub.levels = 1
        bpy.ops.object.modifier_apply(modifier=sub.name)
        extras.append(obj)

    for sign in (-1, 1):
        for i in range(5):
            a = i/4
            p = H+Vector((sign*HS.x*(.82-.17*a), -.045+.04*a, HS.z*(-.26-.57*a)))
            lock(p, (sign*.28,.05,-1), .023*unit, .062*unit, 'head')
        for i in range(4):
            a = i/3
            p = Vector((sign*BS.x*.88, B.y-BS.y*.6+BS.y*1.4*a, B.z-BS.z*.31))
            owner = 'chest' if a < .22 else ('spine' if a < .64 else 'pelvis')
            lock(p, (sign*.10,.65,-.7), .030*unit, .075*unit, owner)
        pts = ear_points['L' if sign>0 else 'R']
        for i in range(4):
            p = pts[1].lerp(pts[3], i/4) + Vector((sign*.039*unit,0,0))
            lock(p, (sign*.25,0,-1), .018*unit, .048*unit,
                 'ear.'+('L' if sign>0 else 'R')+('.base' if i<3 else '.tip'))
    for i in range(5):
        p = Vector((0, front_y-.17*unit, H.z-HS.z*.95-i*.026*unit))
        lock(p, ((i%3-1)*.23,-.12,-1), (.036-i*.004)*unit, .07*unit, 'neck' if i<2 else 'chest', 'cream')
    for i in range(10):
        segment = min(4, i//2)
        p = tail_points[segment].lerp(tail_points[segment+1], .35)
        a = i*2.399
        tangent = (tail_points[segment+1]-tail_points[segment]).normalized()
        radial = Vector((math.cos(a),math.sin(a)*.6,0))
        p += radial*(.045*tail_scale)
        lock(p, tangent+radial*.18, .029*tail_scale, .075*tail_scale, 'tail.%02d'%segment)
    # Merge accessories into the skinned object, retaining explicit weights/materials.
    active(body)
    for obj in extras:
        obj.select_set(True)
    bpy.ops.object.join()
    # Final simplification retains interpolated skin weights and vertex markings.
    reduction = body.modifiers.new('RuntimeBudget', 'DECIMATE')
    reduction.ratio = .67
    bpy.ops.object.modifier_apply(modifier=reduction.name)
    # Vertices added from non-painted accessories need neutral color in glTF COLOR_0.
    colors = body.data.color_attributes.get('Color')
    for v in body.data.vertices:
        if colors.data[v.index].color[3] < .5:
            colors.data[v.index].color = (1,1,1,1)
    body.parent = rig
    body.modifiers.clear()
    arm = body.modifiers.new('Skin', 'ARMATURE')
    arm.object = rig
    active(body)
    bpy.ops.object.vertex_group_limit_total(limit=4)
    bpy.ops.object.vertex_group_normalize_all(lock_active=False)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15192, island_margin=.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    physical_scale = .40 if puppy else .58
    for v in body.data.vertices:
        v.co *= physical_scale
    active(rig)
    bpy.ops.object.mode_set(mode='EDIT')
    for eb in rig.data.edit_bones:
        eb.head *= physical_scale
        eb.tail *= physical_scale
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in rig.pose.bones:
        pb.rotation_mode = 'XYZ'
    rig['character_stage'] = stage
    rig['forward_blender'] = '-Y'
    rig['units'] = 'meters'
    rig['palette'] = json.dumps(PALETTE)
    rig['rig_usage'] = 'FK deform bones; root for placement. Separate stage-specific bind pose.'

    # Two small loop clips make the binding immediately testable in-engine.
    for clip in ('Idle', 'TailWag'):
        rig.animation_data_create()
        action = bpy.data.actions.new(clip)
        rig.animation_data.action = action
        for frame in range(1, 62, 3):
            t = (frame-1)/60 * 2*math.pi
            for pb in rig.pose.bones:
                pb.rotation_euler = (0,0,0)
                pb.location = (0,0,0)
            rig.pose.bones['neck'].rotation_euler.x = .012*math.sin(t)
            rig.pose.bones['head'].rotation_euler.y = .025*math.sin(t)
            for side in ('L','R'):
                rig.pose.bones['ear.'+side+'.tip'].rotation_euler.x = .04*math.sin(t+.3)
            for i in range(6):
                rig.pose.bones['tail.%02d'%i].rotation_euler.x = (.09 if clip=='Idle' else .23)*math.sin((1 if clip=='Idle' else 3)*t-i*.33)
            for pb in rig.pose.bones:
                pb.keyframe_insert('rotation_euler', frame=frame, group=pb.name)
        track = rig.animation_data.nla_tracks.new()
        track.name = clip
        track.strips.new(clip, 1, action)
        track.mute = True
        rig.animation_data.action = None
    for pb in rig.pose.bones:
        pb.rotation_euler = (0,0,0)
    bpy.context.scene.frame_start, bpy.context.scene.frame_end = 1, 61
    bpy.context.scene.render.fps = 30
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1
    bpy.context.view_layer.update()
    return rig, body


def validate(rig, body, stage):
    body.data.calc_loop_triangles()
    unweighted = []
    badsum = []
    max_weights = 0
    for v in body.data.vertices:
        groups = [g for g in v.groups if g.weight > 1e-6]
        max_weights = max(max_weights, len(groups))
        if not groups:
            unweighted.append(v.index)
        if abs(sum(g.weight for g in groups)-1) > 1e-4:
            badsum.append(v.index)
    report = {'stage':stage, 'vertices':len(body.data.vertices), 'triangles':len(body.data.loop_triangles),
              'bones':len(rig.data.bones), 'max_weights':max_weights, 'unweighted':len(unweighted),
              'bad_weight_sums':len(badsum), 'materials':len(body.data.materials),
              'uv_layers':len(body.data.uv_layers), 'actions':[t.name for t in rig.animation_data.nla_tracks],
              'height_m':round(body.dimensions.z,4)}
    assert not unweighted and not badsum and max_weights<=4, report
    # Exercise all important joints and verify evaluated geometry remains finite.
    poses = {'head':(0,.22,0), 'jaw':(.16,0,0), 'front.L.lower':(.4,0,0),
             'hind.R.lower':(-.3,0,0), 'ear.L.tip':(.18,0,.15),'tail.00':(.32,0,0)}
    for name, rotation in poses.items():
        rig.pose.bones[name].rotation_euler = rotation
    bpy.context.view_layer.update()
    evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    test = evaluated.to_mesh()
    assert all(math.isfinite(c) for v in test.vertices for c in v.co)
    report['pose_test_finite'] = True
    evaluated.to_mesh_clear()
    for pb in rig.pose.bones:
        pb.rotation_euler = (0,0,0)
    bpy.context.view_layer.update()
    (QA/(stage+'_mesh_validation.json')).write_text(json.dumps(report,indent=2),encoding='utf8')
    print('VALIDATION', json.dumps(report), flush=True)
    return report


def look_at(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()


def studio(stage, rig, body):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.world.color = (.22,.22,.22)
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = -.6
    world = scene.world
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs[0].default_value = (.38,.43,.50,1)
    world.node_tree.nodes['Background'].inputs[1].default_value = .5
    ground_mat = material('StudioPaper', 'E7DECC')
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,-.006))
    ground = bpy.context.object
    ground.name = 'StudioGround'
    ground.data.materials.append(ground_mat)
    for name, position, power, size, color in [
        ('Key',(-2,-3,4),450,3.,(1,.88,.74)),
        ('Fill',(3,-2,2),220,3.,(.73,.85,1)),
        ('Rim',(1,3,3),600,2.,(1,.88,.67))]:
        data = bpy.data.lights.new(name,'AREA')
        data.energy, data.shape, data.size, data.color = power,'DISK',size,color
        light = bpy.data.objects.new(name,data)
        scene.collection.objects.link(light)
        light.location = position
        look_at(light,(0,0,.5))
    data = bpy.data.cameras.new('PreviewCamera')
    camera = bpy.data.objects.new('PreviewCamera',data)
    scene.collection.objects.link(camera)
    data.type = 'ORTHO'
    scene.camera = camera
    height = body.dimensions.z
    data.ortho_scale = height*1.65
    camera.location = (1.7,-2.8,1.25 if stage=='puppy' else 1.8)
    look_at(camera,(0,.06,height*.49))
    scene.render.resolution_x, scene.render.resolution_y = 1000,1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(QA/(stage+'_beauty.png'))
    bpy.ops.render.render(write_still=True)
    for label, pos in [('front',(0,-4,height*.52)), ('side',(4,0,height*.52)), ('back',(0,4,height*.52))]:
        camera.location = pos
        look_at(camera,(0,0,height*.52))
        scene.render.resolution_x, scene.render.resolution_y = 800,800
        scene.render.filepath = str(QA/(stage+'_'+label+'.png'))
        bpy.ops.render.render(write_still=True)
    camera.location = (1.7,-2.8,1.25 if stage=='puppy' else 1.8)
    look_at(camera,(0,.06,height*.49))
    rig.pose.bones['head'].rotation_euler.y = .20
    rig.pose.bones['front.L.upper'].rotation_euler.x = -.30
    rig.pose.bones['front.L.lower'].rotation_euler.x = .48
    rig.pose.bones['ear.L.tip'].rotation_euler.x = .20
    rig.pose.bones['tail.00'].rotation_euler.x = .28
    scene.render.filepath = str(QA/(stage+'_pose_check.png'))
    bpy.ops.render.render(write_still=True)
    for pb in rig.pose.bones:
        pb.rotation_euler = (0,0,0)
    for area in bpy.context.screen.areas if bpy.context.screen else []:
        if area.type == 'VIEW_3D':
            area.spaces.active.region_3d.view_distance = height*2.8
            area.spaces.active.region_3d.view_location = (0,0,height*.5)
    active(rig)
    bpy.context.preferences.filepaths.save_version = 0
    source_dir = ROOT / 'art_source/black_dog'
    source_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(source_dir/(stage+'_black_dog_v01.blend')))


def main():
    for stage in ('puppy','adult'):
        print('BUILD',stage,flush=True)
        rig, body = make_dog(stage)
        validate(rig,body,stage)
        active(rig)
        body.select_set(True)
        # One strip per track exports independently; constraints/modifiers are baked to glTF.
        for track in rig.animation_data.nla_tracks:
            track.mute = False
        bpy.ops.export_scene.gltf(filepath=str(OUT/(stage+'_black_dog_v01.glb')),
            export_format='GLB', use_selection=True, export_animations=True,
            export_animation_mode='NLA_TRACKS', export_apply=False,
            export_yup=True, export_skins=True, export_all_influences=False,
            export_def_bones=True, export_materials='EXPORT', export_extras=True)
        for track in rig.animation_data.nla_tracks:
            track.mute = True
        for pb in rig.pose.bones:
            pb.rotation_euler = (0,0,0)
        studio(stage,rig,body)


if __name__ == '__main__':
    main()
