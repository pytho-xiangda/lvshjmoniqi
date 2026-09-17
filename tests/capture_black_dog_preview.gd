extends SceneTree


func _initialize() -> void:
    call_deferred("_capture")


func _capture() -> void:
    root.size = Vector2i(1200, 900)
    var scene := (load("res://scenes/black_dog_3d_preview.tscn") as PackedScene).instantiate()
    root.add_child(scene)
    for stage in range(2):
        scene._load_stage(stage)
        scene._play_clip("TailWag")
        assert(scene.animation_player.is_playing())
        for frame in range(6):
            await process_frame
        await RenderingServer.frame_post_draw
        var screenshot := root.get_texture().get_image()
        var label: String = "puppy" if stage == 0 else "adult"
        var version: String = "v02" if stage == 0 else "v03"
        var path: String = "res://docs/design/art/black_dog_3d/%s/%s_godot.png" % [version, label]
        assert(screenshot.save_png(path) == OK)
        print("CAPTURE_OK ", label)
    scene.free()
    quit(0)
