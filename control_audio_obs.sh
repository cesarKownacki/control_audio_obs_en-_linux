#!/bin/bash

# Script de control dinámico para sinks de audio de OBS - By Chechar
# Repositorio: bazzite-obs-audio-manager

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

ID_FILE="$HOME/.obs_sinks_ids"

# Validación de dependencia
if ! command -v pactl &> /dev/null; then
    clear
    echo -e "${RED}❌ ERROR: 'pactl' no está instalado.${NC}"
    echo -e "${YELLOW}Ejecutá: sudo apt install pulseaudio-utils${NC}"
    exit 1
fi

mostrar_estado() {
    echo -e "\n${BLUE}=== ESTADO ACTUAL DE SINKS ===${NC}"
    if [ -s "$ID_FILE" ]; then
        echo -e "${GREEN}✓ Sinks registrados en el script:${NC}"
        # Creamos una lista de nombres para el grep posterior
        MAPA_NOMBRES=""
        while read -r NOMBRE ID; do
            if pactl list short modules | grep -q "^$ID[[:space:]]"; then
                echo -e "  - ${CYAN}$NOMBRE${NC} (ID: $ID) ${GREEN}[ACTIVO]${NC}"
                MAPA_NOMBRES="$MAPA_NOMBRES|$NOMBRE"
            else
                echo -e "  - ${CYAN}$NOMBRE${NC} (ID: $ID) ${RED}[INACTIVO/DESCONECTADO]${NC}"
            fi
        done < "$ID_FILE"
        
        echo -e "\n${BLUE}Confirmación en el sistema (PipeWire/PulseAudio):${NC}"
        # Limpiamos el mapa de nombres para el grep (quitamos el primer pipe |)
        MAPA_NOMBRES=${MAPA_NOMBRES#|}
        
        if [ -n "$MAPA_NOMBRES" ]; then
            # Buscamos en la lista de sinks del sistema los nombres que creamos
            pactl list short sinks | grep -E "$MAPA_NOMBRES" || echo "  Aviso: Los sinks existen como módulos pero el sistema no los lista aún como salidas."
        else
            echo "  No hay dispositivos activos confirmados."
        fi
    else
        echo -e "${RED}✗ No hay registros de sinks activos.${NC}"
        [ -f "$ID_FILE" ] && rm "$ID_FILE"
    fi
    read -n 1 -s -r -p $'\nPresiona cualquier tecla para continuar...'
}

iniciar_sinks() {
    echo -e "\n${BLUE}=== INICIANDO SINKS DINÁMICOS ===${NC}"
    if [ -s "$ID_FILE" ]; then
        echo -e "${YELLOW}¡Advertencia! Ya existen sinks activos.${NC}"
        echo "Eliminalos con la opción 2 antes de crear nuevos."
        read -n 1 -s -r -p $'\nPresiona cualquier tecla para continuar...'
        return
    fi
    
    echo -ne "¿Cuántos canales querés crear?: "
    read CANTIDAD
    if ! [[ "$CANTIDAD" =~ ^[0-9]+$ ]]; then return; fi

    for (( i=1; i<=$CANTIDAD; i++ )); do
        echo -ne "Nombre para el sink #$i: "
        read NOMBRE_INPUT
        # Sanitización: solo letras, números, guiones y sin espacios
        NOMBRE_LIMPIO=$(echo "$NOMBRE_INPUT" | tr ' ' '-' | tr -cd '[:alnum:]_-')
        [ -z "$NOMBRE_LIMPIO" ] && NOMBRE_LIMPIO="Sink-$i"
        
        ID_SINK=$(pactl load-module module-null-sink sink_name="$NOMBRE_LIMPIO" sink_properties=device.description="$NOMBRE_LIMPIO")
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Creado: $NOMBRE_LIMPIO (ID: $ID_SINK)${NC}"
            echo "$NOMBRE_LIMPIO $ID_SINK" >> "$ID_FILE"
        else
            echo -e "${RED}✗ Error al crear $NOMBRE_LIMPIO${NC}"
        fi
    done
    read -n 1 -s -r -p $'\nPresiona cualquier tecla para continuar...'
}

terminar_sinks() {
    echo -e "\n${BLUE}=== LIMPIANDO SISTEMA ===${NC}"
    if [ -f "$ID_FILE" ]; then
        while read -r NOMBRE ID; do
            echo -n "Eliminando $NOMBRE (ID $ID)... "
            pactl unload-module "$ID" 2>/dev/null && echo -e "${GREEN}OK${NC}" || echo -e "${YELLOW}Saltado${NC}"
        done < "$ID_FILE"
        rm -f "$ID_FILE"
    else
        echo -e "${YELLOW}No hay nada que limpiar.${NC}"
    fi
    echo -e "${GREEN}✅ Operación finalizada.${NC}"
    read -n 1 -s -r -p $'\nPresiona cualquier tecla para continuar...'
}

mostrar_menu() {
    clear
    echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   🎮 GESTOR DE AUDIO DINÁMICO        ║${NC}"
    echo -e "${BLUE}║           (PipeWire / OBS)           ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
    echo -e ""
    if [ -s "$ID_FILE" ]; then
        echo -e "  ${GREEN}● Estado: $(wc -l < "$ID_FILE") Canales registrados${NC}"
    else
        echo -e "  ${RED}● Estado: Sin canales virtuales${NC}"
    fi
    echo -e ""
    echo -e "${YELLOW}1)${NC} Crear Sinks"
    echo -e "${RED}2)${NC} Eliminar Sinks"
    echo -e "${CYAN}3)${NC} Ver Estado Detallado"
    echo -e "${YELLOW}4)${NC} Salir"
    echo -ne "\nElección: "
}

while true; do
    mostrar_menu
    read opcion
    case $opcion in
        1) iniciar_sinks ;;
        2) terminar_sinks ;;
        3) mostrar_estado ;;
        4) echo -e "\n¡Chau! 👋"; exit 0 ;;
        *) sleep 1 ;;
    esac
done
