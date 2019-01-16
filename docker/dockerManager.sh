#!/bin/bash
#title:         dockerManager.sh
#description:   Panel de Administración de docker para decide-ganimedes
#author:        Juan Carlos Utrilla
#created:       Dic 25 2018
#version:       3.0
#usage:         ./dockerManager.sh
#==============================================================================

function salir {
 	echo -e "\n\n"
 	echo " ______________________________________  "
 	echo "/ Script desarrollado por el equipo de \\"
 	echo "| Decide-Ganimedes-Censo. Para más     | "
 	echo "\ información... mira en la wiki xDDD  / "
 	echo " --------------------------------------  "
 	echo "  \                                      "
 	echo "   \                                     "
 	echo "       .--.                              "
 	echo "      |o_o |                             "
 	echo "      |:_/ |                             "
 	echo "     //   \ \                            "
	echo "    (|     | )                           "
	echo "   /'\_   _/\`\                          "
	echo "   \___)=(___/                           "
	echo -e "\n\n"
}

function menuEstadoDocker () {
	estadoDocker=$(sudo systemctl is-active docker)
	
	if [[ $estadoDocker == "inactive" ]];
        then
                echo -e "\e[1m|\e[0m \e[4mEstado del demonio de docker\e[0m: \e[33m\e[5m\e[1mINACTIVO\e[0m                               \e[1m|\e[0m"
	elif [[ $estadoDocker == "failed" ]];
	then
		echo -e "\e[1m|\e[0m \e[4mEstado del demonio de docker\e[0m: \e[31m\e[5m\e[1mFALLIDO\e[0m                                \e[1m|\e[0m"
	elif [[ $estadoDocker == "active" ]];
	then
		echo -e "\e[1m|\e[0m \e[4mEstado del demonio de docker\e[0m: \e[32m\e[1mACTIVO\e[0m                                 \e[1m|\e[0m"
	fi
}


function menu {
	estadoDocker=$(sudo systemctl is-active docker)
        
	clear
	
	echo -e "\e[1m+----------------------------------------------------------------------+\e[0m"
	echo -e "\e[1m|              Panel de Administración - Decide-Ganimedes              |\e[0m"
	echo -e "\e[1m+----------------------------------------------------------------------+\e[0m"
        
        if [[ $estadoDocker == "active" ]];
	then
		# Menú con docker en estado ACTIVO

		echo -e "\e[1m| 1)\e[0m Listar imágenes, contenedores, volúmenes y redes                  \e[1m|\e[0m"
		echo -e "\e[1m| 2)\e[0m Eliminar componentes de docker sin uso                            \e[1m|\e[0m"
		echo -e "\e[1m|                                                                      |\e[0m"
		echo -e "\e[1m| 3)\e[0m Encender contenedores con docker-compose                          \e[1m|\e[0m"
		echo -e "\e[1m| 4)\e[0m Compilar contenedores con docker-compose                          \e[1m|\e[0m"
        	echo -e "\e[1m| 5)\e[0m Apagar contenedores con docker-compose                            \e[1m|\e[0m"
        	echo -e "\e[1m| 6)\e[0m Eliminar contenedores con docker-compose                          \e[1m|\e[0m"
		echo -e "\e[1m| 7)\e[0m Visualizar logs con docker-compose                                \e[1m|\e[0m"
		echo -e "\e[1m|                                                                      |\e[0m"
		echo -e "\e[1m| 8)\e[0m Crear un usuario de administración para web                       \e[1m|\e[0m"
		echo -e "\e[1m|\e[0m                                                                      \e[1m|\e[0m"
		echo -e "\e[1m| 9)\e[0m Desactivar demonio de docker                                      \e[1m|\e[0m"
	elif [[ $estadoDocker == "inactive" ]] || [[ $estadoDocker == "failed" ]];
	then

		# Menú con docker en estado INACTIVO o FALLIDO

		echo -e "\e[1m| 1)\e[0m Activar demonio de docker                                         \e[1m|\e[0m"
		
		if [[ $estadoDocker == "failed" ]];
	        then
			echo -e "\e[1m|\e[0m                                                                      \e[1m|\e[0m"
			echo -e "\e[1m|\e[0m \e[31mSi la activación del demonio de docker ha fallado puede ser debido a \e[0m\e[1m|\e[0m"
			echo -e "\e[1m|\e[0m \e[31mque el servicio se ha activado y apagado demasiadas veces de forma  \e[0m \e[1m|\e[0m"
	        	echo -e "\e[1m|\e[0m \e[31mmuy rápida. Espere 1 minuto para volver a intentarlo. \e[0m               \e[1m|\e[0m"
		fi
	fi

        echo -e "\e[1m|\e[0m                                                                      \e[1m|\e[0m"
	menuEstadoDocker
	echo -e "\e[1m|                                                                      |\e[0m"
        echo -e "\e[1m| 0)\e[0m  Salir                                                            \e[1m|\e[0m"
        echo -e "\e[1m|                                                                      |\e[0m"
	echo -e "\e[1m+----------------------------------------------------------------------+\e[0m"
}

# Acciones a realizar
function ACTIONS {

    # Opción 1
    if [[ ${choices[0]} ]]; then
	echo "Borrando los contenedores sin uso"
	sudo docker container prune -f
    fi

    # Opción 2
    if [[ ${choices[1]} ]]; then
        echo "Borrando las imágenes sin uso"
	sudo docker image prune -af
    fi

    # Opción 3
    if [[ ${choices[2]} ]]; then
        echo "Borrando los volúmenes sin uso"
	sudo docker volume prune -f
    fi

    # Opción 4
    if [[ ${choices[3]} ]]; then
        echo "Borrando las redes sin uso"
	sudo docker network prune -f
    fi
}

# Función MENU
function MENU {
    echo "Opciones disponibles:"
    for NUM in ${!options[@]}; do
        echo "[""${choices[NUM]:- }""]" $(( NUM+1 ))") ${options[NUM]}"
    done
    echo "$ERROR"
}

# Variables
options[0]="Contenedores sin uso"
options[1]="Imágenes sin uso"
options[2]="Volúmenes sin uso"
options[3]="Redes sin uso"

ERROR=""
respuesta=99

while  [ $respuesta -ne 0 ];
do
clear
	menu
	read -n 1 -p "Seleccione una opción: " respuesta
	# Falta controlar algunos caracteres especiales como Intro, Tabulador y Espacio

	estadoDocker=$(sudo systemctl is-active docker)

        if [[ $estadoDocker == "active" ]];
        then
		case "$respuesta" in
			''|*[0-9]*)
				case "$respuesta" in
					1)      echo -e "\n\n\e[1mEjecutando - Listar imágenes y contenedores...\e[0m\n"
						echo -e "\n\e[1m\e[32m----------- Listado de imágenes -----------\e[0m \n"	
						sudo docker images
						echo -e "\n\e[1m\e[32m-------- Listado de contenedores ----------\e[0m \n"
						sudo docker container list --all
						echo -e "\n\e[1m\e[32m---------- Listado de volúmenes -----------\e[0m \n"
						sudo docker volume list
						echo -e "\n\e[1m\e[32m------------- Listado de redes ------------\e[0m \n"
						sudo docker network list
						read -n 1 -p $'\nPresiona una tecla para volver al menú...\n'
						;;
		
					2) 	echo -e "\n\n\e[1mEjecutando - Eliminar componentes de docker...\e[0m\n"

						# Menú en bucle
						
						unset choices
						while MENU && read -e -p "Seleccione las opciones deseadas usando los números indicados (de nuevo para desmarcarlos, ENTER para finalizar): " -n1 SELECTION && [[ -n "$SELECTION" ]]; do
    							clear
    
							if [[ "$SELECTION" == *[[:digit:]]* && $SELECTION -ge 1 && $SELECTION -le ${#options[@]} ]]; 
							then
        							(( SELECTION-- ))
        							if [[ "${choices[SELECTION]}" == "+" ]]; then
            								choices[SELECTION]=""
        							else
            								choices[SELECTION]="+"
        							fi
            							ERROR=" "
    							else
        							ERROR="Opción inválida: $SELECTION"
    							fi
						done

						ACTIONS

						read -n 1 -p $'\nPresiona una tecla para volver al menú...\n'
						;;

					3)      echo -e "\n\n\e[1mEjecutando - Encender contenedores con docker-compose...\e[0m\n"
                                                sudo docker-compose up -d
                                                read -n 1 -p $'\nPresiona una tecla para volver al menú...\n'
                                                ;;


					4)	echo -e "\n\n\e[1mEjecutando - Compilar contenedores con docker-compose...\e[0m\n"

						read -rp $'\nPregunta: ¿Desea utilizar la cache de docker? (Y/n): ' opc;
						
						echo -e "\n\n\e[1m\e[32mCompilando...\e[0m \n\n"
						sleep 5

						if [ $opc = "Y" ] || [ $opc = "y" ];
						then
                                                	sudo docker-compose build
                                               	elif [ $opc = "N" ] || [ $opc = "n" ];
						then
							sudo docker-compose build --no-cache 
                                                fi

						read -n 1 -p $'\nPresiona una tecla para volver al menú...\n'
                                                ;;


                                        5)      echo -e "\n\n\e[1mEjecutando - Apagar contenedores con docker-compose...\e[0m\n"
                                                sudo docker-compose stop
                                                read -n 1 -p $'\nPresiona una tecla para volver al menú...\n'
                                                ;;

					6)	echo -e "\n\n\e[1mEjecutando - Remover contenedores con docker-compose...\e[0m\n"
                                                sudo docker-compose down
                                                read -n 1 -p $'\nPresiona una tecla para volver al menú...\n'
                                                ;;

						
					7)      echo -e "\n\n\e[1mEjecutando - Visualizar logs con docker-compose...\e[0m\n"
                                                
						read -rp $'\nPregunta: ¿Desea visualizar los logs en tiempo real? (Y/n): ' opc;
						
						if [ $opc = "Y" ] || [ $opc = "y" ];
                                                then
							echo -e "\n\n\e[1m\e[32mPulse Ctrl + C para finalizar la ejecución... \e[0m \n\n"
                                                	sleep 5

                                                        sudo docker-compose logs -f 2> /dev/null
                                                elif [ $opc = "N" ] || [ $opc = "n" ];
                                                then
							echo -e "\n\n\e[1m\e[32mMostrando... \e[0m \n\n"
	                                                sleep 1

                                                        sudo docker-compose logs 
                                                fi
						
                                                read -n 1 -p $'\nPresiona una tecla para volver al menú...\n'
                                                ;;


					8)	echo -e "\n\n\e[1mEjecutando - Crear un usuario de administración para web...\e[0m\n"               
		       	                        sudo docker exec -ti decide_web ./manage.py createsuperuser
		               	                read -n 1 -p $'\nPresiona una tecla para volver al menú...\n'
		                       	        ;;
		
					9)	echo -e "\n\n\e[1mEjecutando - Desactivar demonio de Docker...\e[0m\n"
						sudo systemctl stop docker
						;;

					0)      salir
						;;
				esac
				;;
			*)	respuesta=99
				read -n 1 -p $'\n\nEsta opción no existe. Presione una tecla para volver al menú...\n'
				;;	
		esac
	else
		case "$respuesta" in
			''|*[0-1]*)
			case "$respuesta" in
				1) 	echo -e "\nEjecutando - Activar demonio de docker... \n"
					sudo systemctl start docker
					;;

				0)	salir
					;;
			esac
			;;

		*) 	respuesta=99
			read -n 1 -p $'\n\nEsta opción no existe. Presione una tecla para volver al menú...\n'
                        ;;
		esac
	fi
done
