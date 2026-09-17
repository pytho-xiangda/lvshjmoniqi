"""Revise adult V02 into a long-coated game dog; preserve the 29-bone contract.

Run only in an isolated Blender process. V02 files remain untouched.
"""
from pathlib import Path
import sys
import json
import math
import random
import bpy
import bmesh
from mathutils import Vector
from mathutils.kdtree import KDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_black_dog_3d as u
import build_black_dog_v02 as v2

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/models/black_dog/v03'
SOURCE = ROOT / 'art_source/black_dog/v03'
QA = ROOT / 'docs/design/art/black_dog_3d/v03'
for folder in (OUT, SOURCE, QA):
    folder.mkdir(parents=True, exist_ok=True)
TARGET = Vector((.427, .972, .733))
H0 = Vector((0, -.264, .570))
LEG_TOP = .3378
LEG_SCALE = .79
DROP = LEG_TOP * (1-LEG_SCALE)
H = H0 - Vector((0, 0, DROP)) + Vector((0, .025, 0))
COUNTS = {}


def clamp(value):
    return max(0., min(1., value))


def morph(p, head_factor=None):
    p = Vector(p)
    h = clamp((p.z-.415)/.10) if head_factor is None else head_factor
    q = Vector((p.x, p.y, p.z*LEG_SCALE if p.z < LEG_TOP else p.z-DROP))
    h_pivot = H0-Vector((0, 0, DROP))
    enlarged = h_pivot+(q-h_pivot)*1.18+Vector((0, .025, 0))
    return q.lerp(enlarged, h)


def load_base():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    path = ROOT/'art_source/black_dog/v02/adult_black_dog_v02.blend'
    with bpy.data.libraries.load(str(path), link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n in ('BlackDogRigV02', 'BlackDog_adult_V02')]
    for ob in dst.objects:
        bpy.context.collection.objects.link(ob)
    rig = next(o for o in dst.objects if o.type == 'ARMATURE')
    body = next(o for o in dst.objects if o.type == 'MESH')
    rig.name, body.name = 'BlackDogRigV03', 'BlackDog_adult_V03'
    contract = [(b.name, b.parent.name if b.parent else None) for b in rig.data.bones]
    old_rest = {b.name:(b.head_local.copy(), b.tail_local.copy()) for b in rig.data.bones}
    for track in rig.animation_data.nla_tracks:
        track.mute = True
        for strip in track.strips:
            strip.influence = 1.0
    rig.animation_data.action = None
    for pb in rig.pose.bones:
        pb.rotation_euler = (0, 0, 0)
    body.modifiers.clear()
    # Keep only the connected anatomical body. Replace V02 ears, eyes, tail and
    # micro-hair islands instead of piling new geometry over them.
    bm = bmesh.new()
    bm.from_mesh(body.data)
    unseen = set(bm.verts)
    components = []
    while unseen:
        seed = unseen.pop()
        part, stack = {seed}, [seed]
        while stack:
            for edge in stack.pop().link_edges:
                for vertex in edge.verts:
                    if vertex in unseen:
                        unseen.remove(vertex)
                        part.add(vertex)
                        stack.append(vertex)
        components.append(part)
    keep = max(components, key=len)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v not in keep], context='VERTS')
    bm.to_mesh(body.data)
    bm.free()
    for vertex in body.data.vertices:
        vertex.co = morph(vertex.co)
        # Broaden the leg shafts without moving the paw contact points.
        if vertex.co.z < .245:
            sign = 1 if vertex.co.x >= 0 else -1
            axis_x = sign*.0942
            factor = 1.42 if vertex.co.z > .075 else 1.16
            vertex.co.x = axis_x+(vertex.co.x-axis_x)*factor
    body.data.materials.clear()
    for color in list(body.data.color_attributes):
        body.data.color_attributes.remove(color)
    for uv in list(body.data.uv_layers):
        body.data.uv_layers.remove(uv)
    u.active(rig)
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in rig.data.edit_bones:
        for end in ('head', 'tail'):
            p = getattr(bone, end).copy()
            head_factor = 1. if bone.name in ('head', 'jaw') or bone.name.startswith('ear.') else None
            setattr(bone, end, morph(p, head_factor))
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.update()
    return rig, body, contract, old_rest


def bind_near(obj, reference, kd):
    for group in reference.vertex_groups:
        obj.vertex_groups.new(name=group.name)
    for vert in obj.data.vertices:
        _, index, _ = kd.find(obj.matrix_world @ vert.co)
        for g in reference.data.vertices[index].groups:
            if g.weight > 0:
                obj.vertex_groups[g.group].add([vert.index], g.weight, 'REPLACE')


def clump(name, p, direction, normal, width, length, mat, reference=None, kd=None, bone=None):
    """A broad buried root, rounded ridge and tapered tip: a solid fur lock."""
    p, d, n = Vector(p), Vector(direction).normalized(), Vector(normal).normalized()
    length *= .72
    width *= .90
    d = (d-n*d.dot(n)*.65).normalized()
    across = n.cross(d).normalized()
    if across.length < .5:
        across = Vector((1, 0, 0))
    lift = d.cross(across).normalized()
    if lift.dot(n) < 0:
        lift.negate()
    # Flattened elliptical cross-sections avoid round cone/spike silhouettes.
    centers = [p-n*.013, p+d*length*.15-n*.003,
               p+d*length*.48+n*.006, p+d*length*.80+n*.009,
               p+d*length+n*.003]
    widths = [width*.65, width, width*.78, width*.37, .0007]
    depths = [.003, width*.20, width*.19, width*.12, .0005]
    verts, faces = [], []
    sides = 8
    for i, center in enumerate(centers):
        for j in range(sides):
            angle = math.tau*j/sides
            ridge = 1+.09*math.cos(angle*3+i*.4)
            verts.append(center+across*math.cos(angle)*widths[i]*ridge+lift*math.sin(angle)*depths[i])
        if i:
            for j in range(sides):
                a=(i-1)*sides+j;b=(i-1)*sides+(j+1)%sides
                faces.append((a,b,i*sides+(j+1)%sides,i*sides+j))
    faces += [tuple(reversed(range(sides))), tuple(4*sides+j for j in range(sides))]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces);mesh.update()
    ob = bpy.data.objects.new(name, mesh);bpy.context.collection.objects.link(ob)
    mesh.materials.append(mat);u.smooth(ob)
    if bone:
        u.rigid(ob, bone)
    else:
        bind_near(ob, reference, kd)
    COUNTS[name] = COUNTS.get(name, 0)+1
    return ob


def make():
    random.seed(713)
    rig, body, contract, old_rest = load_base()
    dark = u.material('Long coat dark', '1B1716', .90)
    mid = u.material('Long coat mid', '3A2A24', .90)
    bright = u.material('Long coat highlights', '5A3D2A', .92)
    white = u.material('Long ivory bib', 'E9DDC9', .90)
    blue = u.material('Blue iris', '7FB6D8', .27)
    ink = u.material('Nose leather and pupil', '0E0D0D', .31)
    glint = u.material('Eye catchlight', 'FFFFFF', .30)
    painted = u.material('Body vertex paint', '1B1716', .90, True)
    def coat(p):
        shifted_z=p.z+(DROP-LEG_TOP*.15)
        t = clamp((shifted_z-.195)/.275)
        width = .078*math.sin(math.pi*t*.82)+.017
        boundary = width-abs(p.x)+.003*math.sin(p.z*230+p.x*70)
        f = clamp(boundary/.012)*clamp((shifted_z-.195)/.018)*clamp((.475-shifted_z)/.025)*clamp((-p.y-.165)/.025)
        deep,medium=u.linear('1B1716'),u.linear('3A2A24')
        warmth=.18+.12*math.sin(p.y*22+p.z*17)*math.sin(p.x*31)
        a=tuple(deep[i]*(1-warmth)+medium[i]*warmth for i in range(3))
        b=u.linear('E9DDC9')
        return tuple(a[i]*(1-f)+b[i]*f for i in range(3))+(1,)
    body.data.materials.append(painted)
    for p in body.data.polygons:p.material_index=0
    u.colorize(body, coat)
    kd = KDTree(len(body.data.vertices))
    for vertex in body.data.vertices:kd.insert(vertex.co,vertex.index)
    kd.balance()
    extra=[]
    def front(x,z):
        hit, p, normal, _ = body.ray_cast(Vector((x,-1.5,z)), Vector((0,1,0)))
        if not hit:raise RuntimeError('Body ray missed: '+str((x,z)))
        return p,normal
    # Cheek ruff and crown: explicitly staggered long locks change the silhouette.
    for sign in (-1,1):
        for row in range(4):
            for col in range(3):
                x=sign*(.120+.012*col-.006*row)
                z=H.z+.054-row*.043
                p,n=front(x,z)
                extra.append(clump('Cheek',p,(sign*.70,.10,-.70),n,.020,.060+row*.007,
                                   dark if col!=1 else mid,bone='head'))
        for i in range(5):
            p=Vector((sign*(.020+i*.021), H.y+.015, H.z+.163-i*.009))
            extra.append(clump('Crown',p,(sign*.20,.95,.05),(sign*.3,-.1,1),.023,.037,
                               dark,bone='head'))
    for z in [H.z+.106,H.z+.137]:
        for i in range(7):
            x=(i-3)*(.025 if z>H.z+.12 else .036)
            p,n=front(x,z)
            extra.append(clump('Forehead',p,(x*.6,.35,.35),n,.014,.027,dark,bone='head'))
    # Broad hanging leaf ears; their long axis is vertical, not a small round disc.
    ears={}
    for side,sign in [('L',1),('R',-1)]:
        pts=[Vector((sign*.123,H.y+.012,H.z+.125)),
             Vector((sign*.167,H.y-.004,H.z+.089)),
             Vector((sign*.178,H.y-.024,H.z+.013)),
             Vector((sign*.163,H.y-.036,H.z-.079)),
             Vector((sign*.147,H.y-.047,H.z-.142))]
        ears[side]=pts
        ear=u.tube('Large hanging ear '+side,pts,[(.038,.023),(.067,.030),(.064,.031),(.044,.024),(.003,.003)],dark,16)
        u.chain_weights(ear,['ear.'+side+'.base','ear.'+side+'.tip'])
        u.active(ear);sub=ear.modifiers.new('Soft ear fold','SUBSURF');sub.levels=1
        bpy.ops.object.modifier_apply(modifier=sub.name);extra.append(ear)
        for row in range(4):
            for col in range(4):
                t=(row+.35)/4
                center=pts[1].lerp(pts[4],t)
                hit,p,n,_=ear.ray_cast(Vector((center.x+(col-1.5)*.019,-1.5,center.z)),Vector((0,1,0)))
                if not hit:continue
                extra.append(clump('Ear fringe',p,(sign*.17,-.08,-1),n,.020,.069,
                                   dark if (row+col)%3 else mid,bone='ear.'+side+('.base' if row==0 else '.tip')))
        for edge_sign in (-1,1):
            for row in range(6):
                t=(row+.4)/6
                center=pts[1].lerp(pts[4],t)
                n=Vector((edge_sign,0,0))
                hit,p,n,_=ear.ray_cast(center+Vector((edge_sign*.3,0,0)),Vector((-edge_sign,0,0)))
                if hit:
                    extra.append(clump('Ear edge',p,(edge_sign*.45,0,-1),n,.018,.060,
                                       dark,bone='ear.'+side+('.base' if row<2 else '.tip')))
        u.active(rig);bpy.ops.object.mode_set(mode='EDIT')
        rig.data.edit_bones['ear.'+side+'.base'].head=pts[0]
        rig.data.edit_bones['ear.'+side+'.base'].tail=pts[2]
        rig.data.edit_bones['ear.'+side+'.tip'].head=pts[2]
        rig.data.edit_bones['ear.'+side+'.tip'].tail=pts[4]
        bpy.ops.object.mode_set(mode='OBJECT')
    # Large continuous ivory throat/chest ruff with overlapping hanging tips.
    for row,z in enumerate([.454,.419,.384,.349,.314,.279,.244]):
        z-=DROP-LEG_TOP*.15
        span=[.045,.066,.079,.082,.080,.069,.046][row]
        for col in range(5):
            x=span*(col-2)/2
            p,n=front(x,z)
            extra.append(clump('White ruff',p,(x*3,-.15,-1),n,.020 if row<2 else .025,
                               .061 if row<2 else .076,white,reference=body,kd=kd))
    # Body layering follows the back/haunch flow and leaves broad overlapping roots.
    for sign in (-1,1):
        for row,z in enumerate([.398,.351,.305,.260,.215]):
            for col,y in enumerate([-.095,-.035,.035,.105,.175,.245,.303]):
                y+=random.uniform(-.012,.012)
                z+=random.uniform(-.006,.006)
                hit,p,n,_=body.ray_cast(Vector((sign*.7,y,z)),Vector((-sign,0,0)))
                if not hit:continue
                extra.append(clump('Body mantle',p,(sign*.12,.60,-.55),n,.027,.075,
                                   dark if (col+row)%4 else mid,reference=body,kd=kd))
    for i in range(9):
        y=-.06+i*.043
        hit,p,n,_=body.ray_cast(Vector((0,y,1)),Vector((0,0,-1)))
        if hit and p.z<.51:
            for sign in (-1,1):
                extra.append(clump('Back ridge',p+Vector((sign*.025,0,-.003)),(sign*.20,.8,.1),n,.027,.064,
                                   dark,reference=body,kd=kd))
    # Leg feathers cover the ankle; only the rounded paw pads remain exposed.
    for end,y in [('front',-.141),('hind',.282)]:
        for side,sign in [('L',1),('R',-1)]:
            for row,z in enumerate([.220,.166,.112,.072]):
                for angle in [-.65,.35,1.35,2.35,3.35]:
                    axis=Vector((sign*.0942,y,z))
                    normal=Vector((math.cos(angle),math.sin(angle),.12)).normalized()
                    p=axis+normal*(.044 if row<2 else .035)
                    extra.append(clump('Leg feather',p,(normal.x*.30,normal.y*.2,-1),normal,
                                       .023 if row<2 else .018,.066 if row<2 else .043,dark,
                                       reference=body,kd=kd))
    # Keep exactly six articulated tail segments and thicken the root by 2x.
    tp=[morph(old_rest['tail.%02d'%i][0],0) for i in range(6)]+[morph(old_rest['tail.05'][1],0)]
    tp=[p+Vector((0,-.028,0)) for p in tp]
    radii=[r*.60*1.28*2 for r in (.048,.056,.058,.053,.043,.030,.006)]
    tail=u.tube('Thick curled tail',tp,radii,dark,14)
    u.chain_weights(tail,['tail.%02d'%i for i in range(6)])
    u.active(tail);sub=tail.modifiers.new('Soft plume core','SUBSURF');sub.levels=1
    bpy.ops.object.modifier_apply(modifier=sub.name);extra.append(tail)
    for i in range(6):
        d=(tp[i+1]-tp[i]).normalized()
        across=Vector((1,0,0));radial=d.cross(across).normalized()
        for j in range(18):
            angle=math.tau*(j%9)/9+i*.35+(j//9)*.23
            n=across*math.cos(angle)+radial*math.sin(angle)
            center=tp[i].lerp(tp[i+1],.20+(j//9)*.46)
            hit,p,surface_normal,_=tail.ray_cast(center+n*.3,-n)
            if not hit:continue
            extra.append(clump('Tail plume',p,d*.95+n*.12,surface_normal,.022 if i<4 else .017,
                               .070 if i<4 else .047,dark if j%4 else mid,bone='tail.%02d'%i))
    u.active(rig);bpy.ops.object.mode_set(mode='EDIT')
    for i in range(6):
        b=rig.data.edit_bones['tail.%02d'%i];b.head=tp[i];b.tail=tp[i+1]
    bpy.ops.object.mode_set(mode='OBJECT')
    # Unite the coat volumes before adding facial features. The broad roots are
    # continuous skin; the sculpted silhouette survives in an untextured render.
    u.active(body)
    for obj in extra:obj.select_set(True)
    bpy.ops.object.join()
    guide=body.copy();guide.data=body.data.copy();guide.name='WeightTransferGuide'
    bpy.context.collection.objects.link(guide)
    guide.hide_render=True;guide.hide_set(True)
    guide_kd=KDTree(len(guide.data.vertices))
    for v in guide.data.vertices:guide_kd.insert(v.co,v.index)
    guide_kd.balance()
    u.active(body)
    remesh=body.modifiers.new('Sculpted long-coat volume','REMESH')
    remesh.mode='VOXEL';remesh.voxel_size=.0038;remesh.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=remesh.name)
    relax=body.modifiers.new('Blend tuft roots','SMOOTH');relax.factor=.88;relax.iterations=12
    bpy.ops.object.modifier_apply(modifier=relax.name)
    # Thin tuft tips can separate during voxelization. Keep only continuous
    # anatomy, so animation cannot reveal floating opaque fur fragments.
    bm=bmesh.new();bm.from_mesh(body.data)
    unseen=set(bm.verts);parts=[]
    while unseen:
        seed=unseen.pop();part={seed};stack=[seed]
        while stack:
            for edge in stack.pop().link_edges:
                for vertex in edge.verts:
                    if vertex in unseen:
                        unseen.remove(vertex);part.add(vertex);stack.append(vertex)
        parts.append(part)
    largest=max(parts,key=len)
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if v not in largest],context='VERTS')
    bm.to_mesh(body.data);bm.free()
    decimate=body.modifiers.new('Game coat topology','DECIMATE');decimate.ratio=.085
    bpy.ops.object.modifier_apply(modifier=decimate.name)
    body.vertex_groups.clear()
    for group in guide.vertex_groups:body.vertex_groups.new(name=group.name)
    for vert in body.data.vertices:
        nearest=guide_kd.find_n(vert.co,3)
        influences={}
        for _,vi,dist in nearest:
            for g in guide.data.vertices[vi].groups:
                influences[g.group]=influences.get(g.group,0)+g.weight/max(.0001,dist)**2
        top=sorted(influences.items(),key=lambda item:-item[1])[:4]
        total=sum(w for _,w in top)
        for gi,weight in top:body.vertex_groups[gi].add([vert.index],weight/total,'REPLACE')
    bpy.data.objects.remove(guide,do_unlink=True)
    u.active(body)
    neighbors=[set() for v in body.data.vertices]
    for edge in body.data.edges:
        a,b=edge.vertices;neighbors[a].add(b);neighbors[b].add(a)
    weights=[{g.group:g.weight for g in v.groups} for v in body.data.vertices]
    for _ in range(16):
        relaxed=[]
        for i,adjacent in enumerate(neighbors):
            merged={g:w*.2 for g,w in weights[i].items()}
            for j in adjacent:
                for g,w in weights[j].items():merged[g]=merged.get(g,0)+w*.8/max(1,len(adjacent))
            top=sorted(merged.items(),key=lambda pair:-pair[1])[:4]
            total=sum(w for _,w in top)
            relaxed.append({g:w/total for g,w in top})
        weights=relaxed
    for group in body.vertex_groups:group.remove(list(range(len(body.data.vertices))))
    for i,weighted in enumerate(weights):
        for g,w in weighted.items():body.vertex_groups[g].add([i],w,'REPLACE')
    bpy.ops.object.vertex_group_limit_total(limit=4)
    bpy.ops.object.vertex_group_normalize_all(lock_active=False)
    for layer in list(body.data.color_attributes):body.data.color_attributes.remove(layer)
    body.data.materials.clear();body.data.materials.append(painted)
    for poly in body.data.polygons:poly.material_index=0
    u.colorize(body,coat);u.smooth(body)
    extra=[]
    # Blue eyes are 1.8x the old diameter with an outward-facing convex surface.
    for sign in (-1,1):
        p,n=front(sign*.089,H.z+.003)
        n=Vector((sign*.65,-.76,.02)).normalized()
        center=p-n*.006
        for name,offset,scale,mat in [
            ('Eye rim',0,(.0348,.010,.0360),ink),
            ('Blue iris',.006,(.0320,.009,.0330),blue),
            ('Deep pupil',.012,(.0210,.005,.0220),ink),
            ('Eye catchlight',.018,(.0048,.0025,.0055),glint)]:
            pos=center+n*offset
            if name=='Eye catchlight':pos+=Vector((-.009,-.001,.010))
            eye=u.ellipsoid(name,pos,scale,mat,24,16)
            eye.rotation_euler.z=sign*.644
            u.active(eye);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
            u.rigid(eye,'head');extra.append(eye)
    muzzle=morph(Vector((0,-.455,.522)),1)
    np=Vector((0,muzzle.y-.011,muzzle.z+.007))
    nose=u.ellipsoid('Nose leather',np,(.029,.020,.021),ink,24,16)
    for v in nose.data.vertices:v.co.x*=.82+.18*v.co.z/.021
    u.rigid(nose,'head');extra.append(nose)
    u.active(body)
    for obj in extra:obj.select_set(True)
    bpy.ops.object.join()
    # Normalize the asset's rest-pose envelope, including sculpted fur, not a
    # hidden object scale. Apply the same mapping to skeleton and mesh.
    lo=Vector(tuple(min(v.co[i] for v in body.data.vertices) for i in range(3)))
    hi=Vector(tuple(max(v.co[i] for v in body.data.vertices) for i in range(3)))
    factor=Vector(tuple(TARGET[i]/(hi[i]-lo[i]) for i in range(3)))
    center=(lo+hi)*.5
    def fit(p):return Vector(((p.x-center.x)*factor.x,(p.y-center.y)*factor.y,(p.z-lo.z)*factor.z))
    for vertex in body.data.vertices:vertex.co=fit(vertex.co)
    u.active(rig);bpy.ops.object.mode_set(mode='EDIT')
    for bone in rig.data.edit_bones:bone.head=fit(bone.head);bone.tail=fit(bone.tail)
    bpy.ops.object.mode_set(mode='OBJECT')
    assert [(b.name,b.parent.name if b.parent else None) for b in rig.data.bones]==contract
    u.active(body)
    bpy.ops.object.vertex_group_limit_total(limit=4)
    bpy.ops.object.vertex_group_normalize_all(lock_active=False)
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.uv.smart_project(angle_limit=1.1519,island_margin=.012)
    bpy.ops.object.mode_set(mode='OBJECT')
    body.data.validate()
    v2.OUT=OUT
    v2.bake_atlas(body,'adult')
    # Atlas contains every color; stale vertex paint must not multiply it in glTF.
    for layer in list(body.data.color_attributes):body.data.color_attributes.remove(layer)
    sculpted_vertex_count=len(body.data.vertices)
    v2.add_fuzz(body,fit(H),Vector((.17,.16,.17)),fit(muzzle),
                lambda p:coat(Vector((p.x/factor.x+center.x,p.y/factor.y+center.y,p.z/factor.z+lo.z))),
                'adult',count=4500,strand_scale=.90)
    # Detail fibers are constrained inside the approved envelope. The silhouette
    # volume comes from the sculpted mesh, not from these optional fine strands.
    for vert in body.data.vertices:
        vert.co.x=max(-TARGET.x*.5,min(TARGET.x*.5,vert.co.x))
        vert.co.y=max(-TARGET.y*.5,min(TARGET.y*.5,vert.co.y))
        vert.co.z=max(0,min(TARGET.z,vert.co.z))
    body.parent=rig
    arm=body.modifiers.new('Skin','ARMATURE');arm.object=rig
    rig['asset_version']='v03'
    rig['palette']=json.dumps({'deep':'#1B1716','medium':'#3A2A24','highlight':'#5A3D2A',
                              'bib':'#E9DDC9','eyes':'#7FB6D8','nose':'#0E0D0D'})
    bpy.context.view_layer.update()
    report={'target_dimensions_xyz_m':list(TARGET),'actual_dimensions_xyz_m':list(body.dimensions),
            'clumps':COUNTS,'clump_total':sum(COUNTS.values()),'head_pre_fit_scale':1.18,
            'leg_pre_fit_scale':LEG_SCALE,'leg_post_fit_scale':LEG_SCALE*factor.z,
            'eye_pre_fit_scale':1.8,'tail_core_pre_fit_diameter_scale':2,
            'envelope_fit_xyz':list(factor),'bone_contract_unchanged':True,
            'bone_names':[n for n,_ in contract],'sculpted_vertex_count':sculpted_vertex_count,
            'silhouette_is_opaque_geometry':True,'optional_detail_fibers':True}
    assert all(abs(body.dimensions[i]-TARGET[i])<.00001 for i in range(3)),report
    (QA/'proportion_validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    return rig,body


def render(rig,body,quick):
    scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.samples=32
    scene.cycles.use_denoising=True
    scene.cycles.transparent_max_bounces=64
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.48,.53,.60,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004))
    ground=bpy.context.object;ground.name='PreviewGround'
    ground.data.materials.append(u.material('Background','CCD5D0',.9))
    for name,loc,power,size,color in [('Key',(-1.5,-2.0,2.5),170,2,(1,.91,.82)),
        ('Fill',(1.7,-1,1.5),110,2,(.77,.87,1)),('Rim',(0,2,2),240,1.8,(1,.94,.86))]:
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color
        ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=loc;u.look_at(ob,(0,0,.36))
    cam=bpy.data.objects.new('V03Camera',bpy.data.cameras.new('V03Camera'))
    scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=1.15
    scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
    views=[('beauty',(1.8,-3.5,1.45))]
    if not quick:views += [('front',(0,-4,.38)),('side',(4,0,.38)),('back',(0,4,.38))]
    for name,loc in views:
        cam.location=loc;u.look_at(cam,(0,0,.3665));scene.render.filepath=str(QA/('adult_'+name+'.png'))
        bpy.ops.render.render(write_still=True)
    if not quick:
        silhouette=u.material('Silhouette','000000',1)
        original_mesh=body.data
        body.data=original_mesh.copy()
        bm=bmesh.new();bm.from_mesh(body.data)
        bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index==2],context='FACES')
        bm.to_mesh(body.data);bm.free()
        body.data.materials.clear();body.data.materials.append(silhouette)
        for polygon in body.data.polygons:polygon.material_index=0
        ground.hide_render=True
        background=scene.world.node_tree.nodes['Background']
        old_background=tuple(background.inputs[0].default_value)
        background.inputs[0].default_value=(1,1,1,1)
        for name,loc in [('front',(0,-4,.38)),('side',(4,0,.38))]:
            cam.location=loc;u.look_at(cam,(0,0,.3665));scene.render.filepath=str(QA/('adult_silhouette_'+name+'.png'))
            bpy.ops.render.render(write_still=True)
        temporary_mesh=body.data;body.data=original_mesh
        bpy.data.meshes.remove(temporary_mesh)
        ground.hide_render=False
        background.inputs[0].default_value=old_background
        cam.location=views[0][1];u.look_at(cam,(0,0,.3665))
        for n,r in {'head':(0,.16,0),'front.L.lower':(.35,0,0),'ear.L.tip':(.12,0,.12),'tail.00':(.23,0,0)}.items():
            rig.pose.bones[n].rotation_euler=r
        scene.render.filepath=str(QA/'adult_pose_check.png');bpy.ops.render.render(write_still=True)
        for pb in rig.pose.bones:pb.rotation_euler=(0,0,0)
    cam.location=views[0][1];u.look_at(cam,(0,0,.3665))
    for track in rig.animation_data.nla_tracks:
        for strip in track.strips:strip.influence=1.0
    u.active(rig);bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'adult_black_dog_v03.blend'))


def main():
    quick='--quick' in sys.argv
    rig,body=make()
    u.QA=QA
    result=u.validate(rig,body,'adult')
    assert result['triangles']<60000,result
    u.active(rig);body.select_set(True)
    for track in rig.animation_data.nla_tracks:track.mute=False
    bpy.ops.export_scene.gltf(filepath=str(OUT/'adult_black_dog_v03.glb'),export_format='GLB',
        use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_apply=False,
        export_yup=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_extras=True)
    for track in rig.animation_data.nla_tracks:track.mute=True
    for pb in rig.pose.bones:pb.rotation_euler=(0,0,0)
    render(rig,body,quick)


if __name__=='__main__':main()
