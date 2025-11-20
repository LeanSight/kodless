/**
 * Script para extraer opiniones de un thread de Twitter/X
 *
 * Uso:
 * 1. Instalar dependencias: npm install agent-twitter-client dotenv
 * 2. Configurar .env con tus credenciales
 * 3. Ejecutar: npx tsx scripts/extract-tweet-thread.ts
 */

import { Scraper } from 'agent-twitter-client';
import * as fs from 'fs';
import * as path from 'path';

interface TweetData {
  id: string;
  author: string;
  content: string;
  createdAt: string;
  likes: number;
  retweets: number;
  replies: number;
  depth: number;
}

interface ThreadTree {
  tweet: TweetData;
  replies: ThreadTree[];
}

async function extractTweetThread(tweetUrl: string): Promise<void> {
  // Inicializar scraper
  const scraper = new Scraper();

  // Login (opcional pero recomendado para mejores resultados)
  const username = process.env.TWITTER_USERNAME;
  const password = process.env.TWITTER_PASSWORD;

  if (username && password) {
    await scraper.login(username, password);
    console.log('✓ Logged in to Twitter');
  } else {
    console.log('⚠ Running without authentication (limited results)');
  }

  // Extraer ID del tweet de la URL
  const tweetIdMatch = tweetUrl.match(/status\/(\d+)/);
  if (!tweetIdMatch) {
    throw new Error('URL de tweet inválida');
  }
  const tweetId = tweetIdMatch[1];

  console.log(`Extrayendo thread del tweet: ${tweetId}...`);

  // Obtener el tweet principal
  const mainTweet = await scraper.getTweet(tweetId);
  if (!mainTweet) {
    throw new Error('No se pudo obtener el tweet');
  }

  console.log(`✓ Tweet principal obtenido de @${mainTweet.username}`);
  console.log(`  Contenido: ${mainTweet.text?.substring(0, 100)}...`);

  // Estructura para almacenar todos los tweets
  const allTweets: TweetData[] = [];

  // Agregar tweet principal
  allTweets.push({
    id: tweetId,
    author: mainTweet.username || 'unknown',
    content: mainTweet.text || '',
    createdAt: mainTweet.timeParsed?.toISOString() || new Date().toISOString(),
    likes: mainTweet.likes || 0,
    retweets: mainTweet.retweets || 0,
    replies: mainTweet.replies || 0,
    depth: 0
  });

  // Función recursiva para obtener respuestas
  async function getReplies(tweetId: string, depth: number = 1, maxDepth: number = 5): Promise<void> {
    if (depth > maxDepth) return;

    console.log(`  Buscando respuestas (profundidad ${depth})...`);

    try {
      // Obtener respuestas del tweet
      const searchQuery = `conversation_id:${tweetId}`;
      const replies = scraper.searchTweets(searchQuery, 100);

      let count = 0;
      for await (const reply of replies) {
        if (reply.id === tweetId) continue; // Saltar el tweet original

        count++;
        allTweets.push({
          id: reply.id || '',
          author: reply.username || 'unknown',
          content: reply.text || '',
          createdAt: reply.timeParsed?.toISOString() || new Date().toISOString(),
          likes: reply.likes || 0,
          retweets: reply.retweets || 0,
          replies: reply.replies || 0,
          depth: depth
        });

        // Recursivamente obtener respuestas de esta respuesta
        if (reply.id) {
          await getReplies(reply.id, depth + 1, maxDepth);
        }
      }

      console.log(`    ✓ Encontradas ${count} respuestas en profundidad ${depth}`);
    } catch (error) {
      console.error(`    ✗ Error obteniendo respuestas: ${error}`);
    }
  }

  // Obtener todas las respuestas (hasta profundidad 3)
  await getReplies(tweetId, 1, 3);

  // Guardar resultados
  const outputDir = path.join(process.cwd(), 'output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outputFile = path.join(outputDir, `tweet-thread-${tweetId}-${timestamp}.json`);

  fs.writeFileSync(outputFile, JSON.stringify(allTweets, null, 2));
  console.log(`\n✓ Resultados guardados en: ${outputFile}`);
  console.log(`  Total de tweets extraídos: ${allTweets.length}`);

  // Generar resumen de opiniones
  const summary = generateSummary(allTweets);
  const summaryFile = path.join(outputDir, `tweet-summary-${tweetId}-${timestamp}.md`);
  fs.writeFileSync(summaryFile, summary);
  console.log(`✓ Resumen generado en: ${summaryFile}`);

  // Logout
  if (username && password) {
    await scraper.logout();
  }
}

function generateSummary(tweets: TweetData[]): string {
  let summary = `# Resumen del Thread de Twitter\n\n`;
  summary += `**Total de tweets:** ${tweets.length}\n\n`;

  // Tweet principal
  const mainTweet = tweets[0];
  summary += `## Tweet Principal\n\n`;
  summary += `- **Autor:** @${mainTweet.author}\n`;
  summary += `- **Fecha:** ${mainTweet.createdAt}\n`;
  summary += `- **Contenido:** ${mainTweet.content}\n`;
  summary += `- **Estadísticas:** ${mainTweet.likes} likes, ${mainTweet.retweets} retweets, ${mainTweet.replies} respuestas\n\n`;

  // Agrupar por profundidad
  const byDepth: { [key: number]: TweetData[] } = {};
  tweets.forEach(tweet => {
    if (!byDepth[tweet.depth]) byDepth[tweet.depth] = [];
    byDepth[tweet.depth].push(tweet);
  });

  // Opiniones (respuestas)
  summary += `## Opiniones y Respuestas\n\n`;

  for (let depth = 1; depth <= Math.max(...tweets.map(t => t.depth)); depth++) {
    const tweetsAtDepth = byDepth[depth] || [];
    if (tweetsAtDepth.length === 0) continue;

    summary += `### Nivel ${depth} (${tweetsAtDepth.length} respuestas)\n\n`;

    // Ordenar por likes para mostrar las más relevantes primero
    const sorted = tweetsAtDepth.sort((a, b) => b.likes - a.likes);

    sorted.slice(0, 10).forEach((tweet, index) => {
      summary += `${index + 1}. **@${tweet.author}** (${tweet.likes} likes)\n`;
      summary += `   ${tweet.content.substring(0, 200)}${tweet.content.length > 200 ? '...' : ''}\n\n`;
    });

    if (tweetsAtDepth.length > 10) {
      summary += `   _(y ${tweetsAtDepth.length - 10} respuestas más)_\n\n`;
    }
  }

  // Autores más activos
  const authorCounts: { [key: string]: number } = {};
  tweets.forEach(tweet => {
    authorCounts[tweet.author] = (authorCounts[tweet.author] || 0) + 1;
  });

  const topAuthors = Object.entries(authorCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  summary += `## Autores Más Activos\n\n`;
  topAuthors.forEach(([author, count], index) => {
    summary += `${index + 1}. @${author} - ${count} tweets\n`;
  });

  return summary;
}

// Ejecutar
const tweetUrl = process.argv[2] || 'https://x.com/Dwriteway/status/1991025255859544564';
console.log(`Iniciando extracción de: ${tweetUrl}\n`);

extractTweetThread(tweetUrl)
  .then(() => {
    console.log('\n✓ Extracción completada exitosamente!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n✗ Error durante la extracción:', error);
    process.exit(1);
  });
