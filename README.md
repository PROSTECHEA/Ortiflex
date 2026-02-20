# Ortiflex OSCM - Ortiflex Supply Chain Manager

Sistema integral de gestión de inventarios, proyectos y auditoría para **Ortiflex C.A.** Desarrollado con Python Flask y SQLite.

## 🚀 Despliegue Online (con GitHub + Render)

Para visualizar esta página online de forma gratuita a través de tu cuenta de GitHub, sigue estos pasos:

### 1. Preparar el Repositorio en GitHub
1. Crea un nuevo repositorio en tu cuenta de GitHub (ej: `ortiflex-oscm`).
2. Sube todos los archivos de esta carpeta a ese repositorio. 
   * *Nota: El archivo `.gitignore` configurado evitará que subas bases de datos locales o archivos temporales.*

### 2. Despliegue en Render (Recomendado)
Render es una plataforma gratuita que se conecta a GitHub y despliega aplicaciones Flask automáticamente.
1. Crea una cuenta en [Render.com](https://render.com).
2. Haz clic en **"New +"** y selecciona **"Web Service"**.
3. Conecta tu cuenta de GitHub y selecciona el repositorio `ortiflex-oscm`.
4. Configura los siguientes detalles:
   - **Language:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
5. Haz clic en **"Create Web Service"**.

¡Listo! Render te dará una URL (ej: `ortiflex-oscm.onrender.com`) donde podrás ver tu aplicación online.

## 🛠️ Características Principales
- **Gestión de Inventario:** CRUD con sistema de "Soft Delete" (Papelera).
- **Control de Proyectos:** Auditoría detallada, notas y deducción automática de stock.
- **Seguridad Avanzada:** Roles de usuario, permisos granulares y confirmación de clave admin para acciones críticas.
- **Reportes:** Generación de PDF profesionales con vista previa dinámica.
- **Interfaz Responsiva:** Optimizado para PC, tablets y móviles.

## 💻 Instalación Local
Si deseas ejecutarlo en tu computadora:
1. Instala las dependencias: `pip install -r requirements.txt`
2. Ejecuta la aplicación: `python run.py`
3. Abre en tu navegador: `http://127.0.0.1:5000`

---
*Desarrollado para Ortiflex C.A. - 2026*
