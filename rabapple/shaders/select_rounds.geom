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

out vec2 fb_round_from;
out vec2 fb_round_to;


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

void round_join(
    in vec2 a, 
    in vec2 b, 
    in float r,
    in vec4 location)
{
    float sin_ab = cross(vec3(a,0), vec3(b,0)).z;
    float mirror = sign(sin_ab);
    mirror = mirror == 0 ? 1 : mirror;
    
    vec2 offset_from = rot_ccw(b) * r * mirror;
    vec2 offset_to = rot_cw(a) * r * mirror;

    vec4 round_from = location + vec4(offset_from, 0, 0);
    vec4 round_to = location + vec4(offset_to, 0, 0);
    
    round_from = flat_to_pixel * round_from;
    round_to = flat_to_pixel * round_to;
    round_from /= round_from.w;
    round_to /= round_to.w;
    
    vec2 straight = round_to.xy - round_from.xy;
    
    if (dot(straight,straight) > roundness2){
        gl_Position = location;
        fb_round_from = offset_from;
        fb_round_to = round_to;
        EmitVertex(); EndPrimitive();
    }
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

    float r1 = vWidth[1]/2.0;
    float r2 = vWidth[2]/2.0;
    
    if (vStyle[1] == ROUND_JOIN){
        round_join(-d_01, d_12, r1, vPosition[1]);
    }
    if (vStyle[1] == ROUND_END){
        
    }


}