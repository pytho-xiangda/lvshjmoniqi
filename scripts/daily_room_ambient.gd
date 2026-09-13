extends Node2D


var elapsed: float = 0.0
var character_x: float = 1360.0
var monitor_strength: float = 0.0
var footstep_pulse: float = 0.0
var seat_pulse: float = 0.0


func _process(delta: float) -> void:
    elapsed += delta
    footstep_pulse = move_toward(footstep_pulse, 0.0, delta * 4.8)
    seat_pulse = move_toward(seat_pulse, 0.0, delta * 1.7)
    queue_redraw()


func set_monitor_on(enabled: bool, instant: bool = false) -> void:
    var target: float = 1.0 if enabled else 0.0
    if instant:
        monitor_strength = target
        return
    var tween := create_tween()
    tween.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
    tween.tween_property(self, "monitor_strength", target, 0.9)


func pulse_footstep() -> void:
    footstep_pulse = 1.0


func pulse_seat() -> void:
    seat_pulse = 1.0


func _draw() -> void:
    var light_drift: float = sin(elapsed * 0.34) * 14.0
    _draw_ellipse(Vector2(218.0 + light_drift, 774.0), Vector2(92.0, 18.0), Color(1.0, 0.90, 0.62, 0.075), -0.18)
    _draw_ellipse(Vector2(414.0 + light_drift * 0.7, 816.0), Vector2(126.0, 24.0), Color(1.0, 0.92, 0.68, 0.065), -0.12)
    _draw_ellipse(Vector2(570.0 + light_drift * 0.4, 758.0), Vector2(72.0, 15.0), Color(1.0, 0.94, 0.73, 0.055), -0.16)

    var cloud_progress: float = fmod(elapsed * 12.0, 2050.0) - 260.0
    _draw_ellipse(Vector2(cloud_progress, 690.0), Vector2(185.0, 38.0), Color(0.31, 0.39, 0.30, 0.022), -0.08)
    _draw_ellipse(Vector2(cloud_progress - 330.0, 735.0), Vector2(125.0, 27.0), Color(0.28, 0.36, 0.27, 0.018), 0.05)

    var warmth: float = (sin(elapsed * 0.22) + 1.0) * 0.5
    draw_rect(Rect2(0.0, 0.0, 660.0, 690.0), Color(1.0, 0.88, 0.58, 0.008 + warmth * 0.012), true)

    var screen_alpha: float = 0.025 + monitor_strength * 0.16 + (sin(elapsed * 1.15) + 1.0) * 0.012
    draw_rect(Rect2(247.0, 446.0, 112.0, 71.0), Color(0.56, 0.78, 0.78, screen_alpha), true)
    if monitor_strength > 0.01:
        _draw_ellipse(Vector2(312.0, 520.0), Vector2(122.0, 48.0), Color(0.55, 0.78, 0.78, monitor_strength * 0.035), -0.10)

    for index: int in range(18):
        var x: float = 105.0 + fmod(float(index * 83), 510.0)
        x += sin(elapsed * 0.42 + float(index) * 1.7) * 9.0
        var y: float = 165.0 + fmod(float(index * 119), 470.0)
        y += cos(elapsed * 0.29 + float(index)) * 7.0
        var alpha: float = 0.08 + float(index % 4) * 0.018
        draw_circle(Vector2(x, y), 1.1 + float(index % 3) * 0.45, Color(1.0, 0.96, 0.78, alpha))

    for index: int in range(7):
        var mote_x: float = 90.0 + fmod(elapsed * (5.0 + float(index) * 0.7) + float(index * 137), 560.0)
        var mote_y: float = 630.0 - fmod(elapsed * (7.0 + float(index) * 0.4) + float(index * 83), 420.0)
        var mote_alpha: float = 0.05 + (sin(elapsed * 1.1 + float(index)) + 1.0) * 0.025
        draw_circle(Vector2(mote_x, mote_y), 1.3, Color(1.0, 0.94, 0.72, mote_alpha))

    var branch_sway: float = sin(elapsed * 0.48) * 5.0
    for index: int in range(12):
        var leaf := Vector2(126.0 + fmod(float(index * 97), 458.0), 112.0 + fmod(float(index * 71), 238.0))
        var leaf_offset := Vector2(branch_sway * (0.45 + float(index % 4) * 0.16), sin(elapsed * 0.39 + float(index)) * 2.0)
        _draw_ellipse(leaf + leaf_offset, Vector2(9.0, 4.5), Color(0.32, 0.43, 0.24, 0.075), -0.65 + float(index % 5) * 0.28)

    var leaf_sway: float = sin(elapsed * 0.73) * 3.5
    for index: int in range(9):
        var base := Vector2(1161.0 + float(index % 3) * 18.0, 469.0 + float(index / 3) * 17.0)
        _draw_ellipse(base + Vector2(leaf_sway * (0.55 + float(index % 3) * 0.18), 0.0), Vector2(8.0, 4.0), Color(0.25, 0.36, 0.20, 0.10), -0.45 + float(index % 3) * 0.4)

    var clock_center := Vector2(1166.0, 247.0)
    var clock_angle: float = elapsed * TAU / 60.0 - PI * 0.5
    draw_line(clock_center, clock_center + Vector2(cos(clock_angle), sin(clock_angle)) * 26.0, Color(0.28, 0.19, 0.13, 0.68), 1.5, true)

    var shadow_width: float = 48.0 + footstep_pulse * 5.0
    var shadow_alpha: float = 0.15 + footstep_pulse * 0.055
    _draw_ellipse(Vector2(character_x, 793.0), Vector2(shadow_width, 9.0 - footstep_pulse * 1.2), Color(0.10, 0.075, 0.06, shadow_alpha), 0.0)
    _draw_ellipse(Vector2(350.0 - seat_pulse * 3.0, 790.0), Vector2(62.0 + seat_pulse * 4.0, 8.0), Color(0.10, 0.075, 0.06, seat_pulse * 0.07), 0.0)


func _draw_ellipse(center: Vector2, radius: Vector2, color: Color, rotation: float) -> void:
    var points := PackedVector2Array()
    for index: int in range(28):
        var angle: float = TAU * float(index) / 28.0
        var point := Vector2(cos(angle) * radius.x, sin(angle) * radius.y).rotated(rotation)
        points.append(center + point)
    draw_colored_polygon(points, color)
