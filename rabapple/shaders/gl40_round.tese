#version 400

layout(triangles) in;

patch in vec4 tcCenter;
patch in vec2 tcStart;
patch in vec2 tcEnd;
patch in vec2 tcOther;
patch in float tcStartAngle;
patch in float tcEndAngle;
patch in float tcRadius;

out vec4 tePosition;

void vertex_shader(in vec4 position, in vec3 barycentric, out vec4 new_position, in int in_index);

void main(){
    vec2 offset;
    vec3 barycentric = gl_TessCoord;
    
    if (gl_TessCoord[0] > 0){
        offset = tcOther;
        barycentric = vec3(1,0,0);
    }else{
    
        float start_weight = gl_TessCoord[1];
        float end_weight = gl_TessCoord[2];
    
        int k = int(gl_TessLevelOuter[0]*end_weight+0.5) % 2;
        barycentric.y = k;
        barycentric.z = 1-k;
    

        
        if (start_weight == 1.0){
            offset = tcStart;
        }else if (start_weight == 0.0){
            offset = tcEnd;
        }else{
            float angle = tcStartAngle * start_weight + tcEndAngle * end_weight;
            offset = vec2(cos(angle), sin(angle)) * tcRadius;
        }        
    }

    
    vec4 position = tcCenter;
    position.xy += offset;
   
    vertex_shader(position, barycentric, gl_Position, 0);
    //gl_Position = position;
    tePosition = gl_Position;
    
    
    
}
