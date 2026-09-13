extends Node2D


const VIEW_SIZE := Vector2(1672.0, 941.0)
const DUST_COUNT: int = 42
const WINDOW_DUST_COUNT: int = 18

var elapsed: float = 0.0
var intensity: float = 1.0
var dust_particles: Array[Vector4] = []
var window_particles: Array[Vector4] = []


func _ready() -> void:
    var random := RandomNumberGenerator.new()
    random.seed = 20260913
    for index: int in range(DUST_COUNT):
        dust_particles.append(Vector4(
            random.randf_range(430.0, 1320.0),
            random.randf_range(160.0, 760.0),
            random.randf_range(4.0, 11.0),
            random.randf_range(0.0, TAU)
        ))
    for index: int in range(WINDOW_DUST_COUNT):
        window_particles.append(Vector4(
            random.randf_range(60.0, 720.0),
            random.randf_range(90.0, 590.0),
            random.randf_range(5.0, 13.0),
            random.randf_range(0.0, TAU)
        ))


func _process(delta: float) -> void:
    elapsed += delta
    queue_redraw()


func set_intensity(value: float) -> void:
    intensity = clampf(value, 0.0, 1.5)


func _draw() -> void:
    if intensity <= 0.001:
        return

    var sunlight_pulse: float = 0.5 + sin(elapsed * 0.28) * 0.5
    var beam_alpha: float = (0.016 + sunlight_pulse * 0.012) * intensity
    draw_colored_polygon(
        PackedVector2Array([
            Vector2(12.0, 44.0),
            Vector2(120.0, 44.0),
            Vector2(770.0, 820.0),
            Vector2(560.0, 820.0)
        ]),
        Color(1.0, 0.84, 0.48, beam_alpha)
    )
    draw_colored_polygon(
        PackedVector2Array([
            Vector2(330.0, 40.0),
            Vector2(395.0, 40.0),
            Vector2(1010.0, 820.0),
            Vector2(870.0, 820.0)
        ]),
        Color(1.0, 0.90, 0.62, beam_alpha * 0.62)
    )

    for index: int in range(dust_particles.size()):
        var data: Vector4 = dust_particles[index]
        var drift_x: float = sin(elapsed * 0.31 + data.w) * (8.0 + float(index % 4) * 2.0)
        var travel: float = fmod(elapsed * data.z + data.y, 620.0)
        var position := Vector2(data.x + drift_x, 790.0 - travel)
        var shimmer: float = 0.5 + sin(elapsed * 1.2 + data.w) * 0.5
        var alpha: float = (0.035 + shimmer * 0.075) * intensity
        var radius: float = 0.9 + float(index % 3) * 0.55
        draw_circle(position, radius, Color(1.0, 0.93, 0.68, alpha))

    for index: int in range(window_particles.size()):
        var data: Vector4 = window_particles[index]
        var travel_x: float = fmod(elapsed * data.z + data.x, 690.0)
        var position := Vector2(36.0 + travel_x, data.y + sin(elapsed * 0.42 + data.w) * 8.0)
        var alpha: float = (0.025 + (sin(elapsed * 0.9 + data.w) + 1.0) * 0.022) * intensity
        draw_circle(position, 1.0 + float(index % 2) * 0.6, Color(0.86, 0.95, 1.0, alpha))

    var monitor_pulse: float = 0.5 + sin(elapsed * 0.92) * 0.5
    _draw_ellipse(
        Vector2(972.0, 430.0),
        Vector2(145.0, 92.0),
        Color(0.35, 0.69, 0.94, (0.018 + monitor_pulse * 0.015) * intensity),
        -0.05
    )
    _draw_ellipse(
        Vector2(934.0, 478.0),
        Vector2(94.0, 42.0),
        Color(0.46, 0.75, 1.0, (0.012 + monitor_pulse * 0.010) * intensity),
        -0.10
    )

    var floor_glow: float = 0.5 + sin(elapsed * 0.24 + 0.8) * 0.5
    _draw_ellipse(
        Vector2(690.0 + sin(elapsed * 0.18) * 18.0, 758.0),
        Vector2(290.0, 34.0),
        Color(1.0, 0.71, 0.30, (0.010 + floor_glow * 0.012) * intensity),
        -0.08
    )


func _draw_ellipse(center: Vector2, radius: Vector2, color: Color, rotation: float) -> void:
    var points := PackedVector2Array()
    for index: int in range(32):
        var angle: float = TAU * float(index) / 32.0
        points.append(center + Vector2(cos(angle) * radius.x, sin(angle) * radius.y).rotated(rotation))
    draw_colored_polygon(points, color)
