# Script de automatización de docker para decide-ganimedes para Linux

Este script automatiza varias de las acciones más cotidianas de docker en Linux. Dichas funciones se resumen a continuación:

   * Comprobación del estado del demonio de docker (dockerd)
   * Eliminación de componentes sin uso de docker
   * Creación de usuarios de administración para web
   * Listado de imágenes, contenedores, volúmenes y redes
   * Encendido, compilado, apagado y eliminación con docker-compose 

## ¿Cómo utilizar?

Para ejecutarlo debemos dar permisos de ejecución al script. Bastará con ejecutar el siguiente comando:

```
chmod 777 dockerManager.sh
```

Por último, ejecutamos el script de la siguiente forma:

```
./dockerManager.sh
```

## Interfaz de usuario

El script controla el estado en el que se encuentra el demonio de docker. Dependiendo del estado en el que se encuentre permitirá unas acciones u otras.


### Ópción 1: Con el demonio de Docker ACTIVO

![image](https://user-images.githubusercontent.com/9322398/50784727-cc238480-12ae-11e9-90f3-d17ef01c6cae.png)

A continuación se detallan cada una de las acciones con el demonio de Docker ACTIVO:

 * Listar imágenes, contenedores, volúmenes y redes: muestra información de las imágenes, contenedores, volúmenes y redes desplegadas en el sistema.
 * Eliminar componentes de docker: despliega un menú que permite escoger qué elementos sin uso podemos eliminar.
 * Encender contenedores con docker-compose: su propio nombre lo explica.
 * Compilar contenedores con docker-compose: su propio nombre lo explica. 
 * Apagar contenedores con docker-compose: su propio nombre lo explica.
 * Eliminar contenedores con docker-compose: su propio nombre lo explica.
 * Visualizar logs con docker-compose: su propio nombre lo indica. Permite elegir que se muestren los logs en vivo.
 * Crear un usuario de administración para web: permite crear un usuario de administración en la web de docker basada en Django.
 * Desactivar demonio de Docker: su propio nombre lo explica. 


### Ópción 2: con el demonio de Docker INACTIVO:

![image](https://user-images.githubusercontent.com/9322398/50784674-a7c7a800-12ae-11e9-9020-a0f5127194d2.png)	

A continuación se detallan cada una de las acciones con el demonio de Docker INACTIVO:

 * Activar demonio de Docker: su propio nombre lo explica.


### Ópción 3: con el demonio de Docker FALLIDO:

![image](https://user-images.githubusercontent.com/9322398/50784764-ef4e3400-12ae-11e9-916e-5dc937eb3a7d.png)

A continuación se detallan cada una de las acciones con el demonio de Docker FALLIDO:

 * Activar demonio de Docker: su propio nombre lo explica. Incluye una nota explicando el motivo por el que ha podido fallar.

