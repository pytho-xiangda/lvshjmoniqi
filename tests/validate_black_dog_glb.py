"""Validate the deliverable container, not just the Blender scene."""
from pathlib import Path
import struct
import json

ROOT = Path(__file__).resolve().parents[1]
reports = []
for stage in ('puppy', 'adult'):
    path = ROOT / 'assets/models/black_dog/v02' / (stage + '_black_dog_v02.glb')
    data = path.read_bytes()
    magic, version, size = struct.unpack_from('<4sII', data)
    assert magic == b'glTF' and version == 2 and size == len(data)
    length, kind = struct.unpack_from('<II', data, 12)
    assert kind == 0x4E4F534A
    doc = json.loads(data[20:20+length])
    assert all('uri' not in image and 'bufferView' in image for image in doc['images'])
    assert all('uri' not in buffer for buffer in doc['buffers'])
    assert len(doc['skins']) == 1 and len(doc['skins'][0]['joints']) == 29
    assert {a['name'] for a in doc['animations']} == {'Idle', 'TailWag'}
    masked = [m for m in doc['materials'] if m.get('alphaMode') == 'MASK']
    assert len(masked) == 1 and masked[0].get('doubleSided')
    assert len(doc['materials']) == 3
    triangles = 0
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            assert {'POSITION', 'NORMAL', 'TEXCOORD_0', 'JOINTS_0', 'WEIGHTS_0'} <= primitive['attributes'].keys()
            assert primitive.get('mode', 4) == 4
            triangles += doc['accessors'][primitive['indices']]['count'] // 3
    assert triangles < 60000
    reports.append({'stage': stage, 'triangles': triangles, 'bones': 29,
                    'embedded_images': len(doc['images']), 'materials': 3,
                    'alpha_mode': 'MASK', 'self_contained': True, 'bytes': len(data)})
output = ROOT / 'docs/design/art/black_dog_3d/v02/glb_validation.json'
output.write_text(json.dumps(reports, indent=2), encoding='utf-8')
print('BLACK_DOG_GLB_OK', json.dumps(reports))
