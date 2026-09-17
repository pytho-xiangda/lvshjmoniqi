"""Black dog v02: new silhouette, surface-fitted eyes and baked game materials.

Run in an isolated Blender process; never in an existing artist scene.
"""
from pathlib import Path
import math
import json
import sys
import random
import bisect
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_black_dog_3d as util

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/models/black_dog/v02'
QA = ROOT / 'docs/design/art/black_dog_3d/v02'
SOURCE = ROOT / 'art_source/black_dog/v02'
for folder in (OUT, QA, SOURCE):
    folder.mkdir(parents=True, exist_ok=True)
util.QA = QA
active, sphere, tube = util.active, util.ellipsoid, util.tube
linear, rigid, smooth = util.linear, util.rigid, util.smooth


def fur_material(name, color):
    mat = util.material(name, color, .88)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    shader = nodes.get('Principled BSDF')
    coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeVectorMath')
    mapping.operation = 'MULTIPLY'
    mapping.inputs[1].default_value = (75, 75, 24)
    links.new(coord.outputs['Generated'], mapping.inputs[0])
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 1
    noise.inputs['Detail'].default_value = 2
    links.new(mapping.outputs[0], noise.inputs['Vector'])
    ramp = nodes.new('ShaderNodeValToRGB')
    base = linear(color)
    ramp.color_ramp.elements[0].position = .22
    ramp.color_ramp.elements[0].color = tuple(c*.91 for c in base[:3])+(1,)
    ramp.color_ramp.elements[1].position = .80
    ramp.color_ramp.elements[1].color = tuple(c*1.09 for c in base[:3])+(1,)
    links.new(noise.outputs['Fac'], ramp.inputs[0])
    links.new(ramp.outputs['Color'], shader.inputs['Base Color'])
    return mat


def make(stage):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)
    puppy = stage == 'puppy'
    fur = fur_material('Velvet black coat', '211E1C')
    eye = util.material('Soft dark iris', '171D21', .39)
    nose_mat = util.material('Nose leather', '171616', .42)
    shine = util.material('Eye catchlight', 'FFF9E9', .30)
    brown = util.material('Warm iris lower rim', '302820', .39)
    if puppy:
        H, HS = Vector((0,-.255,.581)), Vector((.207,.192,.182))
        B, BS = Vector((0,.105,.310)), Vector((.181,.278,.189))
        front_y, hip_y, lx, ankle_z, leg_r = -.135,.302,.114,.078,.062
        muzzle_depth = .102
    else:
        H, HS = Vector((0,-.440,.950)), Vector((.231,.216,.231))
        B, BS = Vector((0,.135,.563)), Vector((.223,.485,.245))
        front_y, hip_y, lx, ankle_z, leg_r = -.235,.470,.157,.089,.065
        muzzle_depth = .148
    parts = [sphere('Body', B, BS, fur, 32, 20),
             sphere('Chest', (0,front_y,B.z+.055), (BS.x*.96,.192,BS.z*1.06),fur),
             sphere('Neck',(0,H.y+.065,H.z-.175),(.136,.146,.198),fur),
             sphere('Skull',H,HS,fur,48,32)]
    muzzle = H+Vector((0,-HS.y*.79,-HS.z*.40))
    parts.append(sphere('Short soft muzzle',muzzle,(.111,muzzle_depth,.072),fur,32,20))
    for s in (-1,1):
        parts.append(sphere('Cheek', H+Vector((s*.112,-.085,-.067)),(.092,.101,.082),fur))
    joints = {}
    for end,y in [('front',front_y),('hind',hip_y)]:
        for side,s in [('L',1),('R',-1)]:
            x = s*lx
            a = Vector((x,y,B.z+.012))
            b = Vector((x,y+(.020 if end=='front' else -.082),B.z*.52))
            c = Vector((x,y+(.006 if end=='front' else .044),ankle_z))
            d = Vector((x,y-.045,.040 if puppy else .047))
            joints[end+'.'+side]=(a,b,c,d)
            parts.append(sphere('Rounded shoulder',a,(leg_r*1.34,leg_r*1.40,leg_r*1.5),fur))
            parts.append(tube('Leg',[a,a.lerp(b,.52),b,c],
                              [leg_r*1.33,leg_r*1.1,leg_r*.86,leg_r*.77],fur,16))
            parts.append(sphere('Paw',d,(leg_r*.94,leg_r*1.24,d.z),fur,24,16))
    active(parts[0])
    for obj in parts:
        obj.select_set(True)
    bpy.ops.object.join()
    body=bpy.context.object
    body.name='BlackDog_'+stage+'_V02'
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    mod=body.modifiers.new('Unified skin','REMESH')
    mod.mode='VOXEL'
    mod.voxel_size=.007 if puppy else .010
    mod.use_smooth_shade=True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=body.modifiers.new('Relax','SMOOTH')
    mod.factor=.8
    mod.iterations=4
    bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=body.modifiers.new('Budget','DECIMATE')
    mod.ratio=.12
    bpy.ops.object.modifier_apply(modifier=mod.name)
    body.data.materials.clear()
    body.data.materials.append(fur)
    # Soft interpolated painted bib, with an organic pointed outline.
    def coat_color(p):
        t=(p.z-(B.z-.078))/(H.z-HS.z*.84-(B.z-.078))
        width=.053*max(0,math.sin(math.pi*min(1,max(0,t))*.79))
        edge=width-abs(p.x)+.003*math.sin(p.z*230+p.x*70)
        bib=max(0,min(1,edge/.010))*max(0,min(1,t*20))*max(0,min(1,(1-t)*20))
        bib*=max(0,min(1,(-p.y+front_y-.143)/.013))
        chin=0
        if p.y<muzzle.y-.044 and abs(p.x)<.036 and muzzle.z-.060<p.z<muzzle.z-.045:
            chin=.8
        f=max(bib,chin)
        dark,light=linear('211E1C'),linear('E9DDC9')
        return tuple(dark[i]*(1-f)+light[i]*f for i in range(3))+(1,)
    util.colorize(body,coat_color)
    fur_body=util.material('Painted body','FFFFFF',.88,True)
    nodes,links=fur_body.node_tree.nodes,fur_body.node_tree.links
    attr=next(n for n in nodes if n.type=='VERTEX_COLOR')
    coord=nodes.new('ShaderNodeTexCoord')
    mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY'
    mapping.inputs[1].default_value=(130,130,26)
    links.new(coord.outputs['Generated'],mapping.inputs[0])
    noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1
    links.new(mapping.outputs[0],noise.inputs['Vector'])
    ramp=nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=(.50,.50,.50,1)
    ramp.color_ramp.elements[1].color=(1,1,1,1)
    links.new(noise.outputs['Fac'],ramp.inputs[0])
    mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1
    links.new(attr.outputs['Color'],mix.inputs[1]);links.new(ramp.outputs['Color'],mix.inputs[2])
    links.new(mix.outputs[0],nodes.get('Principled BSDF').inputs['Base Color'])
    body.data.materials[0]=fur_body
    smooth(body)
    ad=bpy.data.armatures.new('BlackDogSkeletonV02')
    rig=bpy.data.objects.new('BlackDogRigV02',ad)
    bpy.context.collection.objects.link(rig)
    active(rig)
    bpy.ops.object.mode_set(mode='EDIT')
    def bone(name,a,b,parent=None):
        eb=ad.edit_bones.new(name)
        eb.head,eb.tail=a,b
        if parent:
            eb.parent=ad.edit_bones[parent]
    bone('root',(0,0,0),(0,0,.1))
    bone('pelvis',(0,hip_y,B.z),(0,hip_y-.13,B.z+.02),'root')
    bone('spine',(0,hip_y-.13,B.z+.02),(0,front_y+.1,B.z+.035),'pelvis')
    bone('chest',(0,front_y+.1,B.z+.035),(0,front_y-.03,B.z+.09),'spine')
    bone('neck',(0,front_y-.03,B.z+.09),H,'chest')
    bone('head',H,H+Vector((0,-.16,0)),'neck')
    bone('jaw',H+Vector((0,-.06,-.08)),muzzle+Vector((0,-.05,-.04)),'head')
    for name,(a,b,c,d) in joints.items():
        bone(name+'.upper',a,b,'chest' if name.startswith('front') else 'pelvis')
        bone(name+'.lower',b,c,name+'.upper')
        bone(name+'.paw',c,d,name+'.lower')
    ears={}
    for side,s in [('L',1),('R',-1)]:
        pts=[H+Vector((s*.147,.004,.141)), H+Vector((s*.239,-.005,.116)),
             H+Vector((s*.267,-.067,.035)), H+Vector((s*.227,-.102,-.066))]
        ears[side]=pts
        mid=pts[1].lerp(pts[2],.5)
        bone('ear.'+side+'.base',pts[0],mid,'head')
        bone('ear.'+side+'.tip',mid,pts[3],'ear.'+side+'.base')
    tail_root=Vector((0,B.y+BS.y*.89,B.z+BS.z*.43))
    tail_scale=1 if puppy else 1.28
    tp=[tail_root+Vector(p)*tail_scale for p in
        [(0,0,0),(0,.095,.060),(0,.165,.150),(0,.160,.245),(0,.100,.292),(0,.032,.284),(0,-.003,.249)]]
    for i in range(6):
        bone('tail.%02d'%i,tp[i],tp[i+1],'pelvis' if i==0 else 'tail.%02d'%(i-1))
    bpy.ops.object.mode_set(mode='OBJECT')
    active(body)
    rig.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    body.modifiers.clear()
    extras=[]
    for side,pts in ears.items():
        ear=tube('Folded ear '+side,pts,[(.058,.028),(.081,.026),(.058,.019),(.003,.003)],fur,16)
        util.chain_weights(ear,['ear.'+side+'.base','ear.'+side+'.tip'])
        active(ear)
        mod=ear.modifiers.new('Soft fold','SUBSURF');mod.levels=2
        bpy.ops.object.modifier_apply(modifier=mod.name)
        extras.append(ear)
    tail=tube('Feather tail',tp,[r*tail_scale for r in (.048,.056,.058,.053,.043,.030,.006)],fur,12)
    util.chain_weights(tail,['tail.%02d'%i for i in range(6)])
    active(tail)
    mod=tail.modifiers.new('Smooth tail','SUBSURF');mod.levels=2
    bpy.ops.object.modifier_apply(modifier=mod.name)
    extras.append(tail)
    # Eye patches follow the remeshed head surface: no spherical eyeball/goggle rim.
    def face_y(x,z):
        hit,loc,normal,idx=body.ray_cast(Vector((x,-2,z)),Vector((0,1,0)))
        if not hit:
            raise RuntimeError('Eye surface missed face')
        return loc.y
    def patch(name,cx,cz,rx,rz,mat,offset):
        vertices=[(cx,face_y(cx,cz)-offset,cz)]
        rings,sides=5,32
        for r in range(1,rings+1):
            for j in range(sides):
                a=j*math.tau/sides
                x,z=cx+rx*r/rings*math.cos(a),cz+rz*r/rings*math.sin(a)
                bulge=.003*(1-(r/rings)**2)
                vertices.append((x,face_y(x,z)-offset-bulge,z))
        faces=[]
        for j in range(sides):
            faces.append((0,1+j,1+(j+1)%sides))
        for r in range(1,rings):
            a=1+(r-1)*sides;b=1+r*sides
            for j in range(sides):
                faces.append((a+j,b+j,b+(j+1)%sides,a+(j+1)%sides))
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
        ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
        ob.data.materials.append(mat);smooth(ob);rigid(ob,'head');extras.append(ob)
    er=.037 if puppy else .031
    for s in (-1,1):
        x,z=s*.092,H.z-.002
        patch('Inset dark eye',x,z,er,er*1.13,eye,.004)
        patch('Warm lower iris',x,z-.008,er*.83,er*.87,brown,.005)
        patch('Deep pupil',x,z+.005,er*.73,er*.94,eye,.007)
        patch('Large soft catchlight',x-.009,z+.012,.0055,.0065,shine,.010)
        patch('Tiny catchlight',x+.009,z-.012,.0021,.0021,shine,.010)
    np=muzzle+Vector((0,-muzzle_depth*.86,.013))
    nose=sphere('Heart nose',np,(.038,.024,.026),nose_mat,24,16)
    for v in nose.data.vertices:
        v.co.x*=.77+.25*v.co.z/.026
    rigid(nose,'head');extras.append(nose)
    # Fine mouth split, flush into the short muzzle, not a large separate jaw plate.
    mouth=tube('Mouth split',[np+Vector((0,.003,-.020)),np+Vector((0,.005,-.034)),
                              np+Vector((0,.011,-.043))],[.002,.002,.001],nose_mat,6)
    rigid(mouth,'jaw');extras.append(mouth)
    active(body)
    for obj in extras:obj.select_set(True)
    bpy.ops.object.join()
    mod=body.modifiers.new('Game budget','DECIMATE');mod.ratio=.78
    bpy.ops.object.modifier_apply(modifier=mod.name)
    body.data.validate()
    active(body)
    bpy.ops.object.vertex_group_limit_total(limit=4)
    bpy.ops.object.vertex_group_normalize_all(lock_active=False)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.uv.smart_project(angle_limit=1.1519,island_margin=.012)
    bpy.ops.object.mode_set(mode='OBJECT')
    bake_atlas(body,stage)
    add_fuzz(body,H,HS,muzzle,coat_color,stage)
    scale=.40 if puppy else .60
    for v in body.data.vertices:v.co*=scale
    active(rig);bpy.ops.object.mode_set(mode='EDIT')
    for eb in ad.edit_bones:eb.head*=scale;eb.tail*=scale
    bpy.ops.object.mode_set(mode='OBJECT')
    body.parent=rig
    arm=body.modifiers.new('Skin','ARMATURE');arm.object=rig
    rig.show_in_front=True
    rig['stage']=stage;rig['asset_version']='v02';rig['units']='meters'
    rig['palette']=json.dumps(util.PALETTE)
    animate(rig)
    bpy.context.view_layer.update()
    return rig,body


def add_fuzz(body,H,HS,muzzle,coat_color,stage,count=8500,strand_scale=1.0):
    """Layered alpha-cutout hair cards with inherited skin weights and normals."""
    random.seed(180 if stage=='puppy' else 181)
    body.data.calc_loop_triangles()
    triangles=[t for t in body.data.loop_triangles if t.material_index==0]
    weights=[];total=0
    for t in triangles:
        total+=t.area;weights.append(total)
    vs=[];fs=[];vg=[];colors=[];normals=[];uvs=[]
    for i in range(count):
        t=triangles[bisect.bisect_left(weights,random.random()*total)]
        a,b,c=[body.data.vertices[j] for j in t.vertices]
        u,v=random.random(),random.random()
        if u+v>1:u,v=1-u,1-v
        p=a.co*(1-u-v)+b.co*u+c.co*v
        n=(a.normal*(1-u-v)+b.normal*u+c.normal*v).normalized()
        if p.z<.045:continue
        # Keep the expression and the nose completely readable.
        face=(p.y<H.y-HS.y*.40 and abs(p.x)<HS.x*.82 and p.z>H.z-HS.z*.69)
        near_eye=min(((p.x-s*.092)/.050)**2+((p.z-H.z)/.053)**2 for s in (-1,1))<1.0
        near_nose=abs(p.x)<.055 and p.y<muzzle.y-.024 and abs(p.z-muzzle.z)<.049
        if face and (near_eye or near_nose):continue
        direction=Vector((p.x*2.5,.15,-1))
        if face and p.z>H.z+.040:direction=Vector((p.x*2,.08,1))
        tangent=(direction-n*direction.dot(n)).normalized()
        side=n.cross(tangent).normalized()
        length=random.uniform(.036,.069)*(.80 if face else 1)*strand_scale
        width=random.uniform(.010,.020)*(.85 if face else 1)*strand_scale
        base=p-n*.001
        mid=p+tangent*length*.46+n*(.004 if face else .008)
        end=p+tangent*length+n*(.007 if face else .015)
        start=len(vs)
        vs.extend([base-side*width,base+side*width,mid-side*width,mid+side*width,end-side*width*.85,end+side*width*.85])
        # Winding must agree with outward custom normals; double-sided glTF
        # otherwise flips the lit side inward and turns every strand black.
        fs.extend([(start,start+2,start+3,start+1),(start+2,start+4,start+5,start+3)])
        normals.extend([n]*6)
        uvs.extend([(0,0),(1,0),(0,.46),(1,.46),(0,1),(1,1)])
        influences={}
        for vertex,factor in [(a,1-u-v),(b,u),(c,v)]:
            for group in vertex.groups:influences[group.group]=influences.get(group.group,0)+group.weight*factor
        top=sorted(influences.items(),key=lambda item:-item[1])[:4]
        norm=sum(w for _,w in top)
        vg.extend([[(g,w/norm) for g,w in top]]*6)
        col=coat_color(p) if abs(p.x)<.09 and p.y<H.y+.09 else linear('211E1C')
        for brightness in (1.10,1.10,1.40,1.40,1.65,1.65):
            colors.append(tuple(c*brightness for c in col[:3])+(1,))
    mesh=bpy.data.meshes.new('Short coat fibers');mesh.from_pydata(vs,[],fs);mesh.update()
    assert all(p.normal.dot(normals[p.vertices[0]]) > 0 for p in mesh.polygons), 'Inverted hair-card winding'
    fuzz=bpy.data.objects.new('Skinned coat fibers',mesh);bpy.context.collection.objects.link(fuzz)
    uv=mesh.uv_layers.new(name='UVMap')
    for loop in mesh.loops:uv.data[loop.index].uv=uvs[loop.vertex_index]
    for group in body.vertex_groups:fuzz.vertex_groups.new(name=group.name)
    for i,influences in enumerate(vg):
        for group,w in influences:fuzz.vertex_groups[group].add([i],w,'REPLACE')
    color=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='POINT')
    mesh.color_attributes.active_color=color
    for i,col in enumerate(colors):color.data[i].color=col
    mat=util.material('Coat fibers game','FFFFFF',.94,True)
    nodes,links=mat.node_tree.nodes,mat.node_tree.links
    shader=nodes.get('Principled BSDF')
    shader.inputs['Specular IOR Level'].default_value=.16
    texture=nodes.new('ShaderNodeTexImage');texture.image=hair_texture()
    threshold=nodes.new('ShaderNodeMath');threshold.operation='GREATER_THAN';threshold.inputs[1].default_value=.35
    links.new(texture.outputs['Alpha'],threshold.inputs[0]);links.new(threshold.outputs[0],shader.inputs['Alpha'])
    mat.use_backface_culling=False
    mesh.materials.append(mat)
    smooth(fuzz)
    mesh.normals_split_custom_set_from_vertices(normals)
    active(body);fuzz.select_set(True);bpy.ops.object.join()
    assert not body.data.validate(), 'Unexpected invalid fiber geometry'
    # Neutral vertex colors on atlas surfaces keep their baked colors unchanged.
    layer=body.data.color_attributes.get('Color')
    fiber_index=len(body.data.materials)-1
    for p in body.data.polygons:
        if p.material_index!=fiber_index:
                for vi in p.vertices:layer.data[vi].color=(1,1,1,1)


def hair_texture():
    # A deterministic shared cutout map; its white RGB multiplies vertex coat colors.
    name='CoatStrandsRGBA'
    if name in bpy.data.images:return bpy.data.images[name]
    random.seed(244)
    hairs=[((i+.5)/22,random.uniform(.62,1),random.uniform(-.055,.055),random.uniform(.70,1.1)) for i in range(22)]
    width,height=128,256
    pixels=[]
    for y in range(height):
        t=y/(height-1)
        for x in range(width):
            u=x/(width-1);alpha=0
            for pos,length,bend,thick in hairs:
                if t>length:continue
                center=pos+bend*t*t
                radius=.0042*thick*max(.12,1-(t/length)**3)
                alpha=max(alpha,max(0,min(1,1-abs(u-center)/radius))*min(1,(length-t)*40))
            pixels.extend((1,1,1,alpha))
    image=bpy.data.images.new(name,width=width,height=height,alpha=True)
    image.alpha_mode='STRAIGHT'
    image.pixels.foreach_set(pixels)
    image.filepath_raw=str(OUT/'coat_strands.png');image.file_format='PNG';image.save();image.pack()
    return image


def bake_atlas(body,stage):
    scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.samples=1
    atlas=bpy.data.images.new(stage+'_BaseColor_2048',width=2048,height=2048,alpha=False)
    for mat in body.data.materials:
        nodes=mat.node_tree.nodes
        tex=nodes.new('ShaderNodeTexImage');tex.image=atlas;nodes.active=tex
    scene.render.bake.use_pass_direct=False
    scene.render.bake.use_pass_indirect=False
    scene.render.bake.use_pass_color=True
    scene.render.bake.margin=12
    active(body)
    bpy.ops.object.bake(type='DIFFUSE')
    atlas.filepath_raw=str(OUT/(stage+'_basecolor.png'))
    atlas.file_format='PNG';atlas.save();atlas.pack()
    glossy={i for i,m in enumerate(body.data.materials) if any(k in m.name for k in ('iris','pupil','catchlight','leather'))}
    indices=[1 if p.material_index in glossy else 0 for p in body.data.polygons]
    body.data.materials.clear()
    for name,roughness in [('Coat',.86),('EyesNose',.32)]:
        mat=util.material(stage+'_'+name+'_Game','FFFFFF',roughness)
        tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=atlas
        shader=mat.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Specular IOR Level'].default_value=.20 if name=='Coat' else .35
        mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
        body.data.materials.append(mat)
    for poly,index in zip(body.data.polygons,indices):poly.material_index=index


def animate(rig):
    for pb in rig.pose.bones:pb.rotation_mode='XYZ'
    for clip in ('Idle','TailWag'):
        rig.animation_data_create()
        action=bpy.data.actions.new(clip);rig.animation_data.action=action
        for frame in range(1,62,3):
            t=(frame-1)/60*math.tau
            for pb in rig.pose.bones:pb.rotation_euler=(0,0,0)
            rig.pose.bones['neck'].rotation_euler.x=.009*math.sin(t)
            rig.pose.bones['head'].rotation_euler.y=.018*math.sin(t)
            for side in ('L','R'):rig.pose.bones['ear.'+side+'.tip'].rotation_euler.x=.035*math.sin(t+.4)
            for i in range(6):rig.pose.bones['tail.%02d'%i].rotation_euler.x=(.065 if clip=='Idle' else .21)*math.sin(t*(1 if clip=='Idle' else 3)-i*.30)
            for pb in rig.pose.bones:pb.keyframe_insert('rotation_euler',frame=frame,group=pb.name)
        track=rig.animation_data.nla_tracks.new();track.name=clip
        track.strips.new(clip,1,action);track.mute=True
        rig.animation_data.action=None
    for pb in rig.pose.bones:pb.rotation_euler=(0,0,0)
    scene=bpy.context.scene
    scene.frame_start,scene.frame_end=1,61;scene.render.fps=30
    scene.unit_settings.system='METRIC'


def studio(stage,rig,body,quick=False):
    scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.samples=32 if quick else 48
    scene.cycles.transparent_max_bounces=64
    scene.cycles.use_denoising=True
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.48,.53,.60,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
    scene.view_settings.view_transform='AgX'
    scene.view_settings.look='AgX - Medium High Contrast'
    scene.view_settings.exposure=0
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.004))
    ground=bpy.context.object;ground.name='PreviewGround'
    ground.data.materials.append(util.material('Background','CCD5D0',.9))
    for name,loc,power,size,color in [('Key',(-1.5,-2.0,2.5),160,2,(1,.91,.82)),
        ('Fill',(1.7,-1,1.5),95,2,(.77,.87,1)),('Rim',(0,2,2),240,1.8,(1,.94,.86))]:
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color
        ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=loc
        util.look_at(ob,(0,0,body.dimensions.z*.5))
    cam=bpy.data.objects.new('V02Camera',bpy.data.cameras.new('V02Camera'))
    scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO'
    h=body.dimensions.z;cam.data.ortho_scale=h*1.48
    views=[('beauty',(1.8,-3.5,h*1.9))]
    if not quick:views += [('front',(0,-4,h*.53)),('side',(4,0,h*.53)),('back',(0,4,h*.53))]
    scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
    for label,loc in views:
        cam.location=loc;util.look_at(cam,(0,.025,h*.49))
        scene.render.filepath=str(QA/(stage+'_'+label+'.png'))
        bpy.ops.render.render(write_still=True)
    if not quick:
        cam.location=views[0][1];util.look_at(cam,(0,.025,h*.49))
        rig.pose.bones['head'].rotation_euler.y=.16
        rig.pose.bones['front.L.upper'].rotation_euler.x=-.25
        rig.pose.bones['front.L.lower'].rotation_euler.x=.42
        rig.pose.bones['ear.L.tip'].rotation_euler.x=.18
        rig.pose.bones['tail.00'].rotation_euler.x=.25
        scene.render.filepath=str(QA/(stage+'_pose_check.png'))
        bpy.ops.render.render(write_still=True)
        for pb in rig.pose.bones:pb.rotation_euler=(0,0,0)
    cam.location=views[0][1];util.look_at(cam,(0,.025,h*.49))
    active(rig)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/(stage+'_black_dog_v02.blend')))


def main():
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    stages=['puppy'] if '--quick' in args else ['puppy','adult']
    for stage in stages:
        print('BUILD_V02',stage,flush=True)
        rig,body=make(stage)
        report=util.validate(rig,body,stage)
        assert report['triangles']<60000,report
        active(rig);body.select_set(True)
        for track in rig.animation_data.nla_tracks:track.mute=False
        bpy.ops.export_scene.gltf(filepath=str(OUT/(stage+'_black_dog_v02.glb')),export_format='GLB',
            use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_apply=False,
            export_yup=True,export_skins=True,export_all_influences=False,export_def_bones=True,export_extras=True)
        for track in rig.animation_data.nla_tracks:track.mute=True
        for pb in rig.pose.bones:pb.rotation_euler=(0,0,0)
        studio(stage,rig,body,'--quick' in args)


if __name__=='__main__':
    main()
