# Voice Models API - Aplicación Simple

API y frontend para gestionar modelos de voz RVC.

## Características

- ✅ CRUD completo de modelos de voz
- ✅ Subida de archivos .pth y .index
- ✅ Búsqueda por nombre
- ✅ Paginación (10 por página)
- ✅ Documentación API automática en /docs
- ✅ Base de datos SQLite3
- ✅ Frontend con directorio de modelos

## Instalación

```bash
# Instalar dependencias
pip install -r requirements-simple.txt

# Ejecutar servidor
python -m uvicorn simple_app.main:app --reload
```

## Uso

- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **OpenAPI Spec**: ModelAPI.yml

## Campos del Modelo

- **Fecha de creación**: Insertada por el usuario
- **Nombre**: Nombre del modelo
- **Descripción**: Descripción opcional
- **Archivo .pth**: Modelo (~50MB)
- **Archivo .index**: Índice del modelo
- **Tecnología**: RVMPE (única opción)
- **Epochs**: Número de epochs entrenados
- **Idioma**: Español o Inglés

## Endpoints API

- `GET /api/model` - Listar modelos (paginado, búsqueda)
- `POST /api/model` - Crear modelo
- `GET /api/model/{id}` - Obtener modelo
- `PUT /api/model/{id}` - Actualizar modelo
- `DELETE /api/model/{id}` - Eliminar modelo
- `GET /api/model/{id}/download/{type}` - Descargar archivo (pth/index)

## Base de Datos

SQLite3 en `voice_models.db`

Los archivos se guardan en el directorio `uploads/` con timestamps únicos para evitar colisiones.
