shader_type canvas_item;

uniform float motion_strength : hint_range(0.0, 2.0) = 1.25;

float ellipse_mask(vec2 uv, vec2 center, vec2 radius, float feather) {
    float distance_from_center = length((uv - center) / radius);
    return 1.0 - smoothstep(1.0 - feather, 1.0, distance_from_center);
}

void fragment() {
    vec2 uv = UV;
    float strength = motion_strength;

    float curtain_mask = ellipse_mask(uv, vec2(0.445, 0.275), vec2(0.075, 0.28), 0.48);
    float curtain_wave = sin(TIME * 0.62 + uv.y * 11.0) * 0.0024;
    uv.x += curtain_wave * curtain_mask * strength;

    float window_plant_mask = ellipse_mask(uv, vec2(0.405, 0.505), vec2(0.090, 0.225), 0.50);
    float shelf_vine_mask = ellipse_mask(uv, vec2(0.728, 0.190), vec2(0.086, 0.145), 0.56);
    float left_foreground_mask = ellipse_mask(uv, vec2(0.055, 0.765), vec2(0.110, 0.260), 0.58);
    float right_foreground_mask = ellipse_mask(uv, vec2(0.885, 0.865), vec2(0.160, 0.170), 0.60);
    uv.x += sin(TIME * 0.92 + uv.y * 15.0) * 0.0025 * window_plant_mask * strength;
    uv.x += sin(TIME * 0.73 + uv.y * 19.0 + 1.3) * 0.0022 * shelf_vine_mask * strength;
    uv.x += sin(TIME * 0.66 + uv.y * 10.0 + 0.4) * 0.0018 * left_foreground_mask * strength;
    uv.x -= sin(TIME * 0.61 + uv.y * 12.0 + 2.0) * 0.0016 * right_foreground_mask * strength;

    float torso_mask = ellipse_mask(uv, vec2(0.532, 0.455), vec2(0.082, 0.175), 0.52);
    float head_mask = ellipse_mask(uv, vec2(0.532, 0.315), vec2(0.047, 0.070), 0.48);
    float breath = sin(TIME * 1.35);
    uv.y += breath * 0.00105 * torso_mask * strength;
    uv.x += sin(TIME * 0.56 + 0.8) * 0.00055 * head_mask * strength;

    float keyboard_hand = ellipse_mask(uv, vec2(0.572, 0.493), vec2(0.036, 0.038), 0.58);
    float mouse_hand = ellipse_mask(uv, vec2(0.596, 0.486), vec2(0.028, 0.034), 0.58);
    uv.x += sin(TIME * 2.45) * 0.00075 * keyboard_hand * strength;
    uv.y += sin(TIME * 2.05 + 1.7) * 0.00048 * mouse_hand * strength;

    float desk_files_mask = ellipse_mask(uv, vec2(0.674, 0.453), vec2(0.058, 0.045), 0.62);
    float loose_paper_mask = ellipse_mask(uv, vec2(0.617, 0.461), vec2(0.045, 0.032), 0.62);
    float paper_lift = sin(TIME * 0.82 + 0.5) * 0.5 + sin(TIME * 1.73) * 0.22;
    float paper_ripple = sin(TIME * 1.18 + uv.x * 42.0) * 0.00055;
    uv.y += (paper_lift * 0.00145 + paper_ripple) * desk_files_mask * strength;
    uv.y += sin(TIME * 0.96 + uv.x * 36.0 + 1.1) * 0.00115 * loose_paper_mask * strength;
    uv.x += sin(TIME * 0.70 + 2.4) * 0.00065 * desk_files_mask * strength;

    vec4 color = texture(TEXTURE, clamp(uv, vec2(0.001), vec2(0.999)));
    float light_breath = sin(TIME * 0.23) * 0.5 + 0.5;
    color.rgb *= 1.0 + light_breath * 0.012 * strength;
    COLOR = color;
}
