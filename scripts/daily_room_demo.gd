extends Node2D


const BACKGROUND: Texture2D = preload("res://assets/art/daily/daily_room_side_v04.png")
const AMBIENT_SCRIPT: Script = preload("res://scripts/daily_room_ambient.gd")
const CHARACTER_SCRIPT: Script = preload("res://scripts/daily_room_character.gd")

const VIEW_SIZE := Vector2(1672.0, 941.0)
const GROUND_Y: float = 795.0
const DOOR_X: float = 1360.0
const WALK_STOP_X: float = 410.0
const SEAT_X: float = 320.0
const MIN_X: float = 360.0
const MAX_X: float = 1420.0
const CAMERA_HOME := Vector2(836.0, 470.0)
const CAMERA_WALK := Vector2(725.0, 470.0)
const CAMERA_DESK := Vector2(470.0, 500.0)

var character: Node2D
var ambient: Node2D
var camera: Camera2D
var curtain_left: Node2D
var curtain_right: Node2D
var hanging_lamp: Node2D
var window_leaves: Node2D
var room_plant: Node2D
var status_label: Label
var action_panel: PanelContainer
var action_title: Label
var elapsed: float = 0.0
var screenshot_saved: bool = false
var render_demo: bool = false
var sequence_running: bool = false
var fade: ColorRect


func _ready() -> void:
    render_demo = "--render-demo" in OS.get_cmdline_user_args()
    _build_room()
    _build_ambient_motion()
    _build_character()
    _build_camera()
    _build_interface()
    call_deferred("_play_desk_sequence", true)


func _process(delta: float) -> void:
    elapsed += delta
    _animate_room()
    ambient.set("character_x", character.position.x)
    if render_demo and not screenshot_saved and elapsed >= 10.8:
        screenshot_saved = true
        call_deferred("_save_demo_screenshot")
    if render_demo and elapsed >= 12.4:
        get_tree().quit()


func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and not event.echo:
        if event.keycode == KEY_SPACE:
            call_deferred("_play_desk_sequence", true)
        elif event.keycode == KEY_ESCAPE:
            get_tree().quit()
    elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        if event.position.y > 700.0 and not sequence_running:
            call_deferred("_walk_to_free_point", clampf(event.position.x, MIN_X, MAX_X))


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
    hanging_lamp = _add_swaying_crop("HangingLamp", Rect2(750.0, 12.0, 150.0, 108.0), Vector2(825.0, 12.0))
    window_leaves = _add_bottom_swaying_crop("WindowLeaves", Rect2(0.0, 115.0, 158.0, 310.0), Vector2(79.0, 425.0))
    room_plant = _add_bottom_swaying_crop("RoomPlant", Rect2(1128.0, 410.0, 122.0, 210.0), Vector2(1189.0, 620.0))


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


func _add_bottom_swaying_crop(node_name: String, region: Rect2, pivot_position: Vector2) -> Node2D:
    var pivot := Node2D.new()
    pivot.name = node_name
    pivot.position = pivot_position
    var atlas := AtlasTexture.new()
    atlas.atlas = BACKGROUND
    atlas.region = region
    var sprite := Sprite2D.new()
    sprite.texture = atlas
    sprite.position = Vector2(0.0, -region.size.y * 0.5)
    sprite.modulate = Color(1.0, 1.0, 1.0, 0.72)
    pivot.add_child(sprite)
    add_child(pivot)
    return pivot


func _build_character() -> void:
    character = CHARACTER_SCRIPT.new()
    character.name = "Protagonist"
    character.position = Vector2(DOOR_X, GROUND_Y)
    character.z_index = 4
    add_child(character)
    character.connect("footstep", _on_footstep)


func _build_camera() -> void:
    camera = Camera2D.new()
    camera.name = "PerformanceCamera"
    camera.position = CAMERA_HOME
    camera.zoom = Vector2(1.035, 1.035)
    camera.position_smoothing_enabled = true
    camera.position_smoothing_speed = 4.2
    camera.enabled = true
    add_child(camera)


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
    kicker.text = "律师模拟器 · 日常房间"
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
    controls.add_child(_make_button("去电脑桌", _request_desk))
    controls.add_child(_make_button("去门口", _request_door))

    var hint := Label.new()
    hint.position = Vector2(38.0, 882.0)
    hint.text = "点击地板移动   Space 重播完整演出   Esc 退出"
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

    fade = ColorRect.new()
    fade.name = "Fade"
    fade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
    fade.color = Color(0.055, 0.045, 0.035, 1.0)
    root.add_child(fade)


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
    hanging_lamp.rotation = sin(elapsed * 0.43 + 0.6) * 0.0045
    window_leaves.rotation = sin(elapsed * 0.67 + 0.9) * 0.010
    room_plant.rotation = -sin(elapsed * 0.74 + 1.7) * 0.012


func _play_desk_sequence(reset_first: bool) -> void:
    if sequence_running:
        return
    sequence_running = true
    action_panel.visible = false
    if reset_first:
        await _fade_to(1.0, 0.28)
        character.call("reset_at", Vector2(DOOR_X, GROUND_Y))
        character.call("set_facing", false)
        camera.position = CAMERA_HOME
        camera.zoom = Vector2(1.035, 1.035)
        ambient.call("set_monitor_on", false, true)
        await _fade_to(0.0, 0.62)

    if character.call("is_seated"):
        await character.call("stand_up", WALK_STOP_X)
    status_label.text = "准备出发……"
    await get_tree().create_timer(0.32).timeout
    await character.call("anticipate")
    await get_tree().create_timer(0.10).timeout

    status_label.text = "轻松走向电脑桌……"
    var distance: float = absf(character.position.x - WALK_STOP_X)
    var duration: float = character.call("duration_for", distance)
    _tween_camera(CAMERA_WALK, Vector2(1.055, 1.055), duration + 0.35)
    await character.call("walk_to_x", WALK_STOP_X, duration)

    status_label.text = "在椅子前停一下……"
    await get_tree().create_timer(0.40).timeout
    ambient.call("pulse_seat")
    await character.call("sit_down", SEAT_X)

    status_label.text = "电脑已经打开"
    ambient.call("set_monitor_on", true, false)
    _tween_camera(CAMERA_DESK, Vector2(1.16, 1.16), 1.60)
    await get_tree().create_timer(1.62).timeout
    action_title.text = "今天从哪件事开始？"
    action_panel.visible = true
    sequence_running = false


func _walk_to_free_point(target_x: float) -> void:
    if sequence_running:
        return
    sequence_running = true
    action_panel.visible = false
    ambient.call("set_monitor_on", false, false)
    if character.call("is_seated"):
        status_label.text = "起身……"
        await character.call("stand_up", WALK_STOP_X)
        await get_tree().create_timer(0.18).timeout
    await character.call("anticipate")
    var duration: float = character.call("duration_for", character.position.x - target_x)
    _tween_camera(CAMERA_HOME, Vector2(1.035, 1.035), duration + 0.35)
    status_label.text = "走过去看看……"
    await character.call("walk_to_x", target_x, duration)
    status_label.text = "已经走到门口" if absf(target_x - DOOR_X) < 3.0 else "停下来看看"
    if absf(target_x - DOOR_X) < 3.0:
        action_title.text = "准备去哪里？"
        action_panel.visible = true
    sequence_running = false


func _request_desk() -> void:
    if not sequence_running:
        call_deferred("_play_desk_sequence", false)


func _request_door() -> void:
    if not sequence_running:
        call_deferred("_walk_to_free_point", DOOR_X)


func _tween_camera(target_position: Vector2, target_zoom: Vector2, duration: float) -> void:
    var camera_tween := create_tween().set_parallel(true)
    camera_tween.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
    camera_tween.tween_property(camera, "position", target_position, duration)
    camera_tween.tween_property(camera, "zoom", target_zoom, duration)


func _fade_to(alpha: float, duration: float) -> void:
    var fade_tween := create_tween()
    fade_tween.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
    fade_tween.tween_property(fade, "color:a", alpha, duration)
    await fade_tween.finished


func _on_footstep() -> void:
    ambient.call("pulse_footstep")


func _save_demo_screenshot() -> void:
    await RenderingServer.frame_post_draw
    var image: Image = get_viewport().get_texture().get_image()
    image.save_png(ProjectSettings.globalize_path("res://assets/art/daily/daily_room_godot_preview_v10.png"))
