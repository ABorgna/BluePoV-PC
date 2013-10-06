The BluePov driver for PC
-------------------------

b = driver.BluePov("70:05:14:CE:65:11",(16,8))

Contenidos:
a. Dependencias
1. Funcionamiento
2. Funciones
    2.1 Comandos
        2.1.1 Lectura
        2.1.2 Escritura
    2.2 Datos
3. Paquetes
    3.1 Token (TKN)

a. Dependencias

    . Python 2/3
    . Numpy - python3-numpy
    . Pygame - from source
        - python3-dev
        - ffmpeg
        - libsdl1.2-dev
        - libsdl-image1.2-dev
        - libavcodec-dev
        - libavformat-dev
        - libswscale-dev
        - libportmidi-dev
        - libsdl-ttf2.0-dev
        - libsmpeg-dev
        - libfreetype6-dev
        - libsdl-mixer1.2-dev
        - libsdl-pango-dev
        - libjpeg-dev
        - libpng12-dev

    Comunicaciones:
        py3 - Bluetooth nativo
        py2 - Pybluez
        py2/3 - Pyserial - python-serial

b. Todo

- Separate bluetooth.connect
- Detect disconnection
- Set screen X-offset
  Cambiar nombre funcion encoder (sacar *_func)
  Devolver bytes
  Agregar opciones al encoder


1. Funcionamiento

Luego de establecer una coneccion con el dispositivo permite transmitir datos y comandos a este.

La comunicacion se realiza por medio de paquetes, que seguiran siempre el esquema

Enviado (master):
        TOKEN->DATA
len:     1 B   n B

Respuesta (slave):
        ACK
len:    2 B

    El Token llevara el codigo de operacion. (1 byte)

    Luego se transmiten los datos, si fuesen necesarios.

    El ACK informa que el dispositivo recibio y ejecuto la operacion, y se devuelve el resultado de esta. (2 bytes)

    La trama termina cuando no hay comunicacion por mas de 100uS.

La cantidad de pixeles se puede modificar dinamicamente, asi como la cantidad de colores y la densidad de columnas.

2. Funciones

Dividimos en dos categorias, datos y comandos.

2.1 Comandos

Divididos a su vez en lectura y escritura, bytes de data entre parentesis.

2.1.1 Lectura

Ping: (1B) Responde con la misma data que se mando si el dispositivo esta operativo.

Get fps: (0B) Devuelve las revoluciones por segundo del motor.

Get Height: (0B) Altura actual de la pantalla

Get Width: (0B) Ancho actual de la pantalla

Get Depth: (0B) Profundidad de color actual.

Get Total Width: (0B) Cantidad de columnas en todo el circulo.

2.1.2 Escritura

Store: (0B) Guarda en ROM el contenido actual de la pantalla.

Clean: (0B) Borra la pantalla. (Rellena con negro).

Set Height: (2B) Altura de la pantalla

Set Width: (2B) Ancho de la pantalla

Set Depth: (1B) Profundidad de color.

Set Total Width: (2B) Cantidad de columnas en todo el circulo (Varia el ancho del pixel).

2.2 Datos

Write column: Actualiza una columna,
    1er byte de data: Direccion horizontal.
    Luego: Datos

Write section: Actualiza un grupo de columnas,
    1er byte de data: Direccion horizontal de inicio.
    2do byte de data: Cantidad de columnas.
    Luego: Datos

Burst: Envia toda la pantalla, columna por columna, secuencialmente.

Interlaced burst: Envia toda la pantalla, primero columnas pares y luego las impares.

3. Paquetes

Cada paquete se conforma de tres secciones; TKN, DATA, ACK.

3.1 Token (TKN)

Contiene un byte, el codigo de operacion

3.1.2 Codigos de operacion

0x00 Ping
0x01 Get fps
0x04 Get height
0x05 Get width
0x06 Get depth
0x07 Get total width

0x10 Store
0x11 Clean
0x14 Set height
0x15 Set width
0x16 Set depth
0x17 Set total width

0x80 Write column
0x81 Write section
0x82 Burst
0x83 Interlaced burst

3.2 Data (DATA)

Longitud variable segun la operacion, contiene los datos necesarios para realizarla.

3.3 Acknowledge (ACK)

2 bytes de largo, contiene el resultado de la operacion.

Valores especiales:

0xffff Sin errores
0xff.. Error (Y codigo de error)

3.3.1 Errores

0xff00 Error en el codigo de operacion
0xfff1 Datos invalidos / fuera de rango
0xfff2 Motor detenido


