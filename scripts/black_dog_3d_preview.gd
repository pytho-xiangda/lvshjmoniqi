extends Node3D
## Standalone asset viewer; leaves the 2D game's main scene unchanged.

const MODELS: Array[String] = [
    "res://assets/models/black_dog/v02/puppy_black_dog_v02.glb",
    "res://assets/models/black_dog/v03/adult_black_dog_v03.glb",
]
var model: Node3D
var animation_player: AnimationPlayer
var camera: Camera3D
var current_stage: int = 0
var clip_name: String = "Idle"
var orbit_angle: float = 0.5
var is_rotating: bool = false
var status_label: Label


func _ready() -> void:
    get_viewport().msaa_3d = Viewport.MSAA_4X
    var environment_node := WorldEnvironment.new()
    var environment := Environment.new()
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color("bac6c1")
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color("c7d2df")
    environment.ambient_light_energy = 0.7
    environment.tonemap_mode = Environment.TONE_MAPPER_LINEAR
    environment.tonemap_exposure = 1.0
    environment_node.environment = environment
    add_child(environment_node)
    var light := DirectionalLight3D.new()
    light.rotation_degrees = Vector3(-40.0, -35.0, 0.0)
    light.light_color = Color("fff1dd")
    light.light_energy = 1.0
    light.shadow_enabled = true
    add_child(light)
    var fill := DirectionalLight3D.new()
    fill.rotation_degrees = Vector3(-30.0, 125.0, 0.0)
    fill.light_color = Color("c2d6ee")
    fill.light_energy = 0.65
    add_child(fill)
    var floor_mesh := MeshInstance3D.new()
    var plane := PlaneMesh.new()
    plane.size = Vector2(200.0, 200.0)
    floor_mesh.mesh = plane
    var floor_material := StandardMaterial3D.new()
    floor_material.albedo_color = Color("788781")
    floor_material.roughness = 0.9
    floor_mesh.material_override = floor_material
    floor_mesh.position.y = -0.003
    add_child(floor_mesh)
    camera = Camera3D.new()
    camera.projection = Camera3D.PROJECTION_ORTHOGONAL
    add_child(camera)
    camera.make_current()
    var canvas := CanvasLayer.new()
    add_child(canvas)
    var margin := MarginContainer.new()
    margin.position = Vector2(24.0, 20.0)
    canvas.add_child(margin)
    var column := VBoxContainer.new()
    margin.add_child(column)
    status_label = Label.new()
    status_label.add_theme_color_override("font_color", Color("3c3025"))
    status_label.add_theme_font_size_override("font_size", 24)
    column.add_child(status_label)
    var row := HBoxContainer.new()
    column.add_child(row)
    _button(row, "幼犬", func() -> void: _load_stage(0))
    _button(row, "成年", func() -> void: _load_stage(1))
    _button(row, "待机", func() -> void: _play_clip("Idle"))
    _button(row, "摆尾", func() -> void: _play_clip("TailWag"))
    _button(row, "正面", func() -> void: orbit_angle = 0.0; _update_camera())
    _button(row, "侧面", func() -> void: orbit_angle = PI / 2.0; _update_camera())
    _button(row, "背面", func() -> void: orbit_angle = PI; _update_camera())
    _button(row, "旋转", func() -> void: is_rotating = not is_rotating)
    _load_stage(0)


func _button(parent: Node, title: String, callback: Callable) -> void:
    var button := Button.new()
    button.text = title
    button.custom_minimum_size = Vector2(76.0, 42.0)
    button.pressed.connect(callback)
    parent.add_child(button)


func _load_stage(stage: int) -> void:
    if is_instance_valid(model):
        remove_child(model)
        model.queue_free()
    current_stage = stage
    model = (load(MODELS[stage]) as PackedScene).instantiate() as Node3D
    add_child(model)
    animation_player = model.find_child("AnimationPlayer", true, false) as AnimationPlayer
    _update_camera()
    _play_clip(clip_name)


func _play_clip(requested: String) -> void:
    clip_name = requested
    if animation_player != null:
        for actual: StringName in animation_player.get_animation_list():
            if String(actual).get_slice("/", String(actual).get_slice_count("/") - 1) == requested:
                animation_player.get_animation(actual).loop_mode = Animation.LOOP_LINEAR
                animation_player.play(actual)
                break
    status_label.text = "%s · %s · 29 bones" % ["v02 幼犬" if current_stage == 0 else "v03 成年犬", requested]


func _update_camera() -> void:
    var height: float = 0.32 if current_stage == 0 else 0.74
    var target := Vector3(0.0, height * 0.5, 0.0)
    camera.size = height * 1.55
    camera.position = target + Vector3(sin(orbit_angle) * height * 3.0, height * 0.35, cos(orbit_angle) * height * 3.0)
    camera.look_at(target)


func _process(delta: float) -> void:
    if is_rotating:
        orbit_angle += delta * 0.4
        _update_camera()
