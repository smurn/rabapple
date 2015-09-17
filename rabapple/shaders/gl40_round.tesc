#version 400

layout(vertices = 1) out;

in vec4 vCenter[];
in vec2 vStart[];
in vec2 vEnd[];
in vec2 vOther[];

patch out vec4 tcCenter;
patch out vec2 tcStart;
patch out vec2 tcEnd;
patch out vec2 tcOther;

patch out float tcStartAngle;
patch out float tcEndAngle;
patch out float tcRadius;

uniform mat4 flat_to_pixel;

const float roundness = 5;

const float PI = 3.1415926535897932384626433832795;

void main(){
    tcCenter = vCenter[0];
    tcStart = vStart[0];
    tcEnd = vEnd[0];
    tcOther = vOther[0];
    
    tcRadius = length(tcStart);
    
    tcStartAngle = atan(tcStart.y, tcStart.x);
    tcEndAngle = atan(tcEnd.y, tcEnd.x);
    tcEndAngle = tcEndAngle >= tcStartAngle ? tcEndAngle : tcEndAngle + 2*PI;

    vec4 round_from = tcCenter + vec4(tcStart, 0, 0);
    vec4 round_to = tcCenter + vec4(tcEnd, 0, 0);

    round_from = flat_to_pixel * round_from;
    round_to = flat_to_pixel * round_to;
    round_from /= round_from.w;
    round_to /= round_to.w;
    
    float dist = distance(round_from.xy, round_to.xy);
    
    int segments = int((dist + roundness) / roundness);
    segments = clamp(segments, 3, 20);
    
    gl_TessLevelInner[0] = 1;
    gl_TessLevelOuter[0] = segments;
    gl_TessLevelOuter[1] = 1;
    gl_TessLevelOuter[2] = 1;
}
