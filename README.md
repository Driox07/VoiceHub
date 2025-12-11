# Voice Models API - Aplicación Simple

API y frontend para gestionar modelos de voz RVC.

## Características

- ✅ CRUD completo de modelos de voz
- ✅ Subida de archivos .pth y .index
- ✅ Búsqueda por nombre
- ✅ Paginación (10 por página)
- ✅ **Probar modelos con TTS en la web** 🎤
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
- `POST /api/model/{id}/test-tts` - Probar modelo con TTS (simulado)

## Probar Modelos (TTS)

Cada modelo tiene un botón "🎤 Probar" que abre un modal donde puedes:
1. Escribir texto para sintetizar
2. Generar audio con el modelo (simulado)

**Nota:** La implementación actual es una simulación. Para audio real, integra con [RVC Inference](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI):

```python
# Ejemplo de integración real con RVC
from infer import infer_pipeline
pipeline = infer_pipeline(model.pth_file, model.index_file)
audio = pipeline.synthesize(text)
```

## Base de Datos

SQLite3 en `voice_models.db`

Los archivos se guardan en:
- `uploads/` - Archivos .pth y .index
- `audio_outputs/` - Audios generados por TTS

## Licencia
[VoiceHub](https://github.com/Driox07/VoiceHub) © 2025 by [Adrián Sánchez Galera & José Manuel de Torres Domínguez](https://github.com/Driox07 & https://github.com/PiporGames) is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
![cc](https://mirrors.creativecommons.org/presskit/icons/cc.svg)
![by](https://mirrors.creativecommons.org/presskit/icons/by.svg)
![nc](https://mirrors.creativecommons.org/presskit/icons/nc.svg)
![sa](https://mirrors.creativecommons.org/presskit/icons/sa.svg)


