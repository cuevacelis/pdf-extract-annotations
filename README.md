# PDF Extract Tool

Una herramienta de línea de comandos para extraer texto y anotaciones de archivos PDF utilizando PyMuPDF.

## 📋 Características

- ✅ **Extracción de texto**: Extrae todo el texto de archivos PDF
- ✅ **Extracción de anotaciones**: Extrae comentarios, resaltados y otras anotaciones
- ✅ **Interfaz de línea de comandos**: Menú interactivo fácil de usar
- ✅ **Organización automática**: Guarda los resultados en directorios organizados
- ✅ **Múltiples formatos**: Salida en texto plano y JSON

## 🛠️ Requisitos

### Sistema
- **Python**: 3.10 o superior
- **uv**: Gestor de paquetes y entornos virtuales de Python

### Instalación de uv

Si no tienes `uv` instalado, puedes instalarlo siguiendo las instrucciones oficiales:

```bash
# En macOS y Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# En Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternativamente, con pip
pip install uv
```

## 🚀 Instalación

1. **Clona el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd pdf-extract
   ```

2. **Instala las dependencias con uv**:
   ```bash
   uv sync
   ```

   Esto creará automáticamente un entorno virtual y instalará todas las dependencias necesarias.

## 📖 Uso

### Menú Interactivo

Ejecuta el programa con el menú interactivo:

```bash
uv run main.py
```

Esto mostrará un menú con las siguientes opciones:
- **1. Extract text from PDF**: Extrae todo el texto del PDF
- **2. Extract annotations from PDF**: Extrae anotaciones y comentarios
- **0. Exit**: Salir del programa

### Línea de Comandos

También puedes usar la herramienta directamente desde la línea de comandos:

```bash
# Extraer texto de un PDF específico
uv run main.py --text /ruta/al/archivo.pdf

# Extraer anotaciones de un PDF específico
uv run main.py --annotations /ruta/al/archivo.pdf

# Usar un PDF como argumento posicional
uv run main.py /ruta/al/archivo.pdf
```

### Opciones de Ayuda

```bash
uv run main.py --help
```

## 📁 Estructura del Proyecto

```
pdf-extract/
├── main.py                 # Archivo principal con menú y CLI
├── pyproject.toml          # Configuración del proyecto y dependencias
├── uv.lock                 # Lock file de dependencias
├── README.md               # Este archivo
├── .gitignore              # Archivos a ignorar por Git
├── data/
│   ├── input/              # Coloca aquí tus archivos PDF
│   └── output/             # Archivos de salida generados
│       ├── text/           # Texto extraído (.txt)
│       └── annotations/    # Anotaciones extraídas (.json)
└── src/
    ├── extractors/
    │   ├── text_extractor.py       # Extractor de texto
    │   └── annotation_extractor.py # Extractor de anotaciones
    └── utils/
        └── file_utils.py    # Utilidades para manejo de archivos
```

## 📦 Dependencias

El proyecto utiliza las siguientes dependencias principales:

- **PyMuPDF (fitz)** `1.23.14`: Biblioteca para manipulación de archivos PDF
- **Python** `≥3.10`: Versión mínima requerida de Python

Para ver todas las dependencias exactas, consulta:
```bash
uv tree
```

## 🔧 Desarrollo

### Instalar en modo desarrollo

```bash
# Instalar dependencias de desarrollo
uv sync --dev

# Ejecutar en modo desarrollo
uv run python main.py
```

### Estructura de Código

- **`main.py`**: Punto de entrada principal con interfaz CLI y menú interactivo
- **`src/extractors/`**: Módulos para extracción de texto y anotaciones
- **`src/utils/`**: Utilidades comunes para manejo de archivos

### Linting y Formato

```bash
# Verificar código (si tienes herramientas de linting configuradas)
uv run ruff check .
uv run black --check .
```

## 📋 Ejemplos de Uso

### Ejemplo 1: Extracción de Texto

```bash
# Ejecutar el menú interactivo
uv run main.py

# Seleccionar opción 1
# El programa buscará PDFs en data/input/ automáticamente
# El texto se guardará en data/output/text/
```

### Ejemplo 2: Extracción de Anotaciones

```bash
# Directamente desde línea de comandos
uv run main.py --annotations "data/input/documento.pdf"

# Las anotaciones se guardarán en data/output/annotations/documento_annotations.json
```

### Ejemplo 3: Procesamiento con PDF Específico

```bash
# Usar un PDF específico como argumento
uv run main.py "/ruta/completa/al/documento.pdf"

# Esto abrirá el menú interactivo con el PDF ya seleccionado
```

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'fitz'"

Si encuentras este error, asegúrate de ejecutar con `uv run`:

```bash
# ❌ No hagas esto
python main.py

# ✅ Haz esto
uv run main.py
```

### El programa no encuentra PDFs

1. Asegúrate de que tus archivos PDF estén en `data/input/`
2. O proporciona la ruta completa al archivo PDF
3. Verifica que el archivo tenga extensión `.pdf`

### Problemas con permisos

En Linux/macOS, asegúrate de que el directorio tenga permisos de escritura:

```bash
chmod +w data/output/
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu función (`git checkout -b feature/nueva-funcion`)
3. Commit tus cambios (`git commit -am 'Agregar nueva función'`)
4. Push a la rama (`git push origin feature/nueva-funcion`)
5. Abre un Pull Request

## 📄 Licencia

[Especificar licencia aquí]

## 🆕 Changelog

### v0.1.0
- ✅ Extracción básica de texto de PDFs
- ✅ Extracción de anotaciones y comentarios
- ✅ Interfaz de línea de comandos
- ✅ Menú interactivo
- ✅ Organización automática de archivos de salida
