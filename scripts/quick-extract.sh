#!/bin/bash
# Script rápido para extraer opiniones de un tweet usando Nitter

TWEET_URL="${1:-https://x.com/Dwriteway/status/1991025255859544564}"
OUTPUT_DIR="output"

echo "🐦 Extractor Rápido de Tweets"
echo "=============================="
echo ""
echo "URL: $TWEET_URL"
echo ""

# Crear directorio de salida
mkdir -p "$OUTPUT_DIR"

# Extraer ID del tweet
TWEET_ID=$(echo "$TWEET_URL" | grep -oP 'status/\K\d+')

if [ -z "$TWEET_ID" ]; then
    echo "❌ Error: No se pudo extraer el ID del tweet de la URL"
    exit 1
fi

echo "📍 ID del tweet: $TWEET_ID"
echo ""

# Lista de instancias de Nitter para probar
NITTER_INSTANCES=(
    "nitter.poast.org"
    "nitter.privacydev.net"
    "nitter.it"
    "nitter.net"
)

# Probar cada instancia hasta encontrar una que funcione
for INSTANCE in "${NITTER_INSTANCES[@]}"; do
    echo "🔍 Probando instancia: $INSTANCE"

    # Convertir URL a Nitter
    NITTER_URL=$(echo "$TWEET_URL" | sed "s|x\.com|$INSTANCE|" | sed "s|twitter\.com|$INSTANCE|")

    # Descargar página
    HTTP_CODE=$(curl -s -o "$OUTPUT_DIR/tweet-$TWEET_ID.html" -w "%{http_code}" \
        -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
        "$NITTER_URL")

    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Descargado exitosamente desde $INSTANCE"
        echo ""
        echo "📄 HTML guardado en: $OUTPUT_DIR/tweet-$TWEET_ID.html"
        echo ""
        echo "Para ver el contenido:"
        echo "  - Abre el archivo HTML en un navegador"
        echo "  - O usa el script de Python para análisis más detallado:"
        echo ""
        echo "    python scripts/extract-tweet-thread.py \"$TWEET_URL\""
        echo ""

        # Intentar extraer información básica con grep
        echo "📊 Información básica:"
        echo ""

        # Contar tweets en la página
        TWEET_COUNT=$(grep -o 'class="timeline-item' "$OUTPUT_DIR/tweet-$TWEET_ID.html" | wc -l)
        echo "  Tweets encontrados en la página: $TWEET_COUNT"

        exit 0
    else
        echo "  ❌ No disponible (HTTP $HTTP_CODE)"
    fi
done

echo ""
echo "❌ No se pudo acceder a ninguna instancia de Nitter"
echo ""
echo "💡 Alternativas:"
echo "  1. Usa el script de Python con snscrape:"
echo "     pip install snscrape"
echo "     python scripts/extract-tweet-thread.py --method snscrape \"$TWEET_URL\""
echo ""
echo "  2. Prueba manualmente en tu navegador:"
for INSTANCE in "${NITTER_INSTANCES[@]}"; do
    NITTER_URL=$(echo "$TWEET_URL" | sed "s|x\.com|$INSTANCE|" | sed "s|twitter\.com|$INSTANCE|")
    echo "     - $NITTER_URL"
done

exit 1
