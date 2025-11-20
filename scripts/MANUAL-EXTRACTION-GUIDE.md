# Guía de Extracción Manual de Opiniones de Twitter

Si las herramientas automatizadas no funcionan, aquí hay métodos alternativos:

## 🔧 Método 1: Usando la Consola del Navegador

1. **Abre el tweet** en tu navegador:
   https://x.com/Dwriteway/status/1991025255859544564

2. **Haz scroll** hacia abajo para cargar todas las respuestas

3. **Abre la consola de desarrollador** (F12)

4. **Pega este código JavaScript**:

```javascript
// Extraer todos los tweets visibles
function extractTweets() {
    const tweets = [];
    const articles = document.querySelectorAll('article[data-testid="tweet"]');

    articles.forEach((article, index) => {
        try {
            // Extraer texto
            const textEl = article.querySelector('[data-testid="tweetText"]');
            const text = textEl ? textEl.innerText : '';

            // Extraer usuario
            const userEl = article.querySelector('[data-testid="User-Name"]');
            const userText = userEl ? userEl.innerText : '';
            const username = userText.split('\n').find(line => line.startsWith('@')) || '';

            // Extraer estadísticas
            const likeButton = article.querySelector('[data-testid="like"]');
            const likeLabel = likeButton ? likeButton.getAttribute('aria-label') : '';
            const likes = likeLabel.match(/(\d+)/) ? parseInt(likeLabel.match(/(\d+)/)[1]) : 0;

            const retweetButton = article.querySelector('[data-testid="retweet"]');
            const retweetLabel = retweetButton ? retweetButton.getAttribute('aria-label') : '';
            const retweets = retweetLabel.match(/(\d+)/) ? parseInt(retweetLabel.match(/(\d+)/)[1]) : 0;

            const replyButton = article.querySelector('[data-testid="reply"]');
            const replyLabel = replyButton ? replyButton.getAttribute('aria-label') : '';
            const replies = replyLabel.match(/(\d+)/) ? parseInt(replyLabel.match(/(\d+)/)[1]) : 0;

            // Extraer timestamp
            const timeEl = article.querySelector('time');
            const timestamp = timeEl ? timeEl.getAttribute('datetime') : '';

            tweets.push({
                index: index,
                author: username.replace('@', ''),
                content: text,
                likes: likes,
                retweets: retweets,
                replies: replies,
                timestamp: timestamp
            });
        } catch (e) {
            console.error('Error en tweet', index, e);
        }
    });

    return tweets;
}

// Ejecutar extracción
const tweets = extractTweets();
console.log('Tweets extraídos:', tweets.length);

// Copiar al portapapeles como JSON
copy(JSON.stringify(tweets, null, 2));
console.log('✅ JSON copiado al portapapeles!');

// Mostrar resumen
console.table(tweets.map(t => ({
    autor: t.author,
    likes: t.likes,
    contenido: t.content.substring(0, 50) + '...'
})));
```

5. **Guarda el JSON**:
   - El JSON se copió automáticamente al portapapeles
   - Pégalo en un archivo `tweets.json`

6. **Genera el resumen** (opcional):
   ```bash
   python scripts/generate-summary-from-json.py tweets.json
   ```

## 🌐 Método 2: Usar Extensiones de Navegador

### Twitter Archive Google Sheet
1. Instala: https://chrome.google.com/webstore/detail/twitter-archive/
2. Navega al tweet
3. Click en la extensión
4. Exporta a Google Sheets o CSV

### Treeverse
1. Instala: https://chrome.google.com/webstore/detail/treeverse/
2. Click en cualquier tweet
3. Visualiza y exporta el thread completo

## 📱 Método 3: Usar Aplicaciones de Terceros

### Thread Reader App
1. Ve a: https://threadreaderapp.com/
2. Pega: https://x.com/Dwriteway/status/1991025255859544564
3. Click en "Compile Thread"
4. Descarga como PDF o texto

### Vicinitas
1. Ve a: https://www.vicinitas.io/free-tools/download-twitter-timeline
2. Ingresa el username: @Dwriteway
3. Descarga el timeline en CSV
4. Filtra por tweet ID: 1991025255859544564

## 🔑 Método 4: Twitter API (Requiere cuenta de desarrollador)

Si tienes acceso a la API de Twitter:

```python
import tweepy
import json

# Configurar credenciales
bearer_token = "TU_BEARER_TOKEN"
client = tweepy.Client(bearer_token=bearer_token)

# ID del tweet
tweet_id = "1991025255859544564"

# Obtener conversación
tweets = client.search_recent_tweets(
    query=f"conversation_id:{tweet_id}",
    max_results=100,
    tweet_fields=['created_at', 'public_metrics', 'author_id'],
    expansions=['author_id']
)

# Guardar
with open('tweets-api.json', 'w') as f:
    json.dump([t.data for t in tweets.data], f, indent=2, default=str)

print(f"Extraídos {len(tweets.data)} tweets")
```

## 📋 Método 5: Copiar Manualmente

Para threads pequeños:

1. Abre el tweet
2. Crea un documento de texto
3. Para cada respuesta interesante:
   ```markdown
   ## @username (X likes)

   Contenido del tweet...

   ---
   ```

## 🎯 Para tu Tweet Específico

URL: https://x.com/Dwriteway/status/1991025255859544564

1. Abre la URL en tu navegador
2. Haz scroll para cargar todas las respuestas (aprox 30-50 segundos)
3. Usa el script JavaScript de la consola (Método 1)
4. El JSON se copiará automáticamente
5. Guárdalo como `tweet-1991025255859544564.json`

## 🔍 Análisis Post-Extracción

Una vez que tengas el JSON, puedes:

```bash
# Generar resumen
python scripts/generate-summary-from-json.py tweet-1991025255859544564.json

# Analizar sentimiento (si tienes OpenAI API)
python scripts/analyze-sentiment.py tweet-1991025255859544564.json

# Visualizar como árbol
python scripts/visualize-thread.py tweet-1991025255859544564.json
```

## ⚠️ Notas Importantes

1. **Rate Limits**: Twitter limita cuántas solicitudes puedes hacer
2. **Autenticación**: Iniciar sesión mejora los resultados
3. **Privacidad**: Respeta la privacidad de los usuarios
4. **TOS**: Revisa los términos de servicio de Twitter

## 🆘 Problemas Comunes

**"No veo todas las respuestas"**
- Haz scroll más despacio
- Espera 2-3 segundos entre scrolls
- Algunas respuestas pueden estar colapsadas

**"El script de consola no funciona"**
- Twitter puede haber cambiado su estructura
- Revisa la consola para errores
- Actualiza el script según los nuevos selectores

**"403 Forbidden"**
- Twitter bloqueó tu IP temporalmente
- Espera 15-30 minutos
- Usa VPN o red diferente

## 📚 Recursos Adicionales

- [Twitter Developer Docs](https://developer.twitter.com/en/docs)
- [Tweepy Documentation](https://docs.tweepy.org/)
- [Twitter API Rate Limits](https://developer.twitter.com/en/docs/twitter-api/rate-limits)
