# Diagnóstico: Puerto 5000 no se abre automáticamente al iniciar el environment

## Fecha
2025-11-17

## Problema Observado

Al iniciar el environment de Gitpod/Ona, el puerto 5000 (servicio docsify) presenta dos problemas:

1. **El puerto no se expone públicamente de forma automática** - Requiere ejecutar manualmente `gitpod environment port open 5000 --name docsify`
2. **No se muestra el link de preview al usuario** - El `postAttachCommand` intenta mostrar la URL pero no funciona correctamente

## Configuración Actual

### devcontainer.json
```json
{
  "postStartCommand": "bash -c 'cd investigacion && setsid python3 -m http.server 5000 > /tmp/docsify.log 2>&1 < /dev/null &'",
  "postAttachCommand": "bash -c 'sleep 3 && echo \"\" && echo \"📚 Documentación WYSIWID (Docsify) disponible en:\" && gitpod environment port list | grep 5000 | awk \"{print \\$3}\" && echo \"\" && echo \"✨ Features: Syntax highlighting + Mermaid diagrams + Dark mode\"'",
  "forwardPorts": [5000],
  "portsAttributes": {
    "5000": {
      "label": "Docsify Docs",
      "onAutoForward": "notify"
    }
  }
}
```

## Análisis de Causas Raíz

### Problema 1: Puerto no se expone públicamente

**Causa Raíz:** Diferencia entre "forward" y "open" en Gitpod/Ona

Según la documentación oficial de Dev Containers (https://containers.dev/implementors/json_reference/):

- **`forwardPorts`**: Reenvía puertos desde el contenedor al host local, pero NO los expone públicamente en entornos cloud como Gitpod
- **`onAutoForward`**: Controla notificaciones cuando se detecta un puerto, pero no controla la exposición pública

En Gitpod/Ona, hay dos conceptos distintos:
1. **Port forwarding** (devcontainer.json): Hace el puerto accesible desde el host
2. **Port opening** (Gitpod CLI): Expone el puerto públicamente con una URL HTTPS

**Evidencia:**
- El servidor Python está corriendo correctamente (verificado en `/tmp/docsify.log`)
- El puerto está en LISTEN (verificado con `lsof -i -P -n`)
- Pero `gitpod environment port list` inicialmente NO muestra el puerto 5000
- Solo después de ejecutar `gitpod environment port open 5000 --name docsify` aparece la URL pública

**Limitación de devcontainer.json:**
El estándar de Dev Containers no incluye una propiedad para exponer puertos públicamente porque es específico de cada plataforma cloud. Gitpod requiere su propio mecanismo.

### Problema 2: Link de preview no se muestra

**Causa Raíz:** Timing y dependencias del comando

El `postAttachCommand` tiene múltiples problemas:

1. **Timing incorrecto**: Ejecuta `gitpod environment port list` antes de que el puerto esté abierto públicamente
   - `postStartCommand` inicia el servidor
   - `postAttachCommand` se ejecuta "cada vez que una herramienta se conecta"
   - Pero el puerto NO se abre automáticamente, por lo que `port list` no encuentra la URL

2. **Dependencia circular**: El comando intenta mostrar una URL que no existe hasta que se ejecute manualmente `port open`

3. **Comando grep/awk frágil**: Asume un formato específico de salida que puede no existir si el puerto no está en la lista

**Evidencia:**
```bash
$ gitpod environment port list
PORT  NAME           URL                                                                         PROTOCOL 
50432 VS Code Server https://50432--019a8fc8-5490-7dac-8c16-c1fe616620d7.us-east-1-01.gitpod.dev HTTP     
61000 ona-swe-agent  https://61000--019a8fc8-5490-7dac-8c16-c1fe616620d7.us-east-1-01.gitpod.dev HTTP
# Puerto 5000 NO aparece hasta ejecutar 'port open'
```

## Búsqueda en Documentación Oficial

### Documentación de Ona consultada:
- AGENTS.md Configuration
- LLM Providers (Anthropic, Bedrock, Google Vertex)
- Agents Overview

**Resultado:** La documentación de Ona no contiene información específica sobre:
- Configuración de puertos en environments
- Exposición automática de puertos públicos
- Integración entre devcontainer.json y Gitpod CLI para puertos

### Documentación de Dev Containers consultada:
- https://containers.dev/implementors/json_reference/

**Hallazgos clave:**
- `forwardPorts`: "should always be forwarded from inside the primary container to the local machine"
- `onAutoForward`: Valores posibles: `none`, `notify` (default), `openBrowser`, `openPreview`, `silent`
- `portsAttributes`: Permite configurar label y comportamiento de auto-forward
- **NO existe** una propiedad estándar para exposición pública en cloud

### Lifecycle Scripts relevantes:
- `postStartCommand`: Ejecuta cada vez que el contenedor inicia exitosamente
- `postAttachCommand`: Ejecuta cada vez que una herramienta se conecta al contenedor
- `postCreateCommand`: Ejecuta solo en la creación inicial

## Soluciones Posibles (No Implementadas)

### Opción 1: Usar postCreateCommand o postStartCommand para abrir el puerto
```json
"postStartCommand": "bash -c 'cd investigacion && setsid python3 -m http.server 5000 > /tmp/docsify.log 2>&1 < /dev/null & sleep 2 && gitpod environment port open 5000 --name \"Docsify Docs\" || true'"
```

**Pros:**
- Abre el puerto automáticamente al iniciar
- Un solo comando maneja todo

**Contras:**
- Mezcla responsabilidades (iniciar servidor + configurar infraestructura)
- El `sleep 2` es arbitrario y puede fallar si el servidor tarda más
- Puede fallar si el puerto ya está abierto (de ahí el `|| true`)

### Opción 2: Usar postAttachCommand para mostrar URL después de abrir puerto
```json
"postStartCommand": "bash -c 'cd investigacion && setsid python3 -m http.server 5000 > /tmp/docsify.log 2>&1 < /dev/null & sleep 2 && gitpod environment port open 5000 --name \"Docsify Docs\" > /tmp/port-url.txt 2>&1'",
"postAttachCommand": "bash -c 'if [ -f /tmp/port-url.txt ]; then echo \"\"; echo \"📚 Documentación WYSIWID (Docsify) disponible en:\"; cat /tmp/port-url.txt; echo \"\"; echo \"✨ Features: Syntax highlighting + Mermaid diagrams + Dark mode\"; fi'"
```

**Pros:**
- Separa la apertura del puerto de la notificación
- Usa un archivo temporal para comunicar la URL
- Más robusto que grep/awk

**Contras:**
- Más complejo
- Depende de archivos temporales
- Aún tiene el problema del timing

### Opción 3: Usar Gitpod Automations (si está disponible)
Según la documentación de Ona, existe `gitpod automations` para workflow management:
- `gitpod automations service start/stop/logs`

**Investigación necesaria:**
- ¿Se pueden definir automations en el repositorio?
- ¿Pueden las automations abrir puertos automáticamente?
- ¿Cuál es la sintaxis y configuración?

### Opción 4: Script de inicialización dedicado
Crear un script `scripts/init-environment.sh` que:
1. Inicie el servidor docsify
2. Espere a que el puerto esté en LISTEN
3. Abra el puerto públicamente
4. Guarde la URL en un archivo conocido
5. Muestre la URL al usuario

Luego llamarlo desde `postStartCommand`.

## Recomendaciones

1. **Investigar Gitpod Automations**: Puede ser la forma "oficial" de manejar este tipo de configuración
2. **Considerar .gitpod.yml**: Aunque Ona usa Dev Containers, puede haber compatibilidad con configuración legacy de Gitpod
3. **Contactar soporte de Gitpod/Ona**: Este es un caso de uso común que debería tener una solución documentada
4. **Implementar Opción 1 como workaround temporal**: Es la más simple y funcional, aunque no sea elegante

## Referencias

- [Dev Containers JSON Reference](https://containers.dev/implementors/json_reference/)
- [Docker CLI --mount flag](https://docs.docker.com/engine/reference/commandline/run/#mount)
- Documentación de Ona (consultada pero sin información específica sobre puertos)

## Estado

**Sin corregir** - Este documento es solo diagnóstico según lo solicitado.
