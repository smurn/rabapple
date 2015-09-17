#pragma in_attribs bfrPosition bfrStyle

uniform mat4 model_to_flat;

in vec4 bfrPosition;
in int bfrStyle;

void point_shader(out vec4 position, out float width, out int style){
    position = model_to_flat * bfrPosition;
    width = 30;
    style = bfrStyle;
}
