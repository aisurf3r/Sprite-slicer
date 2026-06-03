import os
import sys
import subprocess
import threading
import time
import webbrowser  
import tkinter as tk
import site  

# ==========================================
# 🚀 SISTEMA DE AUTO-INSTALACIÓN PREVIA
# ==========================================
def comprobar_e_instalar_dependencias():
    """Comprueba las dependencias e instala las faltantes usando pip."""
    dependencias = {
        "customtkinter": "customtkinter",
        "PIL": "pillow"
    }
    
    faltantes = []
    for modulo, paquete in dependencias.items():
        try:
            __import__(modulo)
        except ImportError:
            faltantes.append(paquete)
            
    if faltantes:
        for paquete in faltantes:
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", paquete],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass 
        
        # Fuerza a Python a actualizar sus rutas internas en caliente para reconocer los nuevos paquetes
        for path in site.getsitepackages():
            site.addsitedir(path)
        if hasattr(site, 'getusersitepackages'):
            site.addsitedir(site.getusersitepackages())

# ==========================================
# ⏱️ VENTANA DE CARGA (SPLASH SCREEN)
# ==========================================
class VentanaCarga:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Iniciando...")
        self.root.configure(bg="#18181B")
        
        # Centrar la ventana de carga en la pantalla
        ancho, alto = 400, 180
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        pos_x = (pantalla_ancho // 2) - (ancho // 2)
        pos_y = (pantalla_alto // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")
        self.root.overrideredirect(True) 

        self.lbl_titulo = tk.Label(
            self.root, text="Sprite Slicer Pro", 
            fg="#F4F4F5", bg="#18181B", font=("Arial", 18, "bold")
        )
        self.lbl_titulo.pack(pady=(25, 5))

        self.lbl_estado = tk.Label(
            self.root, text="Verificando entorno de Python...", 
            fg="#A1A1AA", bg="#18181B", font=("Arial", 10)
        )
        self.lbl_estado.pack(pady=5)

        self.canvas_barra = tk.Canvas(self.root, width=320, height=8, bg="#27272A", highlightthickness=0)
        self.canvas_barra.pack(pady=15)
        self.progreso_rect = self.canvas_barra.create_rectangle(0, 0, 0, 8, fill="#3B82F6", width=0)

        self.progreso_actual = 0
        self.completado = False

        threading.Thread(target=self.hilo_instalacion, daemon=True).start()
        self.actualizar_animacion()
        self.root.mainloop()

    def hilo_instalacion(self):
        time.sleep(0.5) 
        self.lbl_estado.configure(text="Buscando componentes (customtkinter, pillow)...")
        comprobar_e_instalar_dependencias()
        self.completado = True

    def actualizar_animacion(self):
        if not self.completado:
            if self.progreso_actual < 280:
                self.progreso_actual += 4
            else:
                self.progreso_actual += 0.5 
                self.lbl_estado.configure(text="Descargando e instalando librerías...")
        else:
            self.progreso_actual += 15 
            self.lbl_estado.configure(text="¡Todo listo! Iniciando entorno gráfico...")

        self.canvas_barra.coords(self.progreso_rect, 0, 0, self.progreso_actual, 8)

        if self.progreso_actual >= 320:
            self.root.destroy() 
        else:
            self.root.after(20, self.actualizar_animacion)

# Ejecutar la verificación inicial usando únicamente Tkinter nativo
VentanaCarga()

# ==========================================
# 🎨 APLICACIÓN PRINCIPAL
# ==========================================
try:
    import customtkinter as ctk
    from tkinter import filedialog
    from PIL import Image, ImageTk
except ModuleNotFoundError:
    # FALLBACK ANTI-ERRORES: Si la recarga dinámica falló en este sistema operativo,
    # reiniciamos el script de forma totalmente transparente. Esta vez abrirá al instante.
    subprocess.Popen([sys.executable] + sys.argv)
    sys.exit()

class SpriteSlicerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Universal Sprite Slicer & Cutter Pro")
        self.geometry("1150x850")
        self.minsize(1000, 700)
        
        self.after(100, self.forzar_maximizado)
        
        # Variables globales de control
        self.ruta_imagen_original = None
        self.imagen_pil_original = None
        self.imagen_tk_render = None
        
        # Coordenadas y estados del ratón
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.recorte_en_progreso = False
        
        # Estructuras de datos para cálculo rápido
        self.islas_base_detectadas = []
        self.cajas_previsualizadas = []

        # Configuración del Layout (Grid)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ---------------- Panel Lateral (Controles) ----------------
        self.panel_control = ctk.CTkFrame(self, width=290, corner_radius=0)
        self.panel_control.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.panel_control.pack_propagate(False) 

        self.titulo_label = ctk.CTkLabel(
            self.panel_control, 
            text="Sprite Slicer Pro", 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.titulo_label.pack(pady=(20, 10), padx=15)

        # 1. Botón para importar imágenes
        self.btn_importar = ctk.CTkButton(
            self.panel_control, 
            text="1. Importar Imagen", 
            command=self.importar_imagen,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_importar.pack(pady=10, padx=15, fill="x")

        # Configuración del nombre del archivo de salida
        self.lbl_nombre = ctk.CTkLabel(self.panel_control, text="Nombre de salida (se añadirá 1, 2, 3...):", font=ctk.CTkFont(size=12))
        self.lbl_nombre.pack(pady=(10, 2), padx=15, anchor="w")
        
        self.entry_nombre = ctk.CTkEntry(self.panel_control, placeholder_text="ej. arbol, asset_item")
        self.entry_nombre.pack(pady=5, padx=15, fill="x")
        self.entry_nombre.insert(0, "sprite")

        # --- SECCIÓN: MODO AUTOMÁTICO (ESTRICTAMENTE OPCIONAL) ---
        self.lbl_seccion_auto = ctk.CTkLabel(self.panel_control, text="⚙️ Modo Automático (Solo PNG):", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_seccion_auto.pack(pady=(15, 2), padx=15, anchor="w")

        # Mensaje de advertencia dinámico para formatos sin transparencia (JPG)
        self.lbl_aviso_jpg = ctk.CTkLabel(
            self.panel_control,
            text="",
            text_color="#F59E0B",
            font=ctk.CTkFont(size=11, weight="bold"),
            wraplength=250,
            justify="left"
        )
        self.lbl_aviso_jpg.pack(pady=2, padx=15, anchor="w")

        # SWITCH: El usuario decide cuándo quiere ver las cajas automáticas
        self.switch_auto = ctk.CTkSwitch(
            self.panel_control, 
            text="Ver Previsualización Auto", 
            command=self.alternar_modo_auto,
            font=ctk.CTkFont(size=12)
        )
        self.switch_auto.pack(pady=5, padx=15, anchor="w")
        self.switch_auto.deselect()
        self.switch_auto.configure(state="disabled")

        self.frame_tolerancia = ctk.CTkFrame(self.panel_control, fg_color="transparent")
        self.frame_tolerancia.pack(pady=5, padx=15, fill="x")
        
        self.lbl_tolerancia_txt = ctk.CTkLabel(
            self.frame_tolerancia, 
            text="Tolerancia de Agrupación: 4px", 
            font=ctk.CTkFont(size=12)
        )
        self.lbl_tolerancia_txt.pack(anchor="w")
        
        self.slider_tolerancia = ctk.CTkSlider(
            self.frame_tolerancia, 
            from_=0, 
            to=50, 
            number_of_steps=50,
            command=self.al_cambiar_tolerancia
        )
        self.slider_tolerancia.pack(pady=5, fill="x")
        self.slider_tolerancia.set(4)
        self.slider_tolerancia.configure(state="disabled")

        self.btn_autocorte = ctk.CTkButton(
            self.panel_control, 
            text="💾 Guardar Todo el Autocorte", 
            command=self.guardar_autocorte_confirmado,
            fg_color="#10B981",
            hover_color="#059669",
            state="disabled",
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_autocorte.pack(pady=5, padx=15, fill="x")

        # --- SECCIÓN: MODO MANUAL ---
        self.lbl_seccion_manual = ctk.CTkLabel(self.panel_control, text="🖱️ Modo Manual (Siempre Activo):", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_seccion_manual.pack(pady=(15, 2), padx=15, anchor="w")

        self.btn_cancelar = ctk.CTkButton(
            self.panel_control, 
            text="Cancelar Arrastre Manual (Esc)", 
            command=self.cancelar_seleccion,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            state="disabled",
            font=ctk.CTkFont(size=11)
        )
        self.btn_cancelar.pack(pady=5, padx=15, fill="x")

        # --- PANEL CONTENEDOR PARA EL LOADER ANIMADO ---
        self.loader_frame = ctk.CTkFrame(self.panel_control, fg_color="#1E1E22", height=75)
        self.loader_frame.pack(pady=15, padx=15, fill="x")
        self.loader_frame.pack_propagate(False) 
        
        self.lbl_loader_status = ctk.CTkLabel(
            self.loader_frame, 
            text="Esperando acción...", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#71717A"
        )
        self.lbl_loader_status.pack(pady=(8, 2), padx=10)
        
        self.progressbar = ctk.CTkProgressBar(self.loader_frame, mode="determinate", progress_color="#3B82F6", fg_color="#27272A")
        self.progressbar.pack(pady=5, padx=15, fill="x")
        self.progressbar.set(0)
        
        # Control del Loader desde el hilo principal
        self.loader_progreso_actual = 0.0
        self.loader_direccion = 0.05
        self.animacion_corriendo = False

        self.btn_github = ctk.CTkButton(
            self.panel_control,
            text="🐙 GitHub",
            command=self.abrir_repositorio_github,
            width=100,
            height=28,
            fg_color="#27272A",          
            hover_color="#3F3F46",      
            text_color="#E4E4E7",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        self.btn_github.pack(side="bottom", anchor="center", pady=(10, 15), padx=15)

        # Cuadro de Información de Estado General
        self.info_frame = ctk.CTkFrame(self.panel_control, fg_color="transparent")
        self.info_frame.pack(pady=5, padx=15, fill="both", expand=True)

        self.info_label = ctk.CTkLabel(
            self.info_frame, 
            text="• MODO MANUAL:\nHaz clic y arrastra el ratón sobre la imagen limpia.\n\n• MODO AUTOMÁTICO:\nRequiere formato PNG transparente para poder precalcular las cajas verdes.", 
            justify="left",
            wraplength=250,
            font=ctk.CTkFont(size=11),
            text_color="#9CA3AF"
        )
        self.info_label.pack(pady=5, padx=5, anchor="w")
        
        self.status_label = ctk.CTkLabel(
            self.panel_control, 
            text="Estado: Listo", 
            text_color="#9CA3AF",
            font=ctk.CTkFont(weight="bold")
        )
        self.status_label.pack(pady=10, padx=15)

        # ---------------- Zona de Lienzo (Canvas) ----------------
        self.zona_canvas = ctk.CTkFrame(self, fg_color="#1E1E1E")
        self.zona_canvas.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.zona_canvas.grid_rowconfigure(0, weight=1)
        self.zona_canvas.grid_columnconfigure(0, weight=1)

        self.canvas = ctk.CTkCanvas(self.zona_canvas, bg="#18181B", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.scroll_x = ctk.CTkScrollbar(self.zona_canvas, orientation="horizontal", command=self.canvas.xview)
        self.scroll_x.grid(row=1, column=0, sticky="ew")
        
        self.scroll_y = ctk.CTkScrollbar(self.zona_canvas, orientation="vertical", command=self.canvas.yview)
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        
        self.canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)

        # Eventos del Canvas
        self.canvas.bind("<Button-1>", self.al_hacer_click)
        self.canvas.bind("<B1-Motion>", self.al_arrastrar)
        self.canvas.bind("<ButtonRelease-1>", self.al_soltar_raton)
        self.bind("<Escape>", lambda event: self.cancelar_seleccion())

    def forzar_maximizado(self):
        try:
            self.state('zoomed')
        except:
            ancho = self.winfo_screenwidth()
            alto = self.winfo_screenheight()
            self.geometry(f"{ancho}x{alto}+0+0")

    def abrir_repositorio_github(self):
        webbrowser.open_new_tab("https://github.com/aisurf3r/Sprite-slicer")

    # --- ANIMACION LOADER ---
    def iniciar_animacion_loader(self, texto):
        self.lbl_loader_status.configure(text=texto, text_color="#60A5FA")
        self.btn_importar.configure(state="disabled")
        if not self.animacion_corriendo:
            self.animacion_corriendo = True
            self.loader_progreso_actual = 0.0
            self.loader_direccion = 0.05
            self._actualizar_frame_loader()

    def _actualizar_frame_loader(self):
        if not self.animacion_corriendo:
            return
            
        self.loader_progreso_actual += self.loader_direccion
        if self.loader_progreso_actual >= 1.0:
            self.loader_progreso_actual = 1.0
            self.loader_direccion = -0.05
        elif self.loader_progreso_actual <= 0.0:
            self.loader_progreso_actual = 0.0
            self.loader_direccion = 0.05
            
        self.progressbar.set(self.loader_progreso_actual)
        self.after(30, self._actualizar_frame_loader)

    def detener_animacion_loader(self, texto_final="Completado"):
        self.animacion_corriendo = False
        self.progressbar.set(1.0)
        self.lbl_loader_status.configure(text=texto_final, text_color="#10B981")
        self.btn_importar.configure(state="normal")

    # --- LÓGICA INCREMENTAL ---
    def obtener_siguiente_indice(self, carpeta, nombre_base):
        indice = 1
        while True:
            nombre_archivo = f"{nombre_base}{indice}.png"
            if not os.path.exists(os.path.join(carpeta, nombre_archivo)):
                return indice
            indice += 1

    def importar_imagen(self):
        tipos_archivos = [('Imágenes de Assets', '*.png *.jpg *.jpeg *.bmp *.tga')]
        ruta = filedialog.askopenfilename(title="Seleccionar hoja de assets", filetypes=tipos_archivos)
        
        if ruta:
            self.ruta_imagen_original = r"" + ruta
            self.imagen_pil_original = Image.open(self.ruta_imagen_original)
            
            self.limpiar_lienzo_y_recargar_base()
            
            self.islas_base_detectadas = []
            self.cajas_previsualizadas = []
            
            self.switch_auto.deselect()
            self.switch_auto.configure(state="disabled")
            self.slider_tolerancia.configure(state="disabled")
            self.btn_autocorte.configure(state="disabled", text="💾 Guardar Autocorte (0 partes)")
            self.lbl_aviso_jpg.configure(text="")
            
            tiene_alfa = self.imagen_pil_original.mode in ('RGBA', 'LA') or (self.imagen_pil_original.mode == 'P' and 'transparency' in self.imagen_pil_original.info)
            
            if tiene_alfa:
                self.iniciar_animacion_loader("Analizando transparencia...")
                threading.Thread(target=self.hilo_analisis_subpíxel, daemon=True).start()
            else:
                self.lbl_aviso_jpg.configure(text="⚠️ El Modo Auto requiere imágenes PNG\ncon fondo transparente.")
                self.detener_animacion_loader("Modo manual activo")
                self.status_label.configure(text="Imagen opaca cargada.\nUsa el arrastre manual.", text_color="#F59E0B")

    def hilo_analisis_subpíxel(self):
        img = self.imagen_pil_original.convert('RGBA')
        ancho, alto = img.size
        pixeles = img.load()

        visitado = set()
        islas = []
        UMBRAL_ALFA = 10 

        for y in range(alto):
            for x in range(ancho):
                if pixeles[x, y][3] > UMBRAL_ALFA and (x, y) not in visitado:
                    cola = [(x, y)]
                    visitado.add((x, y))
                    min_x, max_x = x, x
                    min_y, max_y = y, y
                    
                    while cola:
                        cx, cy = cola.pop(0)
                        if cx < min_x: min_x = cx
                        if cx > max_x: max_x = cx
                        if cy < min_y: min_y = cy
                        if cy > max_y: max_y = cy
                        
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < ancho and 0 <= ny < alto:
                                if (nx, ny) not in visitado and pixeles[nx, ny][3] > UMBRAL_ALFA:
                                    visitado.add((nx, ny))
                                    cola.append((nx, ny))
                    
                    if (max_x - min_x) > 0 or (max_y - min_y) > 0:
                        islas.append([min_x, min_y, max_x, max_y])

        self.islas_base_detectadas = islas
        self.after(0, self.finalizar_carga_silenciosa)

    def finalizar_carga_silenciosa(self):
        if self.islas_base_detectadas:
            self.switch_auto.configure(state="normal")
            self.detener_animacion_loader("¡Modo Auto Disponible!")
            self.status_label.configure(text="PNG transparente listo.\nModo manual activo.\nPuedes encender el Modo Auto.", text_color="#34D399")
        else:
            self.lbl_aviso_jpg.configure(text="⚠️ No se detectó transparencia real\nen este archivo PNG.")
            self.detener_animacion_loader("Modo manual activo")
            self.status_label.configure(text="PNG sin transparencia.\nUsa el arrastre manual.", text_color="#F59E0B")

    def toggle_modo_auto_wrapper(self):
        self.alternar_modo_auto()

    def alternar_modo_auto(self):
        if self.switch_auto.get() == 1:
            self.slider_tolerancia.configure(state="normal")
            self.btn_autocorte.configure(state="normal")
            self.al_cambiar_tolerancia(self.slider_tolerancia.get())
        else:
            self.slider_tolerancia.configure(state="disabled")
            self.btn_autocorte.configure(state="disabled")
            self.canvas.delete("rect_auto")
            self.btn_autocorte.configure(text="💾 Guardar Autocorte (0 partes)")
            self.status_label.configure(text="Modo Auto oculto.\nLienzo limpio para cortes manuales.", text_color="#9CA3AF")

    def limpiar_lienzo_y_recargar_base(self):
        self.canvas.delete("all")
        self.imagen_tk_render = ImageTk.PhotoImage(self.imagen_pil_original)
        self.canvas.create_image(0, 0, image=self.imagen_tk_render, anchor="nw")
        self.canvas.config(scrollregion=(0, 0, self.imagen_pil_original.width, self.imagen_pil_original.height))

    def al_cambiar_tolerancia(self, valor):
        if not self.islas_base_detectadas or self.switch_auto.get() == 0:
            return
            
        valor_int = int(valor)
        self.lbl_tolerancia_txt.configure(text=f"Tolerancia de Agrupación: {valor_int}px")
        
        islas_trabajo = [list(caja) for caja in self.islas_base_detectadas]
        
        cambio = True
        while cambio:
            cambio = False
            cajas_fusionadas = []
            while islas_trabajo:
                actual = islas_trabajo.pop(0)
                fusiono = False
                
                for otra in cajas_fusionadas:
                    en_rango_x = not (actual[2] + valor_int < otra[0] or actual[0] - valor_int > otra[2])
                    en_rango_y = not (actual[3] + valor_int < otra[1] or actual[1] - valor_int > otra[3])
                    
                    if en_rango_x and en_rango_y:
                        otra[0] = min(actual[0], otra[0])
                        otra[1] = min(actual[1], otra[1])
                        otra[2] = max(actual[2], otra[2])
                        otra[3] = max(actual[3], otra[3])
                        fusiono = True
                        cambio = True
                        break
                
                if not fusiono:
                    cajas_fusionadas.append(actual)
            islas_trabajo = cajas_fusionadas

        self.cajas_previsualizadas = islas_trabajo

        self.canvas.delete("rect_auto")
        ancho, alto = self.imagen_pil_original.size
        for (x1, y1, x2, y2) in self.cajas_previsualizadas:
            self.canvas.create_rectangle(
                max(0, x1 - 2), max(0, y1 - 2), 
                min(ancho, x2 + 2), min(alto, y2 + 2), 
                outline="#34D399", width=2, tags="rect_auto"
            )

        self.btn_autocorte.configure(text=f"💾 Guardar Autocorte ({len(self.cajas_previsualizadas)} partes)")

    def guardar_autocorte_confirmado(self):
        if not self.imagen_pil_original or not self.cajas_previsualizadas:
            return

        self.iniciar_animacion_loader("Exportando archivos...")
        threading.Thread(target=self.hilo_guardado_automatico, daemon=True).start()

    def hilo_guardado_automatico(self):
        carpeta_salida = "assets_recortados"
        if not os.path.exists(carpeta_salida):
            os.makedirs(carpeta_salida)

        nombre_base = self.entry_nombre.get().strip()
        if not nombre_base:
            nombre_base = "sprite"

        ancho, alto = self.imagen_pil_original.size
        elementos_guardados = 0

        for (x1, y1, x2, y2) in self.cajas_previsualizadas:
            x1_m, y1_m = max(0, x1 - 2), max(0, y1 - 2)
            x2_m, y2_m = min(ancho, x2 + 2), min(alto, y2 + 2)

            fragmento = self.imagen_pil_original.crop((x1_m, y1_m, x2_m, y2_m))
            siguiente_id = self.obtener_siguiente_indice(carpeta_salida, nombre_base)
            
            nombre_archivo = f"{nombre_base}{siguiente_id}.png"
            fragmento.save(os.path.join(carpeta_salida, nombre_archivo), "PNG")
            elementos_guardados += 1

        self.after(0, lambda: self.finalizar_guardado_automatico(elementos_guardados))

    def finalizar_guardado_automatico(self, cantidad):
        self.detener_animacion_loader("¡Guardado completado!")
        self.status_label.configure(text=f"¡Éxito! {cantidad} archivos exportados.", text_color="#10B981")
        self.after(3000, self.limpiar_mensajes_estado)

    # ---------------- Lógica del Modo Manual ----------------
    def al_hacer_click(self, event):
        if not self.imagen_pil_original:
            return
        self.recorte_en_progreso = True
        self.btn_cancelar.configure(state="normal")
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, 
            outline="#06B6D4", width=2, dash=(5, 3)
        )

    def al_arrastrar(self, event):
        if not self.recorte_en_progreso or self.rect_id is None:
            return
        cur_x = max(0, min(self.canvas.canvasx(event.x), self.imagen_pil_original.width))
        cur_y = max(0, min(self.canvas.canvasy(event.y), self.imagen_pil_original.height))
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, cur_x, cur_y)

    def cancelar_seleccion(self):
        if self.recorte_en_progreso:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
            self.recorte_en_progreso = False
            self.btn_cancelar.configure(state="disabled")

    def al_soltar_raton(self, event):
        if not self.recorte_en_progreso or self.rect_id is None:
            return
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        self.recorte_en_progreso = False
        self.btn_cancelar.configure(state="disabled")

        x1 = int(max(0, min(self.start_x, end_x)))
        y1 = int(max(0, min(self.start_y, end_y)))
        x2 = int(min(self.imagen_pil_original.width, max(self.start_x, end_x)))
        y2 = int(min(self.imagen_pil_original.height, max(self.start_y, end_y)))

        self.canvas.delete(self.rect_id)
        self.rect_id = None

        if (x2 - x1) > 5 and (y2 - y1) > 5:
            self.iniciar_animacion_loader("Guardando recorte manual...")
            threading.Thread(target=self.procesar_y_guardar_recorte_manual, args=(x1, y1, x2, y2), daemon=True).start()

    def procesar_y_guardar_recorte_manual(self, x1, y1, x2, y2):
        carpeta_salida = "assets_recortados"
        if not os.path.exists(carpeta_salida):
            os.makedirs(carpeta_salida)

        sprite_recortado = self.imagen_pil_original.crop((x1, y1, x2, y2))
        nombre_base = self.entry_nombre.get().strip()
        if not nombre_base:
            nombre_base = "sprite"

        siguiente_id = self.obtener_siguiente_indice(carpeta_salida, nombre_base)
        
        nombre_archivo = f"{nombre_base}{siguiente_id}.png"
        sprite_recortado.save(os.path.join(carpeta_salida, nombre_archivo), "PNG")

        self.after(0, lambda: self.finalizar_guardado_manual(x1, y1, x2, y2, nombre_archivo))

    def finalizar_guardado_manual(self, x1, y1, x2, y2, nombre_archivo):
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="#38BDF8", width=1)
        self.detener_animacion_loader(f"Guardado: {nombre_archivo}")
        self.status_label.configure(text=f"¡Manual Guardado!\n{nombre_archivo}", text_color="#38BDF8")
        self.after(3000, self.limpiar_mensajes_estado)

    def limpiar_mensajes_estado(self):
        self.status_label.configure(text="Estado: Listo", text_color="#9CA3AF")
        self.lbl_loader_status.configure(text="Esperando acción...", text_color="#71717A")
        self.progressbar.set(0)

if __name__ == "__main__":
    app = SpriteSlicerApp()
    app.mainloop()
