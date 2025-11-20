#!/usr/bin/env python3
"""
Script para extraer opiniones de un thread de Twitter/X
usando técnicas de scraping sin necesidad de API oficial

Instalación:
    pip install tweepy snscrape playwright beautifulsoup4

Uso básico:
    python scripts/extract-tweet-thread.py https://x.com/Dwriteway/status/1991025255859544564

Uso con diferentes métodos:
    python scripts/extract-tweet-thread.py --method snscrape <URL>
    python scripts/extract-tweet-thread.py --method playwright <URL>
"""

import json
import argparse
import os
from datetime import datetime
from typing import List, Dict, Any
import re


class TweetExtractor:
    """Clase base para extractores de tweets"""

    def __init__(self, tweet_url: str):
        self.tweet_url = tweet_url
        self.tweet_id = self._extract_tweet_id(tweet_url)
        self.tweets = []

    def _extract_tweet_id(self, url: str) -> str:
        """Extrae el ID del tweet de la URL"""
        match = re.search(r'status/(\d+)', url)
        if not match:
            raise ValueError(f"URL de tweet inválida: {url}")
        return match.group(1)

    def extract(self) -> List[Dict[str, Any]]:
        """Método a implementar por subclases"""
        raise NotImplementedError


class SNScrapeExtractor(TweetExtractor):
    """Extractor usando snscrape (más confiable pero más lento)"""

    def extract(self) -> List[Dict[str, Any]]:
        try:
            import snscrape.modules.twitter as sntwitter
        except ImportError:
            print("❌ snscrape no está instalado. Instalalo con: pip install snscrape")
            return []

        print(f"🔍 Buscando conversación del tweet {self.tweet_id} con snscrape...")

        tweets = []

        # Buscar el tweet principal y sus respuestas
        query = f"conversation_id:{self.tweet_id}"

        try:
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
                if i > 500:  # Límite de seguridad
                    break

                tweet_data = {
                    'id': str(tweet.id),
                    'author': tweet.user.username,
                    'author_name': tweet.user.displayname,
                    'content': tweet.rawContent,
                    'created_at': tweet.date.isoformat(),
                    'likes': tweet.likeCount or 0,
                    'retweets': tweet.retweetCount or 0,
                    'replies': tweet.replyCount or 0,
                    'views': getattr(tweet, 'viewCount', 0) or 0,
                    'is_reply': tweet.inReplyToTweetId is not None,
                    'reply_to': str(tweet.inReplyToTweetId) if tweet.inReplyToTweetId else None,
                }
                tweets.append(tweet_data)

                if (i + 1) % 10 == 0:
                    print(f"  📊 Extraídos {i + 1} tweets...")

        except Exception as e:
            print(f"⚠️  Error durante scraping: {e}")

        print(f"✅ Total de tweets extraídos: {len(tweets)}")
        return tweets


class NitterExtractor(TweetExtractor):
    """Extractor usando instancia de Nitter (alternativa ligera)"""

    def __init__(self, tweet_url: str, nitter_instance: str = "nitter.net"):
        super().__init__(tweet_url)
        self.nitter_instance = nitter_instance

    def extract(self) -> List[Dict[str, Any]]:
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            print("❌ requests o beautifulsoup4 no están instalados.")
            print("   Instala con: pip install requests beautifulsoup4")
            return []

        # Convertir URL de Twitter a Nitter
        nitter_url = self.tweet_url.replace('x.com', self.nitter_instance).replace('twitter.com', self.nitter_instance)

        print(f"🔍 Scrapeando desde Nitter: {nitter_url}")

        try:
            response = requests.get(nitter_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Error accediendo a Nitter: {e}")
            print("   Intenta con otra instancia: nitter.it, nitter.poast.org, etc.")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        tweets = []

        # Extraer tweets de la página
        timeline_items = soup.find_all('div', class_='timeline-item')

        for item in timeline_items:
            try:
                # Extraer información del tweet
                tweet_link = item.find('a', class_='tweet-link')
                if not tweet_link:
                    continue

                tweet_id = tweet_link.get('href', '').split('/')[-1].replace('#m', '')

                username_elem = item.find('a', class_='username')
                fullname_elem = item.find('a', class_='fullname')
                content_elem = item.find('div', class_='tweet-content')
                date_elem = item.find('span', class_='tweet-date')

                # Stats
                stats = item.find('div', class_='tweet-stats')
                likes = 0
                retweets = 0
                replies = 0

                if stats:
                    for stat in stats.find_all('span', class_='tweet-stat'):
                        icon = stat.find('div', class_='icon-container')
                        if not icon:
                            continue

                        value_elem = stat.find('div', class_='icon-text')
                        value = int(value_elem.text.strip().replace(',', '')) if value_elem and value_elem.text.strip() else 0

                        icon_class = icon.get('class', [])
                        if 'icon-heart' in icon_class:
                            likes = value
                        elif 'icon-retweet' in icon_class:
                            retweets = value
                        elif 'icon-comment' in icon_class:
                            replies = value

                tweet_data = {
                    'id': tweet_id,
                    'author': username_elem.text.strip().replace('@', '') if username_elem else 'unknown',
                    'author_name': fullname_elem.text.strip() if fullname_elem else '',
                    'content': content_elem.text.strip() if content_elem else '',
                    'created_at': date_elem.get('title', '') if date_elem else '',
                    'likes': likes,
                    'retweets': retweets,
                    'replies': replies,
                    'views': 0,
                }
                tweets.append(tweet_data)

            except Exception as e:
                print(f"⚠️  Error procesando tweet: {e}")
                continue

        print(f"✅ Total de tweets extraídos: {len(tweets)}")
        return tweets


def calculate_depth(tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calcula la profundidad de cada tweet en el thread"""

    # Crear mapa de tweet_id -> tweet
    tweet_map = {t['id']: t for t in tweets}

    def get_depth(tweet_id: str, visited: set = None) -> int:
        if visited is None:
            visited = set()

        if tweet_id in visited:
            return 0

        visited.add(tweet_id)
        tweet = tweet_map.get(tweet_id)

        if not tweet or not tweet.get('reply_to'):
            return 0

        parent_id = tweet['reply_to']
        return 1 + get_depth(parent_id, visited)

    # Calcular profundidad para cada tweet
    for tweet in tweets:
        tweet['depth'] = get_depth(tweet['id'])

    return tweets


def generate_summary(tweets: List[Dict[str, Any]], output_dir: str, tweet_id: str):
    """Genera un resumen en markdown de los tweets extraídos"""

    if not tweets:
        return

    # Ordenar por fecha
    tweets_sorted = sorted(tweets, key=lambda t: t.get('created_at', ''))

    # Tweet principal (el primero o el que no es respuesta)
    main_tweet = next((t for t in tweets if not t.get('is_reply')), tweets[0])

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    summary_file = os.path.join(output_dir, f'tweet-summary-{tweet_id}-{timestamp}.md')

    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"# Análisis del Thread de Twitter\n\n")
        f.write(f"**ID del Tweet:** {tweet_id}\n")
        f.write(f"**Total de tweets:** {len(tweets)}\n")
        f.write(f"**Fecha de extracción:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Tweet principal
        f.write(f"## Tweet Principal\n\n")
        f.write(f"- **Autor:** @{main_tweet['author']} ({main_tweet.get('author_name', '')})\n")
        f.write(f"- **Fecha:** {main_tweet.get('created_at', 'N/A')}\n")
        f.write(f"- **Contenido:**\n\n")
        f.write(f"> {main_tweet['content']}\n\n")
        f.write(f"- **Estadísticas:** {main_tweet['likes']} ❤️  | {main_tweet['retweets']} 🔄 | {main_tweet['replies']} 💬\n\n")

        # Separar respuestas por profundidad
        replies = [t for t in tweets if t.get('is_reply') or t['id'] != main_tweet['id']]

        if replies:
            f.write(f"## Opiniones y Respuestas ({len(replies)} total)\n\n")

            # Agrupar por profundidad
            by_depth = {}
            for tweet in replies:
                depth = tweet.get('depth', 1)
                if depth not in by_depth:
                    by_depth[depth] = []
                by_depth[depth].append(tweet)

            # Mostrar por profundidad
            for depth in sorted(by_depth.keys()):
                depth_tweets = by_depth[depth]
                f.write(f"### Nivel {depth} - {len(depth_tweets)} respuestas\n\n")

                # Ordenar por engagement (likes)
                sorted_tweets = sorted(depth_tweets, key=lambda t: t['likes'], reverse=True)

                for i, tweet in enumerate(sorted_tweets[:20], 1):  # Top 20
                    f.write(f"{i}. **@{tweet['author']}** ({tweet['likes']} ❤️)\n\n")
                    content = tweet['content'][:300]
                    if len(tweet['content']) > 300:
                        content += '...'
                    f.write(f"   {content}\n\n")

                if len(depth_tweets) > 20:
                    f.write(f"   *... y {len(depth_tweets) - 20} respuestas más*\n\n")

        # Autores más activos
        author_counts = {}
        for tweet in tweets:
            author = tweet['author']
            author_counts[author] = author_counts.get(author, 0) + 1

        f.write(f"## Autores Más Activos\n\n")
        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:15]

        for i, (author, count) in enumerate(top_authors, 1):
            f.write(f"{i}. @{author} - {count} tweets\n")

        # Tweets con más engagement
        f.write(f"\n## Tweets con Más Engagement\n\n")
        top_engagement = sorted(tweets, key=lambda t: t['likes'] + t['retweets'], reverse=True)[:10]

        for i, tweet in enumerate(top_engagement, 1):
            f.write(f"{i}. **@{tweet['author']}** ({tweet['likes']} ❤️, {tweet['retweets']} 🔄)\n\n")
            content = tweet['content'][:200]
            if len(tweet['content']) > 200:
                content += '...'
            f.write(f"   {content}\n\n")

    print(f"📄 Resumen guardado en: {summary_file}")


def main():
    parser = argparse.ArgumentParser(description='Extraer opiniones de un thread de Twitter')
    parser.add_argument('url', nargs='?', default='https://x.com/Dwriteway/status/1991025255859544564',
                        help='URL del tweet')
    parser.add_argument('--method', choices=['snscrape', 'nitter'], default='nitter',
                        help='Método de extracción (default: nitter)')
    parser.add_argument('--nitter-instance', default='nitter.poast.org',
                        help='Instancia de Nitter a usar (default: nitter.poast.org)')
    parser.add_argument('--output-dir', default='output',
                        help='Directorio de salida (default: output)')

    args = parser.parse_args()

    # Crear directorio de salida
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"\n🐦 Extractor de Threads de Twitter/X")
    print(f"{'=' * 50}\n")
    print(f"URL: {args.url}")
    print(f"Método: {args.method}\n")

    # Seleccionar extractor
    if args.method == 'snscrape':
        extractor = SNScrapeExtractor(args.url)
    elif args.method == 'nitter':
        extractor = NitterExtractor(args.url, args.nitter_instance)
    else:
        print(f"❌ Método desconocido: {args.method}")
        return

    # Extraer tweets
    tweets = extractor.extract()

    if not tweets:
        print("❌ No se pudieron extraer tweets")
        return

    # Calcular profundidad si es posible
    tweets = calculate_depth(tweets)

    # Guardar JSON
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    json_file = os.path.join(args.output_dir, f'tweet-thread-{extractor.tweet_id}-{timestamp}.json')

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(tweets, f, indent=2, ensure_ascii=False)

    print(f"💾 Datos guardados en: {json_file}")

    # Generar resumen
    generate_summary(tweets, args.output_dir, extractor.tweet_id)

    print(f"\n✅ Extracción completada exitosamente!")
    print(f"   Total de tweets: {len(tweets)}")


if __name__ == '__main__':
    main()
