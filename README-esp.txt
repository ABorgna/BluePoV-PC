The BluePov driver for PC
-------------------------

Contenidos:
1. Funcionamiento
2. Funciones
    2.1 Comandos
        2.1.1 Lectura
        2.1.2 Escritura
    2.2 Datos
3. Paquetes
    3.1 Token (TKN)



1. Funcionamiento

Luego de establecer una coneccion con el dispositivo permite transmitir datos y comandos a este.

La comunicacion se realiza por medio de paquetes, que seguiran siempre el esquema

TOKEN->DATA->ACK
  m     m     s       Master/Slave

    El Token llevara el codigo de operacion. (1 byte)

    Luego se transmiten los datos, si fuesen necesarios.

    El ACK informa que el dispositivo recibio y ejecuto la operacion, y se devuelve el resultado de esta. (2 bytes)

El la cantidad de pixeles se puede modificar dinamicamente, asi como la cantidad de colores y la densidad de columnas.

2. Funciones

Dividimos en dos categorias, datos y comandos.

2.1 Comandos

Divididos a su vez en lectura y escritura.

2.1.1 Lectura

Ping: Responde con la misma data que se mando si el dispositivo esta operativo.

Velocidad: Devuelve las revoluciones por segundo del motor.

Get Height: Altura actual de la pantalla

Get Width: Ancho actual de la pantalla

Get Depht: Profundidad de color actual.

Get Total Width: Cantidad de columnas en todo el circulo.

2.1.2 Escritura

Store: Guarda en ROM el contenido actual de la pantalla.

Clean: Borra la pantalla. (Rellena con negro).

Set Height: Altura de la pantalla

Set Width: Ancho de la pantalla

Set Depht: Profundidad de color.

Set Total Width: Cantidad de columnas en todo el circulo (Varia el ancho del pixel).

2.2 Datos

Write column: Actualiza una columna,
    1er byte de data: Direccion horizontal.
    Luego: Datos

Write section: Actualiza un grupo de columnas,
    1er byte de data: Direccion horizontal de inicio.
    2do byte de data: Direccion horizontal final.
    Luego: Datos

Burst: Envia toda la pantalla, columna por columna, secuencialmente.

Interlaced burst: Envia toda la pantalla, primero columnas pares y luego las impares.

3. Paquetes

Cada paquete se conforma de tres secciones; TKN, DATA, ACK.

3.1 Token (TKN)

Contiene el codigo de operacion a realizar, longitud de 1 byte.

3.1.1 Codigos de operacion

0x00 Ping
0x01 Leer velocidad
0x04 Get height
0x05 Get width
0x06 Get depht
0x07 Get total width

0x10 Store
0x11 Clean
0x14 Set height
0x15 Set width
0x16 Set depht
0x17 Set total width

0x80 Write column
0x81 Write section
0x82 Burst
0x83 Interlaced burst

3.2 Data (DATA)

Longitud variable segun la operacion, contiene los datos necesarios para realizarla.

3.3 Token (TKN)

2 bytes de largo, contiene el resultado de la operacion.

Valores especiales:

0xffff Sin errores
0xfff. Error (Y codigo de error)

3.3.1 Errores

0xff00 Error en el codigo de operacion
0xfff1 Datos invalidos / fuera de rango
0xfff2 Motor detenido
