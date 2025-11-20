#!/usr/bin/env python3
"""
Genera un resumen analítico de un archivo JSON de tweets

Uso:
    python scripts/generate-summary-from-json.py tweets.json
    python scripts/generate-summary-from-json.py tweets.json --output-dir analysis
"""

import json
import argparse
import os
from datetime import datetime
from typing import List, Dict, Any
from collections import Counter


def load_tweets(json_file: str) -> List[Dict[str, Any]]:
    """Carga tweets desde un archivo JSON"""
    with open(json_file, 'r', encoding='utf-8') as f:
        tweets = json.load(f)

    print(f"✅ Cargados {len(tweets)} tweets desde {json_file}")
    return tweets


def generate_detailed_analysis(tweets: List[Dict[str, Any]], output_dir: str):
    """Genera análisis detallado en Markdown"""

    if not tweets:
        print("❌ No hay tweets para analizar")
        return

    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = os.path.join(output_dir, f'analisis-tweets-{timestamp}.md')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Análisis Detallado de Opiniones en Twitter\n\n")
        f.write(f"**Fecha de análisis:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total de tweets:** {len(tweets)}\n\n")

        # Separar tweet principal de respuestas
        main_tweet = tweets[0] if tweets else None
        replies = tweets[1:] if len(tweets) > 1 else []

        # 1. Tweet Principal
        if main_tweet:
            f.write(f"## 📌 Tweet Principal\n\n")
            f.write(f"**Autor:** @{main_tweet.get('author', 'unknown')}\n")
            f.write(f"**Fecha:** {main_tweet.get('timestamp', 'N/A')}\n\n")
            f.write(f"**Contenido:**\n\n")
            f.write(f"> {main_tweet.get('content', '')}\n\n")

            stats = f"**Engagement:**\n"
            stats += f"- ❤️  Likes: {main_tweet.get('likes', 0):,}\n"
            stats += f"- 🔄 Retweets: {main_tweet.get('retweets', 0):,}\n"
            stats += f"- 💬 Respuestas: {main_tweet.get('replies', 0):,}\n"
            total_engagement = (main_tweet.get('likes', 0) +
                              main_tweet.get('retweets', 0) +
                              main_tweet.get('replies', 0))
            stats += f"- 📊 Total: {total_engagement:,}\n"
            f.write(stats + "\n")

        # 2. Respuestas Ordenadas por Engagement
        if replies:
            f.write(f"## 💬 Opiniones y Respuestas ({len(replies)} total)\n\n")

            # Ordenar por engagement total
            sorted_replies = sorted(
                replies,
                key=lambda t: t.get('likes', 0) + t.get('retweets', 0) * 2,
                reverse=True
            )

            f.write(f"### Top 20 Respuestas con Más Engagement\n\n")
            for i, tweet in enumerate(sorted_replies[:20], 1):
                engagement = tweet.get('likes', 0) + tweet.get('retweets', 0) * 2

                f.write(f"#### {i}. @{tweet.get('author', 'unknown')} "
                       f"({tweet.get('likes', 0)} ❤️, {tweet.get('retweets', 0)} 🔄)\n\n")

                content = tweet.get('content', '')
                if len(content) > 500:
                    content = content[:500] + '...'

                f.write(f"{content}\n\n")
                f.write(f"*Engagement score: {engagement}*\n\n")
                f.write(f"---\n\n")

            # 3. Análisis de Autores
            f.write(f"## 👥 Análisis de Autores\n\n")

            # Contar participaciones
            author_counts = Counter(t.get('author', 'unknown') for t in replies)
            f.write(f"**Autores únicos:** {len(author_counts)}\n\n")

            f.write(f"### Top 15 Autores Más Activos\n\n")
            for i, (author, count) in enumerate(author_counts.most_common(15), 1):
                # Calcular engagement total del autor
                author_tweets = [t for t in replies if t.get('author') == author]
                total_likes = sum(t.get('likes', 0) for t in author_tweets)
                total_rts = sum(t.get('retweets', 0) for t in author_tweets)

                f.write(f"{i}. **@{author}** - {count} tweets\n")
                f.write(f"   - Total likes: {total_likes:,}\n")
                f.write(f"   - Total retweets: {total_rts:,}\n")
                f.write(f"   - Promedio likes/tweet: {total_likes/count:.1f}\n\n")

            # 4. Análisis Temporal
            f.write(f"## 📅 Análisis Temporal\n\n")

            tweets_with_time = [t for t in tweets if t.get('timestamp')]
            if tweets_with_time:
                timestamps = [t['timestamp'] for t in tweets_with_time]
                f.write(f"**Período:** {min(timestamps)} a {max(timestamps)}\n")
                f.write(f"**Tweets con timestamp:** {len(tweets_with_time)}/{len(tweets)}\n\n")

            # 5. Estadísticas Generales
            f.write(f"## 📊 Estadísticas Generales\n\n")

            total_likes = sum(t.get('likes', 0) for t in tweets)
            total_retweets = sum(t.get('retweets', 0) for t in tweets)
            total_replies = sum(t.get('replies', 0) for t in tweets)

            f.write(f"### Engagement Total\n\n")
            f.write(f"- **Total de likes:** {total_likes:,}\n")
            f.write(f"- **Total de retweets:** {total_retweets:,}\n")
            f.write(f"- **Total de respuestas:** {total_replies:,}\n")
            f.write(f"- **Engagement total:** {total_likes + total_retweets + total_replies:,}\n\n")

            f.write(f"### Promedios\n\n")
            f.write(f"- **Likes por tweet:** {total_likes/len(tweets):.2f}\n")
            f.write(f"- **Retweets por tweet:** {total_retweets/len(tweets):.2f}\n")
            f.write(f"- **Respuestas por tweet:** {total_replies/len(tweets):.2f}\n\n")

            # 6. Análisis de Contenido
            f.write(f"## 📝 Análisis de Contenido\n\n")

            # Palabras más comunes (simplificado)
            all_text = ' '.join(t.get('content', '') for t in tweets).lower()
            words = [w for w in all_text.split() if len(w) > 4]  # Palabras de 5+ letras
            word_counts = Counter(words)

            f.write(f"### Palabras Más Frecuentes (5+ letras)\n\n")
            for word, count in word_counts.most_common(30):
                f.write(f"- `{word}`: {count} veces\n")

            f.write(f"\n### Estadísticas de Texto\n\n")
            avg_length = sum(len(t.get('content', '')) for t in tweets) / len(tweets)
            f.write(f"- **Longitud promedio:** {avg_length:.0f} caracteres\n")

            long_tweets = [t for t in tweets if len(t.get('content', '')) > 200]
            f.write(f"- **Tweets largos (200+ chars):** {len(long_tweets)} ({len(long_tweets)/len(tweets)*100:.1f}%)\n")

            # 7. Distribución de Engagement
            f.write(f"\n## 📈 Distribución de Engagement\n\n")

            # Categorizar tweets por engagement
            high_engagement = [t for t in replies if t.get('likes', 0) >= 10]
            medium_engagement = [t for t in replies if 3 <= t.get('likes', 0) < 10]
            low_engagement = [t for t in replies if t.get('likes', 0) < 3]

            f.write(f"- **Alto engagement (10+ likes):** {len(high_engagement)} tweets ({len(high_engagement)/len(replies)*100:.1f}%)\n")
            f.write(f"- **Medio engagement (3-9 likes):** {len(medium_engagement)} tweets ({len(medium_engagement)/len(replies)*100:.1f}%)\n")
            f.write(f"- **Bajo engagement (0-2 likes):** {len(low_engagement)} tweets ({len(low_engagement)/len(replies)*100:.1f}%)\n\n")

            # 8. Resumen Ejecutivo
            f.write(f"## 🎯 Resumen Ejecutivo\n\n")

            f.write(f"1. **Alcance:** El tweet principal generó {len(replies)} respuestas directas\n")
            f.write(f"2. **Engagement:** Total de {total_likes:,} likes y {total_retweets:,} retweets\n")
            f.write(f"3. **Participación:** {len(author_counts)} usuarios únicos participaron\n")

            if author_counts:
                top_author = author_counts.most_common(1)[0]
                f.write(f"4. **Usuario más activo:** @{top_author[0]} con {top_author[1]} tweets\n")

            if sorted_replies:
                top_reply = sorted_replies[0]
                f.write(f"5. **Respuesta más popular:** @{top_reply.get('author')} con {top_reply.get('likes', 0)} likes\n")

    print(f"\n✅ Análisis guardado en: {output_file}")
    return output_file


def main():
    parser = argparse.ArgumentParser(description='Generar análisis de tweets desde JSON')
    parser.add_argument('json_file', help='Archivo JSON con los tweets')
    parser.add_argument('--output-dir', default='output',
                       help='Directorio de salida (default: output)')

    args = parser.parse_args()

    if not os.path.exists(args.json_file):
        print(f"❌ Error: No se encuentra el archivo {args.json_file}")
        return 1

    print(f"\n📊 Generador de Análisis de Tweets")
    print(f"{'=' * 50}\n")

    # Cargar tweets
    tweets = load_tweets(args.json_file)

    # Generar análisis
    generate_detailed_analysis(tweets, args.output_dir)

    print(f"\n✅ Análisis completado!")


if __name__ == '__main__':
    main()
