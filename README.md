# Voice Models API - Aplicación Simple

API y frontend para gestionar modelos de voz RVC.

## Características

- ✅ CRUD completo de modelos de voz
- ✅ Subida de archivos .pth y .index
- ✅ Búsqueda por nombre
- ✅ Paginación (10 por página)
- ✅ Probar modelos con TTS en la web 
- ✅ Documentación API automática en /docs
- ✅ Base de datos SQLite3
- ✅ Frontend con directorio de modelos

## Instalación

```bash
# Crear un entorno virtual
python -m venv venv

# Activar el entorno virtual

# Linux/MacOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python run.py
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

Cada modelo tiene un botón "🎤 Probar" que permite al usuario probar el modelo con un sintetizador TTS:
1. Escribir texto para sintetizar
2. Selecciona el modelo TTS base que se usará para inferir
3. Seleccionar el tono de voz (pitch)
4. Se infiere el audio con RVC y se devuelve un archivo reproducible

## Base de Datos

SQLite3 en `voice_models.db`

Los archivos se guardan en:
- `uploads/` - Archivos .pth y .index
- `audio_outputs/` - Audios generados por TTS y RVC

## Licencia
[VoiceHub](https://github.com/Driox07/VoiceHub) © 2025 by [Adrián Sánchez Galera](https://github.com/Driox07) & [José Manuel de Torres Domínguez](https://github.com/PiporGames) is licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
![cc](https://mirrors.creativecommons.org/presskit/icons/cc.svg)
![by](https://mirrors.creativecommons.org/presskit/icons/by.svg)
![nc](https://mirrors.creativecommons.org/presskit/icons/nc.svg)
![sa](https://mirrors.creativecommons.org/presskit/icons/sa.svg)


