import json
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr

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
        nombre = data.get('nombre')
        celular = data.get('celular')

        if not tenant_id:
            return {'statusCode': 400, 'body': json.dumps({'error': "Falta 'tenant_id'."})}

        if alumno_id:
            resp = table.get_item(Key={'tenant_id': tenant_id, 'alumno_id': alumno_id})
            item = resp.get('Item')
            if not item:
                return {'statusCode': 404, 'body': json.dumps({'error': 'No existe el alumno.'})}
            return {'statusCode': 200, 'body': json.dumps({'results': [item]})}

        expr_names = {'#ad': 'alumno_datos', '#nombre': 'nombre', '#cel': 'celular'}
        filter_expr = None
        if nombre:
            filter_expr = Attr('#ad.#nombre').contains(nombre)
        if celular:
            filter_expr = (filter_expr & Attr('#ad.#cel').eq(celular)) if filter_expr else Attr('#ad.#cel').eq(celular)

        if filter_expr is not None:
            resp = table.query(
                KeyConditionExpression=Key('tenant_id').eq(tenant_id),
                FilterExpression=filter_expr,
                ExpressionAttributeNames=expr_names
            )
            items = resp.get('Items', [])
            if not items:
                return {'statusCode': 404, 'body': json.dumps({'error': 'Sin coincidencias.'})}
            return {'statusCode': 200, 'body': json.dumps({'results': items})}

        resp = table.query(KeyConditionExpression=Key('tenant_id').eq(tenant_id))
        return {'statusCode': 200, 'body': json.dumps({'results': resp.get('Items', [])})}

    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
