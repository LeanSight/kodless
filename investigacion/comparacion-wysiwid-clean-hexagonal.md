# Comparación: WYSIWID vs Clean Architecture vs Hexagonal Architecture

**Fecha**: Noviembre 2025  
**Autor**: Análisis comparativo basado en investigación académica y práctica

---

## Resumen Ejecutivo

Este documento compara tres patrones arquitecturales modernos:

- **WYSIWID** (What You See Is What It Does) - MIT CSAIL, 2024
- **Clean Architecture** - Robert C. Martin (Uncle Bob), 2012
- **Hexagonal Architecture** (Ports & Adapters) - Alistair Cockburn, 2005

Aunque los tres buscan separación de responsabilidades y testabilidad, difieren fundamentalmente en su enfoque de modularidad y acoplamiento.

---

## Índice

1. [Tabla Comparativa Rápida](#1-tabla-comparativa-rápida)
2. [Conceptos Fundamentales](#2-conceptos-fundamentales)
3. [Estructura y Capas](#3-estructura-y-capas)
4. [Manejo de Dependencias](#4-manejo-de-dependencias)
5. [Ejemplo Práctico: Sistema de Blog](#5-ejemplo-práctico-sistema-de-blog)
6. [Ventajas y Desventajas](#6-ventajas-y-desventajas)
7. [Cuándo Usar Cada Una](#7-cuándo-usar-cada-una)
8. [Diagramas Comparativos](#8-diagramas-comparativos)

---

## 1. Tabla Comparativa Rápida

| Aspecto | WYSIWID | Clean Architecture | Hexagonal Architecture |
|---------|---------|-------------------|----------------------|
| **Año** | 2024 | 2012 | 2005 |
| **Autor** | Daniel Jackson (MIT) | Robert C. Martin | Alistair Cockburn |
| **Unidad básica** | Concept (módulo independiente) | Entity/Use Case | Application Core |
| **Coordinación** | Synchronizations (declarativas) | Use Cases (imperativas) | Ports & Adapters |
| **Acoplamiento** | Cero entre concepts | Bajo entre capas | Bajo entre core y adapters |
| **Dependencias** | Concepts no se conocen | Inner → Outer (nunca al revés) | Core → Ports (nunca adapters) |
| **Testabilidad** | Concepts aislados | Por capas | Core aislado |
| **Complejidad** | Baja (concepts simples) | Media (múltiples capas) | Media (ports/adapters) |
| **LLM-friendly** | ✅ Muy alto | ⚠️ Medio | ⚠️ Medio |
| **Reutilización** | ✅ Concepts portables | ⚠️ Entities reutilizables | ⚠️ Core reutilizable |

---

## 2. Conceptos Fundamentales

### 2.1 WYSIWID: Concepts + Synchronizations

**Filosofía**: Separación radical entre lógica de negocio (concepts) y coordinación (synchronizations).

**Concepts**:
- Módulos completamente independientes
- Estado propio y acciones propias
- NO conocen otros concepts
- Reutilizables en múltiples contextos

**Synchronizations**:
- Reglas declarativas que coordinan concepts
- No contienen lógica de negocio
- Actúan como "pegamento" puro

```typescript
// Concept: Completamente independiente
class User {
  private users = new Map<string, UserData>();
  
  create(username: string, email: string): UserId {
    // Lógica solo de User
  }
  
  authenticate(username: string): UserId {
    // No sabe nada de Password, Session, etc.
  }
}

// Synchronization: Coordina sin lógica
sync login(username: string, password: string) {
  userId = User.authenticate(username);
  Password.verify(userId, password);
  sessionId = Session.create(userId);
  return sessionId;
}
```

### 2.2 Clean Architecture: Capas Concéntricas

**Filosofía**: Dependencias apuntan hacia adentro, protegiendo la lógica de negocio.

**Capas** (de adentro hacia afuera):
1. **Entities**: Reglas de negocio empresariales
2. **Use Cases**: Reglas de negocio de aplicación
3. **Interface Adapters**: Conversores (Controllers, Presenters)
4. **Frameworks & Drivers**: UI, DB, Web, etc.

**Regla de Dependencia**: El código en capas internas NO puede conocer capas externas.

```typescript
// Entity: Reglas de negocio puras
class User {
  constructor(
    public id: string,
    public username: string,
    public email: string
  ) {}
  
  changeEmail(newEmail: string) {
    // Validación de negocio
    if (!this.isValidEmail(newEmail)) {
      throw new Error("Invalid email");
    }
    this.email = newEmail;
  }
}

// Use Case: Orquesta entities
class LoginUseCase {
  constructor(
    private userRepo: UserRepository,
    private authService: AuthService
  ) {}
  
  execute(username: string, password: string): Session {
    const user = this.userRepo.findByUsername(username);
    const isValid = this.authService.verify(user, password);
    if (!isValid) throw new Error("Invalid credentials");
    return this.authService.createSession(user);
  }
}
```

### 2.3 Hexagonal Architecture: Ports & Adapters

**Filosofía**: Aislar el core de la aplicación de tecnologías externas.

**Componentes**:
- **Application Core**: Lógica de negocio pura
- **Ports**: Interfaces que definen cómo comunicarse con el core
- **Adapters**: Implementaciones concretas para tecnologías específicas

**Tipos de Ports**:
- **Primary (Driving)**: Quien usa la aplicación (UI, Tests, API)
- **Secondary (Driven)**: Lo que la aplicación usa (DB, Email, etc.)

```typescript
// Port (Interface)
interface UserRepository {
  save(user: User): void;
  findById(id: string): User | null;
}

// Application Core
class UserService {
  constructor(private repo: UserRepository) {}
  
  registerUser(username: string, email: string): User {
    const user = new User(username, email);
    this.repo.save(user);
    return user;
  }
}

// Adapter: Implementación concreta
class MongoUserRepository implements UserRepository {
  save(user: User): void {
    // Código específico de MongoDB
  }
  
  findById(id: string): User | null {
    // Código específico de MongoDB
  }
}
```

---

## 3. Estructura y Capas

### 3.1 WYSIWID: Plana y Horizontal

```
┌─────────────────────────────────────────────────────┐
│              SYNCHRONIZATIONS LAYER                 │
│  (Routes, API endpoints, coordinación declarativa)  │
└─────────────────────────────────────────────────────┘
                        ↓ ↓ ↓
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  User    │  │ Password │  │  Post    │  │ Comment  │
│ Concept  │  │ Concept  │  │ Concept  │  │ Concept  │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
     ↓             ↓             ↓             ↓
┌─────────────────────────────────────────────────────┐
│                   DATABASE LAYER                    │
└─────────────────────────────────────────────────────┘
```

**Características**:
- Concepts en el mismo nivel (no hay jerarquía)
- Synchronizations coordinan sin crear dependencias
- Cada concept tiene su propia tabla/colección

### 3.2 Clean Architecture: Circular y Concéntrica

```
        ┌─────────────────────────────────┐
        │  Frameworks & Drivers (UI, DB)  │
        │  ┌───────────────────────────┐  │
        │  │  Interface Adapters       │  │
        │  │  ┌─────────────────────┐  │  │
        │  │  │   Use Cases         │  │  │
        │  │  │  ┌───────────────┐  │  │  │
        │  │  │  │   Entities    │  │  │  │
        │  │  │  └───────────────┘  │  │  │
        │  │  └─────────────────────┘  │  │
        │  └───────────────────────────┘  │
        └─────────────────────────────────┘
             ← Dependency Rule
```

**Características**:
- 4 capas concéntricas
- Dependencias apuntan hacia el centro
- Entities en el núcleo (más estables)
- Frameworks en el exterior (más volátiles)

### 3.3 Hexagonal Architecture: Hexágono Central

```
        ┌─────────────┐
        │  UI Adapter │
        └──────┬──────┘
               │ Primary Port
        ┌──────▼──────────────┐
        │                     │
  ┌─────┤  Application Core   ├─────┐
  │     │   (Business Logic)  │     │
  │     └──────┬──────────────┘     │
  │            │ Secondary Port     │
  │     ┌──────▼──────┐      ┌──────▼──────┐
  │     │ DB Adapter  │      │ Email Adapter│
  │     └─────────────┘      └─────────────┘
  │
  │ Primary Port
  │
┌─▼──────────┐
│ Test Adapter│
└────────────┘
```

**Características**:
- Core en el centro (hexágono)
- Ports definen interfaces
- Adapters implementan tecnologías
- Simetría: todos los lados son iguales

---

## 4. Manejo de Dependencias

### 4.1 WYSIWID: Cero Dependencias entre Concepts

```typescript
// ❌ PROHIBIDO: Concept no puede importar otro concept
class Post {
  create(userId: string, content: string) {
    // NO puede llamar a User.exists(userId)
  }
}

// ✅ CORRECTO: Synchronization coordina
sync createPost(userId: string, content: string) {
  User.assertExists(userId);  // Verifica en User
  postId = Post.create(content);  // Crea en Post
  Post.setAuthor(postId, userId);  // Asocia en Post
}
```

**Ventaja**: Concepts son completamente portables y reutilizables.

### 4.2 Clean Architecture: Dependency Inversion

```typescript
// ❌ PROHIBIDO: Use Case no puede depender de implementación
class LoginUseCase {
  execute(username: string, password: string) {
    const db = new MongoDatabase();  // ❌ Dependencia concreta
  }
}

// ✅ CORRECTO: Use Case depende de abstracción
interface UserRepository {
  findByUsername(username: string): User;
}

class LoginUseCase {
  constructor(private userRepo: UserRepository) {}  // ✅ Inyección
  
  execute(username: string, password: string) {
    const user = this.userRepo.findByUsername(username);
  }
}
```

**Ventaja**: Lógica de negocio independiente de frameworks.

### 4.3 Hexagonal: Ports como Contratos

```typescript
// Port: Define el contrato
interface PaymentGateway {
  charge(amount: number, cardToken: string): PaymentResult;
}

// Core: Usa el port
class OrderService {
  constructor(private payment: PaymentGateway) {}
  
  checkout(order: Order): void {
    const result = this.payment.charge(order.total, order.cardToken);
  }
}

// Adapters: Implementan el port
class StripeAdapter implements PaymentGateway {
  charge(amount: number, cardToken: string): PaymentResult {
    // Lógica específica de Stripe
  }
}

class PayPalAdapter implements PaymentGateway {
  charge(amount: number, cardToken: string): PaymentResult {
    // Lógica específica de PayPal
  }
}
```

**Ventaja**: Fácil cambiar implementaciones sin tocar el core.

---

## 5. Ejemplo Práctico: Sistema de Blog

### 5.1 WYSIWID

```typescript
// Concept: User
class UserConcept {
  private users = new Map<UserId, UserData>();
  
  create(username: string, email: string): UserId {
    const id = generateId();
    this.users.set(id, { username, email });
    return id;
  }
  
  exists(id: UserId): boolean {
    return this.users.has(id);
  }
}

// Concept: Post
class PostConcept {
  private posts = new Map<PostId, PostData>();
  
  create(title: string, content: string): PostId {
    const id = generateId();
    this.posts.set(id, { title, content, authorId: null });
    return id;
  }
  
  setAuthor(postId: PostId, authorId: UserId): void {
    const post = this.posts.get(postId);
    post.authorId = authorId;
  }
}

// Synchronization: Coordina concepts
sync createPost(userId: UserId, title: string, content: string) {
  User.assertExists(userId);
  postId = Post.create(title, content);
  Post.setAuthor(postId, userId);
  return postId;
}
```

**Estructura de archivos**:
```
src/
├── concepts/
│   ├── user.ts
│   ├── post.ts
│   └── comment.ts
├── routes.ts  (synchronizations)
└── app.ts
```

### 5.2 Clean Architecture

```typescript
// Entity (Core)
class Post {
  constructor(
    public id: string,
    public title: string,
    public content: string,
    public authorId: string
  ) {}
  
  publish(): void {
    // Lógica de negocio
  }
}

// Use Case
class CreatePostUseCase {
  constructor(
    private postRepo: PostRepository,
    private userRepo: UserRepository
  ) {}
  
  execute(request: CreatePostRequest): Post {
    const user = this.userRepo.findById(request.authorId);
    if (!user) throw new Error("User not found");
    
    const post = new Post(
      generateId(),
      request.title,
      request.content,
      user.id
    );
    
    this.postRepo.save(post);
    return post;
  }
}

// Interface Adapter (Controller)
class PostController {
  constructor(private createPost: CreatePostUseCase) {}
  
  async create(req: Request, res: Response) {
    const result = await this.createPost.execute({
      title: req.body.title,
      content: req.body.content,
      authorId: req.user.id
    });
    res.json(result);
  }
}
```

**Estructura de archivos**:
```
src/
├── domain/
│   └── entities/
│       ├── post.ts
│       └── user.ts
├── application/
│   └── use-cases/
│       ├── create-post.ts
│       └── get-post.ts
├── infrastructure/
│   ├── repositories/
│   │   ├── post-repository.ts
│   │   └── user-repository.ts
│   └── web/
│       └── controllers/
│           └── post-controller.ts
└── main.ts
```

### 5.3 Hexagonal Architecture

```typescript
// Domain (Core)
class Post {
  constructor(
    public id: string,
    public title: string,
    public content: string,
    public authorId: string
  ) {}
}

// Port (Interface)
interface PostRepository {
  save(post: Post): void;
  findById(id: string): Post | null;
}

// Application Service (Core)
class PostService {
  constructor(private postRepo: PostRepository) {}
  
  createPost(title: string, content: string, authorId: string): Post {
    const post = new Post(generateId(), title, content, authorId);
    this.postRepo.save(post);
    return post;
  }
}

// Adapter: MongoDB
class MongoPostRepository implements PostRepository {
  save(post: Post): void {
    db.collection('posts').insertOne(post);
  }
  
  findById(id: string): Post | null {
    return db.collection('posts').findOne({ id });
  }
}

// Adapter: REST API
class PostController {
  constructor(private postService: PostService) {}
  
  async create(req: Request, res: Response) {
    const post = this.postService.createPost(
      req.body.title,
      req.body.content,
      req.user.id
    );
    res.json(post);
  }
}
```

**Estructura de archivos**:
```
src/
├── domain/
│   ├── post.ts
│   └── user.ts
├── ports/
│   ├── post-repository.ts
│   └── user-repository.ts
├── application/
│   ├── post-service.ts
│   └── user-service.ts
├── adapters/
│   ├── persistence/
│   │   ├── mongo-post-repository.ts
│   │   └── mongo-user-repository.ts
│   └── web/
│       └── post-controller.ts
└── main.ts
```

---

## 6. Ventajas y Desventajas

### 6.1 WYSIWID

**✅ Ventajas**:
- **Modularidad extrema**: Concepts completamente independientes
- **LLM-friendly**: Generación incremental con contexto mínimo
- **Reutilización máxima**: Concepts portables entre proyectos
- **Simplicidad**: Menos capas, menos abstracciones
- **Testabilidad**: Cada concept se testea aisladamente
- **Mantenibilidad**: Funcionalidad localizada, fácil de encontrar
- **Debugging**: Provenance tracking integrado

**❌ Desventajas**:
- **Nuevo paradigma**: Requiere cambio de mentalidad
- **Tooling limitado**: Framework aún en desarrollo
- **Comunidad pequeña**: Menos recursos y ejemplos
- **Sincronizaciones complejas**: Pueden volverse difíciles de seguir
- **Performance**: Overhead de coordinación en algunos casos

### 6.2 Clean Architecture

**✅ Ventajas**:
- **Independencia de frameworks**: Lógica de negocio protegida
- **Testabilidad**: Cada capa se testea independientemente
- **Flexibilidad**: Fácil cambiar UI o DB sin tocar el core
- **Madurez**: Patrón bien establecido con mucha documentación
- **Comunidad grande**: Muchos ejemplos y herramientas
- **Escalabilidad**: Funciona bien en proyectos grandes

**❌ Desventajas**:
- **Complejidad**: Muchas capas y abstracciones
- **Boilerplate**: Mucho código repetitivo (interfaces, DTOs, mappers)
- **Curva de aprendizaje**: Requiere entender múltiples conceptos
- **Over-engineering**: Puede ser excesivo para proyectos pequeños
- **Acoplamiento residual**: Use Cases aún conocen Entities

### 6.3 Hexagonal Architecture

**✅ Ventajas**:
- **Aislamiento del core**: Lógica de negocio completamente independiente
- **Testabilidad**: Core se testea sin dependencias externas
- **Flexibilidad**: Fácil cambiar adapters (DB, UI, etc.)
- **Simetría**: Todos los lados se tratan igual
- **Claridad**: Separación clara entre core y tecnología

**❌ Desventajas**:
- **Complejidad**: Requiere definir ports y adapters
- **Boilerplate**: Interfaces para cada dependencia externa
- **Confusión**: Difícil decidir qué va en el core vs adapters
- **Over-engineering**: Puede ser excesivo para proyectos simples
- **Performance**: Overhead de indirección

---

## 7. Cuándo Usar Cada Una

### 7.1 Usa WYSIWID cuando:

- ✅ Estás desarrollando con LLMs (GPT-4, Claude, etc.)
- ✅ Quieres máxima reutilización de componentes
- ✅ El equipo es pequeño o está aprendiendo
- ✅ Necesitas desarrollo incremental rápido
- ✅ La aplicación es modular por naturaleza
- ✅ Quieres debugging con provenance tracking
- ❌ NO cuando: Necesitas integración con frameworks legacy complejos

**Casos de uso ideales**:
- Prototipos rápidos
- MVPs generados con LLMs
- Aplicaciones educativas
- Sistemas con conceptos bien definidos (e-commerce, redes sociales)

### 7.2 Usa Clean Architecture cuando:

- ✅ El proyecto es grande y de larga duración
- ✅ Múltiples equipos trabajando en paralelo
- ✅ Necesitas independencia total de frameworks
- ✅ Los requisitos de negocio son complejos
- ✅ El equipo tiene experiencia en arquitectura
- ✅ Necesitas múltiples interfaces (web, mobile, API)
- ❌ NO cuando: El proyecto es pequeño o tiene deadline ajustado

**Casos de uso ideales**:
- Aplicaciones empresariales
- Sistemas bancarios o financieros
- Plataformas con múltiples clientes
- Proyectos con requisitos cambiantes

### 7.3 Usa Hexagonal Architecture cuando:

- ✅ Necesitas cambiar tecnologías frecuentemente
- ✅ Quieres testear el core sin dependencias
- ✅ Múltiples formas de acceder a la aplicación (CLI, API, UI)
- ✅ El equipo entiende el patrón ports/adapters
- ✅ La lógica de negocio es compleja pero estable
- ❌ NO cuando: El proyecto es muy simple o tiene pocas integraciones

**Casos de uso ideales**:
- Sistemas con múltiples integraciones
- Aplicaciones que necesitan diferentes UIs
- Proyectos donde la tecnología cambia frecuentemente
- Sistemas que requieren alta testabilidad

---

## 8. Diagramas Comparativos

### 8.1 Flujo de una Request: Crear Post

#### WYSIWID
```
HTTP POST /posts
      ↓
Route (Synchronization)
      ↓
   ┌──────────────────┐
   │ User.exists(id)  │ ← Concept independiente
   └──────────────────┘
      ↓
   ┌──────────────────┐
   │ Post.create()    │ ← Concept independiente
   └──────────────────┘
      ↓
   ┌──────────────────┐
   │ Post.setAuthor() │ ← Concept independiente
   └──────────────────┘
      ↓
Response JSON
```

#### Clean Architecture
```
HTTP POST /posts
      ↓
Controller (Interface Adapter)
      ↓
CreatePostUseCase (Use Case)
      ↓
   ┌──────────────────┐
   │ UserRepository   │ ← Interface
   │ .findById()      │
   └──────────────────┘
      ↓
   ┌──────────────────┐
   │ Post Entity      │ ← Domain
   │ .create()        │
   └──────────────────┘
      ↓
   ┌──────────────────┐
   │ PostRepository   │ ← Interface
   │ .save()          │
   └──────────────────┘
      ↓
Response JSON
```

#### Hexagonal
```
HTTP POST /posts
      ↓
PostController (Primary Adapter)
      ↓
PostService (Application Core)
      ↓
   ┌──────────────────┐
   │ UserRepository   │ ← Port (Interface)
   │ (Secondary)      │
   └──────────────────┘
      ↓
   ┌──────────────────┐
   │ Post Domain      │ ← Core
   │ .create()        │
   └──────────────────┘
      ↓
   ┌──────────────────┐
   │ PostRepository   │ ← Port (Interface)
   │ (Secondary)      │
   └──────────────────┘
      ↓
Response JSON
```

### 8.2 Dependencias entre Componentes

#### WYSIWID: Sin Dependencias
```
User ←─┐
       │
Post ←─┼─ Synchronizations (coordinan sin acoplar)
       │
Comment ←┘

Concepts NO se conocen entre sí
```

#### Clean Architecture: Hacia Adentro
```
Frameworks → Interface Adapters → Use Cases → Entities

Dependencias apuntan hacia el centro
```

#### Hexagonal: Hacia el Core
```
UI Adapter ──→ Primary Port ──→ Application Core
                                      ↓
DB Adapter ←── Secondary Port ←──────┘

Dependencias apuntan hacia el core
```

---

## 9. Conclusiones

### Similitudes

Todos los patrones buscan:
- ✅ Separación de responsabilidades
- ✅ Testabilidad
- ✅ Independencia de tecnología
- ✅ Mantenibilidad

### Diferencias Clave

| Aspecto | WYSIWID | Clean/Hexagonal |
|---------|---------|-----------------|
| **Granularidad** | Concepts (muy finos) | Entities/Services (más gruesos) |
| **Acoplamiento** | Cero entre concepts | Bajo pero existe |
| **Coordinación** | Declarativa (syncs) | Imperativa (use cases) |
| **Complejidad** | Baja | Media-Alta |
| **LLM Generation** | Optimizado | Posible pero complejo |

### Recomendación Final

- **Proyectos nuevos con LLMs**: WYSIWID
- **Proyectos empresariales grandes**: Clean Architecture
- **Sistemas con múltiples integraciones**: Hexagonal Architecture
- **Proyectos pequeños**: Ninguna (KISS principle)

---

## 10. Referencias

### WYSIWID
- Paper: "What You See Is What It Does" (SPLASH Onward! 2024)
- Autores: Daniel Jackson, Eagon Meng (MIT CSAIL)
- Repositorio: https://github.com/kodless-org/kodless
- Paper: https://arxiv.org/abs/2508.14511

### Clean Architecture
- Libro: "Clean Architecture" - Robert C. Martin (2017)
- Blog: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- Libro: "Clean Code" - Robert C. Martin (2008)

### Hexagonal Architecture
- Paper original: Alistair Cockburn (2005)
- URL: https://alistair.cockburn.us/hexagonal-architecture/
- También conocida como: Ports and Adapters

---

**Última actualización**: Noviembre 2025  
**Autor**: Análisis comparativo basado en documentación oficial y práctica
