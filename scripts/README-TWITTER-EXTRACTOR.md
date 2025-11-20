# Extractor de Opiniones de Threads de Twitter/X

Herramientas para extraer y analizar opiniones de threads/conversaciones de Twitter/X.

## 🎯 Objetivo

Extraer todas las respuestas y opiniones de un tweet específico, organizarlas jerárquicamente, y generar un análisis detallado.

## 📋 Opciones Disponibles

### Opción 1: Script Python (RECOMENDADO) ⭐

El script de Python es más confiable y no requiere credenciales de Twitter.

#### Instalación

```bash
# Crear entorno virtual (opcional pero recomendado)
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install requests beautifulsoup4 snscrape
```

#### Uso Básico

```bash
# Método 1: Usando Nitter (más rápido, sin autenticación)
python scripts/extract-tweet-thread.py https://x.com/Dwriteway/status/1991025255859544564

# Método 2: Usando snscrape (más completo pero más lento)
python scripts/extract-tweet-thread.py --method snscrape https://x.com/Dwriteway/status/1991025255859544564

# Con instancia de Nitter personalizada
python scripts/extract-tweet-thread.py --nitter-instance nitter.it https://x.com/Dwriteway/status/1991025255859544564
```

#### Salida

El script genera dos archivos en el directorio `output/`:

1. **JSON con datos completos** (`tweet-thread-{id}-{timestamp}.json`):
   ```json
   [
     {
       "id": "1991025255859544564",
       "author": "Dwriteway",
       "content": "Contenido del tweet...",
       "created_at": "2025-01-15T10:30:00",
       "likes": 42,
       "retweets": 5,
       "replies": 23,
       "depth": 0
     },
     ...
   ]
   ```

2. **Resumen en Markdown** (`tweet-summary-{id}-{timestamp}.md`):
   - Tweet principal
   - Opiniones organizadas por profundidad
   - Autores más activos
   - Tweets con más engagement

### Opción 2: Script TypeScript/Node.js

Requiere más configuración pero se integra mejor con el stack de Kodless.

#### Instalación

```bash
npm install agent-twitter-client dotenv tsx
```

#### Configuración

Crear archivo `.env` en la raíz del proyecto:

```env
# Opcional: Para mejores resultados con autenticación
TWITTER_USERNAME=tu_usuario
TWITTER_PASSWORD=tu_contraseña
```

#### Uso

```bash
# Ejecutar con tsx
npx tsx scripts/extract-tweet-thread.ts https://x.com/Dwriteway/status/1991025255859544564

# O especificar la URL como argumento
npx tsx scripts/extract-tweet-thread.ts
```

## 🔧 Métodos de Extracción

### 1. Nitter (Recomendado para uso rápido)

**Ventajas:**
- No requiere autenticación
- Rápido y ligero
- No cuenta contra rate limits de Twitter

**Desventajas:**
- Las instancias de Nitter a veces están caídas
- Puede tener menos datos que otros métodos

**Instancias de Nitter disponibles:**
- `nitter.poast.org` (por defecto)
- `nitter.it`
- `nitter.net`
- `nitter.unixfox.eu`

### 2. SNScrape

**Ventajas:**
- No requiere API oficial
- Muy completo y confiable
- Obtiene datos históricos

**Desventajas:**
- Más lento
- Puede requerir actualizaciones frecuentes

### 3. Twitter API Oficial (No implementado aún)

**Ventajas:**
- Datos oficiales y completos
- Más confiable

**Desventajas:**
- Requiere cuenta de desarrollador
- Tiene límites de rate
- Puede tener costos

## 📊 Ejemplo de Salida

### JSON
```json
[
  {
    "id": "1991025255859544564",
    "author": "Dwriteway",
    "author_name": "Daniel Wright",
    "content": "Este es un tweet interesante sobre arquitectura de software...",
    "created_at": "2025-01-15T10:30:00+00:00",
    "likes": 156,
    "retweets": 23,
    "replies": 45,
    "views": 3200,
    "is_reply": false,
    "reply_to": null,
    "depth": 0
  },
  {
    "id": "1991025255859544565",
    "author": "usuario1",
    "author_name": "Usuario Ejemplo",
    "content": "Totalmente de acuerdo, especialmente en proyectos grandes...",
    "created_at": "2025-01-15T10:35:00+00:00",
    "likes": 23,
    "retweets": 2,
    "replies": 5,
    "views": 850,
    "is_reply": true,
    "reply_to": "1991025255859544564",
    "depth": 1
  }
]
```

### Markdown Summary

```markdown
# Análisis del Thread de Twitter

**ID del Tweet:** 1991025255859544564
**Total de tweets:** 47
**Fecha de extracción:** 2025-01-15 14:30:00

## Tweet Principal

- **Autor:** @Dwriteway (Daniel Wright)
- **Fecha:** 2025-01-15T10:30:00+00:00
- **Contenido:**

> Este es un tweet interesante sobre arquitectura de software...

- **Estadísticas:** 156 ❤️  | 23 🔄 | 45 💬

## Opiniones y Respuestas (46 total)

### Nivel 1 - 25 respuestas

1. **@usuario1** (23 ❤️)

   Totalmente de acuerdo, especialmente en proyectos grandes...

...
```

## 🚀 Uso Avanzado

### Procesar múltiples tweets

```bash
# Crear un script para procesar varios tweets
for url in \
  "https://x.com/tweet1" \
  "https://x.com/tweet2" \
  "https://x.com/tweet3"
do
  python scripts/extract-tweet-thread.py "$url"
  sleep 5  # Esperar 5 segundos entre requests
done
```

### Integrar con análisis de IA

```bash
# Extraer tweets
python scripts/extract-tweet-thread.py https://x.com/Dwriteway/status/1991025255859544564

# Luego puedes usar los JSONs generados con:
# - OpenAI API para análisis de sentimiento
# - Claude API para resumir opiniones
# - Análisis de tendencias
```

### Ejemplo de análisis con Claude

```typescript
import Anthropic from "@anthropic-ai/sdk";
import fs from "fs";

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Leer el JSON extraído
const tweets = JSON.parse(fs.readFileSync("output/tweet-thread-xxx.json", "utf-8"));

// Preparar el prompt
const tweetsText = tweets.map(t =>
  `@${t.author}: ${t.content} (${t.likes} likes)`
).join("\n\n");

// Analizar con Claude
const message = await anthropic.messages.create({
  model: "claude-3-5-sonnet-20241022",
  max_tokens: 1024,
  messages: [{
    role: "user",
    content: `Analiza las siguientes opiniones de un thread de Twitter y proporciona:
1. Temas principales discutidos
2. Sentimiento general (positivo/negativo/neutral)
3. Puntos de consenso
4. Puntos de desacuerdo
5. Insights clave

Opiniones:
${tweetsText}`
  }],
});

console.log(message.content);
```

## 🐛 Solución de Problemas

### Error: "Instancia de Nitter no disponible"

Prueba con otra instancia:
```bash
python scripts/extract-tweet-thread.py --nitter-instance nitter.it <URL>
```

### Error: "snscrape no funciona"

snscrape puede necesitar actualizaciones frecuentes:
```bash
pip install --upgrade snscrape
# o instalar desde git
pip install git+https://github.com/JustAnotherArchivist/snscrape.git
```

### "No se extraen todos los tweets"

Twitter limita el acceso a conversaciones muy largas. Prueba:
1. Usar el método snscrape
2. Autenticarse (para el script de Node.js)
3. Dividir la extracción en partes

### Rate Limiting

Si ves errores de rate limit:
```bash
# Agregar delays entre requests
sleep 10
python scripts/extract-tweet-thread.py <URL>
```

## 📝 Notas Importantes

1. **Respeta los Términos de Servicio**: El scraping de Twitter/X puede violar sus TOS. Usa estas herramientas responsablemente y solo para fines educativos o de investigación.

2. **Privacidad**: No extraigas información sensible o privada.

3. **Rate Limits**: No hagas scraping masivo. Añade delays entre requests.

4. **Instancias de Nitter**: Las instancias públicas pueden estar saturadas. Considera montar tu propia instancia.

## 🔮 Próximas Mejoras

- [ ] Soporte para Twitter API v2
- [ ] Análisis de sentimiento automático
- [ ] Visualización de threads como árbol
- [ ] Exportar a otros formatos (CSV, Excel)
- [ ] Detección de bots y spam
- [ ] Análisis de influencers en el thread
- [ ] Clustering de opiniones similares

## 📚 Referencias

- [SNScrape Documentation](https://github.com/JustAnotherArchivist/snscrape)
- [Nitter Project](https://github.com/zedeus/nitter)
- [Twitter API Documentation](https://developer.twitter.com/en/docs)
- [agent-twitter-client](https://github.com/ai16z/agent-twitter-client)
