uniform mat4 flat_to_screen;

out vec3 fBarycentric;

void vertex_shader(in vec4 position, in vec3 barycentric, out vec4 new_position, in int in_index){
    new_position = flat_to_screen * position;
    fBarycentric = barycentric;
}

