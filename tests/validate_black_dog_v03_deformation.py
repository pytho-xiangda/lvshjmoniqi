"""Run in isolated Blender; catch stretching that finite-coordinate checks miss."""
from pathlib import Path
import json
import bpy

ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art_source/black_dog/v03/adult_black_dog_v03.blend'))
rig = bpy.data.objects['BlackDogRigV03']
body = bpy.data.objects['BlackDog_adult_V03']
edge_pairs = set()
for polygon in body.data.polygons:
    if polygon.material_index != 2:
        edge_pairs.update(tuple(sorted(pair)) for pair in polygon.edge_keys)
edges = [(a, b, (body.data.vertices[a].co-body.data.vertices[b].co).length) for a, b in edge_pairs]
reports = []
for track in rig.animation_data.nla_tracks:
    for candidate in rig.animation_data.nla_tracks:
        candidate.mute = True
    rig.animation_data.action = track.strips[0].action
    rig.animation_data.action_slot = track.strips[0].action_slot
    sampled_rotations = []
    for frame in [1, 8, 16, 23, 31, 46, 61]:
        bpy.context.scene.frame_set(frame)
        bpy.context.view_layer.update()
        sampled_rotations.append(tuple(rig.pose.bones['tail.00'].rotation_euler))
        evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        lengths = [((mesh.vertices[a].co-mesh.vertices[b].co).length, length) for a,b,length in edges]
        ratios = sorted(deformed/max(rest, .002) for deformed,rest in lengths)
        result = {'clip': track.name, 'frame': frame, 'p999_edge_stretch': ratios[int(len(ratios)*.999)],
                  'maximum_edge_stretch': max(ratios), 'edges_above_4x': sum(r>4 for r in ratios),
                  'maximum_edge_extension_m': max(deformed-rest for deformed,rest in lengths)}
        reports.append(result)
        evaluated.to_mesh_clear()
    assert len(set(sampled_rotations)) > 1, 'Animation did not evaluate: ' + track.name
output = ROOT/'docs/design/art/black_dog_3d/v03/deformation_validation.json'
output.write_text(json.dumps(reports, indent=2), encoding='utf8')
# Ratio alone is unstable for sub-millimetre tip edges. Also constrain actual
# extension, so a tiny local tip does not mask a visible 2.5 cm stretching spike.
assert all(r['p999_edge_stretch'] < 2.5 and r['maximum_edge_extension_m'] < .025 for r in reports), reports
print('V03_DEFORMATION_OK', json.dumps(reports))
