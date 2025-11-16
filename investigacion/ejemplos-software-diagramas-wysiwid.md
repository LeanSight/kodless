# Ejemplos de Software Reales y Diagramas: WYSIWID (What You See Is What It Does)

## Resumen Ejecutivo

Este documento presenta ejemplos concretos de software y diagramas que explican la investigación "What You See Is What It Does" de Daniel Jackson y Eagon Meng (MIT CSAIL). La propuesta central separa el software en **"concepts"** (servicios independientes) y **"synchronizations"** (reglas declarativas que los coordinan), facilitando tanto el desarrollo humano como la generación de código con LLMs.

---

## 1. ARQUITECTURA CONCEPTUAL: Diagramas y Estructura

### 1.1 Diagrama Fundamental: Concepts vs. Synchronizations

```
ARQUITECTURA TRADICIONAL (OOP/Microservicios)
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   User      │◄────►│   Article   │◄────►│  Comment    │
│   Stack     │      │   Stack     │      │   Stack     │
└─────────────┘      └─────────────┘      └─────────────┘
     │                     │                     │
     └─────────────────────┴─────────────────────┘
              (Funcionalidad fragmentada)
              
ARQUITECTURA WYSIWID
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   User      │  │  Password   │  │   Article   │  │  Comment    │
│  (Concept)  │  │  (Concept)  │  │  (Concept)  │  │  (Concept)  │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
       ▲              ▲                  ▲                ▲
       │              │                  │                │
       └──────────────┴──────────────────┴────────────────┘
                   Synchronizations
              (Reglas declarativas de coordinación)
```

**Diferencia clave**: En WYSIWID, los conceptos NO se conocen entre sí. Las sincronizaciones actúan como mediadores puros.

### 1.2 Diagrama de Estado: Ejemplo del Concepto "Group"

Basado en el ejemplo WhatsUp de Daniel Jackson:

```
CONCEPTO: Group
┌────────────────────────────────────────────────────────┐
│ Estado (State):                                        │
│   - users: Set<User>                                   │
│   - groups: Set<Group>                                 │
│   - posts: Set<Post>                                   │
│   - members: Group → Set<User>                         │
│   - postsInGroup: Group → Set<Post>                    │
│   - author: Post → User                                │
│                                                         │
│ Invariante:                                            │
│   ∀ post ∈ postsInGroup(g) : author(post) ∈ members(g)│
│                                                         │
│ Acciones (Actions):                                    │
│   - create(name: String, out g: Group)                 │
│   - delete(g: Group)                                   │
│   - join(u: User, g: Group)                            │
│   - leave(u: User, g: Group)                           │
│   - addPost(u: User, g: Group, content: String)        │
│   - reply(u: User, p: Post, content: String)           │
└────────────────────────────────────────────────────────┘
```

**Representación como diagrama ER** (Entity-Relationship):

```
     ┌──────────┐
     │   User   │
     └────┬─────┘
          │ members
          │
     ┌────▼─────┐       postsInGroup     ┌──────────┐
     │  Group   │◄─────────────────────►│   Post   │
     └──────────┘                        └────┬─────┘
                                              │ author
                                              ▼
                                         ┌──────────┐
                                         │   User   │
                                         └──────────┘
```

---

## 2. EJEMPLOS DE SOFTWARE REALES

### 2.1 Kodless: El Prototipo Original

**Repositorio**: https://github.com/kodless-org/kodless  
**Desarrollador**: Barish Namazov (MIT '24)

**Descripción**: Sistema que genera aplicaciones web completas desde prompts en lenguaje natural usando GPT-4.

**Arquitectura**:
```
┌─────────────────────────────────────────────────────┐
│               KODLESS SYSTEM                        │
├─────────────────────────────────────────────────────┤
│  Input: Natural Language Prompt                     │
│         "Create a HackerNews clone"                 │
├─────────────────────────────────────────────────────┤
│  LLM → Concept Specifications                       │
│        ├─ User concept                              │
│        ├─ Post concept                              │
│        ├─ Comment concept                           │
│        └─ Upvote concept                            │
├─────────────────────────────────────────────────────┤
│  LLM → Concept Implementations (TypeScript)         │
│        Each concept generated independently          │
├─────────────────────────────────────────────────────┤
│  Routes (HTTP Endpoints) = Synchronizations         │
│        HTTP routes coordinate concepts              │
├─────────────────────────────────────────────────────┤
│  Output: Fully functional web application           │
│          Backend: Express.js + TypeScript            │
│          Database: MongoDB                           │
│          Frontend: Custom DSL (reactive HTML)        │
└─────────────────────────────────────────────────────┘
```

**Resultados demostrados**:
- Más del 50% de reducción en tiempo de desarrollo para estudiantes MIT
- Generación exitosa de clone completo de HackerNews
- Framework modular reutilizable

### 2.2 Conception: POC de Aplicación Web Modular

**Repositorio**: https://github.com/kodless-org/conception  
**Stack**: TypeScript, Express, MongoDB, Vue

**Estructura de Directorios**:
```
conception/
├── server/
│   ├── concepts/           ← Implementaciones de conceptos
│   │   ├── user.ts
│   │   ├── post.ts
│   │   ├── comment.ts
│   │   └── errors.ts      ← Clases base de errores
│   ├── app.ts             ← Definición de app (instanciaciones)
│   ├── routes.ts          ← Routes = Synchronizations
│   ├── responses.ts       ← Formateo de respuestas
│   └── db.ts              ← Setup MongoDB
├── framework/             ← Framework mágico
└── public/                ← Cliente de pruebas
```

**Ejemplo de Código: Concepto User** (simplificado):
```typescript
// server/concepts/user.ts
import { ObjectId } from "mongodb";

export default class UserConcept {
  // Estado del concepto
  private users: Collection<UserDoc>;

  // Acciones del concepto
  async create(username: string, password: string): Promise<UserDoc> {
    // Implementación completamente independiente
    const _id = new ObjectId();
    await this.users.insertOne({ _id, username, password });
    return { _id, username, password };
  }

  async authenticate(username: string, password: string): Promise<UserDoc> {
    const user = await this.users.findOne({ username, password });
    if (!user) {
      throw new NotFoundError("Invalid credentials");
    }
    return user;
  }

  async delete(userId: ObjectId): Promise<void> {
    await this.users.deleteOne({ _id: userId });
  }
}
```

**Ejemplo de Routes (Synchronizations)**:
```typescript
// server/routes.ts
import { Router } from "express";

// Los routes actúan como sincronizaciones
router.post("/register", async (req, res) => {
  // Sync: Cuando se registra un usuario, crear User Y crear Session
  const { username, password } = req.body;
  
  // Acción en User concept
  const user = await Concepts.users.create(username, password);
  
  // Acción en Session concept (sincronización)
  const session = await Concepts.sessions.start(user._id);
  
  res.json({ user, session });
});

router.post("/login", async (req, res) => {
  // Sync: Autenticar User Y crear Session
  const { username, password } = req.body;
  
  const user = await Concepts.users.authenticate(username, password);
  const session = await Concepts.sessions.start(user._id);
  
  res.json({ session });
});
```

### 2.3 RealWorld/Conduit: Caso de Estudio del Paper

**Benchmark**: http://realworld.io  
**Aplicación**: Clone de Medium llamado "Conduit"

**Conceptos Identificados en el Paper**:
```
CONCEPTOS PRINCIPALES:
┌─────────────────────────────────────────────────────────┐
│ 1. User          - Gestión de usuarios                 │
│ 2. Password      - Autenticación                       │
│ 3. Profile       - Perfiles de usuario                 │
│ 4. Article       - Artículos/posts                     │
│ 5. Comment       - Comentarios en artículos            │
│ 6. Tag           - Etiquetas para artículos            │
│ 7. Favorite      - Marcar artículos como favoritos     │
│ 8. JWT           - Autenticación token-based           │
│ 9. Web           - Bootstrap concept para HTTP         │
└─────────────────────────────────────────────────────────┘
```

**Problema en Implementaciones Tradicionales**:

En implementaciones tradicionales de RealWorld, los investigadores encontraron:

```
VIOLACIONES DE DISEÑO ENCONTRADAS:
❌ Controladores incluyen accesos directos a DB (saltando capa modelo)
❌ Controladores acceden modelos de OTROS controladores
   Ejemplo: ArticleController accede UserModel, TagModel
❌ Routers no se limitan a sus controladores
❌ Funcionalidad de "favoriting" dividida entre User y Article
❌ Tagging no completamente encapsulado
```

**Solución con Concepts/Synchronizations**:

```
ENFOQUE WYSIWID:
✅ Cada concepto es completamente independiente
✅ Favoriting y Tagging son conceptos propios
✅ Mapeo directo: funcionalidad → concepto
✅ Sincronizaciones manejan interacciones
✅ No hay accesos cross-concept en código de conceptos
```

### 2.4 Fritter: Proyecto Educativo MIT 6.1040

**Repositorio**: https://github.com/61040-fa22/fritter-backend  
**Aplicación**: Clone de Twitter para enseñanza

**Implementación por Conceptos**:
```
CONCEPTOS EN FRITTER:
├── User (autenticación, registro)
├── Session (login sessions)
├── Freet (posts tipo tweet)
├── Follow (seguir usuarios)
├── Like (dar me gusta)
└── Refreet (retweets)

ORGANIZACIÓN DE CÓDIGO:
server/
├── user/
│   ├── model.ts      ← Esquema de datos
│   ├── collection.ts ← Lógica de negocio
│   └── router.ts     ← API endpoints
├── freet/
│   ├── model.ts
│   ├── collection.ts
│   └── router.ts
└── ...
```

---

## 3. EL DSL DE SINCRONIZACIONES

### 3.1 Sintaxis del DSL

**Estructura básica**:
```
sync <nombre_sincronización>(<parámetros>)
  when <acciones_disparadoras>
  where <condiciones>
  then <acciones_resultantes>
```

### 3.2 Ejemplos Reales de Sincronizaciones

**Ejemplo 1: Registro de Usuario**
```typescript
// Sincronización: Al registrar usuario, crear password
sync register(url: URL, username: String, password: String, out user: User)
  when Web.request(url)
  where url.path = "/register"
  then 
    User.create(username, user)
    Password.set(user, password)
```

**Ejemplo 2: Eliminar Artículo y sus Comentarios**
```typescript
// Cuando se elimina artículo, eliminar todos sus comentarios
sync deleteArticleWithComments(article: Article)
  when Article.delete(article)
  then
    for each comment in Comment.getByArticle(article):
      Comment.delete(comment)
      Notification.send(comment.author, "Your comment was deleted")
```

**Ejemplo 3: Solo el Autor Puede Editar**
```typescript
// Sincronización de autorización
sync authorizeEdit(user: User, article: Article, newContent: String)
  when Article.edit(article, newContent)
  where Article.getAuthor(article) = user
  then proceed
```

### 3.3 Diagramas del Flujo de Sincronizaciones

```
FLUJO DE EJECUCIÓN:

1. HTTP Request llega
   │
   ▼
2. Bootstrap Concept (Web) procesa request
   │
   ▼
3. Synchronization Engine busca reglas que matcheen
   │
   ├─► when clause matches?
   │   │
   │   ├─ No → Buscar siguiente sync
   │   │
   │   └─ Sí → Evaluar where clause
   │          │
   │          ├─ False → Rechazar
   │          │
   │          └─ True → Ejecutar then actions
   │                    │
   │                    ▼
4. Ejecutar acciones en conceptos
   │
   ├─► Action 1 en Concept A
   │
   ├─► Action 2 en Concept B
   │
   └─► ...
   │
   ▼
5. Engine registra provenance (trazabilidad)
   │
   ▼
6. Respuesta HTTP generada
```

---

## 4. CARACTERÍSTICAS TÉCNICAS DEL SISTEMA

### 4.1 Nomenclatura Basada en URI

**Problema**: Los nombres de argumentos en orden pueden confundir a LLMs y desarrolladores.

**Solución**: URIs fully-qualified para todos los elementos.

```
Ejemplo de URI para concepto Password:
https://essenceofsoftware.com/concepts/0.1/Password/set/password

Estructura:
https://essenceofsoftware.com/concepts/{version}/{Concept}/{action}/{argument}
                                           0.1     Password    set      password
```

**Beneficios**:
- Claridad para LLMs al generar código
- No ambigüedad en referencias
- Facilita debugging y trazabilidad

### 4.2 Manejo de Estado

**Principio de Separación**:
```
READS vs WRITES:

WRITES (Modificación):
├─ Solo vía APIs de acciones de conceptos
├─ Conceptos NO pueden escribir estado de otros
└─ Sincronizaciones invocan acciones (no modifican directamente)

READS (Consultas):
├─ GraphQL o SPARQL para queries cross-concept
├─ Sincronizaciones pueden leer múltiples conceptos
└─ Queries se ejecutan en cláusulas 'where'
```

**Ejemplo de Query Cross-Concept**:
```sparql
# SPARQL query en una sincronización
PREFIX user: <https://essenceofsoftware.com/concepts/0.1/User/>
PREFIX article: <https://essenceofsoftware.com/concepts/0.1/Article/>

SELECT ?author ?email
WHERE {
  ?article article:id "123" .
  ?article article:author ?authorId .
  ?authorId user:email ?email .
}
```

### 4.3 Provenance y Debugging

**Sistema de Trazabilidad**:
```
ACTION GRAPH (Grafo de Provenance):

[HTTP Request #1234]
       │
       ▼
[Web.request] ──sync(register)──► [User.create] ──sync(sendWelcome)──► [Email.send]
                                          │
                                          │
                                  sync(initProfile)
                                          │
                                          ▼
                                   [Profile.create]
```

**Estructura de Registro**:
```json
{
  "actionId": "act_789",
  "concept": "User",
  "action": "create",
  "timestamp": "2025-11-08T10:30:00Z",
  "flow": "flow_1234",
  "causedBy": {
    "actionId": "act_788",
    "syncId": "sync_register"
  },
  "arguments": {
    "username": "alice",
    "userId": "uuid-123"
  },
  "triggers": [
    {
      "syncId": "sync_initProfile",
      "nextAction": "act_790"
    },
    {
      "syncId": "sync_sendWelcome",
      "nextAction": "act_791"
    }
  ]
}
```

**Beneficios**:
- **Atomicidad**: Todo o nada por flow
- **Idempotencia**: Prevenir ejecuciones duplicadas
- **Debugging**: Rastrear causalidad de acciones
- **LLM-assisted debugging**: Proveer grafo a LLM para diagnóstico

---

## 5. EJEMPLOS DE CONCEPTOS COMUNES

### 5.1 Concepto: Label (de Gmail)

```
CONCEPTO: Label
┌────────────────────────────────────────────────────┐
│ Propósito: Organizar items con etiquetas          │
│                                                     │
│ Estado:                                            │
│   labels: Set<Label>                               │
│   items: Set<Item>                                 │
│   tagged: Item → Set<Label>                        │
│                                                     │
│ Acciones:                                          │
│   create(name: String, out l: Label)               │
│     labels += l                                    │
│                                                     │
│   delete(l: Label)                                 │
│     labels -= l                                    │
│     for all i where l ∈ tagged(i):                 │
│       tagged(i) -= l                               │
│                                                     │
│   attach(i: Item, l: Label)                        │
│     tagged(i) += l                                 │
│                                                     │
│   detach(i: Item, l: Label)                        │
│     tagged(i) -= l                                 │
│                                                     │
│   find(l: Label, out items: Set<Item>)             │
│     items = {i | l ∈ tagged(i)}                    │
│                                                     │
│ Principio Operacional:                             │
│   Si creas label L, adjuntas items I1, I2 a L,     │
│   entonces find(L) retorna {I1, I2}                │
└────────────────────────────────────────────────────┘
```

### 5.2 Concepto: Upvote

```
CONCEPTO: Upvote
┌────────────────────────────────────────────────────┐
│ Propósito: Usuarios votan items para darles       │
│            prominencia                             │
│                                                     │
│ Estado:                                            │
│   upvotes: Item → Int                              │
│   upvoters: Item → Set<User>                       │
│                                                     │
│ Acciones:                                          │
│   upvote(u: User, i: Item)                         │
│     require: u ∉ upvoters(i)                       │
│     upvoters(i) += u                               │
│     upvotes(i) += 1                                │
│                                                     │
│   downvote(u: User, i: Item)                       │
│     require: u ∈ upvoters(i)                       │
│     upvoters(i) -= u                               │
│     upvotes(i) -= 1                                │
│                                                     │
│   getScore(i: Item, out score: Int)                │
│     score = upvotes(i)                             │
│                                                     │
│   getTopItems(n: Int, out items: Set<Item>)        │
│     items = top n items by upvotes(i)              │
└────────────────────────────────────────────────────┘
```

### 5.3 Concepto: Session

```
CONCEPTO: Session
┌────────────────────────────────────────────────────┐
│ Propósito: Mantener estado de autenticación       │
│                                                     │
│ Estado:                                            │
│   activeSessions: Set<SessionId>                   │
│   sessionUser: SessionId → User                    │
│   lastActivity: SessionId → DateTime               │
│                                                     │
│ Acciones:                                          │
│   start(u: User, out s: SessionId)                 │
│     s = generateId()                               │
│     activeSessions += s                            │
│     sessionUser(s) = u                             │
│     lastActivity(s) = now()                        │
│                                                     │
│   end(s: SessionId)                                │
│     activeSessions -= s                            │
│     delete sessionUser(s)                          │
│     delete lastActivity(s)                         │
│                                                     │
│   getUser(s: SessionId, out u: User)               │
│     require: s ∈ activeSessions                    │
│     u = sessionUser(s)                             │
│     lastActivity(s) = now()                        │
│                                                     │
│   cleanup()  // Sistema periodico                  │
│     for s in activeSessions:                       │
│       if now() - lastActivity(s) > 30 minutes:     │
│         end(s)                                     │
└────────────────────────────────────────────────────┘
```

---

## 6. COMPARACIÓN: ANTES Y DESPUÉS

### 6.1 Ejemplo: Feature "Favoriting" en Conduit

**ANTES (Arquitectura Tradicional)**:
```
ArticleController:
  ├─ getFavoriteCount(articleId)  ← Parte en Article
  └─ ...

UserController:
  ├─ addFavorite(userId, articleId)  ← Parte en User
  ├─ getFavorites(userId)
  └─ ...

Database:
  ├─ articles table
  │   └─ favorite_count column
  └─ user_favorites table
      ├─ user_id
      └─ article_id

Problema: ¿Dónde está la funcionalidad de "favoriting"?
Respuesta: Fragmentada en múltiples lugares
```

**DESPUÉS (Arquitectura WYSIWID)**:
```
FavoriteConcept:
  Estado:
    favorites: Item → Set<User>
  
  Acciones:
    add(user, item)
    remove(user, item)
    getFavoriters(item) → Set<User>
    getFavorites(user) → Set<Item>
    getCount(item) → Int
    isFavorited(user, item) → Bool

Sincronizaciones:
  sync favoriteArticle(user, article)
    when Article.view(article)
    then 
      if Favorite.isFavorited(user, article):
        showAsFavorited()

Beneficios:
✅ Funcionalidad cohesiva y localizada
✅ Fácil de entender, testear y modificar
✅ Reutilizable para cualquier tipo de item
```

### 6.2 Diagrama Comparativo: Complejidad

```
TRADICIONAL (OOP/Microservicios):
Feature: "Comentar en artículo"

User Service ───► Article Service ───► Comment Service
   │                   │                      │
   │                   │                      │
   └───► Auth Service ◄┴──────────────────────┘
            │
            └───► Notification Service

Dependencias: 5 servicios interconectados
Líneas de comunicación: 7+
Puntos de fallo: Múltiples
Testing: Complejo (requiere mocks de todos los servicios)


WYSIWID (Concepts + Synchronizations):
Feature: "Comentar en artículo"

[User]  [Article]  [Comment]  [Auth]  [Notification]
  │         │          │         │           │
  └─────────┴──────────┴─────────┴───────────┘
              Synchronizations
              (4 reglas simples)

Dependencias: 0 (conceptos independientes)
Líneas de comunicación: 4 syncs declarativas
Puntos de fallo: Localizados por concepto
Testing: Simple (cada concepto se testea aisladamente)
```

---

## 7. GENERACIÓN CON LLMS

### 7.1 Prompts para Generar Conceptos

**Ejemplo de Prompt Mínimo**:
```
Create a concept specification for a "Comment" feature 
in a blogging platform.

Users should be able to:
- Add comments to articles
- Reply to other comments (threading)
- Delete their own comments
- View all comments on an article
```

**Output del LLM** (GPT-4):
```typescript
concept Comment
  purpose: Enable threaded discussions on articles
  
  state:
    comments: Set<CommentId>
    content: CommentId → String
    author: CommentId → UserId
    article: CommentId → ArticleId
    parent: CommentId → CommentId?
    timestamp: CommentId → DateTime
  
  actions:
    create(author: UserId, article: ArticleId, 
           content: String, parent?: CommentId, 
           out comment: CommentId)
      comment = generateId()
      comments += comment
      this.content(comment) = content
      this.author(comment) = author
      this.article(comment) = article
      this.parent(comment) = parent
      this.timestamp(comment) = now()
    
    delete(commentId: CommentId)
      require: commentId ∈ comments
      comments -= commentId
      // Delete replies recursively
      for c in comments where parent(c) = commentId:
        delete(c)
    
    getByArticle(articleId: ArticleId, out results: Set<CommentId>)
      results = {c | c ∈ comments ∧ article(c) = articleId}
    
    getReplies(commentId: CommentId, out results: Set<CommentId>)
      results = {c | c ∈ comments ∧ parent(c) = commentId}
```

### 7.2 Flujo de Generación Completa

```
PROCESO DE GENERACIÓN CON LLM:

1. ESPECIFICACIONES DE CONCEPTOS
   ├─ Prompt: "Create User concept for auth"
   ├─ LLM genera: User concept spec
   ├─ Prompt: "Create Article concept"
   └─ LLM genera: Article concept spec
   
2. IMPLEMENTACIONES DE CONCEPTOS
   ├─ Prompt: "Implement User concept in TypeScript"
   │   Context: Solo la spec de User
   ├─ LLM genera: user.ts (100-200 líneas)
   │
   ├─ Prompt: "Implement Article concept"
   │   Context: Solo la spec de Article
   └─ LLM genera: article.ts
   
3. SINCRONIZACIONES
   ├─ Prompt: "Create sync for user registration"
   │   Context: Specs de User + Password
   ├─ LLM genera: sync register(...)
   │
   ├─ Prompt: "Create sync for article deletion"
   │   Context: Specs de Article + Comment
   └─ LLM genera: sync deleteWithComments(...)
   
4. TESTING
   ├─ Cada concepto se testea independientemente
   └─ Syncs se testean con mocks de conceptos

Ventajas:
✅ Contexto pequeño (1 módulo a la vez)
✅ Menor cantidad de tokens
✅ Mayor calidad de código generado
✅ Fácil iteración y refinamiento
```

---

## 8. RECURSOS Y MATERIALES ADICIONALES

### 8.1 Repositorios de Código

| Proyecto | URL | Descripción |
|----------|-----|-------------|
| Kodless | https://github.com/kodless-org/kodless | Sistema completo de generación LLM |
| Conception | https://github.com/kodless-org/conception | POC aplicación modular |
| Fritter Backend | https://github.com/61040-fa22/fritter-backend | Proyecto educativo MIT |
| MIT 6.1040 | https://61040-fa25.github.io/ | Curso completo de diseño de software |

### 8.2 Presentaciones con Diagramas

**Presentaciones Clave de Daniel Jackson**:

1. **"Building an entire app with an LLM"** (Junio 2024)
   - Video: https://www.youtube.com/watch?v=WgOhtH3lugk
   - Contenido: Demo de Kodless, diagramas de arquitectura

2. **"What makes software work?"** (Mayo 2024)
   - Video: https://www.youtube.com/watch?v=pCr3GjdoTbg
   - Slides disponibles en página de talks
   - Contenido: Explicación visual de concepts con ejemplos

3. **"How to design software"** (Enero 2024)
   - Video: https://www.youtube.com/watch?v=HoKp93KUMko
   - Contenido: Principios de diseño conceptual

4. **"A new modularity for software"** (OOPSLA 2018 Keynote)
   - Video: https://youtu.be/YoEkXHZ6Gbg
   - Contenido: Fundamentos teóricos, comparación con OOP

### 8.3 Documentación y Tutoriales

**Sitio Web Essence of Software**: https://essenceofsoftware.com/

Tutoriales Disponibles:
- Software = Concepts
- Principles Operacionales
- Estados y Acciones de Conceptos
- **Composición y Sincronización** ← Clave para entender syncs
- Modularidad de Conceptos

### 8.4 Papers Académicos

1. **Paper Principal (SPLASH Onward! 2025)**:
   - Título: "What You See Is What It Does: A Structural Pattern for Legible Software"
   - Autores: Eagon Meng, Daniel Jackson
   - PDF: https://arxiv.org/abs/2508.14511
   - HTML: https://arxiv.org/html/2508.14511

2. **Papers Fundacionales**:
   - "Towards a Theory of Conceptual Design for Software" (Onward! 2015)
   - "Purposes, Concepts, Misfits, and a Redesign of Git" (OOPSLA 2016)
   - "Concept Design Moves" (NFM 2022)

### 8.5 Herramientas Disponibles

1. **LegibleSync Framework** (Implementación Independiente)
   - GitHub: https://github.com/mastepanoski/legiblesync
   - NPM: `@legible-sync/core`
   - Implementación TypeScript del patrón WYSIWID
   - Incluye motor de ejecución de sincronizaciones

2. **MIT 6.1040 Course Materials**
   - Repositorios de estudiantes con implementaciones
   - Ejemplos de proyectos completos
   - Plantillas de código

---

## 9. CASOS DE USO Y APLICACIONES PRÁCTICAS

### 9.1 E-Commerce: Carrito de Compras

```typescript
// CONCEPTOS INVOLUCRADOS:
// - Product
// - Cart
// - User
// - Payment
// - Order
// - Inventory

// SINCRONIZACIÓN: Checkout Process
sync checkout(user: User, cart: Cart, payment: PaymentInfo)
  when Cart.checkout(cart)
  where Cart.getUser(cart) = user
        AND Cart.isEmpty(cart) = false
  then
    // Validar inventario
    for each item in Cart.getItems(cart):
      require Inventory.isAvailable(item.product, item.quantity)
    
    // Procesar pago
    Payment.process(user, payment, Cart.getTotal(cart), out transaction)
    
    // Crear orden
    Order.create(user, Cart.getItems(cart), transaction, out order)
    
    // Actualizar inventario
    for each item in Cart.getItems(cart):
      Inventory.decrement(item.product, item.quantity)
    
    // Vaciar carrito
    Cart.clear(cart)
    
    // Notificar usuario
    Notification.send(user, "Order " + order.id + " confirmed")
```

### 9.2 Sistema de Educación Online

```typescript
// CONCEPTOS:
// - Course
// - Enrollment
// - Lesson
// - Progress
// - Certificate

// SINCRONIZACIÓN: Completar Curso
sync completeCourse(student: User, course: Course)
  when Progress.markComplete(student, course)
  where Enrollment.isEnrolled(student, course)
        AND Progress.getCompletionRate(student, course) >= 100%
  then
    // Generar certificado
    Certificate.generate(student, course, now(), out cert)
    
    // Actualizar perfil
    Profile.addAchievement(student, cert)
    
    // Notificar
    Email.send(student, "Certificate ready", cert.url)
    
    // Analytics
    Analytics.track("course_completed", {
      student: student.id,
      course: course.id,
      duration: Progress.getDuration(student, course)
    })
```

---

## 10. CONCLUSIONES Y MEJORES PRÁCTICAS

### 10.1 Principios de Diseño de Conceptos

1. **Un Propósito, Un Concepto**
   - Cada concepto debe tener exactamente UN propósito claro
   - Si tiene múltiples propósitos, dividir en conceptos separados

2. **Independencia Radical**
   - Conceptos NO deben conocerse entre sí
   - Usar polimorfismo completo (generics/templates)
   - Estado nunca compartido directamente

3. **Completitud Funcional**
   - Un concepto debe ser completo respecto a su propósito
   - Incluir todas las acciones necesarias para su función
   - No depender de otros conceptos para funcionar

4. **Reusabilidad**
   - Diseñar para uso en múltiples contextos
   - Evitar acoplamientos específicos de aplicación
   - Documentar claramente precondiciones y postcondiciones

### 10.2 Principios de Sincronizaciones

1. **Granularidad**
   - Preferir muchas syncs pequeñas sobre pocas grandes
   - Una sync por regla de negocio
   - Facilita comprensión y mantenimiento

2. **Declaratividad**
   - Expresar QUÉ debe pasar, no CÓMO
   - Usar cláusulas where para condiciones
   - Dejar implementación al motor

3. **Atomicidad**
   - Toda sync es transaccional
   - Todo o nada, nunca parcial
   - Manejo de errores consistente

4. **Trazabilidad**
   - Nombrar syncs descriptivamente
   - Registrar provenance completa
   - Facilitar debugging y auditoría

### 10.3 Trabajando con LLMs

1. **Contexto Mínimo**
   - Generar un concepto a la vez
   - Solo incluir specs necesarias
   - Evitar contexto innecesario

2. **Iteración Guiada**
   - Generar spec → Revisar → Generar código
   - Testear cada concepto aisladamente
   - Refinar basado en tests

3. **Patrones Consistentes**
   - Usar mismo estilo para todos los conceptos
   - Mantener nomenclatura consistente
   - Seguir convenciones establecidas

4. **Validación**
   - Tests unitarios por concepto
   - Tests de integración para syncs
   - Validación de invariantes

---

## APÉNDICE: Glosario de Términos

**Concept (Concepto)**  
Módulo completamente independiente que encapsula funcionalidad con propósito claro, incluyendo estado y acciones.

**Synchronization (Sincronización)**  
Regla declarativa que coordina acciones entre conceptos sin crear dependencias entre ellos.

**Action (Acción)**  
Operación que modifica el estado de un concepto o realiza consultas.

**State (Estado)**  
Datos internos de un concepto, no accesibles directamente por otros conceptos.

**Operational Principle (Principio Operacional)**  
Escenario arquetípico que muestra cómo se usa típicamente un concepto.

**Provenance (Procedencia)**  
Registro de la causalidad de acciones, qué sync causó qué acción.

**Flow (Flujo)**  
Token que identifica un conjunto de acciones causalmente relacionadas.

**Bootstrap Concept**  
Concepto especial que modela la entrada al sistema (ej. Web para HTTP requests).

**Legibility (Legibilidad)**  
Correspondencia directa entre estructura de código y comportamiento observable.

---

**Documento compilado por**: Claude (Anthropic)  
**Fecha**: Noviembre 2025  
**Fuentes**: Paper WYSIWID, repositorios MIT, presentaciones Daniel Jackson, materiales curso 6.1040
