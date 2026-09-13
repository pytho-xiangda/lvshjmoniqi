shader_type canvas_item;

uniform float motion_strength : hint_range(0.0, 1.5) = 1.0;

float ellipse_mask(vec2 uv, vec2 center, vec2 radius, float feather) {
    float distance_from_center = length((uv - center) / radius);
    return 1.0 - smoothstep(1.0 - feather, 1.0, distance_from_center);
}

void fragment() {
    vec2 uv = UV;
    float strength = motion_strength;

    float curtain_mask = ellipse_mask(uv, vec2(0.445, 0.275), vec2(0.075, 0.28), 0.48);
    float curtain_wave = sin(TIME * 0.62 + uv.y * 11.0) * 0.0018;
    uv.x += curtain_wave * curtain_mask * strength;

    float foliage_mask = ellipse_mask(uv, vec2(0.420, 0.505), vec2(0.090, 0.225), 0.50);
    uv.x += sin(TIME * 0.78 + uv.y * 13.0) * 0.0011 * foliage_mask * strength;

    float torso_mask = ellipse_mask(uv, vec2(0.532, 0.455), vec2(0.082, 0.175), 0.52);
    float head_mask = ellipse_mask(uv, vec2(0.532, 0.315), vec2(0.047, 0.070), 0.48);
    float breath = sin(TIME * 1.35);
    uv.y += breath * 0.00105 * torso_mask * strength;
    uv.x += sin(TIME * 0.56 + 0.8) * 0.00055 * head_mask * strength;

    float keyboard_hand = ellipse_mask(uv, vec2(0.572, 0.493), vec2(0.036, 0.038), 0.58);
    float mouse_hand = ellipse_mask(uv, vec2(0.596, 0.486), vec2(0.028, 0.034), 0.58);
    uv.x += sin(TIME * 2.45) * 0.00075 * keyboard_hand * strength;
    uv.y += sin(TIME * 2.05 + 1.7) * 0.00048 * mouse_hand * strength;

    vec4 color = texture(TEXTURE, clamp(uv, vec2(0.001), vec2(0.999)));
    float light_breath = sin(TIME * 0.23) * 0.5 + 0.5;
    color.rgb *= 1.0 + light_breath * 0.012 * strength;
    COLOR = color;
}
