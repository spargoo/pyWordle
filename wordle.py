import tkinter as tk
from tkinter import font, messagebox
import random
import json

# File paths for JSON data
RUTA_TODAS = "palabras5.json"  # All valid words for input
RUTA_WORDLE = "palabraswordle.json"  # Words that can be the answer

def cargar_palabras(ruta_json, clave="palabras"):
    """Load words from a JSON file."""
    try:
        with open(ruta_json, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            return [palabra.lower() for palabra in datos.get(clave, []) if len(palabra) == 5]
    except FileNotFoundError:
        messagebox.showerror("Error", f"El archivo {ruta_json} no existe.")
        return []
    except json.JSONDecodeError:
        messagebox.showerror("Error", f"El archivo {ruta_json} no tiene un formato JSON válido.")
        return []

# Load word sets
PALABRAS_TODAS = cargar_palabras(RUTA_TODAS)
PALABRAS_WORDLE = cargar_palabras(RUTA_WORDLE)
if not PALABRAS_TODAS or not PALABRAS_WORDLE:
    raise ValueError("No se pudieron cargar palabras válidas desde los archivos JSON.")

intentos, longitud_palabra, fila_actual, columna_actual = 6, 5, 0, 0
tiempo_restante, tiempo_inicial, after_id, modo_actual = 120, 120, None, None

# Colors 
COLOR_FONDO, COLOR_TEXTO, COLOR_VERDE = "#121213", "#FFFFFF", "#538d4e"
COLOR_AMARILLO, COLOR_GRIS, COLOR_BORDE = "#b59f3b", "#3a3a3c", "#3a3a3c"
COLOR_RECUADRO, COLOR_TECLADO_FONDO, COLOR_HOVER = "#526589", "#404454", "#6B7280"
COLOR_ERROR, COLOR_TOOLTIP, COLOR_ARROW = "#FF0000", "#023047", "#f75000"
COLOR_DESTACADO, COLOR_SUBTITULO = "#FF6F61", "#4A90E2"
FADE_COLORES = ["#538d4e","#6b9b4e","#83a94e","#9bb74e","#b3c54e","#cbd34e","#e3e14e","#f7d948","#f7c140","#f7a938","#f79130","#f77928","#f76120","#f74918","#f73110","#FF0000"]

# Main window "root" settings
root = tk.Tk()
root.iconbitmap("favicon.ico")
root.title("Wordle en Python")
root.geometry("450x650")
root.configure(bg=COLOR_FONDO)
root.minsize(450, 650)
x, y = (root.winfo_screenwidth() - 450) // 2, (root.winfo_screenheight() - 650) // 2
root.geometry(f"450x650+{x}+{y}")

# Font definitions
FUENTE_TEXTO_GRANDE, FUENTE_TEXTO_GRANDE_BOLD = font.Font(family="Arial", size=16), font.Font(family="Arial", size=16, weight="bold")
FUENTE_PIXEL, FUENTE_PIXEL_PEQUENA, FUENTE_PIXEL_GRANDE = font.Font(family="Courier", size=18, weight="bold"), font.Font(family="Courier", size=12, weight="bold"), font.Font(family="Courier", size=30, weight="bold")
FUENTE_EMOJI, FUENTE_TEXTO, FUENTE_TOOLTIP = font.Font(family="Arial", size=30), font.Font(family="Arial", size=14), font.Font(family="Courier", size=int(18 * 0.7), weight="bold")
FUENTE_BOTONES_MENU, FUENTE_BOTONES_RESULTADO = font.Font(family="Courier", size=14, weight="bold"), font.Font(family="Courier", size=12, weight="bold")

# Main menu
menu_frame = tk.Frame(root, bg=COLOR_FONDO)
menu_frame.pack(expand=True, pady=67)
icono = tk.PhotoImage(file="favicon.png").subsample(2, 2)
icono_label = tk.Label(menu_frame, image=icono, bg=COLOR_FONDO)
icono_label.pack(pady=(5, 20))

def crear_boton_menu(texto, comando, pady):
    boton = tk.Button(menu_frame, text=f"→ {texto}", font=FUENTE_BOTONES_MENU, bg=COLOR_FONDO, fg=COLOR_TEXTO, relief="flat", activebackground=COLOR_FONDO, activeforeground=COLOR_HOVER, borderwidth=0, highlightthickness=0, command=comando)
    boton.pack(pady=pady)
    boton.bind("<Enter>", lambda e: boton.config(fg=COLOR_HOVER))
    boton.bind("<Leave>", lambda e: boton.config(fg=COLOR_TEXTO, bg=COLOR_FONDO))
    return boton

def configurar_vinculaciones_teclado(modo):
    # Key bindings
    root.unbind("<Return>")
    if modo == "juego":
        root.bind("<Return>", lambda event: verificar_palabra())
    elif modo == "resultados" and 'boton_accion' in globals():
        root.bind("<Return>", lambda event: boton_accion.invoke() if resultado_frame.winfo_ismapped() else None)

def iniciar_modo_clasico():
    # Classic mode init
    global palabra_secreta, fila_actual, columna_actual, estado_letras, after_id, modo_actual
    if after_id: root.after_cancel(after_id)
    palabra_secreta, fila_actual, columna_actual = random.choice(PALABRAS_WORDLE), 0, 0
    estado_letras, modo_actual = {letra: None for fila in letras_teclado for letra in fila}, "clasico"
    for fila in cuadros:
        for cuadro in fila:
            cuadro.config(text="", bg=COLOR_FONDO, highlightbackground=COLOR_BORDE)
    for boton in botones_teclado.values():
        boton.config(bg=COLOR_TECLADO_FONDO)
    menu_frame.pack_forget()
    juego_frame.pack(expand=True, fill="both")
    top_frame.pack(fill="x", pady=40)
    info_label.pack(expand=True)
    tiempo_label.pack_forget()
    frame_grid.pack(pady=30)
    teclado_frame.pack(pady=50)
    configurar_vinculaciones_teclado("juego")

def mostrar_seleccion_tiempo():
    # Time "menu", hehe
    menu_frame.pack_forget()
    seleccion_tiempo_frame.pack(expand=True, pady=40)

def iniciar_modo_contrarreloj(tiempo_elegido):
    # Init contrarreloj mode w/ the time selected
    global palabra_secreta, fila_actual, columna_actual, estado_letras, tiempo_restante, tiempo_inicial, after_id, modo_actual
    if after_id: root.after_cancel(after_id)
    palabra_secreta, fila_actual, columna_actual = random.choice(PALABRAS_WORDLE), 0, 0
    tiempo_restante, tiempo_inicial = tiempo_elegido, tiempo_elegido
    estado_letras, modo_actual = {letra: None for fila in letras_teclado for letra in fila}, "contrarreloj"
    for fila in cuadros:
        for cuadro in fila:
            cuadro.config(text="", bg=COLOR_FONDO, highlightbackground=COLOR_BORDE)
    for boton in botones_teclado.values():
        boton.config(bg=COLOR_TECLADO_FONDO)
    seleccion_tiempo_frame.pack_forget()
    juego_frame.pack(expand=True, fill="both")
    top_frame.pack(fill="x", pady=40)
    info_label.pack(expand=True)
    tiempo_label.pack(pady=5)
    tiempo_label.config(text=f"Tiempo restante: {tiempo_restante} segundos", fg=COLOR_VERDE)
    frame_grid.pack(pady=30)
    teclado_frame.pack(pady=50)
    configurar_vinculaciones_teclado("juego")
    verificar_tiempo()

def mostrar_como_jugar():
    menu_frame.pack_forget()
    como_jugar_frame = tk.Frame(root, bg=COLOR_FONDO)
    como_jugar_frame.pack(expand=True, fill="both", pady=10)
    imagen_frame = tk.Frame(como_jugar_frame, bg=COLOR_FONDO)
    imagen_frame.pack(expand=True, fill="both")
    try:
        imagen = tk.PhotoImage(file="pywordle_example.png")
        imagen_label = tk.Label(imagen_frame, image=imagen, bg=COLOR_FONDO, borderwidth=0, highlightthickness=0)
        imagen_label.image = imagen
        imagen_label.pack(expand=True)
    except tk.TclError:
        tk.Label(imagen_frame, text="No se pudo cargar la imagen", font=FUENTE_TEXTO_GRANDE, bg=COLOR_FONDO, fg=COLOR_ERROR).pack(expand=True)
    boton = tk.Button(imagen_frame, text="← Volver", font=FUENTE_BOTONES_MENU, bg=COLOR_FONDO, fg=COLOR_TEXTO, relief="flat", activebackground=COLOR_FONDO, activeforeground=COLOR_HOVER, borderwidth=0, highlightthickness=0, width=10, height=1, command=lambda: [como_jugar_frame.pack_forget(), menu_frame.pack(expand=True, pady=47)])
    boton.place(relx=0.5, rely=0.82, anchor="center")
    boton.bind("<Enter>", lambda e: boton.config(fg=COLOR_HOVER))
    boton.bind("<Leave>", lambda e: boton.config(fg=COLOR_TEXTO, bg=COLOR_FONDO))

# Buttons 
crear_boton_menu("Modo clásico", iniciar_modo_clasico, 5)
crear_boton_menu("Modo contrarreloj", mostrar_seleccion_tiempo, 10)
crear_boton_menu("Cómo jugar", mostrar_como_jugar, 15)

seleccion_tiempo_frame = tk.Frame(root, bg=COLOR_FONDO)
titulo_frame = tk.Frame(seleccion_tiempo_frame, bg=COLOR_FONDO)
titulo_frame.pack(pady=20)
tk.Label(titulo_frame, text="Elige el ", font=FUENTE_PIXEL, bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side="left")
tk.Label(titulo_frame, text="tiempo", font=FUENTE_PIXEL, bg=COLOR_FONDO, fg=COLOR_ARROW).pack(side="left")
tiempos_frame = tk.Frame(seleccion_tiempo_frame, bg=COLOR_FONDO)
tiempos_frame.pack(pady=30)

def crear_boton_tiempo(texto, tiempo):
    """Create a time selection button."""
    boton = tk.Button(tiempos_frame, text=texto, font=FUENTE_BOTONES_MENU, bg=COLOR_FONDO, fg=COLOR_TEXTO, relief="flat", activebackground=COLOR_FONDO, activeforeground=COLOR_HOVER, borderwidth=0, highlightthickness=0, width=10, height=1, command=lambda: iniciar_modo_contrarreloj(tiempo))
    boton.pack(side="left", padx=5)
    boton.bind("<Enter>", lambda e: boton.config(fg=COLOR_HOVER))
    boton.bind("<Leave>", lambda e: boton.config(fg=COLOR_TEXTO, bg=COLOR_FONDO))
    return boton

for t in [("30 seg", 30), ("60 seg", 60), ("90 seg", 90), ("120 seg", 120)]:
    crear_boton_tiempo(t[0], t[1])

tk.Button(seleccion_tiempo_frame, text="← Volver", font=FUENTE_BOTONES_MENU, bg=COLOR_FONDO, fg=COLOR_TEXTO, relief="flat", activebackground=COLOR_FONDO, activeforeground=COLOR_HOVER, borderwidth=0, highlightthickness=0, width=8, height=1, command=lambda: [seleccion_tiempo_frame.pack_forget(), menu_frame.pack(expand=True, pady=67)]).pack(pady=40)
juego_frame = tk.Frame(root, bg=COLOR_FONDO)
top_frame = tk.Frame(juego_frame, bg=COLOR_FONDO)
back_frame = tk.Frame(top_frame, bg=COLOR_FONDO)
back_frame.place(relx=0.35, rely=0.6, anchor="e")
back_image = tk.PhotoImage(file="back.png").subsample(4, 4)
back_label = tk.Label(back_frame, image=back_image, bg=COLOR_FONDO, cursor="hand2")
back_label.pack()
tooltip = tk.Toplevel(root)
tooltip.wm_overrideredirect(True)
tooltip.withdraw()
tooltip_label = tk.Label(tooltip, text="Volver al menú", font=FUENTE_TOOLTIP, bg=COLOR_TOOLTIP, fg=COLOR_TEXTO, padx=5, pady=2)
tooltip_label.pack()

def mostrar_tooltip(event):
    tooltip.wm_geometry(f"+{back_label.winfo_rootx()}+{back_label.winfo_rooty() + back_label.winfo_height() + 5}") # positions the 'tooltip' window relative to the 'back_label' widget
    tooltip.deiconify()

def ocultar_tooltip(event):
    tooltip.withdraw()

def mostrar_confirmacion_volver():
    # Confirmation dialog
    confirm = tk.Toplevel(root)
    confirm.title("Volver al menú")
    confirm.geometry(f"250x150+{root.winfo_x() + (root.winfo_width() - 250) // 2}+{root.winfo_y() + (root.winfo_height() - 150) // 2}") # centering the confirm window into the root one 
    confirm.configure(bg=COLOR_FONDO)
    confirm.transient(root)
    confirm.grab_set() # grabbing all events for the confirmation window
    confirm.resizable(False, False)
    confirm.attributes('-toolwindow', True) 
    confirm.iconbitmap("favicon.ico")
    tk.Label(confirm, text="¿Estás seguro?", font=font.Font(family="Courier", size=14, weight="bold"), bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(expand=True, pady=10)
    btn_frame = tk.Frame(confirm, bg=COLOR_FONDO)
    btn_frame.pack(expand=True, pady=10)
    tk.Button(btn_frame, text="Sí", font=FUENTE_BOTONES_RESULTADO, bg=COLOR_GRIS, fg=COLOR_TEXTO, relief="flat", activebackground=COLOR_GRIS, borderwidth=0, highlightthickness=0, width=5, height=1, command=lambda: [confirm.destroy(), volver_al_menu(), root.deiconify(), root.lift(), root.focus_force()]).pack(side="left", padx=5)
    btn_no = tk.Button(btn_frame, text="Cancelar", font=FUENTE_BOTONES_RESULTADO, bg=COLOR_GRIS, fg=COLOR_TEXTO, relief="flat", activebackground=COLOR_GRIS, borderwidth=0, highlightthickness=0, width=8, height=1, command=lambda: [confirm.destroy(), root.deiconify(), root.lift(), root.focus_force()])
    btn_no.pack(side="left", padx=5)
    btn_no.focus_set()
    confirm.protocol("WM_DELETE_WINDOW", lambda: [confirm.destroy(), root.deiconify(), root.lift(), root.focus_force()])
    confirm.bind("<Return>", lambda event: [confirm.destroy(), root.deiconify(), root.lift(), root.focus_force()])

back_label.bind("<Enter>", mostrar_tooltip)
back_label.bind("<Leave>", ocultar_tooltip)
back_label.bind("<Button-1>", lambda e: mostrar_confirmacion_volver())
info_label = tk.Label(top_frame, text="¡Adivina la palabra!", font=FUENTE_PIXEL, bg=COLOR_FONDO, fg=COLOR_TEXTO)
tiempo_label = tk.Label(top_frame, text=f"Tiempo restante: {tiempo_restante} segundos", font=FUENTE_PIXEL_PEQUENA, bg=COLOR_FONDO, fg=COLOR_VERDE)
frame_grid = tk.Frame(juego_frame, bg=COLOR_FONDO)
cuadros = [[tk.Label(frame_grid, text="", width=4, height=2, font=FUENTE_PIXEL, relief="solid", bg=COLOR_FONDO, fg=COLOR_TEXTO, borderwidth=2, highlightbackground=COLOR_BORDE, highlightthickness=2) for j in range(longitud_palabra)] for i in range(intentos)]

for i in range(intentos):
    for j in range(longitud_palabra):
        cuadros[i][j].grid(row=i, column=j, padx=7, pady=7)
        cuadros[i][j].bind("<Button-1>", lambda e, r=i, c=j: seleccionar_letra(r, c))

teclado_frame = tk.Frame(juego_frame, bg=COLOR_FONDO)

def actualizar_borde_activo():
    # Constantly updating the ACTIVE cell border
    for i in range(intentos):
        for j in range(longitud_palabra):
            cuadros[i][j].config(highlightbackground=COLOR_BORDE, highlightthickness=2)
    if fila_actual < intentos:
        cuadros[fila_actual][columna_actual].config(highlightbackground=COLOR_RECUADRO, highlightthickness=2)

def seleccionar_letra(fila, columna):
    global columna_actual
    if fila == fila_actual:
        columna_actual = columna
        actualizar_borde_activo() #.

def actualizar_teclado():
    # Updating the keyboard colors based on the letter states
    for letra, estado in estado_letras.items():
        boton = botones_teclado[letra]
        if estado == "verde": boton.config(bg=COLOR_VERDE, fg=COLOR_TEXTO)
        elif estado == "amarillo": boton.config(bg=COLOR_AMARILLO, fg=COLOR_TEXTO)
        elif estado == "gris": boton.config(bg=COLOR_GRIS, fg=COLOR_TEXTO)
        else: boton.config(bg=COLOR_TECLADO_FONDO, fg=COLOR_TEXTO)

def escribir_letra(letra):
    global columna_actual
    if columna_actual < longitud_palabra:
        cuadros[fila_actual][columna_actual].config(text=letra)
        if columna_actual < longitud_palabra - 1:
            columna_actual += 1
        actualizar_borde_activo()

def borrar_letra():
    global columna_actual
    if cuadros[fila_actual][columna_actual].cget("text"):
        cuadros[fila_actual][columna_actual].config(text="")
    elif columna_actual > 0:
        columna_actual -= 1
        cuadros[fila_actual][columna_actual].config(text="")
    actualizar_borde_activo()

def reiniciar_juego():
    # Full reset
    global palabra_secreta, fila_actual, columna_actual, estado_letras, tiempo_restante
    palabra_secreta, fila_actual, columna_actual = random.choice(PALABRAS_WORDLE), 0, 0
    if modo_actual == "contrarreloj": tiempo_restante = tiempo_inicial
    estado_letras = {letra: None for fila in letras_teclado for letra in fila}
    for fila in cuadros:
        for cuadro in fila:
            cuadro.config(text="", bg=COLOR_FONDO, highlightbackground=COLOR_BORDE)
    for boton in botones_teclado.values():
        boton.config(bg=COLOR_TECLADO_FONDO)
    info_label.config(text="¡Adivina la palabra!", fg=COLOR_TEXTO)
    resultado_frame.pack_forget()
    juego_frame.pack(expand=True, fill="both")
    top_frame.pack(fill="x", pady=40)
    info_label.pack(expand=True)
    if modo_actual == "contrarreloj": tiempo_label.pack(pady=5); tiempo_label.config(text=f"Tiempo restante: {tiempo_restante} segundos", fg=COLOR_VERDE)
    else: tiempo_label.pack_forget()
    frame_grid.pack(pady=30)
    teclado_frame.pack(pady=50)
    actualizar_borde_activo()
    actualizar_teclado()
    configurar_vinculaciones_teclado("juego")

def volver_al_menu():
    global after_id
    if after_id: root.after_cancel(after_id)
    juego_frame.pack_forget()
    if 'resultado_frame' in globals(): resultado_frame.pack_forget()
    menu_frame.pack(expand=True, pady=67)
    configurar_vinculaciones_teclado("menu")

def volver_a_seleccion_tiempo():
    global after_id
    if after_id: root.after_cancel(after_id)
    resultado_frame.pack_forget()
    seleccion_tiempo_frame.pack(expand=True, pady=40)
    configurar_vinculaciones_teclado("menu")

def mostrar_resultado(gano, es_por_tiempo=False):
    # Displaying the result
    global resultado_frame, boton_accion
    juego_frame.pack_forget()
    if after_id: root.after_cancel(after_id)
    if 'resultado_frame' in globals(): resultado_frame.destroy()
    resultado_frame = tk.Frame(root, bg=COLOR_FONDO)
    resultado_frame.pack(expand=True, pady=67)
    if gano:
        if modo_actual == "contrarreloj":
            tk.Label(resultado_frame, text="¡Ganaste el modo contrarreloj!", font=FUENTE_PIXEL, bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=5)
        else:
            intentos_texto = fila_actual + 1
            mensajes = ["Ah, sos un capo", "Only one try needed..."] if intentos_texto == 1 else ["¡Sí, señor!", f"¡Adivinaste en {intentos_texto} intentos!"]
            for msg in mensajes:
                tk.Label(resultado_frame, text=msg, font=FUENTE_PIXEL, bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=5)
        tk.Label(resultado_frame, text=f"La palabra era: {palabra_secreta.upper()}", font=FUENTE_PIXEL, bg=COLOR_FONDO, fg=COLOR_VERDE).pack(pady=10)
    else:
        texto = "¡Se acabó el tiempo!" if es_por_tiempo else "No se pudo..."
        tk.Label(resultado_frame, text=texto, font=FUENTE_PIXEL, bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=10)
        tk.Label(resultado_frame, text=f"La palabra era: {palabra_secreta.upper()}", font=FUENTE_PIXEL, bg=COLOR_FONDO, fg=COLOR_ERROR).pack(pady=10)
    tk.Frame(resultado_frame, height=20, bg=COLOR_FONDO).pack()
    botones_frame = tk.Frame(resultado_frame, bg=COLOR_FONDO)
    botones_frame.pack(pady=10)
    boton_texto = "Reintentar" if not gano else "Volver a jugar"
    boton_accion = tk.Button(botones_frame, text=boton_texto, font=FUENTE_BOTONES_RESULTADO, bg=COLOR_GRIS, fg=COLOR_TEXTO, relief="flat", activebackground=COLOR_GRIS, borderwidth=0, highlightthickness=0, width=14, height=1, command=reiniciar_y_mostrar)
    boton_accion.pack(side="left", padx=5)
    boton_accion.bind("<Enter>", lambda e: boton_accion.config(bg=COLOR_HOVER))
    boton_accion.bind("<Leave>", lambda e: boton_accion.config(bg=COLOR_GRIS))
    boton_accion.focus_set()
    if modo_actual == "contrarreloj":
        boton_cambiar = tk.Button(botones_frame, text="Cambiar tiempo", font=FUENTE_BOTONES_RESULTADO, bg=COLOR_GRIS, fg=COLOR_TEXTO, relief="flat", activebackground=COLOR_GRIS, borderwidth=0, highlightthickness=0, width=14, height=1, command=volver_a_seleccion_tiempo)
        boton_cambiar.pack(side="left", padx=5)
        boton_cambiar.bind("<Enter>", lambda e: boton_cambiar.config(bg=COLOR_HOVER))
        boton_cambiar.bind("<Leave>", lambda e: boton_cambiar.config(bg=COLOR_GRIS))
    boton_volver = tk.Button(botones_frame, text="Volver al menú", font=FUENTE_BOTONES_RESULTADO, bg=COLOR_GRIS, fg=COLOR_TEXTO, relief="flat", activebackground=COLOR_GRIS, borderwidth=0, highlightthickness=0, width=14, height=1, command=volver_al_menu)
    boton_volver.pack(side="left", padx=5)
    boton_volver.bind("<Enter>", lambda e: boton_volver.config(bg=COLOR_HOVER))
    boton_volver.bind("<Leave>", lambda e: boton_volver.config(bg=COLOR_GRIS))
    emoji = "😎" if (gano and modo_actual != "contrarreloj" and fila_actual + 1 > 1) else "⭐" if (gano and modo_actual != "contrarreloj" and fila_actual + 1 == 1) else "😢"
    tk.Label(resultado_frame, text=emoji, font=FUENTE_EMOJI, bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=20)
    configurar_vinculaciones_teclado("resultados")

def animar_letra(index, intento):
    if index >= longitud_palabra:
        verificar_fin_juego(intento)
        return
    letra = intento[index]
    cuadro = cuadros[fila_actual][index]
    if letra == palabra_secreta[index]:
        color, estado_letras[letra.upper()] = COLOR_VERDE, "verde"
    elif letra in palabra_secreta:
        color = COLOR_AMARILLO
        if estado_letras[letra.upper()] != "verde": estado_letras[letra.upper()] = "amarillo"
    else:
        color = COLOR_GRIS
        if estado_letras[letra.upper()] is None: estado_letras[letra.upper()] = "gris"
    cuadro.config(bg=color)
    root.after(150, animar_letra, index + 1, intento) # 150 ms delay between next letter animation

def verificar_fin_juego(intento):
    global fila_actual, columna_actual
    actualizar_teclado()
    if intento == palabra_secreta:
        root.after(500, lambda: mostrar_resultado(True))
        return
    fila_actual += 1
    columna_actual = 0
    if fila_actual >= intentos:
        root.after(500, lambda: mostrar_resultado(False, es_por_tiempo=modo_actual == "contrarreloj"))
    else:
        actualizar_borde_activo()

def mostrar_error(mensaje):
    global error_after_id
    if 'error_after_id' in globals() and error_after_id: root.after_cancel(error_after_id)
    info_label.config(text=mensaje, fg=COLOR_ERROR)
    error_after_id = root.after(2000, lambda: info_label.config(text="¡Adivina la palabra!", fg=COLOR_TEXTO))

def verificar_palabra():
    """Verify the entered word."""
    global fila_actual, columna_actual
    intento = "".join(cuadros[fila_actual][i].cget("text").lower() for i in range(longitud_palabra))
    if len(intento) != longitud_palabra or not intento.isalpha():
        mostrar_error("Debes ingresar 5 letras")
        return
    if intento not in PALABRAS_TODAS:
        mostrar_error("La palabra no está en la lista")
        return
    animar_letra(0, intento)

def verificar_tiempo():
    # Checking & updating time :3
    global tiempo_restante, after_id
    if tiempo_restante <= 0:
        root.after(500, lambda: mostrar_resultado(False, es_por_tiempo=True))
        return
    tiempo_restante -= 1
    tiempo_label.config(text=f"Tiempo restante: {tiempo_restante} segundos")
    porcentaje = tiempo_restante / tiempo_inicial
    tiempo_label.config(fg=FADE_COLORES[int((1 - porcentaje) * (len(FADE_COLORES) - 1))])
    after_id = root.after(1000, verificar_tiempo)

def reiniciar_y_mostrar():
    # Restarting the game, based in the mode previosuly selected 
    global after_id
    if after_id: root.after_cancel(after_id)
    resultado_frame.pack_forget()
    if modo_actual == "contrarreloj": iniciar_modo_contrarreloj(tiempo_inicial)
    else: iniciar_modo_clasico()

letras_teclado = [["Q","W","E","R","T","Y","U","I","O","P"],["A","S","D","F","G","H","J","K","L","Ñ"],["TICK","Z","X","C","V","B","N","M","BORRAR"]]
estado_letras = {letra: None for fila in letras_teclado for letra in fila}
botones_teclado = {}

for i, fila in enumerate(letras_teclado):
    frame_fila = tk.Frame(teclado_frame, bg=COLOR_FONDO)
    frame_fila.pack(pady=3)
    for letra in fila:
        if letra == "TICK": boton = tk.Button(frame_fila, text="↳", font=FUENTE_PIXEL, width=3, height=1, bg=COLOR_TECLADO_FONDO, fg=COLOR_TEXTO, relief="flat", borderwidth=0, command=verificar_palabra)
        elif letra == "BORRAR": boton = tk.Button(frame_fila, text="⌫", font=FUENTE_PIXEL, width=3, height=1, bg=COLOR_TECLADO_FONDO, fg=COLOR_TEXTO, relief="flat", borderwidth=0, command=borrar_letra)
        else: boton = tk.Button(frame_fila, text=letra, font=FUENTE_PIXEL, width=3, height=1, bg=COLOR_TECLADO_FONDO, fg=COLOR_TEXTO, relief="flat", borderwidth=0, command=lambda l=letra: escribir_letra(l))
        boton.bind("<Enter>", lambda e, b=boton: b.config(bg=COLOR_HOVER))
        boton.bind("<Leave>", lambda e, b=boton: b.config(bg=COLOR_VERDE if estado_letras.get(b["text"]) == "verde" else COLOR_AMARILLO if estado_letras.get(b["text"]) == "amarillo" else COLOR_GRIS if estado_letras.get(b["text"]) == "gris" else COLOR_TECLADO_FONDO))
        boton.pack(side="left", padx=3, pady=3)
        botones_teclado[letra] = boton

root.bind("<KeyPress>", lambda event: escribir_letra(event.char.upper()) if event.char.isalpha() else None)
root.bind("<BackSpace>", lambda event: borrar_letra())

root.mainloop()