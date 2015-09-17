#version 330

out vec4 vPosition;
out float vWidth;
out int vStyle;
out float vMiterThreashold;

void point_shader(out vec4 position, out float width, out int style);

void main(){

    vec4 position;
    float width;
    int style;
    
    point_shader(position, width, style);

    vPosition = position;
    vWidth = width;
    vStyle = style;
    
    float T = 2.5;
    vMiterThreashold = 1.0/(T*T);
}

