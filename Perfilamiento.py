import io
import json
import boto3
import pandas as pd

# AQUÍ SE REALIZA LA CONFIGURACIÓN Y PARÁMETROS DE CONEXIÓN A AWS S3
# Se define de la región geodistribuida de AWS asignada por AWS Academy que por lo general es la misma de siempre.
AWS_REGION = 'us-east-1'

# MARCADORES DE SEGURIDAD (DEVSECOPS):
# Reemplazamos las llaves activas por variables genéricas antes de subir a GitHub.
# Si no los encuentras, lo buscas en AWS details y ahí te lo dan jóven.

AWS_ACCESS_KEY_ID = ' '
AWS_SECRET_ACCESS_KEY = ' '
AWS_SESSION_TOKEN = ' '

# Aquí ingresas el nombre de tu Buckets.
BUCKET_NAME = ' '

# AQUÍ SE REALIZA LA INICIALIZACIÓN DEL CLIENTE BOTO3 (SDK DE AWS)
# Se instancia el cliente de bajo nivel 's3' pasando los argumentos explícitos.
# Esto establece un canal de comunicación seguro vía HTTPS/TLS con la API de AWS.
s3_client = boto3.client(
    's3',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN
)


def generar_y_subir_archivos_prueba():
    """
    Crea dinámicamente un dataset estructurado (.csv) y uno semiestructurado (.json)
    y los persiste en el bucket S3 bajo el prefijo 'raw/'.
    
    Usa s3_client.put_object() para enviar los flujos de bytes codificados en UTF-8.
    """
    print("=" * 70)
    print("=== PASO 1: CREANDO Y SUBIENDO ARCHIVOS DE PRUEBA A S3 ===")
    print("=" * 70)
    
    # Dataset Estructurado: transacciones.csv
    # Definición de filas en formato CSV en texto plano
    csv_content = (
        "id_transaccion,monto,fecha_transaccion,tipo_pago\n"
        "1001,150.50,2026-10-18,Tarjeta\n"
        "1002,89.00,2026-10-18,Efectivo\n"
        "1003,1200.00,2026-10-17,Transferencia\n"
        "1004,45.25,2026-10-16,Tarjeta\n"
        "1005,310.00,2026-10-15,Efectivo\n"
    )
    
    # Ingesta hacia S3: Se codifica la cadena a bytes en formato UTF-8
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key='raw/transacciones.csv',
        Body=csv_content.encode('utf-8')
    )
    print(" [ÉXITO] Archivo 'raw/transacciones.csv' subido correctamente al bucket.")

    # 2. Dataset Semiestructurado: logs_m2m.json (Estructura anidada IoT)
    # Objeto de lista de diccionarios con atributos anidados ('payload')

    json_data = [
        {
            "device_id": "sensor_01",
            "timestamp": "2026-10-18T10:00:00Z",
            "status": "OK",
            "payload": {"temperature": 23.5, "humidity": 60.2}
        },
        {
            "device_id": "sensor_02",
            "timestamp": "2026-10-18T10:01:00Z",
            "status": "WARNING",
            "payload": {"temperature": 38.1, "humidity": 75.0}
        },
        {
            "device_id": "sensor_03",
            "timestamp": "2026-10-18T10:02:00Z",
            "status": "CRITICAL",
            "payload": {"temperature": 52.4, "humidity": 88.9}
        }
    ]
    
    # Conversión del objeto de Python a cadena en formato JSON formateado
    json_content = json.dumps(json_data, indent=2)
    
    # Ingesta hacia S3
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key='raw/logs_m2m.json',
        Body=json_content.encode('utf-8')
    )
    print(" [ÉXITO] Archivo 'raw/logs_m2m.json' subido correctamente al bucket.\n")


def cargar_y_perfilar_s3(file_key, is_json=False):
    """
    Descarga en tiempo real un objeto desde AWS S3 hacia la memoria RAM (sin tocar disco local)
    y realiza un análisis de perfilamiento estructural y estadístico.

    Parámetros:
        file_key (str): Ruta/Llave del objeto dentro del bucket S3 (ej. 'raw/transacciones.csv').
        is_json (bool): Bandera para alternar entre procesamiento tabular o desanidamiento JSON.

    Retorna:
        pd.DataFrame: DataFrame de Pandas cargado y procesado en memoria.
    """
    print("=" * 70)
    print(f"=== PASO 2: PROCESANDO Y PERFILANDO OBJETO S3: {file_key} ===")
    print("=" * 70)
    
    try:
        # Petición HTTP GET al API de S3 para obtener el objeto binario
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
        
        # Lectura del StreamingBody retornado por Boto3 en memoria volátil (bytes)
        body = response['Body'].read()
        
        # PROCESAMIENTO IN-MEMORY SEGÚN EL TIPO DE ESTRUCTURA

        if is_json:
            # Decodificación de bytes a string y parseo a diccionario JSON
            data_json = json.loads(body.decode('utf-8'))
            
            # Aplanamiento de estructuras anidadas (payload.temperature, payload.humidity)
            df = pd.json_normalize(data_json)
        else:
            # io.BytesIO envuelve el flujo de bytes para que pandas lo lea como archivo
            df = pd.read_csv(io.BytesIO(body))
            
        # HASTA AQUÍ SE REALIZAN LAS IMPRESIÓNES DE RESULTADOS DEL PERFILAMIENTO DE DATOS

        print(f"\n1. DIMENSIONES DEL DATASET:")
        print(f"   -> Filas: {df.shape[0]} | Columnas: {df.shape[1]}")
        
        print("\n2. PERFIL DE TIPOS DE DATOS E IDENTIFICACIÓN:")
        print(df.dtypes)
        
        print("\n3. RESUMEN DE ESTADÍSTICOS DESCRIPTIVOS (CUANTITATIVOS):")
        # .describe().T calcula media, std, mín, máx y percentiles (transpuesto)
        print(df.describe().T)
        print("\n")
        
        return df

    except Exception as e:
        # Manejo de excepciones (e.g. NoSuchKey 404, AccessDenied 403 o fallos de red)
        print(f"\n[ERROR] Ocurrió un error al procesar 's3://{BUCKET_NAME}/{file_key}':")
        print(f"Detalle: {e}\n")
        return None


# YA POR ULTIMO AQUÍ ESTA EL PUNTO DE ENTRADA PRINCIPAL.

if __name__ == "__main__":
    # Ejecutar función para poblar el bucket con los archivos de prueba.
    generar_y_subir_archivos_prueba()
    
    # Ejecutar ingesta streaming e inspección en memoria RAM.
    df_transacciones = cargar_y_perfilar_s3('raw/transacciones.csv')
    df_logs = cargar_y_perfilar_s3('raw/logs_m2m.json', is_json=True)