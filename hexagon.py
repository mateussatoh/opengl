import sys
import glm # Versão em Python da OpenGL Mathematics (GLM)
import OpenGL.GL as gl # Funcoes da API OpenGL
import OpenGL.GLUT as glut # Criacao de janelas acesso ao teclado
import numpy as np


# Variáveis globais
shaderProgramRef = None
VertexBufferObject = None # VBO
VertexArrayObject = None # VAO

number_vertices = None

#Shaders escritos na linguagem GLSL
vertex_shader_codigo= """
in vec3 position;
void main()
{
    gl_Position = vec4(position.x, position.y, position.z, 1.0f);
}
"""

fragment_shader_codigo= """
out vec4 FragColor;
void main()
{
    FragColor = vec4(1.0f, 1.0f, 0.0f, 1.0f);
}
"""
        
def create_triangulo_vertices():

    # === a) Define dados dos vertices da geometria ===
    
    # Vertices do triangulo
    vert1 = glm.vec3(-0.5, -0.5, 0.0) # esquerda embaixo
    vert2 = glm.vec3(0.5, -0.5, 0.0) # direita embaixo
    vert3 = glm.vec3(0.0, 0.5, 0.0) # centro cima 
    triangulo = glm.mat3(vert1, vert2, vert3) 
    return triangulo

def create_star_vertices():
    lista_vertices = [
        [0.0, 0.5, 0.0],
        [0.1, 0.3, 0.0],
        [0.3, 0.3, 0.0],
        [0.2, 0.1, 0.0],
        [0.3, -0.1, 0.0],
        [0.1, -0.1, 0.0],
        [0.0, -0.3, 0.0],
        [-0.1, -0.1, 0.0],
        [-0.3, -0.1, 0.0],
        [-0.2, 0.1, 0.0],
        [-0.3, 0.3, 0.0],
        [-0.1, 0.3, 0.0]
    ]

    vertices = np.array(lista_vertices, dtype=np.float32)
    quant_vertices = len(vertices)
    #print("quant_vertices: {}".format(quant_vertices))
    
    return vertices, quant_vertices

def create_hex_vertices():
    '''
    Vertices para desenhar Hexagono
    '''
    lista_vertices = [
        [ 0.1,  0.4,  0.0],
        [ 0.4,  0.2,  0.0],
        [0.4,  -0.1,  0.0],
        [0.1,  -0.4,  0.0],
        [-0.4, -0.2,  0.0],
        [ -0.3, 0.3,  0.0]
    ]

    vertices = np.array(lista_vertices, dtype=np.float32)
    quant_vertices = len(vertices)
    #print("quant_vertices: {}".format(quant_vertices))
    
    return vertices, quant_vertices


# === C) Cria os objetos OpenGL VBO e VAO ===
def create_VBO_VAO(data_to_buffer):

    global VertexBufferObject # (VBO)
    global VertexArrayObject # (VAO)

    # Cria um objeto Buffer (VBO) para armazenar os vertices da geometria
    VertexBufferObject = gl.glGenBuffers(1) # Cria o buffer (VBO) para armazenar os vértices
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VertexBufferObject) # Efetua o bind do VBO
    # Envia os dados para o buffer
    gl.glBufferData(target=gl.GL_ARRAY_BUFFER, size= glm.sizeof(data_to_buffer), data=glm.value_ptr(data_to_buffer), usage=gl.GL_STATIC_DRAW)

    # Cria um objeto Buffer (VAO) que descreve a forma de organização 
    # dos dados dentro do objeto Vertex Buffer (VBO)
    VertexArrayObject = gl.glGenVertexArrays(1) # Cria ID para objeto OpenGL VAO
    gl.glBindVertexArray(VertexArrayObject) # Vincula objeto OpenGL VAO

    # Ponteiro para o atributo dentro do código do Shader
    indice = gl.glGetAttribLocation(shaderProgramRef, 'vPos') # Obtem a localização variável vPos dentro do shader program

    vertexDim = 3 # Quantidade de posições em vPos (Vertex Shader), que são 3 pois é do tipo vec3
    stride = 0 # Espaço entre os dados (i.e. cada vértice)
    offset = None # Onde os dados iniciam no Vertex Buffer
    # Descreve a forma de organização dos dados dentro do último buffer (VBO) vinculado (glBindBuffer)
    gl.glVertexAttribPointer(indice, vertexDim, gl.GL_FLOAT, gl.GL_FALSE, stride, offset) 
    gl.glEnableVertexAttribArray(indice) # Associa e habilita os dados do Vertex Buffer (VBO) no Array

    # Desvincula o VAO
    gl.glBindVertexArray(0) # Importante: Unbind do VAO primeiro
    # Desabilita das outras coisas
    gl.glDisableVertexAttribArray(indice)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0) 


def refer_to_var_program( program_ref, var_in_program, var_data_type, vbo_ref):
    '''
    '''

    var_ref = gl.glGetAttribLocation( program_ref, var_in_program)

    # If the program does not reference the variable, then exit
    if var_ref != -1:
        # Select buffer used by the following functions
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_ref)
        # Specify how data will be read from the currently bound buffer into the specified variable
        # glVertexAttribPointer esta associando ao VAO (chamado anteriormete) o VBO com variavel do shader, 
        # i.e., ao VAO ativo no momento.
        if var_data_type == "int":
            gl.glVertexAttribPointer(var_ref, 1, gl.GL_INT, False, 0, None)
        elif var_data_type == "float":
            gl.glVertexAttribPointer(var_ref, 1, gl.GL_FLOAT, False, 0, None)
        elif var_data_type == "vec2":
            gl.glVertexAttribPointer(var_ref, 2, gl.GL_FLOAT, False, 0, None)
        elif var_data_type == "vec3":
            gl.glVertexAttribPointer(var_ref, 3, gl.GL_FLOAT, False, 0, None)
        elif var_data_type == "vec4":
            gl.glVertexAttribPointer(var_ref, 4, gl.GL_FLOAT, False, 0, None)
        else:
            raise Exception(f'Erro Shader : Variavel {var_in_program} com tipo desconhecido = {var_data_type}.')
        # Indicate that data will be streamed to this variable
        gl.glEnableVertexAttribArray(var_ref)
    else:
        return -1


def data_buffer(data_to_buffer, program_ref, var_in_program, var_data_type):
    '''
    Observacao:
        data_to_buffer: pode ser atualizada caso os vertices sejam alterados.
        Nesse caso esta funcao pode ser chamada novamente.
    '''

    # Converte os dados para numpy com float de 32 bits
    data = np.array(data_to_buffer).astype(np.float32)

    VertexBufferObject = gl.glGenBuffers(1) # Referencia para um buffer (VBO) disponivel na GPU

    # Seleciona o buffer
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VertexBufferObject) # Cria buffer (VBO) object

    # Armazena os dados no buffer selecionado
    gl.glBufferData(gl.GL_ARRAY_BUFFER, data.ravel(), gl.GL_STATIC_DRAW)
    #gl.glBufferData(target=gl.GL_ARRAY_BUFFER, size= glm.sizeof(data), data=glm.value_ptr(data), usage=gl.GL_STATIC_DRAW)

    refer_to_var_program(program_ref, var_in_program, var_data_type, VertexBufferObject)


def draw_hexagono():
    '''
    '''
    global shaderProgramRef 
    shaderProgramRef = init_shader_program(vertex_shader_codigo, fragment_shader_codigo)

    # Cria um objeto Buffer (VAO) que descreve a forma de organização 
    # dos dados dentro do objeto Vertex Buffer (VBO)
    VertexArrayObject = gl.glGenVertexArrays(1) # Cria ID para objeto OpenGL VAO
    gl.glBindVertexArray(VertexArrayObject) # Vincula objeto OpenGL VAO

    # Especifica os dados da geometria
    #data_vertices = create_triangulo_vertices() 
    data_vertices, quant_vert = create_hex_vertices()

    # program var
    data_buffer(data_to_buffer=data_vertices, program_ref=shaderProgramRef, var_in_program='position', var_data_type='vec3')

    return quant_vert

def display():

    gl.glClearColor(0.5, 0.5, 0.5, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    gl.glUseProgram(shaderProgramRef)


    gl.glDrawArrays(gl.GL_TRIANGLE_FAN, 0, number_vertices)

    # # === d) Chama o Programa Shader ativo e 
    # # desenha conforme os dados do VBO no VAO ===
    # gl.glUseProgram(shaderProgramRef)
    # gl.glBindVertexArray(VertexArrayObject) # Chamada ao VAO
    
    # # Quantos vertices do triangulo serão utilizados
    # quant_vertices = 3 
    # # Chamada do OpenGL para desenhar conforme o VAO
    # gl.glDrawArrays(gl.GL_TRIANGLES, 0, quant_vertices) 

    # gl.glBindVertexArray(0) # Desvincula o VAO
    # gl.glUseProgram(0) # Desvincula o Shader Program

    glut.glutSwapBuffers()


def reshape(width,height):
    gl.glViewport(0, 0, width, height)


def keyboard( key, x, y ):
    print("TECLA PRESSIONADA: {}".format(key))
    if key == b'\x1b': # ESC
        sys.exit( ) 

def init_shader(codigo_shader, tipo_shader, glsl_version_str = '#version 330\n'): 

    # glsl_version_str = '#version 330\n'
    codigo_shader = glsl_version_str + codigo_shader

    # Compilar vertex shader
    shader_object = gl.glCreateShader(tipo_shader) # Cria objeto shader do tipo GL_VERTEX_SHADER
    gl.glShaderSource(shader_object, codigo_shader) # Associa o código fonte ao objeto
    gl.glCompileShader(shader_object) # Compila o shader

    sucesso_compilacao = gl.glGetShaderiv(shader_object, gl.GL_COMPILE_STATUS)

    if not sucesso_compilacao:
        mensagem_erro = gl.glGetShaderInfoLog(shader_object).decode('utf-8')
        gl.glDeleteShader(shader_object)  
        raise RuntimeError(mensagem_erro)
    
    return shader_object

def init_shader_program(vertex_shader_codigo, fragment_shader_codigo):

    vertex_shader_object = init_shader(vertex_shader_codigo, gl.GL_VERTEX_SHADER)
    fragment_shader_object = init_shader(fragment_shader_codigo, gl.GL_FRAGMENT_SHADER)

    shaderProgram = gl.glCreateProgram()

    gl.glAttachShader(shaderProgram, vertex_shader_object)
    gl.glAttachShader(shaderProgram, fragment_shader_object)
    
    gl.glLinkProgram(shaderProgram)

    sucesso_linking = gl.glGetProgramiv(shaderProgram, gl.GL_LINK_STATUS)

    if not sucesso_linking:
        mensagem_erro = gl.glGetProgramInfoLog(shaderProgram).decode('utf-8')
        gl.glDeleteProgram(shaderProgram)  
        raise RuntimeError(mensagem_erro)
    
    return shaderProgram


def init_window(title_str, largura, altura):
    
    glut.glutInit()
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
    glut.glutInitWindowSize(largura, altura)
    glut.glutCreateWindow(title_str)

def main_opengl(titulo_janela):
    print(" ==== main_opengl ====")

    init_window(titulo_janela, 400, 400)

    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)

    global number_vertices
    number_vertices = draw_hexagono()

    glut.glutMainLoop()

if __name__ == '__main__':

    titulo_janela = 'HEXAGONO'
    print("\n")
    print(titulo_janela)
    print("\n")

    main_opengl(titulo_janela)