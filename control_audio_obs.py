import subprocess
import json
import os
import sys

# Configuración de colores (ANSI)
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    END = '\033[0m'

ID_FILE = os.path.expanduser("~/.obs_sinks_config.json")

def run_command(command):
    """Ejecuta un comando de sistema y devuelve la salida."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1

def check_dependencies():
    """Verifica si pactl está instalado."""
    _, code = run_command("command -v pactl")
    if code != 0:
        print(f"{Colors.RED}❌ Error: 'pactl' no encontrado. Instala pulseaudio-utils.{Colors.END}")
        sys.exit(1)

def cargar_config():
    """Lee el archivo JSON con los sinks guardados."""
    if os.path.exists(ID_FILE) and os.path.getsize(ID_FILE) > 0:
        with open(ID_FILE, 'r') as f:
            return json.load(f)
    return {}

def guardar_config(config):
    """Guarda el diccionario en un archivo JSON."""
    with open(ID_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def mostrar_estado():
    print(f"\n{Colors.BLUE}=== ESTADO ACTUAL DE SINKS ==={Colors.END}")
    config = cargar_config()
    
    if not config:
        print(f"{Colors.RED}No hay canales registrados.{Colors.END}")
    else:
        for nombre, module_id in config.items():
            # Verificamos si el módulo sigue vivo en PipeWire
            _, code = run_command(f"pactl list short modules | grep -q '^{module_id}[[:space:]]'")
            status = f"{Colors.GREEN}[ACTIVO]{Colors.END}" if code == 0 else f"{Colors.RED}[DESCONECTADO]{Colors.END}"
            print(f"  - {Colors.CYAN}{nombre}{Colors.END} (ID: {module_id}) {status}")

    print(f"\n{Colors.BLUE}Confirmación en PipeWire (pactl):{Colors.END}")
    sinks_raw, _ = run_command("pactl list short sinks")
    print(sinks_raw if sinks_raw else "  No se detectan salidas virtuales.")
    input(f"\nPresiona Enter para continuar...")

def crear_sinks():
    config = cargar_config()
    if config:
        print(f"{Colors.YELLOW}⚠️ Ya existen canales. Eliminalos primero.{Colors.END}")
        input()
        return

    try:
        cantidad = int(input(f"¿Cuántos canales querés crear?: "))
    except ValueError:
        print("Ingresá un número válido.")
        return

    nueva_config = {}
    for i in range(1, cantidad + 1):
        nombre_raw = input(f"Nombre para el canal #{i}: ")
        nombre = "".join(e for e in nombre_raw.replace(" ", "-") if e.isalnum() or e == "-")
        if not nombre: nombre = f"Sink-{i}"

        # Comando para crear el sink
        cmd = f'pactl load-module module-null-sink sink_name="{nombre}" sink_properties=device.description="{nombre}"'
        module_id, code = run_command(cmd)

        if code == 0:
            print(f"{Colors.GREEN}✓ Creado: {nombre} (ID: {module_id}){Colors.END}")
            nueva_config[nombre] = module_id
        else:
            print(f"{Colors.RED}❌ Error creando {nombre}{Colors.END}")

    guardar_config(nueva_config)
    input(f"\nProceso terminado. Presiona Enter...")

def eliminar_sinks():
    config = cargar_config()
    if not config:
        print("Nada que eliminar.")
    else:
        for nombre, module_id in config.items():
            print(f"Eliminando {nombre}...", end=" ")
            _, code = run_command(f"pactl unload-module {module_id}")
            print(f"{Colors.GREEN}OK{Colors.END}" if code == 0 else f"{Colors.YELLOW}Saltado{Colors.END}")
        
    if os.path.exists(ID_FILE):
        os.remove(ID_FILE)
    print(f"{Colors.GREEN}✅ Sistema limpio.{Colors.END}")
    input()

def main():
    check_dependencies()
    while True:
        os.system('clear')
        config = cargar_config()
        estado = f"{Colors.GREEN}{len(config)} activos{Colors.END}" if config else f"{Colors.RED}Inactivo{Colors.END}"
        
        print(f"{Colors.CYAN}╔══════════════════════════════════════╗")
        print(f"║   🐍 GESTOR DE AUDIO PYTHON (v2.0)   ║")
        print(f"╚══════════════════════════════════════╝{Colors.END}")
        print(f"  Estado: {estado}\n")
        print("1) Crear Canales")
        print("2) Eliminar Canales")
        print("3) Ver Estado Detallado")
        print("4) Salir")
        
        opcion = input("\nElección: ")
        if opcion == "1": crear_sinks()
        elif opcion == "2": eliminar_sinks()
        elif opcion == "3": mostrar_estado()
        elif opcion == "4": break

if __name__ == "__main__":
    main()
