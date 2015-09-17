out vec4 color;

in vec3 fBarycentric;

float edgeFactor(in vec3 barycentric){
    vec3 d = fwidth(barycentric);
    vec3 a3 = smoothstep(vec3(0.0), d*1.5, barycentric);
    return min(min(a3.x, a3.y), a3.z);
}

void fragment_shader(){
    color = vec4(1,0,0,1);
    
    color.a = 1.0;
    color.rgb = mix(vec3(0.0), vec3(0.5), edgeFactor(fBarycentric));
}