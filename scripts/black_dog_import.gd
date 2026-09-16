@tool
extends EditorScenePostImport
## Godot 4.7.1 imported the first vertex-colored surface with this flag disabled.
## Store the fix in the imported asset, so every instance receives correct colors.


func _post_import(scene: Node) -> Object:
    for node: Node in scene.find_children("*", "MeshInstance3D", true, false):
        var mesh_instance := node as MeshInstance3D
        for surface in range(mesh_instance.mesh.get_surface_count()):
            var arrays := mesh_instance.mesh.surface_get_arrays(surface)
            var colors: PackedColorArray = arrays[Mesh.ARRAY_COLOR]
            var material := mesh_instance.mesh.surface_get_material(surface) as BaseMaterial3D
            if material != null and not colors.is_empty():
                material.vertex_color_use_as_albedo = true
                material.vertex_color_is_srgb = false
    return scene
