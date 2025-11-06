import json
import os
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.getenv('TABLE_ALUMNOS', 't_alumnos')
table = dynamodb.Table(TABLE_NAME)

def _get_body(event):
    body = event.get('body') if isinstance(event, dict) else None
    if isinstance(body, str) and body:
        try:
            return json.loads(body)
        except Exception:
            pass
    return body if isinstance(body, dict) else (event if isinstance(event, dict) else {})

def lambda_handler(event, context):
    try:
        data = _get_body(event) or {}
        tenant_id = data.get('tenant_id')
        alumno_id = data.get('alumno_id')
        alumno_datos = data.get('alumno_datos')

        if not tenant_id or not alumno_id:
            return {'statusCode': 400, 'body': json.dumps({'error': "Faltan 'tenant_id' y/o 'alumno_id'."})}
        if alumno_datos is None:
            return {'statusCode': 400, 'body': json.dumps({'error': "Envíe 'alumno_datos' para actualizar."})}

        resp = table.update_item(
            Key={'tenant_id': tenant_id, 'alumno_id': alumno_id},
            UpdateExpression="SET #ad = :ad",
            ExpressionAttributeNames={'#ad': 'alumno_datos'},
            ExpressionAttributeValues={':ad': alumno_datos},
            ConditionExpression=Attr('tenant_id').exists() & Attr('alumno_id').exists(),
            ReturnValues='ALL_NEW'
        )

        return {'statusCode': 200, 'body': json.dumps({'message': 'Alumno modificado', 'item': resp.get('Attributes')})}

    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return {'statusCode': 404, 'body': json.dumps({'error': 'No existe el alumno.'})}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
