
# API Alumnos (Serverless + AWS Lambda + DynamoDB)

Este repo contiene los handlers para **ModificarAlumno**, **EliminarAlumno** y **BuscarAlumno**, más una colección de Postman para probar el API.

## Requisitos
- AWS CLI configurado (`aws configure`)
- Node.js 18+ y Serverless Framework (`npm i -g serverless`)
- Tabla DynamoDB (por defecto `t_alumnos`) con PK `tenant_id` (string) y SK `alumno_id` (string)

## Estructura
```
.
├─ handlers/
│  ├─ ModificarAlumno.py
│  ├─ EliminarAlumno.py
│  └─ BuscarAlumno.py
├─ postman/
│  └─ Alumnos.postman_collection.json
├─ .gitignore
├─ README.md
└─ serverless.sample.yml
```

> Copia tu `serverless.yml` real en la raíz. El `serverless.sample.yml` es una guía mínima.

## serverless.yml (ejemplo mínimo)
Pega esto como referencia y ajusta rutas/handlers si usas carpetas diferentes:

```yaml
service: api-alumnos

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  stage: dev
  environment:
    TABLE_ALUMNOS: t_alumnos

functions:
  ModificarAlumno:
    handler: handlers/ModificarAlumno.lambda_handler
    events:
      - httpApi:
          path: /alumnos/modificar
          method: POST

  EliminarAlumno:
    handler: handlers/EliminarAlumno.lambda_handler
    events:
      - httpApi:
          path: /alumnos/eliminar
          method: POST

  BuscarAlumno:
    handler: handlers/BuscarAlumno.lambda_handler
    events:
      - httpApi:
          path: /alumnos/buscar
          method: POST
```

## Deploy
```bash
serverless deploy
```
Copia los endpoints que retorna el deploy y colócalos en Postman (o cambia la variable `baseUrl` de la colección).

## Postman
1. Importa `postman/Alumnos.postman_collection.json`.
2. Edita la variable `baseUrl` con tu URL (por ej. `https://xxxx.execute-api.us-east-1.amazonaws.com/dev`).
3. Ejecuta las requests: Crear, Listar, Buscar, Modificar, Eliminar.
4. Toma captura de pantalla con la respuesta y súbela al aula.

## Git rápido
```bash
git init
git add .
git commit -m "API alumnos: buscar/modificar/eliminar + postman"
# crea un repo en GitHub y pega su URL:
git branch -M main
git remote add origin https://github.com/USUARIO/api-alumnos.git
git push -u origin main
```
