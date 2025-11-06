import boto3
import uuid
import os
import json
from botocore.exceptions import BotoCoreError, ClientError

# Reusar recursos fuera del handler para rendimiento en Lambda
_dynamodb = boto3.resource('dynamodb')
_s3 = boto3.client('s3')


def _build_response(status_code: int, body: dict):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }


def lambda_handler(event, context):
    """Handler que guarda el comentario en DynamoDB y sube el JSON al bucket de ingesta.

    Entrada esperada (API Gateway proxy): event['body'] -> JSON string o dict con keys:
      - tenant_id
      - texto

    Strategy: Ingesta Push -> Mientras se guarda la referencia en DynamoDB, también se sube
    el mismo JSON al bucket S3 correspondiente al stage (env S3_BUCKET).
    """
    try:
        print('event:', event)

        raw_body = event.get('body', '')
        if isinstance(raw_body, str) and raw_body:
            try:
                body = json.loads(raw_body)
            except json.JSONDecodeError:
                return _build_response(400, {'error': 'body debe ser JSON válido'})
        elif isinstance(raw_body, dict):
            body = raw_body
        else:
            body = {}

        tenant_id = body.get('tenant_id')
        texto = body.get('texto')

        if not tenant_id or not texto:
            return _build_response(400, {'error': 'faltan campos requeridos: tenant_id y texto'})

        table_name = os.environ.get('TABLE_NAME')
        s3_bucket = os.environ.get('S3_BUCKET')
        if not table_name or not s3_bucket:
            return _build_response(500, {'error': 'TABLE_NAME o S3_BUCKET no configuradas en variables de entorno'})

        comentario_uuid = str(uuid.uuid4())
        comentario = {
            'tenant_id': tenant_id,
            'uuid': comentario_uuid,
            'detalle': {
                'texto': texto
            }
        }

        # Guardar en DynamoDB
        table = _dynamodb.Table(table_name)
        table.put_item(Item=comentario)

        # Subir el JSON al bucket de ingesta (key: <tenant_id>/<uuid>.json)
        key = f"{tenant_id}/{comentario_uuid}.json"
        _s3.put_object(
            Bucket=s3_bucket,
            Key=key,
            Body=json.dumps(comentario).encode('utf-8'),
            ContentType='application/json'
        )

        return _build_response(200, {'comentario': comentario, 's3_key': key})

    except (BotoCoreError, ClientError) as e:
        # Errores relacionados con AWS (DynamoDB/S3)
        return _build_response(502, {'error': 'error al comunicarse con AWS', 'detail': str(e)})
    except Exception as e:
        return _build_response(500, {'error': 'error interno', 'detail': str(e)})
