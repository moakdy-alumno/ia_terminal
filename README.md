# 🚀 Asistente de IA Inteligente para Terminal (Lubuntu CLI)

Un asistente de inteligencia artificial ultraligero y optimizado para la terminal de **Lubuntu (LXQt/QTerminal)** escrito en Python. Utiliza la API oficial de **OpenAI** (`gpt-4o-mini`) para ofrecer respuestas veloces, analizar código fuente en tiempo real, inspeccionar componentes del sistema y sugerir comandos CLI con ejecución segura.

---

## ✨ Características Principales

- **🧠 Análisis Inteligente de Rutas y Código:** Si mencionas una ruta en tu pregunta (ej. `/ruta/al/archivo.py`), el script inspecciona automáticamente sus metadatos (tamaño, tipo MIME, permisos) y extrae las primeras 120 líneas de código fuente si es un archivo de texto/programación.
- **🖥️ Integración Segura con el Sistema:** La IA puede sugerir comandos de Linux para automatizar tareas. El script intercepta estos comandos y solicita tu confirmación expresa `(s/n)` antes de ejecutarlos en el sistema operativo.
- **📟 Paginador Nativo Integrado (`| more`):** Si la respuesta de la IA es más larga que el alto actual de tu ventana de terminal, el texto se detiene dinámicamente y te permite avanzar presionando `ENTER` o salir con `q`.
- **📏 Ajuste de Línea Dinámico (Word Wrap):** Adapta el flujo de texto automáticamente al ancho en caracteres de tu terminal en tiempo real para evitar incómodos saltos de línea horizontales.
- **💾 Memoria de Contexto Avanzada:** El modo interactivo mantiene un historial de conversación optimizado en memoria con un límite de tokens para evitar ralentizaciones.

---

## 🛠️ Requisitos e Instalación

### 1. Preparar el Entorno en Lubuntu
Debido a las políticas de entornos gestionados externamente (**PEP 668**), se debe instalar mediante un entorno virtual aislado:

```bash
# Asegurar dependencias del sistema
sudo apt update && sudo apt install python3-venv python3-full git -y

# Clonar o entrar a la carpeta del proyecto
cd ~/preguntar-ia

# Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar librerias
pip install -r requeriments.txt
```

### 2. Configuración de Credenciales
Debes obtener una API Key en la plataforma de [OpenAI](https://openai.com). Para que el sistema funcione de forma permanente, añade tu clave al archivo de configuración de tu terminal Bash:

```bash
featherpad ~/.bashrc
```

Añade estas líneas al final del archivo (reemplaza con tus datos reales):

```bash
export OPENAI_API_KEY="sk-proj-TU_CLAVE_SECRETA_AQUI"
alias ia="tu ruta de entorno virtual(por ejemplo:
/home/preguntar-ia/venv/bin/python
tu ruta de descarga (por ejemplo:
/home/preguntar-ia/ia_terminal.py"

Para que no quepan dudas en mi caso quedaria asi:

export OPENAI_API_KEY="sk-proj-TU_CLAVE_SECRETA_AQUI"
alias ia="/home/tu_usuario/preguntar-ia/venv/bin/python /home/tu_usuario/preguntar-ia/ia_terminal.py"

```

Guarda el archivo y recarga tu configuración:
```bash
source ~/.bashrc
```

---

## 🚀 Modos de Uso

A partir de la configuración, puedes invocar al asistente desde cualquier ruta de tu sistema usando el alias `ia`:

### A. Consulta Rápida (Una sola línea)
Envía una pregunta directa entre comillas. Si hay comandos asociados, te pedirá confirmación:
```bash
ia "Dime el comando para ver el espacio libre en disco"
```

### B. Modo Chat Continuo (Interactivo)
Ejecuta el comando sin argumentos para abrir una sesión interactiva que conserva la memoria de los mensajes anteriores:
```bash
ia
```
*Para salir del chat, escribe `salir`, `exit` o `quit`.*

---

## 🔍 Ejemplos de Interacción Inteligente

1. **Análisis de Scripts:**
   ```bash
   ia "Busca bugs o optimizaciones en este script: /home/moakgarsan/preguntar-ia/ia_terminal.py"
   ```
2. **Consulta de Directorios:**
   ```bash
   ia "Explícame qué elementos tengo en ~/Descargas"
   ```
3. **Gestión de Paginación:**
   Si pides una explicación extensa como *"Escribe un tutorial largo del Kernel de Linux"*, aparecerá el paginador interactivo:
   `-- Más -- (Presiona ENTER para continuar, 'q' para salir)`

---

## ⚙️ Estructura del Código

- `ia_terminal.py`: Script principal de ejecución.
- `CONTEXTO_SISTEMA`: Rol preconfigurado que moldea el comportamiento de la IA para administración y desarrollo.
- `inspeccionar_ruta_sistema()`: Módulo de telemetría que extrae las propiedades de hardware y bloques de código antes de enviarlos a la API.
- `imprimir_con_paginador()`: Control del renderizado en bloques según el alto de `os.get_terminal_size()`.

---

## 🔍 Añadida la extración y envio de documentos pdf.10/11/26 (a traves de "pypdf")
