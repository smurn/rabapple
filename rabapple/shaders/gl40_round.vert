#version 400

in vec4 bfrCenter;

in vec4 bfrStart_bfrEnd;
#define bfrStart bfrStart_bfrEnd.xy
#define bfrEnd bfrStart_bfrEnd.zw
in vec2 bfrOther;

out vec4 vCenter;
out vec2 vStart;
out vec2 vEnd;
out vec2 vOther;

void main(){
    vCenter = bfrCenter;
    vStart = bfrStart;
    vEnd = bfrEnd;
    vOther = bfrOther;
}

