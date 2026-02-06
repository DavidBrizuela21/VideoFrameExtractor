import flet as ft
import cv2
import os

def main(page: ft.Page):
    page.title = "Frame Extractor Pro"
    page.theme_mode = "light"
    page.scroll = "adaptive"
    page.window_width = 400
    page.window_height = 700
    
    # --- Variables de Estado ---
    archivos_seleccionados = []

    # --- UI Elements ---
    txt_segundo = ft.TextField(
        label="Segundo exacto", 
        value="0", 
        keyboard_type="number",
        prefix_icon=ft.icons.TIMER,
        width=200
    )
    
    lbl_estado = ft.Text("No hay videos seleccionados", italic=True, color="grey")
    lista_resultados = ft.ListView(expand=1, spacing=10)
    
    # --- Lógica OpenCV ---
    def extraer_frame(video_path, segundo, nombre_archivo):
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duracion = total_frames / fps if fps > 0 else 0
            
            segundo_float = float(segundo)
            if segundo_float < duracion:
                cap.set(cv2.CAP_PROP_POS_MSEC, segundo_float * 1000)
            else:
                cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, total_frames - 1))
                
            exito, frame = cap.read()
            cap.release()
            
            if exito:
                directorio = obtener_ruta_galeria()
                # Limpiamos el nombre para evitar errores de ruta
                nombre_limpio = os.path.basename(nombre_archivo).replace(" ", "_")
                ruta_final = os.path.join(directorio, f"frame_{nombre_limpio}.jpg")
            
                cv2.imwrite(ruta_final, frame)
                return ruta_final
            return None
        except: return None

    # --- Acciones de Botones ---
    def procesar_todo(e):
        if not archivos_seleccionados:
            return
        
        btn_comenzar.disabled = True
        btn_subir.disabled = True
        lista_resultados.controls.clear()
        page.update()

        for path, name in archivos_seleccionados:
            lista_resultados.controls.append(ft.Text(f"Procesando {name}...", size=12))
            page.update()
            
            res = extraer_frame(path, txt_segundo.value, name)
            
            if res:
                lista_resultados.controls.append(
                    ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color="green"),
                        ft.Text(f"Listo: {name}.jpg", color="green")
                    ])
                )
            else:
                lista_resultados.controls.append(ft.Text(f"❌ Error en {name}", color="red"))
        
        btn_subir.disabled = False
        page.update()

    def on_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            archivos_seleccionados.clear()
            for f in e.files:
                archivos_seleccionados.append((f.path, f.name))
            
            lbl_estado.value = f"✅ {len(archivos_seleccionados)} video(s) seleccionados"
            lbl_estado.color = "blue"
            btn_comenzar.disabled = False
            page.update()

    # --- Componentes de la Interfaz ---
    file_picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(file_picker)

    btn_subir = ft.ElevatedButton(
        "1. Seleccionar Videos",
        icon=ft.icons.VIDEO_FILE,
        on_click=lambda _: file_picker.pick_files(allow_multiple=True, file_type="video"),
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
    )

    btn_comenzar = ft.FilledButton(
        "3. Comenzar Extracción",
        icon=ft.icons.PLAY_ARROW,
        disabled=True,
        on_click=procesar_todo,
        style=ft.ButtonStyle(bgcolor="blue", color="white")
    )

    # --- Layout ---
    page.add(
        ft.AppBar(
            title=ft.Text("Frame Extractor"), 
            bgcolor=ft.colors.BLUE_GREY_50,
            center_title=True
        ),
        ft.Container(
            padding=20,
            content=ft.Column([
                ft.Text("Paso 1: Sube tus archivos", weight="bold"),
                btn_subir,
                lbl_estado,
                ft.Divider(height=30),
                
                ft.Text("Paso 2: Configura el tiempo", weight="bold"),
                txt_segundo,
                ft.Text("Si el video es más corto que el tiempo indicado, se tomará el último frame.", 
                        size=11, color="grey"),
                ft.Divider(height=30),
                
                ft.Text("Paso 3: ¡Listo!", weight="bold"),
                btn_comenzar,
                ft.Divider(height=20),
                
                ft.Text("Resultados:", size=14, weight="w500"),
                lista_resultados
            ], spacing=15)
        )
    )

ft.app(target=main)