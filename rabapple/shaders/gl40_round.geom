#version 400

layout(triangles) in;
layout(line_strip, max_vertices=4) out; 

in vec4 tePosition[];

void main(){
    
    gl_Position = tePosition[0];
    EmitVertex();
    gl_Position = tePosition[1];
    EmitVertex();
    gl_Position = tePosition[2];
    EmitVertex();
    gl_Position = tePosition[0];
    EmitVertex();
    EndPrimitive();
}

