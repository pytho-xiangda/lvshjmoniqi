extends SceneTree
## Checks exported files through Godot's real glTF importer and animation system.


func _initialize() -> void:
    call_deferred("_validate")


func _validate() -> void:
    var reports: Array[Dictionary] = []
    for stage: String in ["puppy", "adult"]:
        var path: String = "res://assets/models/black_dog/%s_black_dog_v01.glb" % stage
        var packed := load(path) as PackedScene
        assert(packed != null, "Missing imported model: " + path)
        var instance := packed.instantiate()
        root.add_child(instance)
        var skeletons := instance.find_children("*", "Skeleton3D", true, false)
        var meshes := instance.find_children("*", "MeshInstance3D", true, false)
        var players := instance.find_children("*", "AnimationPlayer", true, false)
        assert(skeletons.size() == 1 and meshes.size() >= 1 and players.size() == 1)
        var skeleton := skeletons[0] as Skeleton3D
        assert(skeleton.get_bone_count() == 29)
        for name: String in ["root", "head", "jaw", "ear.L.tip", "front.L.paw", "tail.05"]:
            assert(skeleton.find_bone(name) >= 0, "Missing bone: " + name)
        var surfaces: int = 0
        for entry: Node in meshes:
            var mesh_instance := entry as MeshInstance3D
            assert(mesh_instance.skin != null and mesh_instance.skin.get_bind_count() > 0)
            surfaces += mesh_instance.mesh.get_surface_count()
            for surface in range(mesh_instance.mesh.get_surface_count()):
                var material := mesh_instance.mesh.surface_get_material(surface) as BaseMaterial3D
                var colors: PackedColorArray = mesh_instance.mesh.surface_get_arrays(surface)[Mesh.ARRAY_COLOR]
                assert(material != null and not colors.is_empty())
                assert(material.vertex_color_use_as_albedo, "Imported material ignores vertex colors")
        var player := players[0] as AnimationPlayer
        var animations: Array[String] = []
        for clip: StringName in player.get_animation_list():
            if clip == &"RESET":
                continue
            animations.append(String(clip))
            var animation := player.get_animation(clip)
            assert(animation.length > 1.9 and animation.get_track_count() > 0)
            player.play(clip)
            player.advance(0.0)
            var before := skeleton.get_bone_pose_rotation(skeleton.find_bone("tail.00"))
            player.advance(0.25)
            var after := skeleton.get_bone_pose_rotation(skeleton.find_bone("tail.00"))
            assert(not before.is_equal_approx(after), "Tail animation has no deformation: " + String(clip))
            for i in range(skeleton.get_bone_count()):
                assert(skeleton.get_bone_global_pose(i).origin.is_finite())
        assert(animations.size() == 2, "Expected two usable clips")
        reports.append({"stage": stage, "bones": skeleton.get_bone_count(), "surfaces": surfaces,
            "clips": animations, "skin_loaded": true, "animation_changes_pose": true,
            "vertex_colors_enabled": true})
        instance.free()
    var output := FileAccess.open("res://docs/design/art/black_dog_3d/godot_validation.json", FileAccess.WRITE)
    output.store_string(JSON.stringify(reports, "  "))
    print("BLACK_DOG_VALIDATION_OK ", JSON.stringify(reports))
    quit(0)
