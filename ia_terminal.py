import os
import sys
import subprocess
import mimetypes
import textwrap
import re
from datetime import datetime
from openai import OpenAI

# Verificar clave API de forma segura
if not os.environ.get("OPENAI_API_KEY"):
    print("❌ Error: La variable de entorno OPENAI_API_KEY no está configurada.")
    sys.exit(1)

client = OpenAI()
MODELO = "gpt-4o-mini"
MAX_HISTORIAL = 20

# Regex para extraer comandos CLI
BASH_REGEX = re.compile(r"```bash\s+(.*?)\s+```", re.DOTALL)

CONTEXTO_SISTEMA = {
    "role": "system", 
    "content": (
        "Eres un asistente de terminal de élite para Lubuntu (Linux), experto tanto en administración de sistemas "
        "como en desarrollo de software y análisis avanzado de código (Python, Bash, C, JS, etc.).\n"
        "Cuando el usuario te pregunte por una ruta, recibirás información técnica de la misma de forma automática. "
        "Si esa ruta es un archivo de código fuente, también recibirás un extracto del código de su interior.\n"
        "Analiza el código a nivel profesional: busca bugs, optimizaciones, explica su lógica o escribe refactorizaciones "
        "si el usuario lo solicita. Sé conciso y directo.\n"
        "Si sugieres comandos para ejecutar en Lubuntu o bloques de código corregidos, estructúralos siempre así:\n"
        "```bash\n"
        "comando_aqui\n"
        "```"
    )
}

def formatear_y_ajustar_texto(texto):
    """Ajusta automáticamente el texto al ancho actual de la terminal."""
    try:
        ancho_pantalla = os.get_terminal_size().columns
    except OSError:
        ancho_pantalla = 80
        
    lineas = texto.split('\n')
    lineas_ajustadas = []
    en_bloque_codigo = False
    
    for linea in lineas:
        if linea.strip().startswith("```"):
            en_bloque_codigo = not en_bloque_codigo
            lineas_ajustadas.append(linea)
            continue
            
        if en_bloque_codigo:
            lineas_ajustadas.append(linea)
        else:
            if linea.strip() == "":
                lineas_ajustadas.append("")
            else:
                lineas_ajustadas.extend(textwrap.wrap(linea, width=max(40, ancho_pantalla - 2)))
                
    return lineas_ajustadas

def imprimir_con_paginador(lineas, prefijo=""):
    """Imprime el texto en bloques simulando el comportamiento de '| more'."""
    try:
        # Detectamos el alto de tu QTerminal en tiempo real
        alto_pantalla = os.get_terminal_size().lines
    except OSError:
        alto_pantalla = 24  # Medida estándar por defecto
        
    # Dejamos un margen de 3 líneas para el prompt del paginador
    lineas_por_bloque = max(5, alto_pantalla - 3)
    
    contador = 0
    primer_bloque = True
    
    for i, linea in enumerate(lineas):
        # Aplicamos el prefijo ("IA ➜") solo en la primerísima línea de la respuesta
        if i == 0 and prefijo:
            print(f"{prefijo} {linea}")
        else:
            print(linea)
            
        contador += 1
        
        # Cuando se llena la pantalla, pausamos y esperamos al usuario
        if contador >= lineas_por_bloque:
            # Si es el primer bloque restamos el espacio usado por el prompt del usuario
            if primer_bloque:
                primer_bloque = False
                lineas_por_bloque = max(5, alto_pantalla - 2)
            
            # Solo pausamos si quedan más líneas por mostrar
            if i < len(lineas) - 1:
                try:
                    # Imprime el indicador en color amarillo inverso para que resalte
                    print("\033[7;33m-- Más -- (Presiona ENTER para continuar, 'q' para salir)\033[0m", end="", flush=True)
                    seleccion = input().strip().lower()
                    # Borramos la línea del indicador "-- Más --" para que la pantalla quede limpia
                    print("\033[A\033[K", end="")
                    
                    if seleccion == 'q':
                        print("\n[Lectura interrumpida]")
                        break
                except (KeyboardInterrupt, EOFError):
                    print()
                    break
                contador = 0

def inspeccionar_ruta_sistema(posible_ruta):
    """Analiza la ruta de forma eficiente y extrae metadatos o código fuente."""
    ruta_real = os.path.expanduser(posible_ruta.strip("'\" "))
    if not os.path.exists(ruta_real):
        return None 
        
    info = [f"--- DETECTADA RUTA DEL SISTEMA: '{posible_ruta}' ---"]
    try:
        stats = os.stat(ruta_real)
        if os.path.isdir(ruta_real):
            info.append("Tipo: Directorio / Carpeta")
            elementos = os.listdir(ruta_real)
            info.append(f"Cantidad de elementos: {len(elementos)}")
            if elementos:
                info.append("Contenido (muestra): " + ", ".join(elementos[:15]))
        elif os.path.isfile(ruta_real):
            info.append("Tipo: Archivo regular")
            tipo_mime, _ = mimetypes.guess_type(ruta_real)
            info.append(f"Tipo de datos (MIME): {tipo_mime or 'Desconocido'}")
            #Para que no muestre ochocientos mil bytes y resuma
            tamano_bytes = stats.st_size
            if tamano_bytes > 1024 * 1024:
                info.append(f"Tamaño: {tamano_bytes / (1024*1024):.2f} MB")
            elif tamano_bytes > 1024:
                info.append(f"Tamaño: {tamano_bytes / 1024:.2f} KB")
            else:
                info.append(f"Tamaño: {tamano_bytes} bytes")
                
            if os.access(ruta_real, os.X_OK):
                info.append("Atributos: Es un archivo EJECUTABLE.")

            extensiones_codigo = {'.py', '.sh', '.js', '.json', '.html', '.css', '.c', '.cpp', '.h', '.txt', '.md', '.conf'}
            _, ext = os.path.splitext(ruta_real.lower())
            
            if ext in extensiones_codigo or (tipo_mime and 'text' in tipo_mime):
                with open(ruta_real, 'r', encoding='utf-8', errors='ignore') as f:
                    bloque = f.read(40960)
                    info.append(f"\n[EXTRACTO DEL CÓDIGO FUENTE DE {os.path.basename(ruta_real)}]:\n{bloque}")

        info.append(f"Permisos (Octal): {oct(stats.st_mode)[-4:]}")
        modificado = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        info.append(f"Última modificación: {modificado}")
    except Exception as e:
        info.append(f"[Error leyendo componentes de la ruta: {e}]")
        
    info.append("------------------------------------------------------------------")
    return "\n".join(info)

def escanear_pregunta_usuario(user_input):
    palabras = user_input.split()
    metadatos_totales = ""
    rutas_procesadas = set()
    
    for palabra in palabras:
        palabra_limpia = palabra.strip("'\",;()[]{}")
        if palabra_limpia not in rutas_procesadas and ("/" in palabra_limpia or palabra_limpia.startswith("~") or "." in palabra_limpia):
            reporte_sistema = inspeccionar_ruta_sistema(palabra_limpia)
            if reporte_sistema:
                rutas_procesadas.add(palabra_limpia)
                metadatos_totales += f"\n\n{reporte_sistema}"
                print(f"🔍 [Sistema]: Análisis optimizado completado en: {palabra_limpia}...")
                
    return user_input + metadatos_totales

def ejecutar_comando_sistema(comando):
    print(f"\n⚠️  [SISTEMA] ¿Ejecutar comando sugerido?: \033[1;33m{comando}\033[0m")
    if input("¿Confirmar? (s/n): ").strip().lower() == 's':
        print(" Ejecutando...\n" + "-"*40)
        try:
            subprocess.run(comando, shell=True)
            print("-"*40)
        except Exception as e:
            print(f"❌ Error: {e}\n" + "-"*40)

def extraer_comando(texto):
    match = BASH_REGEX.search(texto)
    return match.group(1).strip() if match else None

def preguntar_ia(prompt):
    try:
        prompt_enriquecido = escanear_pregunta_usuario(prompt)
        respuesta = client.chat.completions.create(
            model=MODELO,
            messages=[CONTEXTO_SISTEMA, {"role": "user", "content": prompt_enriquecido}]
        )
        texto_ia = respuesta.choices[0].message.content
        
        # Procesamos y paginamos el resultado
        lineas_ajustadas = formatear_y_ajustar_texto(texto_ia)
        imprimir_con_paginador(lineas_ajustadas)
        
        comando = extraer_comando(texto_ia)
        if comando:
            ejecutar_comando_sistema(comando)
    except Exception as e:
        print(f"❌ Error: {e}")

def modo_chat():
    print("=== IA de Terminal (Escribe 'salir') ===")
    historial = [CONTEXTO_SISTEMA]
    
    while True:
        try:
            user_input = input("\nTú ➜ ")
            if user_input.lower() in {'salir', 'exit', 'quit'}:
                break
            if not user_input.strip():
                continue
                
            prompt_enriquecido = escanear_pregunta_usuario(user_input)
            historial.append({"role": "user", "content": prompt_enriquecido})
            
            if len(historial) > MAX_HISTORIAL:
                historial = [CONTEXTO_SISTEMA] + historial[-MAX_HISTORIAL:]
            
            respuesta = client.chat.completions.create(model=MODELO, messages=historial)
            texto_ia = respuesta.choices[0].message.content
            
            # Procesamos e imprimimos usando el nuevo paginador integrado
            print() # Salto de línea estético
            lineas_ajustadas = formatear_y_ajustar_texto(texto_ia)
            imprimir_con_paginador(lineas_ajustadas, prefijo="IA ➜")
            
            historial.append({"role": "assistant", "content": texto_ia})
            
            comando = extraer_comando(texto_ia)
            if comando:
                ejecutar_comando_sistema(comando)
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        preguntar_ia(" ".join(sys.argv[1:]))
    else:
        modo_chat()
