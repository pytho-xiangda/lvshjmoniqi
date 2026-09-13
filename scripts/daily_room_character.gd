extends Node2D


signal footstep
signal state_changed(state_name: String)

const WALK_ATLAS: Texture2D = preload("res://assets/art/daily/characters/protagonist_side_walk_v09.png")
const SIT_ATLAS: Texture2D = preload("res://assets/art/daily/characters/protagonist_side_sit_v10.png")
const IDLE_TEXTURE: Texture2D = preload("res://assets/art/daily/characters/protagonist_side_idle_v07.png")
const FRAME_SIZE := Vector2(448.0, 640.0)
const FOOT_Y: float = 610.0
const BASE_OFFSET := Vector2(0.0, -(FOOT_Y - FRAME_SIZE.y * 0.5))
const CRUISE_SPEED: float = 140.0
const STRIDE_LENGTH: float = 140.0

enum State { IDLE, ANTICIPATE, WALK, SIT, SIT_IDLE }

var visual: Node2D
var primary: AnimatedSprite2D
var secondary: AnimatedSprite2D
var state: State = State.IDLE
var facing_right: bool = false
var walk_phase: float = 0.0
var actual_speed: float = 0.0
var _last_x: float = 0.0
var _last_step: int = -1
var _fade_tween: Tween
var _move_tween: Tween


func _ready() -> void:
    visual = Node2D.new()
    visual.name = "Visual"
    add_child(visual)
    var frames := _build_frames()
    primary = _make_sprite("Primary", frames, 1.0)
    secondary = _make_sprite("BlendLayer", frames, 0.0)
    primary.animation = "idle"
    primary.play()
    _last_x = position.x


func _process(delta: float) -> void:
    var moved: float = position.x - _last_x
    actual_speed = absf(moved) / maxf(delta, 0.0001)
    _last_x = position.x

    if state == State.WALK:
        walk_phase = fmod(walk_phase + absf(moved) / STRIDE_LENGTH * TAU, TAU)
        _apply_walk_frame(primary)
        _apply_walk_frame(secondary)
        _apply_walk_secondary_motion()
        _emit_footstep_if_needed()
    elif state == State.IDLE:
        _apply_idle_motion()
    elif state == State.SIT_IDLE:
        _apply_seated_idle_motion()
    else:
        actual_speed = 0.0


func _build_frames() -> SpriteFrames:
    var frames := SpriteFrames.new()
    frames.add_animation("walk")
    frames.set_animation_speed("walk", 12.0)
    frames.set_animation_loop("walk", true)
    for index: int in range(12):
        frames.add_frame("walk", _atlas_frame(WALK_ATLAS, index))

    frames.add_animation("idle")
    frames.set_animation_speed("idle", 1.0)
    frames.set_animation_loop("idle", true)
    frames.add_frame("idle", IDLE_TEXTURE)

    frames.add_animation("sit")
    frames.set_animation_speed("sit", 8.0)
    frames.set_animation_loop("sit", false)
    for index: int in range(8):
        frames.add_frame("sit", _atlas_frame(SIT_ATLAS, index))

    frames.add_animation("sit_idle")
    frames.set_animation_speed("sit_idle", 1.0)
    frames.set_animation_loop("sit_idle", true)
    frames.add_frame("sit_idle", _atlas_frame(SIT_ATLAS, 7))
    return frames


func _atlas_frame(atlas: Texture2D, index: int) -> AtlasTexture:
    var frame := AtlasTexture.new()
    frame.atlas = atlas
    frame.region = Rect2(float(index % 4) * FRAME_SIZE.x, float(index / 4) * FRAME_SIZE.y, FRAME_SIZE.x, FRAME_SIZE.y)
    return frame


func _make_sprite(node_name: String, frames: SpriteFrames, alpha: float) -> AnimatedSprite2D:
    var sprite := AnimatedSprite2D.new()
    sprite.name = node_name
    sprite.sprite_frames = frames
    sprite.offset = BASE_OFFSET
    sprite.modulate.a = alpha
    visual.add_child(sprite)
    return sprite


func duration_for(distance: float) -> float:
    return maxf(absf(distance), 1.0) / CRUISE_SPEED


func reset_at(location: Vector2) -> void:
    if _move_tween != null and _move_tween.is_running():
        _move_tween.kill()
    if _fade_tween != null and _fade_tween.is_running():
        _fade_tween.kill()
    position = location
    _last_x = position.x
    walk_phase = 0.0
    visual.position = Vector2.ZERO
    visual.rotation = 0.0
    visual.scale = Vector2.ONE
    primary.modulate.a = 1.0
    secondary.modulate.a = 0.0
    primary.animation = "idle"
    primary.frame = 0
    primary.play()
    secondary.stop()
    state = State.IDLE
    _last_step = -1
    state_changed.emit("idle")


func anticipate() -> void:
    state = State.ANTICIPATE
    state_changed.emit("anticipate")
    var down := create_tween().set_parallel(true)
    down.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
    down.tween_property(visual, "position:y", 4.2, 0.15)
    down.tween_property(visual, "scale", Vector2(1.008, 0.992), 0.15)
    await down.finished
    var release := create_tween().set_parallel(true)
    release.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
    release.tween_property(visual, "position:y", 0.0, 0.22)
    release.tween_property(visual, "scale", Vector2.ONE, 0.22)
    await release.finished


func walk_to_x(target_x: float, duration: float = -1.0) -> void:
    set_facing(target_x > position.x)
    var distance: float = absf(target_x - position.x)
    var travel_time: float = duration if duration > 0.0 else duration_for(distance)
    state = State.WALK
    state_changed.emit("walk")
    _start_crossfade("walk", 0.22)
    _last_x = position.x

    _move_tween = create_tween()
    _move_tween.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
    _move_tween.tween_property(self, "position:x", target_x, travel_time)
    await _move_tween.finished

    state = State.IDLE
    _last_step = -1
    _start_crossfade("idle", 0.28)
    state_changed.emit("idle")


func sit_down(target_x: float = NAN) -> void:
    state = State.SIT
    state_changed.emit("sit")
    _start_crossfade("sit", 0.32)
    var seat_position: float = position.x if is_nan(target_x) else target_x
    var settle := create_tween()
    settle.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
    settle.tween_property(self, "position:x", seat_position, 0.92)
    settle.tween_interval(0.10)
    await settle.finished
    state = State.SIT_IDLE
    _start_crossfade("sit_idle", 0.28)
    state_changed.emit("sit_idle")


func stand_up(target_x: float = NAN) -> void:
    state = State.SIT
    state_changed.emit("stand")
    var target := _inactive_sprite()
    target.animation = "sit"
    target.frame = 7
    target.play_backwards("sit")
    _crossfade_layers(target, 0.30)
    var stand_position: float = position.x if is_nan(target_x) else target_x
    var rise := create_tween()
    rise.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
    rise.tween_property(self, "position:x", stand_position, 0.92)
    rise.tween_interval(0.10)
    await rise.finished
    state = State.IDLE
    _start_crossfade("idle", 0.24)
    state_changed.emit("idle")


func set_facing(value: bool) -> void:
    facing_right = value
    primary.flip_h = facing_right
    secondary.flip_h = facing_right


func is_seated() -> bool:
    return state == State.SIT_IDLE or state == State.SIT


func _start_crossfade(animation_name: StringName, duration: float) -> void:
    var target := _inactive_sprite()
    target.animation = animation_name
    target.frame = 0
    target.frame_progress = 0.0
    target.play()
    _crossfade_layers(target, duration)


func _crossfade_layers(target: AnimatedSprite2D, duration: float) -> void:
    if _fade_tween != null and _fade_tween.is_running():
        _fade_tween.kill()
    var outgoing := primary
    secondary = outgoing
    primary = target
    primary.modulate.a = 0.0
    _fade_tween = create_tween().set_parallel(true)
    _fade_tween.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
    _fade_tween.tween_property(primary, "modulate:a", 1.0, duration)
    _fade_tween.tween_property(secondary, "modulate:a", 0.0, duration)


func _inactive_sprite() -> AnimatedSprite2D:
    return secondary


func _apply_walk_frame(sprite: AnimatedSprite2D) -> void:
    if sprite.animation != "walk" or sprite.modulate.a <= 0.001:
        return
    var frame_value: float = walk_phase / TAU * 12.0
    sprite.frame = mini(11, floori(frame_value))
    sprite.frame_progress = fmod(frame_value, 1.0)


func _apply_walk_secondary_motion() -> void:
    var speed_ratio: float = clampf(actual_speed / CRUISE_SPEED, 0.0, 1.65)
    var double_step: float = sin(walk_phase * 2.0)
    var contact: float = pow(maxf(0.0, cos(walk_phase * 2.0)), 8.0)
    visual.position.y = -absf(sin(walk_phase)) * 3.2 * speed_ratio + contact * 0.8
    visual.rotation = double_step * 0.0045 * speed_ratio
    visual.scale = Vector2(1.0 + contact * 0.003, 1.0 - contact * 0.004)
    primary.offset.x = double_step * 1.2 * speed_ratio
    secondary.offset.x = primary.offset.x


func _apply_idle_motion() -> void:
    var time := Time.get_ticks_msec() * 0.001
    var breath: float = sin(time * 1.55)
    visual.position.y = -breath * 0.65
    visual.rotation = sin(time * 0.68) * 0.0018
    visual.scale = Vector2(1.0 - breath * 0.0012, 1.0 + breath * 0.0022)
    primary.offset = BASE_OFFSET
    secondary.offset = BASE_OFFSET


func _apply_seated_idle_motion() -> void:
    var time := Time.get_ticks_msec() * 0.001
    var breath: float = sin(time * 1.38)
    visual.position.y = -breath * 0.45
    visual.rotation = sin(time * 0.61) * 0.0012
    visual.scale = Vector2(1.0 - breath * 0.0008, 1.0 + breath * 0.0018)


func _emit_footstep_if_needed() -> void:
    var step: int = floori(walk_phase / PI) % 2
    if step != _last_step and actual_speed > 18.0:
        _last_step = step
        footstep.emit()
