#!/usr/bin/env python3
"""
Extractor de tweets usando Playwright para simular navegador real
Esto evita los bloqueos 403 de Twitter

Instalación:
    pip install playwright beautifulsoup4
    playwright install chromium

Uso:
    python scripts/extract-tweet-playwright.py <URL>
"""

import json
import argparse
import os
import re
from datetime import datetime
from typing import List, Dict, Any
import asyncio


async def extract_with_playwright(tweet_url: str, output_dir: str = "output"):
    """Extrae tweets usando Playwright para evitar bloqueos"""

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Playwright no está instalado.")
        print("   Instala con: pip install playwright && playwright install chromium")
        return None

    # Extraer ID del tweet
    match = re.search(r'status/(\d+)', tweet_url)
    if not match:
        print("❌ URL de tweet inválida")
        return None

    tweet_id = match.group(1)

    print(f"🌐 Abriendo navegador para extraer tweet {tweet_id}...")

    async with async_playwright() as p:
        # Lanzar navegador
        browser = await p.chromium.launch(
            headless=True,
            args=['--ignore-certificate-errors', '--disable-web-security']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        page = await context.new_page()

        try:
            print(f"📍 Navegando a: {tweet_url}")

            # Ir a la URL del tweet
            await page.goto(tweet_url, wait_until='networkidle', timeout=60000)

            # Esperar a que se cargue el contenido
            print("⏳ Esperando que cargue el contenido...")
            await asyncio.sleep(5)

            # Scroll para cargar más tweets
            print("📜 Cargando respuestas...")
            for i in range(5):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(2)
                print(f"   Scroll {i+1}/5...")

            # Obtener el HTML
            html_content = await page.content()

            # Guardar HTML para debugging
            os.makedirs(output_dir, exist_ok=True)
            html_file = os.path.join(output_dir, f'tweet-{tweet_id}-raw.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"💾 HTML guardado en: {html_file}")

            # Intentar extraer tweets usando selectores de Twitter
            tweets = []

            # Buscar todos los artículos (tweets)
            tweet_elements = await page.query_selector_all('article[data-testid="tweet"]')

            print(f"✅ Encontrados {len(tweet_elements)} tweets en la página")

            for idx, element in enumerate(tweet_elements):
                try:
                    # Extraer texto del tweet
                    text_element = await element.query_selector('[data-testid="tweetText"]')
                    text = await text_element.inner_text() if text_element else ""

                    # Extraer nombre de usuario
                    user_element = await element.query_selector('[data-testid="User-Name"]')
                    user_text = await user_element.inner_text() if user_element else ""

                    # Parsear username del formato "@username"
                    username = ""
                    if user_text:
                        lines = user_text.split('\n')
                        for line in lines:
                            if line.startswith('@'):
                                username = line[1:]
                                break

                    # Extraer estadísticas
                    like_button = await element.query_selector('[data-testid="like"]')
                    like_text = await like_button.get_attribute('aria-label') if like_button else "0"
                    likes = 0
                    if like_text:
                        like_match = re.search(r'(\d+)', like_text)
                        if like_match:
                            likes = int(like_match.group(1))

                    retweet_button = await element.query_selector('[data-testid="retweet"]')
                    retweet_text = await retweet_button.get_attribute('aria-label') if retweet_button else "0"
                    retweets = 0
                    if retweet_text:
                        retweet_match = re.search(r'(\d+)', retweet_text)
                        if retweet_match:
                            retweets = int(retweet_match.group(1))

                    reply_button = await element.query_selector('[data-testid="reply"]')
                    reply_text = await reply_button.get_attribute('aria-label') if reply_button else "0"
                    replies = 0
                    if reply_text:
                        reply_match = re.search(r'(\d+)', reply_text)
                        if reply_match:
                            replies = int(reply_match.group(1))

                    # Extraer timestamp
                    time_element = await element.query_selector('time')
                    timestamp = await time_element.get_attribute('datetime') if time_element else ""

                    tweet_data = {
                        'id': f"tweet_{idx}",
                        'author': username or f"user_{idx}",
                        'content': text,
                        'created_at': timestamp or datetime.now().isoformat(),
                        'likes': likes,
                        'retweets': retweets,
                        'replies': replies,
                        'depth': 1 if idx > 0 else 0  # Primer tweet es depth 0
                    }

                    tweets.append(tweet_data)

                    if (idx + 1) % 5 == 0:
                        print(f"   📊 Procesados {idx + 1} tweets...")

                except Exception as e:
                    print(f"⚠️  Error procesando tweet {idx}: {e}")
                    continue

            # Guardar JSON
            if tweets:
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                json_file = os.path.join(output_dir, f'tweet-thread-{tweet_id}-{timestamp}.json')

                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(tweets, f, indent=2, ensure_ascii=False)

                print(f"\n💾 Datos guardados en: {json_file}")
                print(f"✅ Total de tweets extraídos: {len(tweets)}")

                # Generar resumen
                generate_summary(tweets, output_dir, tweet_id)

                return tweets
            else:
                print("❌ No se pudieron extraer tweets del HTML")
                print("💡 El HTML se guardó para análisis manual")
                return None

        except Exception as e:
            print(f"❌ Error durante la extracción: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            await browser.close()


def generate_summary(tweets: List[Dict[str, Any]], output_dir: str, tweet_id: str):
    """Genera un resumen en markdown"""

    if not tweets:
        return

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    summary_file = os.path.join(output_dir, f'tweet-summary-{tweet_id}-{timestamp}.md')

    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"# Análisis del Thread de Twitter\n\n")
        f.write(f"**ID del Tweet:** {tweet_id}\n")
        f.write(f"**Total de tweets:** {len(tweets)}\n")
        f.write(f"**Fecha de extracción:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Tweet principal
        main_tweet = tweets[0]
        f.write(f"## Tweet Principal\n\n")
        f.write(f"- **Autor:** @{main_tweet['author']}\n")
        f.write(f"- **Fecha:** {main_tweet.get('created_at', 'N/A')}\n")
        f.write(f"- **Contenido:**\n\n")
        f.write(f"> {main_tweet['content']}\n\n")
        f.write(f"- **Estadísticas:** {main_tweet['likes']} ❤️  | {main_tweet['retweets']} 🔄 | {main_tweet['replies']} 💬\n\n")

        # Respuestas
        if len(tweets) > 1:
            replies = tweets[1:]
            f.write(f"## Respuestas ({len(replies)} total)\n\n")

            # Ordenar por engagement
            sorted_replies = sorted(replies, key=lambda t: t['likes'] + t['retweets'], reverse=True)

            for i, tweet in enumerate(sorted_replies[:30], 1):
                f.write(f"### {i}. @{tweet['author']} ({tweet['likes']} ❤️, {tweet['retweets']} 🔄)\n\n")
                content = tweet['content'][:400]
                if len(tweet['content']) > 400:
                    content += '...'
                f.write(f"{content}\n\n")
                f.write(f"---\n\n")

        # Autores únicos
        authors = set(t['author'] for t in tweets)
        f.write(f"## Estadísticas\n\n")
        f.write(f"- **Autores únicos:** {len(authors)}\n")
        f.write(f"- **Total de likes:** {sum(t['likes'] for t in tweets)}\n")
        f.write(f"- **Total de retweets:** {sum(t['retweets'] for t in tweets)}\n")

    print(f"📄 Resumen guardado en: {summary_file}")


def main():
    parser = argparse.ArgumentParser(description='Extraer thread de Twitter con Playwright')
    parser.add_argument('url', nargs='?',
                       default='https://x.com/Dwriteway/status/1991025255859544564',
                       help='URL del tweet')
    parser.add_argument('--output-dir', default='output',
                       help='Directorio de salida')

    args = parser.parse_args()

    print(f"\n🐦 Extractor de Threads de Twitter con Playwright")
    print(f"{'=' * 50}\n")

    # Ejecutar extracción
    asyncio.run(extract_with_playwright(args.url, args.output_dir))


if __name__ == '__main__':
    main()
