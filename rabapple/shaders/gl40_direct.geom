#version 330

const int BEVEL_JOIN = 0;
const int MITER_JOIN = 1;
const int ROUND_JOIN = 2;
const int FLAT_END = 3;
const int BUTT_END = 4;
const int ROUND_END = 5;
const int DISCARD = 6;

const float roundness2 = 10*10;


layout(lines_adjacency) in;
layout(triangle_strip, max_vertices=6) out; 

in vec4 vPosition[];
in float vWidth[];
in int vStyle[];
in float vMiterThreashold[];

uniform mat4 flat_to_pixel;


void vertex_shader(in vec4 position, in vec3 barycentric, out vec4 new_position, in int in_index);

vec4 shade_vertex(in vec4 position, in vec3 barycentric, in int in_index){
    vec4 new_position;
    vertex_shader(position, barycentric, new_position, in_index);
    return new_position;
}

vec2 rot_cw(in vec2 v){
	return vec2(v.y, -v.x);
}

vec2 rot_ccw(in vec2 v){
    return vec2(-v.y, v.x);
}

void flat_end_calculations(
    in vec2 b,
    in float r,
    out vec2 left,
    out vec2 right,
    out vec2 third
){
    vec2 nb = rot_ccw(b)*r;
    left = nb;
    right = -nb;
    third = left;
}

void but_end_calculations(
    in vec2 b,
    in float r,
    out vec2 left,
    out vec2 right,
    out vec2 third
){
    vec2 staight = b * r;
    vec2 nb = rot_ccw(staight);
    left = nb - staight;
    right = -nb - staight;
    third = left;
}

void join_calculations(
    in vec2 a, 
    in vec2 b, 
    in float r, 
    in int style,
    in float miter_threashold,
    in float bb,
    in vec4 location,
    out vec2 left,
    out vec2 right,
    out vec2 third)
{
    float sin_ab = cross(vec3(a,0), vec3(b,0)).z;
    float cos_ab = dot(a,b);
    float mirror = sign(sin_ab);
    mirror = mirror == 0 ? 1 : mirror;
    a.x *= mirror;
    b.x *= mirror;
    
    vec2 c = cos_ab < 0 ? rot_cw(b - a) : a+b;
    vec2 nb = rot_ccw(b);
    float c_nb = dot(c,nb);
    float cc = dot(c,c);
    
    bool outer_miter_ok = cc * miter_threashold <= c_nb*c_nb;
    bool inner_miter_ok = r*r * cc <= 0.25 * bb * c_nb*c_nb;
    
    vec2 miter_point = c / c_nb;
    vec2 bevel_point = c_nb / cc * c;
    
    vec2 left_tmp;
    vec2 right_tmp;

    if (style == ROUND_JOIN){
        left_tmp = nb;
        
        vec2 from_offset = nb * r;
        vec2 to_offset = rot_cw(a) * r;
        from_offset.x *= mirror;
        to_offset.x *= mirror;
        
        vec4 round_from = location + vec4(from_offset, 0, 0);
        vec4 round_to = location + vec4(to_offset, 0, 0);

        round_from = flat_to_pixel * round_from;
        round_to = flat_to_pixel * round_to;
        round_from /= round_from.w;
        round_to /= round_to.w;
        
        vec2 straight = round_to.xy - round_from.xy;
        
        if (dot(straight,straight) <= roundness2){
            third = -normalize(c);
        }else{
            third = left_tmp;
        }
    }else if (style == MITER_JOIN && outer_miter_ok){
        left_tmp = miter_point;
        third = left_tmp;
    }else{
        left_tmp = nb;
        third = bevel_point;
    }
    
    if (inner_miter_ok){
        right_tmp = -miter_point;
    }else{
        right_tmp = -nb;
    }
    
    left_tmp *= r;
    right_tmp *= r;
    third *= r;
    
    left = mirror > 0 ? left_tmp : right_tmp;
    right = mirror > 0 ? right_tmp : left_tmp;
    
    left.x *= mirror;
    right.x *= mirror;
    third.x *= mirror;
}


void main(){

    
    if (vStyle[1] == DISCARD || vStyle[2] == DISCARD){
        return;
    }
    

    vec2 d_01 = vPosition[1].xy - vPosition[0].xy;
    vec2 d_12 = vPosition[2].xy - vPosition[1].xy;
    vec2 d_23 = vPosition[3].xy - vPosition[2].xy;
    
    float l_12 = dot(d_12, d_12);
    
    d_01 = normalize(d_01);
    d_12 = normalize(d_12);
    d_23 = normalize(d_23);

    vec2 start_left;
    vec2 start_right;
    vec2 start_third;
    vec2 end_left;
    vec2 end_right;
    vec2 end_third;
    
    float r1 = vWidth[1]/2.0;
    float r2 = vWidth[2]/2.0;

    if (vStyle[1] == FLAT_END){
        flat_end_calculations(d_12, r1, start_left, start_right, start_third);
    }else if (vStyle[1] == BUTT_END){
        but_end_calculations(d_12, r1, start_left, start_right, start_third);
    }else{
        join_calculations(-d_01, d_12, r1, vStyle[1],  vMiterThreashold[1], l_12, vPosition[1], start_left, start_right, start_third);
    }
 
    if (vStyle[2] == FLAT_END){
        flat_end_calculations(-d_12, r2, end_right, end_left, end_third);
    }else if (vStyle[2] == BUTT_END){
        but_end_calculations(-d_12, r2, end_right, end_left, end_third);
    }else{ 
        join_calculations(d_23, -d_12, r2, vStyle[2],  vMiterThreashold[2], l_12, vPosition[2], end_right, end_left, end_third);
    }
    
    gl_Position = vPosition[1]+vec4(start_third,0,0);
    gl_Position = shade_vertex(gl_Position, vec3(0,0,1), 1);
    EmitVertex();
    
    gl_Position = vPosition[1]+vec4(start_left,0,0);
    gl_Position = shade_vertex(gl_Position, vec3(0,1,0), 1);
    EmitVertex();
    
    gl_Position = vPosition[1]+vec4(start_right,0,0);
    gl_Position = shade_vertex(gl_Position, vec3(1,0,0), 1);
    EmitVertex();
    
    gl_Position = vPosition[2]+vec4(end_left,0,0);
    gl_Position = shade_vertex(gl_Position, vec3(0,0,1), 2);
    EmitVertex();
    
    gl_Position = vPosition[2]+vec4(end_right,0,0);
    gl_Position = shade_vertex(gl_Position, vec3(0,1,0), 2);
    EmitVertex();
    
    gl_Position = vPosition[2]+vec4(end_third,0,0);
    gl_Position = shade_vertex(gl_Position, vec3(1,0,0), 2);
    EmitVertex();
    EndPrimitive();
}