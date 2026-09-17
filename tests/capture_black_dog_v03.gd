extends SceneTree


func _initialize() -> void:
    call_deferred("_capture")


func _capture() -> void:
    root.size = Vector2i(1200, 900)
    var scene := (load("res://scenes/black_dog_3d_preview.tscn") as PackedScene).instantiate()
    root.add_child(scene)
    scene._load_stage(1)
    if "--flat-coat" in OS.get_cmdline_user_args():
        for node in scene.model.find_children("*", "MeshInstance3D", true, false):
            var flat := StandardMaterial3D.new()
            flat.albedo_color = Color("e9ddc9")
            flat.roughness = 0.9
            node.set_surface_override_material(0, flat)
    if "--no-shadows" in OS.get_cmdline_user_args():
        for light in scene.find_children("*", "DirectionalLight3D", true, false):
            light.shadow_enabled = false
    var opaque_only: bool = "--opaque" in OS.get_cmdline_user_args()
    if opaque_only:
        for node in scene.model.find_children("*", "MeshInstance3D", true, false):
            var hidden := StandardMaterial3D.new()
            hidden.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
            hidden.albedo_color.a = 0.0
            node.set_surface_override_material(2, hidden)
    scene._play_clip("TailWag")
    assert(scene.animation_player.is_playing())
    var rest_only: bool = "--rest" in OS.get_cmdline_user_args()
    if rest_only:
        scene.animation_player.stop()
        scene.status_label.text = "v03 成年犬 · Rest pose · 29 bones"
        var skeleton := scene.model.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
        skeleton.reset_bone_poses()
    for view: Dictionary in [{"name": "beauty", "angle": 0.5}, {"name": "side", "angle": PI / 2.0}]:
        scene.orbit_angle = view.angle
        scene._update_camera()
        for frame in range(8):
            await process_frame
        await RenderingServer.frame_post_draw
        var screenshot := root.get_texture().get_image()
        var path: String = "res://docs/design/art/black_dog_3d/v03/adult_godot_%s.png" % view.name
        if opaque_only:
            path = "res://docs/design/art/black_dog_3d/v03/adult_opaque_%s.png" % view.name
        if rest_only:
            path = "res://docs/design/art/black_dog_3d/v03/adult_rest_%s.png" % view.name
        assert(screenshot.save_png(path) == OK)
        print("V03_CAPTURE_OK ", view.name)
    scene.free()
    quit(0)
