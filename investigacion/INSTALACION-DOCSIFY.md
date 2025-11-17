# Guía de Instalación de Docsify para Investigación

## Descripción

Esta guía explica cómo instalar y ejecutar Docsify para visualizar la documentación de investigación en el directorio `investigacion/` desde cualquier environment de Gitpod/Ona.

Docsify es un generador de sitios de documentación que funciona completamente en el navegador, sin necesidad de compilación. Solo requiere servir archivos estáticos con un servidor HTTP.

## Requisitos Previos

- Python 3 (ya incluido en la imagen universal de devcontainers)
- Acceso a la línea de comandos
- Navegador web

## Estructura de Archivos Necesaria

El directorio `investigacion/` debe contener:

```
investigacion/
├── index.html          # Configuración de Docsify (REQUERIDO)
├── README.md           # Página principal (REQUERIDO)
├── _sidebar.md         # Menú lateral (OPCIONAL)
└── *.md                # Documentos markdown
```

### Archivo index.html

Este es el archivo principal que configura Docsify. Debe incluir:

1. **Tema CSS**: Carga el tema visual (dark/light)
2. **Configuración JavaScript**: Define opciones de Docsify
3. **Plugins**: Añade funcionalidades extra

**Características configuradas en nuestro setup:**
- ✅ Tema oscuro por defecto
- ✅ Búsqueda de texto completo
- ✅ Resaltado de sintaxis (TypeScript, JavaScript, Python, Bash, JSON)
- ✅ Soporte para diagramas Mermaid
- ✅ Copiar código al portapapeles
- ✅ Zoom de imágenes
- ✅ Toggle de modo oscuro/claro

**Dependencias CDN utilizadas:**
- `docsify@4` - Core de Docsify
- `prismjs@1` - Resaltado de sintaxis
- `mermaid@10` - Diagramas
- `docsify-mermaid@2` - Integración Mermaid
- `docsify-copy-code` - Copiar código
- `docsify-darklight-theme` - Toggle dark/light

### Archivo _sidebar.md

Define el menú de navegación lateral. Ejemplo:

```markdown
- [Inicio](/)
- [Documento 1](documento1.md)
- [Documento 2](documento2.md)
```

## Instalación y Ejecución

### Opción 1: Servidor HTTP de Python (Recomendado)

Python 3 incluye un servidor HTTP simple que es perfecto para servir archivos estáticos.

#### Paso 1: Navegar al directorio

```bash
cd investigacion
```

#### Paso 2: Iniciar el servidor

```bash
python3 -m http.server 5000
```

**Explicación:**
- `python3 -m http.server` - Inicia el módulo HTTP server de Python
- `5000` - Puerto en el que escuchar (puedes usar otro puerto si lo prefieres)

#### Paso 3: Abrir el puerto públicamente (en Gitpod/Ona)

```bash
gitpod environment port open 5000 --name "Docsify Docs"
```

**Explicación:**
- `gitpod environment port open` - Expone el puerto públicamente
- `5000` - Puerto a exponer
- `--name "Docsify Docs"` - Etiqueta descriptiva

#### Paso 4: Obtener la URL

```bash
gitpod environment port list
```

Busca la línea con el puerto 5000 y copia la URL.

### Opción 2: Servidor en Background

Para que el servidor siga corriendo incluso si cierras la terminal:

```bash
cd investigacion && setsid python3 -m http.server 5000 > /tmp/docsify.log 2>&1 < /dev/null &
```

**Explicación:**
- `cd investigacion &&` - Cambia al directorio y ejecuta el siguiente comando
- `setsid` - Crea una nueva sesión, desvinculando el proceso de la terminal
- `> /tmp/docsify.log` - Redirige stdout a un archivo de log
- `2>&1` - Redirige stderr al mismo lugar que stdout
- `< /dev/null` - Desvincula stdin
- `&` - Ejecuta en background

**Ver logs:**
```bash
tail -f /tmp/docsify.log
```

**Detener el servidor:**
```bash
pkill -f "python3 -m http.server 5000"
```

### Opción 3: Servidor con Node.js (Alternativa)

Si prefieres usar Node.js:

#### Instalar http-server globalmente:
```bash
npm install -g http-server
```

#### Ejecutar:
```bash
cd investigacion
http-server -p 5000
```

## Verificación

### 1. Verificar que el servidor está corriendo

```bash
ps aux | grep "http.server"
```

Deberías ver un proceso de Python ejecutando el servidor.

### 2. Verificar que el puerto está en LISTEN

```bash
lsof -i :5000
```

Deberías ver algo como:
```
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python3  1234 user    3u  IPv4  12345      0t0  TCP *:5000 (LISTEN)
```

### 3. Verificar que el puerto está expuesto públicamente

```bash
gitpod environment port list | grep 5000
```

Deberías ver una línea con el puerto 5000 y su URL pública.

### 4. Probar en el navegador

Abre la URL pública en tu navegador. Deberías ver:
- La página principal de documentación
- El menú lateral (si existe _sidebar.md)
- Búsqueda funcional
- Diagramas Mermaid renderizados
- Resaltado de sintaxis en bloques de código

## Troubleshooting

### Problema: "Address already in use"

**Causa:** El puerto 5000 ya está siendo usado por otro proceso.

**Solución 1:** Usar otro puerto
```bash
python3 -m http.server 5001
```

**Solución 2:** Matar el proceso existente
```bash
lsof -ti :5000 | xargs kill -9
```

### Problema: "No such file or directory"

**Causa:** No estás en el directorio correcto.

**Solución:**
```bash
cd /workspaces/kodless/investigacion
python3 -m http.server 5000
```

### Problema: El puerto no aparece en "port list"

**Causa:** El puerto no se ha abierto públicamente.

**Solución:**
```bash
gitpod environment port open 5000 --name "Docsify Docs"
```

### Problema: Página en blanco o error 404

**Causa:** Falta el archivo `index.html` o `README.md`.

**Solución:** Verifica que ambos archivos existen:
```bash
ls -la investigacion/index.html investigacion/README.md
```

### Problema: Diagramas Mermaid no se renderizan

**Causa:** Problema con la carga de scripts desde CDN.

**Solución:** Verifica la consola del navegador (F12) para errores de red. Puede ser un problema temporal de CDN.

### Problema: El servidor se detiene al cerrar la terminal

**Causa:** El proceso está vinculado a la terminal.

**Solución:** Usa la Opción 2 (servidor en background) con `setsid`.

## Automatización en devcontainer.json

Para que Docsify se inicie automáticamente al crear el environment:

```json
{
  "postStartCommand": "bash -c 'cd investigacion && setsid python3 -m http.server 5000 > /tmp/docsify.log 2>&1 < /dev/null & sleep 2 && gitpod environment port open 5000 --name \"Docsify Docs\" || true'"
}
```

**Nota:** Esta configuración:
1. Inicia el servidor en background
2. Espera 2 segundos para que el servidor esté listo
3. Abre el puerto públicamente
4. Usa `|| true` para no fallar si el puerto ya está abierto

## Comandos Rápidos de Referencia

### Iniciar servidor
```bash
cd investigacion && python3 -m http.server 5000
```

### Iniciar en background
```bash
cd investigacion && setsid python3 -m http.server 5000 > /tmp/docsify.log 2>&1 < /dev/null &
```

### Abrir puerto
```bash
gitpod environment port open 5000 --name "Docsify Docs"
```

### Ver URL
```bash
gitpod environment port list | grep 5000
```

### Ver logs
```bash
tail -f /tmp/docsify.log
```

### Detener servidor
```bash
pkill -f "python3 -m http.server 5000"
```

### Verificar estado
```bash
ps aux | grep "http.server" && lsof -i :5000
```

## Recursos Adicionales

- **Documentación oficial de Docsify**: https://docsify.js.org/
- **Guía de configuración**: https://docsify.js.org/#/configuration
- **Plugins disponibles**: https://docsify.js.org/#/plugins
- **Temas**: https://docsify.js.org/#/themes
- **Mermaid.js**: https://mermaid.js.org/

## Notas Importantes

1. **No requiere instalación de npm/node**: Python 3 es suficiente
2. **No requiere compilación**: Docsify funciona completamente en el navegador
3. **CDN vs Local**: Usamos CDN para simplicidad, pero puedes descargar los archivos localmente si lo prefieres
4. **Puerto 5000**: Es arbitrario, puedes usar cualquier puerto disponible
5. **Gitpod específico**: Los comandos `gitpod environment port` son específicos de Gitpod/Ona

## Mantenimiento

### Actualizar Docsify

Las versiones se especifican en `index.html`. Para actualizar:

1. Cambiar `@4` por `@latest` en las URLs de CDN
2. O especificar una versión exacta: `@4.13.0`

Ejemplo:
```html
<!-- Versión específica -->
<script src="//cdn.jsdelivr.net/npm/docsify@4.13.0"></script>

<!-- Última versión -->
<script src="//cdn.jsdelivr.net/npm/docsify@latest"></script>
```

### Añadir nuevos documentos

1. Crear archivo `.md` en `investigacion/`
2. Añadir enlace en `_sidebar.md` (opcional)
3. El documento estará disponible automáticamente

### Cambiar tema

Editar `index.html` y cambiar la línea del tema:

```html
<!-- Tema oscuro -->
<link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/dark.css">

<!-- Tema claro -->
<link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/vue.css">

<!-- Otros temas: buble, pure, dolphin -->
```

---

**Última actualización**: Noviembre 2025  
**Versión de Docsify**: 4.x  
**Compatibilidad**: Gitpod/Ona environments con Python 3
