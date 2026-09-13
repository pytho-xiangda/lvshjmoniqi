extends Node2D


const BACKGROUND: Texture2D = preload("res://assets/art/daily/daily_room_side_v04.png")
const WALK_ATLAS: Texture2D = preload("res://assets/art/daily/characters/protagonist_side_walk_v07.png")
const IDLE_TEXTURE: Texture2D = preload("res://assets/art/daily/characters/protagonist_side_idle_v07.png")
const AMBIENT_SCRIPT: Script = preload("res://scripts/daily_room_ambient.gd")

const VIEW_SIZE := Vector2(1672.0, 941.0)
const GROUND_Y: float = 795.0
const DOOR_X: float = 1360.0
const DESK_X: float = 650.0
const MIN_X: float = 555.0
const MAX_X: float = 1420.0
const FRAME_SIZE := Vector2(448.0, 640.0)
const FOOT_Y: float = 610.0
const WALK_SPEED: float = 140.0
const ACCELERATION: float = 310.0

var character: AnimatedSprite2D
var ambient: Node2D
var curtain_left: Node2D
var curtain_right: Node2D
var status_label: Label
var action_panel: PanelContainer
var action_title: Label
var velocity_x: float = 0.0
var target_x: float = DESK_X
var elapsed: float = 0.0
var start_delay: float = 0.85
var screenshot_saved: bool = false
var render_demo: bool = false


func _ready() -> void:
    render_demo = "--render-demo" in OS.get_cmdline_user_args()
    _build_room()
    _build_ambient_motion()
    _build_character()
    _build_interface()
    _set_target(DESK_X, "轻松走向电脑桌……")


func _process(delta: float) -> void:
    elapsed += delta
    _animate_room()
    ambient.set("character_x", character.position.x)
    if start_delay > 0.0:
        start_delay -= delta
        return
    _update_walk(delta)
    if render_demo and not screenshot_saved and elapsed >= 3.4:
        screenshot_saved = true
        call_deferred("_save_demo_screenshot")
    if render_demo and elapsed >= 7.4:
        get_tree().quit()


func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed:
        if event.keycode == KEY_SPACE:
            _replay()
        elif event.keycode == KEY_ESCAPE:
            get_tree().quit()
    elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        if event.position.y > 700.0:
            _set_target(clampf(event.position.x, MIN_X, MAX_X), "走过去看看……")


func _build_room() -> void:
    var background := Sprite2D.new()
    background.name = "Background"
    background.texture = BACKGROUND
    background.centered = false
    add_child(background)


func _build_ambient_motion() -> void:
    ambient = AMBIENT_SCRIPT.new()
    ambient.name = "AmbientMotion"
    add_child(ambient)
    curtain_left = _add_swaying_crop("CurtainLeft", Rect2(25.0, 82.0, 92.0, 520.0), Vector2(71.0, 82.0))
    curtain_right = _add_swaying_crop("CurtainRight", Rect2(526.0, 82.0, 112.0, 525.0), Vector2(582.0, 82.0))


func _add_swaying_crop(node_name: String, region: Rect2, pivot_position: Vector2) -> Node2D:
    var pivot := Node2D.new()
    pivot.name = node_name
    pivot.position = pivot_position
    var atlas := AtlasTexture.new()
    atlas.atlas = BACKGROUND
    atlas.region = region
    var sprite := Sprite2D.new()
    sprite.texture = atlas
    sprite.position = Vector2(0.0, region.size.y * 0.5)
    sprite.modulate = Color(1.0, 1.0, 1.0, 0.88)
    pivot.add_child(sprite)
    add_child(pivot)
    return pivot


func _build_character() -> void:
    var frames := SpriteFrames.new()
    frames.add_animation("walk")
    frames.set_animation_speed("walk", 8.0)
    frames.set_animation_loop("walk", true)
    for index: int in range(8):
        var frame := AtlasTexture.new()
        frame.atlas = WALK_ATLAS
        frame.region = Rect2(float(index % 4) * FRAME_SIZE.x, float(index / 4) * FRAME_SIZE.y, FRAME_SIZE.x, FRAME_SIZE.y)
        frames.add_frame("walk", frame)
    frames.add_animation("idle")
    frames.set_animation_speed("idle", 1.0)
    frames.set_animation_loop("idle", true)
    frames.add_frame("idle", IDLE_TEXTURE)

    character = AnimatedSprite2D.new()
    character.name = "Protagonist"
    character.sprite_frames = frames
    character.position = Vector2(DOOR_X, GROUND_Y)
    character.offset = Vector2(0.0, -(FOOT_Y - FRAME_SIZE.y * 0.5))
    character.animation = "idle"
    add_child(character)


func _build_interface() -> void:
    var layer := CanvasLayer.new()
    layer.name = "Interface"
    add_child(layer)
    var root := Control.new()
    root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    root.mouse_filter = Control.MOUSE_FILTER_IGNORE
    layer.add_child(root)

    var header := PanelContainer.new()
    header.position = Vector2(34.0, 28.0)
    header.size = Vector2(612.0, 92.0)
    header.add_theme_stylebox_override("panel", _panel_style(Color(0.12, 0.095, 0.07, 0.78), Color(0.72, 0.58, 0.38, 0.70), 16.0))
    root.add_child(header)
    var header_box := VBoxContainer.new()
    header_box.add_theme_constant_override("separation", 2)
    header.add_child(header_box)
    var kicker := Label.new()
    kicker.text = "律师模拟器 · 日常房间 Godot 演示"
    kicker.add_theme_font_size_override("font_size", 18)
    kicker.add_theme_color_override("font_color", Color("d8bd8e"))
    header_box.add_child(kicker)
    status_label = Label.new()
    status_label.text = "午后的房间"
    status_label.add_theme_font_size_override("font_size", 30)
    status_label.add_theme_color_override("font_color", Color("fff6df"))
    header_box.add_child(status_label)

    var controls := HBoxContainer.new()
    controls.position = Vector2(1120.0, 38.0)
    controls.add_theme_constant_override("separation", 12)
    root.add_child(controls)
    controls.add_child(_make_button("去电脑桌", _set_target.bind(DESK_X, "轻松走向电脑桌……")))
    controls.add_child(_make_button("去门口", _set_target.bind(DOOR_X, "走向门口……")))

    var hint := Label.new()
    hint.position = Vector2(38.0, 882.0)
    hint.text = "点击地板移动   Space 重新演示   Esc 退出"
    hint.add_theme_font_size_override("font_size", 20)
    hint.add_theme_color_override("font_color", Color(0.20, 0.16, 0.12, 0.82))
    root.add_child(hint)

    action_panel = PanelContainer.new()
    action_panel.position = Vector2(64.0, 652.0)
    action_panel.size = Vector2(420.0, 178.0)
    action_panel.visible = false
    action_panel.add_theme_stylebox_override("panel", _panel_style(Color(0.96, 0.91, 0.80, 0.94), Color(0.42, 0.31, 0.20, 0.72), 18.0))
    root.add_child(action_panel)
    var action_box := VBoxContainer.new()
    action_box.add_theme_constant_override("separation", 8)
    action_panel.add_child(action_box)
    action_title = Label.new()
    action_title.text = "回到日常"
    action_title.add_theme_font_size_override("font_size", 27)
    action_title.add_theme_color_override("font_color", Color("3d3025"))
    action_box.add_child(action_title)
    var action_text := Label.new()
    action_text.text = "整理卷宗  ·  检索法条  ·  查看来信"
    action_text.add_theme_font_size_override("font_size", 19)
    action_text.add_theme_color_override("font_color", Color("665342"))
    action_box.add_child(action_text)


func _make_button(text: String, callback: Callable) -> Button:
    var button := Button.new()
    button.text = text
    button.custom_minimum_size = Vector2(156.0, 54.0)
    button.mouse_filter = Control.MOUSE_FILTER_STOP
    button.add_theme_font_size_override("font_size", 20)
    button.add_theme_color_override("font_color", Color("fff7e4"))
    button.add_theme_stylebox_override("normal", _panel_style(Color(0.16, 0.13, 0.10, 0.78), Color(0.75, 0.60, 0.36, 0.72), 14.0))
    button.add_theme_stylebox_override("hover", _panel_style(Color(0.25, 0.20, 0.13, 0.90), Color(0.88, 0.72, 0.43, 0.92), 14.0))
    button.pressed.connect(callback)
    return button


func _panel_style(background_color: Color, border_color: Color, radius: float) -> StyleBoxFlat:
    var style := StyleBoxFlat.new()
    style.bg_color = background_color
    style.border_color = border_color
    style.set_border_width_all(1)
    style.set_corner_radius_all(int(radius))
    style.content_margin_left = 22.0
    style.content_margin_right = 22.0
    style.content_margin_top = 14.0
    style.content_margin_bottom = 14.0
    return style


func _animate_room() -> void:
    curtain_left.rotation = sin(elapsed * 0.55) * 0.012
    curtain_right.rotation = -sin(elapsed * 0.51 + 0.8) * 0.010


func _set_target(value: float, message: String) -> void:
    target_x = clampf(value, MIN_X, MAX_X)
    action_panel.visible = false
    if status_label != null:
        status_label.text = message


func _update_walk(delta: float) -> void:
    var distance: float = target_x - character.position.x
    var direction: float = signf(distance)
    var braking_distance: float = velocity_x * velocity_x / (2.0 * ACCELERATION)
    var desired_speed: float = direction * WALK_SPEED
    if absf(distance) <= braking_distance + 10.0:
        desired_speed = direction * minf(WALK_SPEED, sqrt(maxf(0.0, 2.0 * ACCELERATION * absf(distance))))
    velocity_x = move_toward(velocity_x, desired_speed, ACCELERATION * delta)
    if absf(distance) <= 1.5 and absf(velocity_x) <= 18.0:
        character.position.x = target_x
        velocity_x = 0.0
        if character.animation != "idle":
            character.play("idle")
            _arrived()
        return

    character.position.x += velocity_x * delta
    if signf(target_x - character.position.x) != direction:
        character.position.x = target_x
    character.flip_h = velocity_x > 0.0
    if character.animation != "walk":
        character.play("walk")
    character.speed_scale = clampf(absf(velocity_x) / WALK_SPEED, 0.68, 1.0)


func _arrived() -> void:
    if absf(character.position.x - DESK_X) < 3.0:
        status_label.text = "已经走到电脑桌前"
        action_title.text = "今天从哪件事开始？"
        action_panel.visible = true
    elif absf(character.position.x - DOOR_X) < 3.0:
        status_label.text = "已经走到门口"
        action_title.text = "准备去哪里？"
        action_panel.visible = true
    else:
        status_label.text = "停下来看看"


func _replay() -> void:
    character.position.x = DOOR_X
    character.flip_h = false
    character.play("idle")
    velocity_x = 0.0
    start_delay = 0.65
    elapsed = 0.0
    screenshot_saved = false
    _set_target(DESK_X, "午后的房间")


func _save_demo_screenshot() -> void:
    await RenderingServer.frame_post_draw
    var image: Image = get_viewport().get_texture().get_image()
    image.save_png(ProjectSettings.globalize_path("res://assets/art/daily/daily_room_godot_preview_v07.png"))
