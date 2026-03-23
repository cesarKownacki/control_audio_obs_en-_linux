# 🎧 Audio Suite V3 - SuperElegante Linux Sink Manager
**By Cesar Adrian Kownacki (Chechar Tech)**

Una herramienta robusta y superelegante diseñada para streamers, creadores de contenido y entusiastas de Linux que necesitan gestionar dispositivos de audio virtuales (Sinks) de forma dinámica y profesional.

---

## 🚀 Características (Features)
* **Gestión Incremental**: Crea múltiples dispositivos de audio nulos (Null Sinks) en una sola tanda.
* **Interfaz QA-Shield**: Lógica de estados blindada para evitar errores de carga y bloqueos accidentales.
* **Diseño Elegante**: UI moderna con `CustomTkinter` y código de colores intuitivo.
* **Persistencia de Sesión**: Limpieza automática de módulos al cerrar para mantener el sistema ligero.
* **Compatibilidad**: Optimizado para entornos con PulseAudio y PipeWire (Ubuntu, Bazzite, Fedora, Arch, etc.).

## 🛠️ Requisitos (Requirements)
Para que esta herramienta funcione correctamente, necesitas:
1.  **Python 3.10+**
2.  **CustomTkinter**: `pip install customtkinter`
3.  **PulseAudio Utils**: Asegúrate de tener instalado el comando `pactl` (habitual en casi todas las distros).

## 📥 Instalación (Installation)
1. Clona este repositorio o descarga el archivo `.py`:
   ```bash
   git clone [https://github.com/cesarKownacki/audio-suite-linux.git](https://github.com/cesarKownacki/audio-suite-linux.git)
   cd audio-suite-linux

    Instala las dependencias:
    Bash

    pip install -r requirements.txt

    Ejecuta la aplicación:
    Bash

    python3 audio_suite.py

🎮 Instrucciones de Uso (How to use)

    Cantidad: Indica cuántos Sinks necesitas crear (Máximo 99).

    Nombres: Define un nombre único para cada uno (ej: DISCORD, MUSICA, JUEGO).

    Crear: Presiona el botón verde 🚀 Crear Sinks para activarlos en tu sistema.

    Ver Sistema: Consulta en tiempo real qué dispositivos están activos.

    Nuevo Grupo: Limpia la tanda actual para configurar un grupo nuevo sin cerrar la app.

🧪 Notas de QA

Este proyecto fue desarrollado bajo una mentalidad de Quality Assurance, testeando flujos críticos de entrada de usuario (teclado numérico vs alfanumérico) y manejo de estados de widgets para garantizar una experiencia "User Friendly" incluso para usuarios no técnicos.
⚖️ Licencia (License)

Distribuido bajo la licencia MIT. Consulta el archivo LICENSE para más información.
