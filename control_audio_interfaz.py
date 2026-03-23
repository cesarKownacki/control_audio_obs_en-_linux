import customtkinter as ctk
import subprocess
import os
import json
import re

class AudioAppQAShield(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CONFIGURACIÓN ---
        self.title("Chechar Tech - Audio Suite V3 Superelegante")
        self.geometry("600x750")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.config_file = os.path.expanduser("~/.audio_sinks_history.json")
        self.reset_variables_estado()

        self.protocol("WM_DELETE_WINDOW", self.finalizar_programa)
        self.cargar_historial_ids()

        # --- UI: INPUT ---
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.pack(pady=20, padx=20, fill="x")

        self.label_instruccion = ctk.CTkLabel(self.header_frame, text="¿Cuántos Sinks desea crear? (1-99):", font=("Arial", 14, "bold"))
        self.label_instruccion.pack(pady=(15, 5))

        self.input_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.input_container.pack(pady=10)

        self.entry_input = ctk.CTkEntry(self.input_container, placeholder_text="Ej: 3", width=150)
        self.entry_input.pack(side="left", padx=(0, 5))
        
        self.btn_ok = ctk.CTkButton(self.input_container, text="OK", width=60, command=self.procesar_retorno_input)
        self.btn_ok.pack(side="left")

        self.entry_input.bind("<Return>", lambda e: self.procesar_retorno_input())
        self.entry_input.bind("<KP_Enter>", lambda e: self.procesar_retorno_input())
        self.entry_input.focus_set()

        # --- UI: LISTADO ---
        self.middle_frame = ctk.CTkFrame(self)
        self.middle_frame.pack(pady=10, padx=20, fill="x")
        self.scroll_list = ctk.CTkScrollableFrame(self.middle_frame, height=200, label_text="Lista de Sinks")
        self.scroll_list.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        self.listado_labels = []
        self.btn_anular = ctk.CTkButton(self.middle_frame, text="❌ Anular", fg_color="#8b2e2e", hover_color="#6b2424", command=self.anular_carga)
        self.btn_anular.pack(side="right", padx=10)
        self.btn_anular.configure(state="disabled")

        # --- UI: BOTONERA (COLORES PULIDOS) ---
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(pady=20, padx=20, fill="x")
        self.control_frame.grid_columnconfigure((0, 1), weight=1)

        # 1. Crear Sinks (Verde Esmeralda)
        self.btn_iniciar = ctk.CTkButton(self.control_frame, text="🚀 Crear Sinks", 
                                        fg_color="#2E7D32", hover_color="#1B5E20",
                                        command=self.iniciar_sinks_incrementales)
        self.btn_iniciar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.btn_iniciar.configure(state="disabled")

        # 2. Ver Sistema (Azul Acero)
        self.btn_consultar = ctk.CTkButton(self.control_frame, text="🔍 Ver Sistema", 
                                          fg_color="#1976D2", hover_color="#1565C0",
                                          command=self.consultar_sistema)
        self.btn_consultar.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # 3. Nuevo Grupo (Ámbar Suave - EL CAMBIO SOLICITADO)
        self.btn_agregar = ctk.CTkButton(self.control_frame, text="➕ Nuevo Grupo", 
                                        fg_color="#FFB74D", hover_color="#FFA726", 
                                        text_color="#1A1A1A", # Texto oscuro para mejor contraste con amarillo claro
                                        command=self.activar_flujo_agregar)
        self.btn_agregar.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.btn_agregar.configure(state="disabled")

        # 4. Salir (Gris Pizarra)
        self.btn_finalizar = ctk.CTkButton(self.control_frame, text="🚪 Salir", 
                                          fg_color="#455A64", hover_color="#37474F",
                                          command=self.finalizar_programa)
        self.btn_finalizar.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # --- CONSOLA ---
        self.txt_log = ctk.CTkTextbox(self, height=120, font=("Courier", 10), fg_color="#1a1a1a")
        self.txt_log.pack(pady=10, padx=20, fill="x")
        self.log("Sistema listo.")

    # --- LÓGICA (Se mantiene la V7.2 Blindada) ---

    def reset_variables_estado(self):
        self.sinks_pedidos_cantidad = 0
        self.indice_nombre_actual = 0
        self.nombres_temporales_sesion = []
        self.cargando_nombres = False
        self.ids_creados_totales = {}

    def procesar_retorno_input(self):
        entrada = self.entry_input.get().strip()
        if not entrada: return

        if not self.cargando_nombres:
            try:
                cant = int(re.sub(r'[^0-9]', '', entrada))
                if 1 <= cant <= 99:
                    self.sinks_pedidos_cantidad = cant
                    self.indice_nombre_actual = 1
                    self.cargando_nombres = True
                    self.btn_anular.configure(state="normal")
                    self.log(f"Preparando {cant} sinks...")
                    self.preparar_interfaz_nombres()
                else:
                    self.log("❌ Error: Use 1-99.")
                    self.entry_input.delete(0, 'end')
            except:
                self.log("❌ Error: Ingrese un número.")
                self.entry_input.delete(0, 'end')
            return

        nombre_limpio = re.sub(r'[^a-zA-Z0-9]', '', entrada).upper()
        if not nombre_limpio:
            self.log("❌ Error: Caracteres inválidos.")
            return

        if nombre_limpio in self.nombres_temporales_sesion or self.chequear_nombre_existe_en_sistema(nombre_limpio):
            self.log(f"❌ Error: '{nombre_limpio}' ya existe.")
            return

        self.nombres_temporales_sesion.append(nombre_limpio)
        self.agregar_label_al_listado(f"#{self.indice_nombre_actual}: {nombre_limpio}")
        self.log(f"Agregado: {nombre_limpio}")

        if self.indice_nombre_actual < self.sinks_pedidos_cantidad:
            self.indice_nombre_actual += 1
            self.preparar_interfaz_nombres()
        else:
            self.finalizar_carga_y_bloquear()

    def preparar_interfaz_nombres(self):
        self.label_instruccion.configure(text=f"Nombre para Sink #{self.indice_nombre_actual}:")
        self.entry_input.delete(0, 'end')
        self.entry_input.configure(state="normal")
        self.btn_ok.configure(state="normal")
        self.entry_input.focus_set()

    def finalizar_carga_y_bloquear(self):
        self.cargando_nombres = False
        self.label_instruccion.configure(text="¡Tanda completa!")
        self.entry_input.delete(0, 'end')
        self.entry_input.configure(state="disabled")
        self.btn_ok.configure(state="disabled")
        self.btn_iniciar.configure(state="normal")
        self.btn_anular.configure(state="disabled")
        self.log("Presione 'Crear Sinks'.")

    def anular_carga(self):
        self.reset_variables_estado()
        self.limpiar_listado_visual()
        self.label_instruccion.configure(text="¿Cuántos Sinks desea crear? (1-99):")
        self.entry_input.configure(state="normal")
        self.btn_ok.configure(state="normal")
        self.entry_input.delete(0, 'end')
        self.entry_input.focus_set()
        self.btn_anular.configure(state="disabled")
        self.btn_iniciar.configure(state="disabled")
        self.log("♻️ Reiniciado.")

    def activar_flujo_agregar(self):
        self.btn_agregar.configure(state="disabled")
        self.anular_carga()

    def iniciar_sinks_incrementales(self):
        self.log("🚀 Aplicando...")
        sinks_actuales = self.obtener_sinks_sistema()
        for nombre in self.nombres_temporales_sesion:
            if nombre not in sinks_actuales:
                cmd = f'pactl load-module module-null-sink sink_name="{nombre}" sink_properties=device.description="{nombre}"'
                stdout, code = self.ejecutar_pactl_safe(cmd)
                if code == 0: self.ids_creados_totales[nombre] = stdout
        
        self.guardar_historial_ids()
        self.btn_agregar.configure(state="normal")
        self.log("✅ Finalizado con éxito.")

    def consultar_sistema(self):
        out, _ = self.ejecutar_pactl_safe("pactl list short sinks")
        self.log("--- ACTUALES ---")
        self.log(out if out else "Vacío.")

    def finalizar_programa(self):
        self.limpiar_modulos_raw()
        if os.path.exists(self.config_file): os.remove(self.config_file)
        self.destroy()

    def ejecutar_pactl_safe(self, cmd):
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return res.stdout.strip(), res.returncode

    def obtener_sinks_sistema(self):
        out, _ = self.ejecutar_pactl_safe("pactl list short sinks | cut -f2")
        return set(out.split('\n')) if out else set()

    def chequear_nombre_existe_en_sistema(self, nombre):
        return nombre in self.obtener_sinks_sistema()

    def limpiar_modulos_raw(self):
        cmd = "for id in $(pactl list short modules | grep -E 'sink_name' | cut -f1); do pactl unload-module $id; done"
        subprocess.run(cmd, shell=True)

    def agregar_label_al_listado(self, texto):
        label = ctk.CTkLabel(self.scroll_list, text=texto, font=("Arial", 11), anchor="w")
        label.pack(fill="x", pady=2, padx=10)
        self.listado_labels.append(label)

    def limpiar_listado_visual(self):
        for label in self.listado_labels: label.destroy()
        self.listado_labels = []

    def log(self, msj):
        self.txt_log.insert("end", f"\n> {msj}")
        self.txt_log.see("end")

    def guardar_historial_ids(self):
        with open(self.config_file, 'w') as f: json.dump(self.ids_creados_totales, f, indent=4)

    def cargar_historial_ids(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f: self.ids_creados_totales = json.load(f)
            except: pass

if __name__ == "__main__":
    app = AudioAppQAShield()
    app.mainloop()
