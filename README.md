# Pipeline de Ingesta Multi-Fuente y Perfilamiento de Datos en AWS S3

Este repositorio contiene la solución técnica para la **Práctica 1: Perfilamiento e Ingesta Multi-Fuente en AWS S3 con Python**. El objetivo principal es establecer una conexión segura con Amazon S3 utilizando el SDK `boto3` para realizar la carga, aplanamiento e inspección estadística de datasets estructurados (`.csv`) y semiestructurados (`.json`) completamente en memoria RAM, optimizando el uso de almacenamiento local en entornos Linux (Ubuntu).

## 🚀 Arquitectura del Pipeline (In-Memory)

A diferencia de los enfoques tradicionales que descargan archivos temporales a disco (`I/O`), este desarrollo lee los objetos directamente desde los endpoints de AWS S3 como un flujo de bytes binarios (`StreamingBody`). Utilizando el módulo `io.BytesIO`, los datos se inyectan directamente en estructuras de datos de `pandas` (`DataFrames`), garantizando un procesamiento ágil, limpio y seguro.

---

## 📋 Requisitos del Sistema

*   **Sistema Operativo:** Linux Ubuntu 20.04 LTS o superior.
*   **IDE:** Visual Studio Code.
*   **Lenguaje:** Python 3.8 o superior.
*   **Plataforma Cloud:** AWS Academy (Learner Lab).

---

## 🛠️ Configuración del Entorno de Desarrollo

Sigue estos pasos secuenciales en la terminal de tu máquina virtual Ubuntu para desplegar y aislar el proyecto:

1. **Clonar el repositorio y acceder a la carpeta:**
   ```bash
   git clone <URL_DE_TU_REPOSITORIO>
   cd <NOMBRE_DE_LA_CARPETA>
   ```

2. **Crear e inicializar el entorno virtual de Python:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   *(Verificarás que el prompt ahora inicia con el prefijo `(.venv)`)*.

3. **Actualizar el gestor de paquetes e instalar dependencias:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 🔐 Gestión de Credenciales de AWS Academy

Debido a que las credenciales del laboratorio de AWS Academy expiran cada pocas horas, **nunca se deben almacenar claves duras en el código ni en el archivo de configuración global `~/.aws/credentials`**.

### Inyección de Credenciales mediante Variables del Código:
Para ejecutar el script, abre `Perfilamiento.py` y actualiza las siguientes variables al inicio del archivo con los datos vigentes extraídos de la consola web de AWS Academy (**AWS Details -> Show**):

```python
AWS_ACCESS_KEY_ID = 'Pega_aquí_tu_aws_access_key_id'
AWS_SECRET_ACCESS_KEY = 'Pega_aquí_tu_aws_secret_access_key'
AWS_SESSION_TOKEN = 'Pega_aquí_tu_aws_session_token_completo'
BUCKET_NAME = 'tu-nombre-de-bucket-asignado'
```

*Nota: El script cuenta con un parche de aislamiento de entorno (`os.environ`) que inhabilita de forma segura cualquier archivo corrupto local en el path `~/.aws/credentials` para evitar excepciones de parseo (`ConfigParseError`).*

---

## 📦 Ejecución del Pipeline

Para correr el pipeline de datos, ejecuta el script principal respetando las mayúsculas en la terminal con el entorno virtual activo:

```bash
python3 Perfilamiento.py
```

### Flujo Interno Ejecutado:
1. **`generar_y_subir_archivos_prueba()`:** Genera datos transaccionales ficticios y logs estructurados en JSON de sensores IoT, persistiendo los archivos binarios directamente en el prefijo `raw/` dentro de tu bucket S3.
2. **`cargar_y_perfilar_s3()`:** Descarga mediante `GET` HTTP los archivos de forma streaming hacia la RAM, procesa y aplana las estructuras anidadas (ej. la llave `payload` en el JSON) mediante `pd.json_normalize` y genera en consola el perfilamiento de tipos de datos (`.dtypes`) junto al resumen estadístico transpuosto (`.describe().T`).

---

## 🛡️ Prácticas de DevSecOps (Control de Versiones)

Este proyecto implementa políticas estrictas para evitar la filtración de credenciales en repositorios públicos:
*   Se incluye un archivo `.gitignore` configurado para omitir directorios de caché (`__pycache__/`), binarios del entorno virtual (`.venv/`) y cualquier archivo residual o llave privada de AWS (`.pem` o carpetas `.aws/`).

---

## 👥 Autores
*   **Nombre del Estudiante** - *Desarrollador Principal* - [TuUsuarioDeGitHub](https://github.com)
*   **Materia:** Procesamiento de Datos en la Nube / Ingeniería de Datos.
