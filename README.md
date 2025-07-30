# 🚀 Sistema de Encuestas en Tiempo Real 📊

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/DRF-3.14+-A30000?style=for-the-badge&logo=django&logoColor=white)
![Channels](https://img.shields.io/badge/Channels-4.0+-092E20?style=for-the-badge&logo=django&logoColor=white)

Un sistema de encuestas dinámico e interactivo, diseñado para ofrecer retroalimentación instantánea a través de gráficas que se actualizan en vivo para todos los participantes.

<p align="center">
  <img src="./assets/sidelogo.jpg" alt="Banner de la aplicación" width="800"/>
</p>

---

## 📖 Tabla de Contenidos

- [🎯 **Acerca del Proyecto**](#-acerca-del-proyecto)
- [✨ **Características Principales**](#-características-principales)
- [🛠️ **Stack Tecnológico**](#️-stack-tecnológico)
- [🏁 **Guía de Instalación y Puesta en Marcha**](#-guía-de-instalación-y-puesta-en-marcha)
- [🕹️ **Modo de Uso**](#️-modo-de-uso)
- [🌐 **Endpoints de la API**](#-endpoints-de-la-api)

---

## 🎯 Acerca del Proyecto

Este proyecto es una solución completa para crear y gestionar encuestas de opinión o sondeos. La principal característica es su capacidad de mostrar los resultados en **tiempo real**, permitiendo a todos los usuarios ver cómo las gráficas cambian al instante con cada nuevo voto.

La aplicación cuenta con un panel de administración robusto para la gestión de encuestas y usuarios, y una interfaz pública optimizada para que la experiencia de contestar sea rápida, intuitiva y visualmente atractiva.

---

## ✨ Características Principales

### **Panel de Administración**
- **Gestión Completa de Cuestionarios (CRUD):** Crea, edita y elimina cuestionarios con una interfaz dinámica para añadir preguntas y opciones.
- **Control de Estado:** Activa o desactiva encuestas con un solo clic para controlar el acceso.
- **Generación de Códigos QR:** Genera y muestra un código QR único para cada encuesta, facilitando el acceso desde dispositivos móviles.
- **Estadísticas en Vivo:** Visualiza los resultados de cada pregunta en gráficas que se actualizan en tiempo real.
- **Borrado Lógico (Soft Delete):** Los cuestionarios eliminados se desactivan en lugar de borrarse permanentemente de la base de datos.

### **Gestión de Usuarios (Exclusivo para Super Admins)**
- **CRUD de Usuarios:** Un panel dedicado permite a los Super Administradores crear, editar y eliminar otros usuarios (Admins y Super Admins).
- **Control de Roles:** Asigna roles de `Admin` o `SUPER_ADMIN` para controlar los permisos.
- **Seguridad:** El acceso a esta sección está protegido y es invisible para los usuarios con rol de `Admin`.

### **Encuesta Pública**
- **Interfaz Interactiva:** Un diseño de dos columnas muestra las preguntas a la izquierda y las gráficas de resultados a la derecha.
- **Actualizaciones en Tiempo Real:** Las gráficas se actualizan para todos los participantes conectados mediante **WebSockets** cada vez que se emite un voto.
- **Flexibilidad:** Los usuarios pueden cambiar su respuesta en cualquier momento.
- **Validación de Participación Única:** Gracias a un sistema de identificador persistente en `localStorage`, se impide que un mismo dispositivo conteste una encuesta más de una vez, tanto por código como por QR.

---

## 🛠️ Stack Tecnológico

| Tecnología | Descripción |
| :--- | :--- |
| **Python** | Lenguaje principal del backend. |
| **Django** | Framework web para la estructura del proyecto. |
| **Django REST Framework** | Para la creación de la API RESTful. |
| **Django Channels** | Para la comunicación en tiempo real con WebSockets. |
| **Uvicorn** | Servidor ASGI de alto rendimiento. |
| **JavaScript (ES6+)** | Lógica del frontend para dinamismo, peticiones a la API y WebSockets. |
| **HTML5 / CSS3** | Estructura y estilos de la aplicación. |
| **Bootstrap 5** | Framework CSS para un diseño responsive y moderno. |
| **Chart.js** | Librería para la creación de las gráficas interactivas. |
| **QRCode.js** | Librería para la generación de códigos QR en el navegador. |

---

## 🏁 Guía de Instalación y Puesta en Marcha

Sigue estos pasos para levantar el proyecto en un entorno de desarrollo local.

### **Pre-requisitos**
- Python 3.8+
- Git (opcional)

### **Instalación**

1.  **Clona el repositorio:**
    ```bash
    git clone https://URL_DE_TU_REPO.git
    cd NOMBRE_DEL_PROYECTO
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    # Crear el entorno
    python -m venv venv

    # Activar en Windows (PowerShell)
    .\venv\Scripts\Activate

    # Activar en macOS/Linux
    source venv/bin/activate
    ```

3.  **Instala las dependencias:**
    *Con el entorno virtual activo, ejecuta los siguientes comandos.*

    ```bash
    # (Opcional pero recomendado) Actualizar pip a la última versión
    python -m pip install --upgrade pip

    # Instalar las librerías principales de Django y la API
    # Nota: djangorestframework-simplejwt es instalado automáticamente como dependencia de djoser
    python -m pip install django djangorestframework Pillow djoser channels mysqlclient

    # Instalar el servidor ASGI con sus dependencias estándar (incluye websockets)
    python -m pip install "uvicorn[standard]"
    ```

4.  **Configura tu base de datos:**
    Abre el archivo `App/settings.py` y asegúrate de que la sección `DATABASES` esté configurada como prefieras (el proyecto está listo para SQLite o MySQL).

5.  **Aplica las migraciones:**
    ```bash
    python manage.py migrate
    ```

6.  **Crea tu primer Super Administrador:**
    ```bash
    python manage.py createsuperuser
    ```
    Después de crearlo, asígnale el rol correcto en el shell de Django:
    ```bash
    python manage.py shell
    ```
    ```python
    from users.models import User
    user = User.objects.get(email='tu-email@ejemplo.com')
    user.role = 'SUPER_ADMIN'
    user.save()
    quit()
    ```

7.  **Inicia el servidor ASGI:**
    ```bash
    uvicorn App.asgi:application --reload
    ```

¡Listo! La aplicación estará corriendo en `http://127.0.0.1:8000`.

---

## 🕹️ Modo de Uso

1.  **Accede a la aplicación** en `http://127.0.0.1:8000`, que te redirigirá a la página de login.
2.  **Inicia sesión** con las credenciales de tu Super Admin.
3.  **Navega** usando la barra superior:
    - **Cuestionarios:** Ve y gestiona todos tus cuestionarios. Aquí puedes activar, desactivar, editar, eliminar y obtener el código QR.
    - **Crear Cuestionario:** Accede al formulario para crear una nueva encuesta.
    - **Usuarios:** Si eres Super Admin, podrás gestionar a los demás usuarios del sistema.
4.  **Para probar una encuesta**, copia el código de acceso o usa el QR y accede desde otro navegador o una ventana de incógnito.

---

## 🌐 Endpoints de la API

<details>
  <summary><strong>Haz clic para ver un resumen de los principales endpoints de la API</strong></summary>

  - **Autenticación (Djoser)**
    - `POST /auth/token/login/`: Iniciar sesión y obtener token.
    - `POST /auth/users/me/`: Obtener detalles del usuario actual.

  - **Gestión de Usuarios (Super Admin)**
    - `GET, POST /api/users/`: Listar o crear usuarios.
    - `GET, PUT, PATCH, DELETE /api/users/{id}/`: Gestionar un usuario específico.

  - **Gestión de Cuestionarios (Admin)**
    - `GET, POST /api/questionnaires/`: Listar o crear cuestionarios.
    - `GET, PUT, PATCH, DELETE /api/questionnaires/{id}/`: Gestionar un cuestionario específico.
    - `POST /api/questionnaires/{id}/toggle-active/`: Activar o desactivar un cuestionario.
    - `GET /api/questionnaires/{id}/stats/`: Obtener estadísticas de un cuestionario.

  - **API Pública (Usuarios Anónimos)**
    - `POST /api/questionnaires/public/check-submission/`: Verificar si un dispositivo ya contestó una encuesta.
    - `GET /api/questionnaires/public/forms/{access_code}/`: Obtener los datos de una encuesta para contestarla.

</details>