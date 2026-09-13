extends Node2D


const BACKGROUND: Texture2D = preload("res://assets/art/daily/protagonist_cinematic_desk_v01.png")
const MOTION_SHADER: Shader = preload("res://shaders/cinematic_desk_motion.gdshader")
const AMBIENT_SCRIPT: Script = preload("res://scripts/cinematic_desk_ambient.gd")
const VIEW_SIZE := Vector2(1672.0, 941.0)
const CAMERA_CENTER := Vector2(836.0, 470.5)

var elapsed: float = 0.0
var motion_strength: float = 1.0
var motion_enabled: bool = true
var screenshot_saved: bool = false
var render_demo: bool = false
var background_material: ShaderMaterial
var ambient: Node2D
var camera: Camera2D


func _ready() -> void:
    render_demo = "--render-demo" in OS.get_cmdline_user_args()
    _build_background()
    _build_ambient()
    _build_camera()


func _process(delta: float) -> void:
    elapsed += delta
    var target_strength: float = 1.0 if motion_enabled else 0.0
    motion_strength = move_toward(motion_strength, target_strength, delta * 0.65)
    background_material.set_shader_parameter("motion_strength", motion_strength)
    ambient.call("set_intensity", motion_strength)
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
