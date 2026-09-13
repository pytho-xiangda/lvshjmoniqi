extends Node2D


const BACKGROUND: Texture2D = preload("res://assets/art/daily/protagonist_cinematic_desk_v01.png")
const MOTION_SHADER: Shader = preload("res://shaders/cinematic_desk_motion.gdshader")
const AMBIENT_SCRIPT: Script = preload("res://scripts/cinematic_desk_ambient.gd")
const VIEW_SIZE := Vector2(1672.0, 941.0)
const CAMERA_CENTER := Vector2(836.0, 470.5)
const ACTIVE_MOTION_STRENGTH: float = 1.25

var elapsed: float = 0.0
var motion_strength: float = ACTIVE_MOTION_STRENGTH
var motion_enabled: bool = true
var screenshot_saved: bool = false
var render_demo: bool = false
var background_material: ShaderMaterial
var ambient: Node2D
var camera: Camera2D
var particle_effects: Node2D


func _ready() -> void:
    render_demo = "--render-demo" in OS.get_cmdline_user_args()
    _build_background()
    _build_ambient()
    _build_particles()
    _build_camera()


func _process(delta: float) -> void:
    elapsed += delta
    var target_strength: float = ACTIVE_MOTION_STRENGTH if motion_enabled else 0.0
    motion_strength = move_toward(motion_strength, target_strength, delta * 0.80)
    background_material.set_shader_parameter("motion_strength", motion_strength)
    ambient.call("set_intensity", motion_strength)
    _update_particles()
    _animate_camera()

    if render_demo and not screenshot_saved and elapsed >= 6.0:
        screenshot_saved = true
        call_deferred("_save_demo_screenshot")
    if render_demo and elapsed >= 7.0:
        get_tree().quit()


func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_SPACE:
            motion_enabled = not motion_enabled
        elif event.keycode == KEY_ESCAPE:
            get_tree().quit()


func _build_background() -> void:
    var background := Sprite2D.new()
    background.name = "CinematicDeskBackground"
    background.texture = BACKGROUND
    background.centered = false
    background_material = ShaderMaterial.new()
    background_material.shader = MOTION_SHADER
    background.material = background_material
    add_child(background)


func _build_ambient() -> void:
    ambient = AMBIENT_SCRIPT.new()
    ambient.name = "AmbientParticles"
    ambient.z_index = 2
    add_child(ambient)


func _build_particles() -> void:
    particle_effects = Node2D.new()
    particle_effects.name = "ParticleEffects"
    particle_effects.z_index = 3
    add_child(particle_effects)

    var golden_dust := _make_particles(
        "GoldenDust",
        68,
        8.5,
        Vector2(760.0, 445.0),
        Vector2(500.0, 275.0),
        Vector2(-0.15, -1.0),
        Vector2(-1.2, -2.8),
        4.0,
        13.0,
        Color(1.0, 0.88, 0.48, 0.42),
        _make_soft_particle_texture(14, 2.2)
    )
    golden_dust.scale_amount_min = 0.35
    golden_dust.scale_amount_max = 1.15

    var window_air := _make_particles(
        "WindowAir",
        34,
        10.0,
        Vector2(350.0, 335.0),
        Vector2(315.0, 245.0),
        Vector2(1.0, -0.12),
        Vector2(1.1, -0.5),
        7.0,
        18.0,
        Color(0.72, 0.91, 1.0, 0.30),
        _make_soft_particle_texture(10, 2.0)
    )
    window_air.scale_amount_min = 0.30
    window_air.scale_amount_max = 0.90

    var leaf_specks := _make_particles(
        "LeafSpecks",
        12,
        9.0,
        Vector2(385.0, 285.0),
        Vector2(300.0, 205.0),
        Vector2(0.82, 0.32),
        Vector2(0.7, 1.6),
        5.0,
        12.0,
        Color(0.48, 0.62, 0.25, 0.30),
        _make_leaf_particle_texture()
    )
    leaf_specks.spread = 24.0
    leaf_specks.angular_velocity_min = -42.0
    leaf_specks.angular_velocity_max = 42.0
    leaf_specks.scale_amount_min = 0.42
    leaf_specks.scale_amount_max = 0.95


func _make_particles(
    node_name: String,
    particle_amount: int,
    particle_lifetime: float,
    emitter_position: Vector2,
    emitter_extents: Vector2,
    particle_direction: Vector2,
    particle_gravity: Vector2,
    velocity_min: float,
    velocity_max: float,
    particle_color: Color,
    particle_texture: Texture2D
) -> CPUParticles2D:
    var particles := CPUParticles2D.new()
    particles.name = node_name
    particles.amount = particle_amount
    particles.lifetime = particle_lifetime
    particles.preprocess = particle_lifetime
    particles.randomness = 0.72
    particles.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
    particles.emission_rect_extents = emitter_extents
    particles.position = emitter_position
    particles.direction = particle_direction.normalized()
    particles.spread = 18.0
    particles.gravity = particle_gravity
    particles.initial_velocity_min = velocity_min
    particles.initial_velocity_max = velocity_max
    particles.color = particle_color
    particles.texture = particle_texture
    particle_effects.add_child(particles)
    return particles


func _make_soft_particle_texture(size: int, falloff: float) -> ImageTexture:
    var image := Image.create(size, size, false, Image.FORMAT_RGBA8)
    var center := Vector2(float(size - 1), float(size - 1)) * 0.5
    var radius: float = float(size) * 0.5
    for y: int in range(size):
        for x: int in range(size):
            var distance_ratio: float = Vector2(float(x), float(y)).distance_to(center) / radius
            var alpha: float = pow(maxf(0.0, 1.0 - distance_ratio), falloff)
            image.set_pixel(x, y, Color(1.0, 1.0, 1.0, alpha))
    return ImageTexture.create_from_image(image)


func _make_leaf_particle_texture() -> ImageTexture:
    var size := Vector2i(18, 10)
    var image := Image.create(size.x, size.y, false, Image.FORMAT_RGBA8)
    var center := Vector2(float(size.x - 1), float(size.y - 1)) * 0.5
    var radius := Vector2(float(size.x) * 0.5, float(size.y) * 0.5)
    for y: int in range(size.y):
        for x: int in range(size.x):
            var normalized := (Vector2(float(x), float(y)) - center) / radius
            var distance_ratio: float = normalized.length()
            var alpha: float = 1.0 - smoothstep(0.72, 1.0, distance_ratio)
            image.set_pixel(x, y, Color(1.0, 1.0, 1.0, alpha))
    return ImageTexture.create_from_image(image)


func _update_particles() -> void:
    var ratio: float = motion_strength / ACTIVE_MOTION_STRENGTH
    particle_effects.modulate.a = clampf(ratio, 0.0, 1.0)
    for child: Node in particle_effects.get_children():
        if child is CPUParticles2D:
            child.speed_scale = maxf(0.08, ratio)
            child.emitting = ratio > 0.02


func _build_camera() -> void:
    camera = Camera2D.new()
    camera.name = "BreathingCamera"
    camera.position = CAMERA_CENTER
    camera.enabled = true
    add_child(camera)


func _animate_camera() -> void:
    var strength: float = motion_strength
    var drift := Vector2(
        sin(elapsed * 0.17) * 2.2,
        cos(elapsed * 0.13 + 0.7) * 1.3
    ) * strength
    camera.position = CAMERA_CENTER + drift
    var zoom_value: float = 1.0 + sin(elapsed * 0.19 + 1.2) * 0.0035 * strength
    camera.zoom = Vector2(zoom_value, zoom_value)


func _save_demo_screenshot() -> void:
    var image: Image = get_viewport().get_texture().get_image()
    if image == null:
        push_warning("当前渲染驱动不提供视口纹理，跳过预览截图。")
        return
    var output_path := ProjectSettings.globalize_path("res://assets/art/daily/protagonist_cinematic_desk_godot_preview_v01.png")
    var save_error: Error = image.save_png(output_path)
    if save_error != OK:
        push_error("无法保存动态场景预览：%s" % error_string(save_error))
