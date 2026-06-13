# PUSAK Login Monitor

PUSAK Login Monitor es un script en Python que utiliza Selenium y Firefox para supervisar automáticamente la disponibilidad del sistema PUSAK del Ministerio de Educación del Ecuador. Su objetivo es detectar cambios de estado del servicio, completar el inicio de sesión cuando corresponde y mantener el navegador abierto para que el usuario pueda continuar trabajando una vez que la aplicación esté disponible.

## Características

- Detecta automáticamente cuándo el sistema sale de mantenimiento.
- Reconoce la página de autenticación del sistema.
- Introduce automáticamente las credenciales desde variables de entorno.
- Identifica posibles problemas del backend o de disponibilidad del servidor.
- Espera de forma automática hasta que la aplicación responda correctamente.
- Emite alertas sonoras para eventos importantes.
- Mantiene Firefox abierto para que el usuario pueda utilizar PUSAK.

## Tecnologías

- Python
- Selenium
- Firefox
- Geckodriver
- python-dotenv

## Instalación

Clona el repositorio y entra a la carpeta del proyecto:

```bash
git clone https://github.com/tu-usuario/pusaklogin.git
cd pusaklogin
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Configuración

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
PUSAK_USER=tu_usuario
PUSAK_PASS=tu_contraseña
GECKODRIVER_PATH=C:\ruta\a\geckodriver.exe
```

> Nunca compartas ni subas credenciales reales. Mantén este archivo fuera del control de versiones si lo consideras necesario.

## Uso

Ejecuta el monitor con:

```bash
python main.py
```

El script abrirá Firefox, navegará a la URL principal de PUSAK, intentará iniciar sesión automáticamente y esperará hasta que la aplicación esté disponible. Mientras tanto, mostrará mensajes de estado y emitirá alertas sonoras cuando sea necesario.

## Estados detectados

El script puede identificar los siguientes estados:

- `Maintenance`: el sitio muestra mensajes de mantenimiento o de mejoras temporales.
- `Server Down`: el servidor responde con errores o indisponibilidad.
- `Login Page`: se detecta la pantalla de autenticación.
- `Possible App`: se identifica una página que parece ser la aplicación ya disponible.
- `Unknown`: el estado no se puede clasificar con claridad.
- `Not Found`: se detecta una respuesta de página no encontrada.

## Alertas sonoras

Se reproducen sonidos para eventos importantes, como:

- entrada en mantenimiento,
- detección del login,
- recuperación de una condición anterior,
- y otras situaciones relevantes del flujo.

## Requisitos

- Python 3.13+
- Firefox instalado y disponible en el sistema
- Geckodriver configurado correctamente

## Limitaciones

El funcionamiento del monitor depende del comportamiento real del sistema PUSAK y de la disponibilidad de sus servidores. En algunos casos, los cambios de interfaz o las condiciones del backend pueden afectar la detección automática.

## Roadmap

Próximas mejoras previstas:

- Reinicio inteligente del navegador.
- Mejor detección de la aplicación.
- Estadísticas más detalladas del monitoreo.
- Mejor recuperación de sesiones ante estados anómalos.

## Licencia

Este proyecto está licenciado bajo la licencia MIT.
