@echo off
REM Crear un nuevo entorno virtual
python -m venv .venv

REM Activar el entorno virtual
call .venv\Scripts\activate

REM Instalar dependencias desde requirements.txt
pip install -r requirements.txt

REM Iniciar la aplicación
python run.py