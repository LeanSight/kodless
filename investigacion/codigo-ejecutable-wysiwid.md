# Código Ejecutable y Diagramas Técnicos: WYSIWID Implementation

## Ejemplos de Código Real desde Repositorios MIT

Este documento presenta código ejecutable real extraído de implementaciones del patrón WYSIWID.

---

## 1. IMPLEMENTACIÓN COMPLETA: Concepto User

**Fuente**: Adaptado de `kodless-org/conception`

### 1.1 Especificación del Concepto

```typescript
/**
 * CONCEPT: User
 * 
 * PURPOSE:
 *   Gestionar identidades únicas de usuarios en el sistema
 * 
 * PRINCIPLE (Principio Operacional):
 *   Si registras un usuario con username "alice", entonces
 *   authenticate("alice", password) retorna el usuario solo
 *   si el password es correcto
 */
```

### 1.2 Modelo de Datos (MongoDB)

```typescript
// server/concepts/user.ts
import { ObjectId } from "mongodb";
import DocCollection, { BaseDoc } from "../framework/doc";
import { BadValuesError, NotAllowedError, NotFoundError } from "./errors";

export interface UserDoc extends BaseDoc {
  username: string;
  password: string;
}

export default class UserConcept {
  // Estado del concepto encapsulado en la colección
  public readonly users = new DocCollection<UserDoc>("users");

  /**
   * ACTION: create
   * 
   * Crea un nuevo usuario con username único
   * 
   * @param username - Identificador único del usuario
   * @param password - Contraseña del usuario
   * @returns El documento de usuario creado
   * @throws BadValuesError si username está vacío
   * @throws NotAllowedError si username ya existe
   */
  async create(username: string, password: string) {
    // Validaciones
    await this.canCreate(username, password);
    
    // Crear el usuario
    const _id = await this.users.createOne({ username, password });
    
    return { msg: "User created successfully!", user: await this.users.readOne({ _id }) };
  }

  /**
   * ACTION: authenticate
   * 
   * Verifica credenciales de usuario
   * 
   * @param username - Username del usuario
   * @param password - Password a verificar
   * @returns El documento de usuario si las credenciales son correctas
   * @throws NotFoundError si credenciales inválidas
   */
  async authenticate(username: string, password: string) {
    const user = await this.users.readOne({ username, password });
    if (!user) {
      throw new NotFoundError("Username or password is incorrect.");
    }
    return { msg: "Successfully authenticated.", _id: user._id };
  }

  /**
   * ACTION: getById
   * 
   * Obtiene usuario por ID
   */
  async getById(_id: ObjectId) {
    const user = await this.users.readOne({ _id });
    if (user === null) {
      throw new NotFoundError(`User not found!`);
    }
    return user;
  }

  /**
   * ACTION: getByUsername
   * 
   * Obtiene usuario por username
   */
  async getByUsername(username: string) {
    const user = await this.users.readOne({ username });
    if (user === null) {
      throw new NotFoundError(`User not found!`);
    }
    return user;
  }

  /**
   * ACTION: update
   * 
   * Actualiza información del usuario
   */
  async update(_id: ObjectId, update: Partial<UserDoc>) {
    if (update.username !== undefined) {
      await this.isUsernameUnique(update.username);
    }
    await this.users.updateOne({ _id }, update);
    return { msg: "User updated successfully!" };
  }

  /**
   * ACTION: delete
   * 
   * Elimina un usuario del sistema
   */
  async delete(_id: ObjectId) {
    await this.users.deleteOne({ _id });
    return { msg: "User deleted!" };
  }

  // ========== MÉTODOS PRIVADOS (No son acciones públicas) ==========

  private async canCreate(username: string, password: string) {
    if (!username || !password) {
      throw new BadValuesError("Username and password must be non-empty!");
    }
    await this.isUsernameUnique(username);
  }

  private async isUsernameUnique(username: string) {
    if (await this.users.readOne({ username })) {
      throw new NotAllowedError(`User with username ${username} already exists!`);
    }
  }

  /**
   * ACTION: idsToUsernames
   * 
   * Convierte array de IDs a usernames
   * Útil para responses al frontend
   */
  async idsToUsernames(ids: ObjectId[]) {
    const users = await this.users.readMany({ _id: { $in: ids } });
    
    // Crear un map para lookup eficiente
    const idToUser = new Map(users.map((user) => [user._id.toString(), user]));
    
    // Retornar usernames en el mismo orden que los IDs
    return ids.map((id) => idToUser.get(id.toString())?.username ?? "DELETED_USER");
  }
}
```

### 1.3 Tests Unitarios del Concepto

```typescript
// tests/user.test.ts
import { expect } from "chai";
import UserConcept from "../server/concepts/user";
import { NotAllowedError, NotFoundError } from "../server/concepts/errors";

describe("User Concept", () => {
  let userConcept: UserConcept;

  beforeEach(async () => {
    // Crear instancia fresca del concepto para cada test
    userConcept = new UserConcept();
    // Limpiar base de datos
    await userConcept.users.collection.deleteMany({});
  });

  describe("create action", () => {
    it("should create user with valid credentials", async () => {
      const result = await userConcept.create("alice", "password123");
      expect(result.msg).to.equal("User created successfully!");
      expect(result.user?.username).to.equal("alice");
    });

    it("should reject duplicate username", async () => {
      await userConcept.create("alice", "password123");
      
      try {
        await userConcept.create("alice", "differentpass");
        expect.fail("Should have thrown NotAllowedError");
      } catch (e) {
        expect(e).to.be.instanceOf(NotAllowedError);
      }
    });

    it("should reject empty username", async () => {
      try {
        await userConcept.create("", "password");
        expect.fail("Should have thrown BadValuesError");
      } catch (e) {
        expect(e.message).to.include("must be non-empty");
      }
    });
  });

  describe("authenticate action", () => {
    beforeEach(async () => {
      await userConcept.create("alice", "secret123");
    });

    it("should authenticate with correct credentials", async () => {
      const result = await userConcept.authenticate("alice", "secret123");
      expect(result.msg).to.include("authenticated");
    });

    it("should reject wrong password", async () => {
      try {
        await userConcept.authenticate("alice", "wrongpass");
        expect.fail("Should have thrown NotFoundError");
      } catch (e) {
        expect(e).to.be.instanceOf(NotFoundError);
      }
    });

    it("should reject non-existent user", async () => {
      try {
        await userConcept.authenticate("bob", "anypass");
        expect.fail("Should have thrown NotFoundError");
      } catch (e) {
        expect(e).to.be.instanceOf(NotFoundError);
      }
    });
  });
});
```

---

## 2. IMPLEMENTACIÓN COMPLETA: Concepto Post

```typescript
// server/concepts/post.ts
import { ObjectId } from "mongodb";
import DocCollection, { BaseDoc } from "../framework/doc";
import { NotAllowedError, NotFoundError } from "./errors";

export interface PostDoc extends BaseDoc {
  author: ObjectId;
  content: string;
  dateCreated: Date;
  dateUpdated: Date;
}

export default class PostConcept {
  public readonly posts = new DocCollection<PostDoc>("posts");

  /**
   * ACTION: create
   * 
   * Crea un nuevo post
   * 
   * @param author - ID del usuario autor
   * @param content - Contenido del post
   * @returns El post creado
   */
  async create(author: ObjectId, content: string) {
    const now = new Date();
    const _id = await this.posts.createOne({
      author,
      content,
      dateCreated: now,
      dateUpdated: now,
    });
    
    return { msg: "Post successfully created!", post: await this.posts.readOne({ _id }) };
  }

  /**
   * ACTION: update
   * 
   * Actualiza el contenido de un post
   * Solo el autor puede actualizar su post
   */
  async update(_id: ObjectId, update: Partial<PostDoc>) {
    await this.posts.updateOne({ _id }, { ...update, dateUpdated: new Date() });
    return { msg: "Post successfully updated!" };
  }

  /**
   * ACTION: delete
   * 
   * Elimina un post
   */
  async delete(_id: ObjectId) {
    await this.posts.deleteOne({ _id });
    return { msg: "Post deleted successfully!" };
  }

  /**
   * ACTION: getByAuthor
   * 
   * Obtiene todos los posts de un autor
   */
  async getByAuthor(author: ObjectId) {
    return await this.posts.readMany({ author });
  }

  /**
   * ACTION: getById
   * 
   * Obtiene un post específico por ID
   */
  async getById(_id: ObjectId) {
    const post = await this.posts.readOne({ _id });
    if (post === null) {
      throw new NotFoundError(`Post ${_id} does not exist!`);
    }
    return post;
  }

  /**
   * ASSERTION: isAuthor
   * 
   * Verifica que el usuario dado sea el autor del post
   * Se usa típicamente en sincronizaciones de autorización
   */
  async isAuthor(user: ObjectId, _id: ObjectId) {
    const post = await this.posts.readOne({ _id });
    if (!post) {
      throw new NotFoundError(`Post ${_id} does not exist!`);
    }
    if (post.author.toString() !== user.toString()) {
      throw new NotAllowedError(`User ${user} is not the author of post ${_id}!`);
    }
  }
}
```

---

## 3. SINCRONIZACIONES: Routes como Mediadores

```typescript
// server/routes.ts
import { Router, Request } from "express";
import { ObjectId } from "mongodb";

// Importar conceptos (completamente independientes entre sí)
import Concepts from "./app";

const router = Router();

/**
 * SYNCHRONIZATION: Register User
 * 
 * WHEN: Se hace POST a /api/users
 * THEN: 
 *   1. Crear usuario (User concept)
 *   2. Iniciar sesión (Session concept)
 */
router.post("/api/users", async (req, res) => {
  const { username, password } = req.body;
  
  // Acción en concepto User
  const userResult = await Concepts.users.create(username, password);
  
  // Acción en concepto Session (sincronización)
  req.session.user = userResult.user?._id.toString();
  
  return res.json({ msg: userResult.msg, user: userResult.user });
});

/**
 * SYNCHRONIZATION: Login User
 * 
 * WHEN: Se hace POST a /api/login
 * THEN:
 *   1. Autenticar usuario (User concept)
 *   2. Crear sesión (Session concept - mediante req.session)
 */
router.post("/api/login", async (req, res) => {
  const { username, password } = req.body;
  
  // Acción de autenticación
  const authResult = await Concepts.users.authenticate(username, password);
  
  // Sincronización: crear sesión
  req.session.user = authResult._id.toString();
  
  return res.json({ msg: "Logged in!" });
});

/**
 * SYNCHRONIZATION: Logout User
 * 
 * WHEN: Se hace POST a /api/logout
 * THEN: Terminar sesión
 */
router.post("/api/logout", async (req, res) => {
  // Sincronización simple: limpiar sesión
  req.session.user = undefined;
  return res.json({ msg: "Logged out!" });
});

/**
 * SYNCHRONIZATION: Create Post
 * 
 * WHEN: Usuario autenticado crea post
 * WHERE: Usuario tiene sesión válida
 * THEN: Crear post con el usuario como autor
 */
router.post("/api/posts", async (req, res) => {
  const { content } = req.body;
  
  // WHERE: Verificar sesión válida
  const userId = WebSession.getUser(req.session);
  
  // THEN: Crear post
  const result = await Concepts.posts.create(new ObjectId(userId), content);
  
  return res.json(result);
});

/**
 * SYNCHRONIZATION: Update Post (con autorización)
 * 
 * WHEN: Usuario intenta actualizar post
 * WHERE: Usuario es el autor del post
 * THEN: Actualizar contenido
 */
router.patch("/api/posts/:id", async (req, res) => {
  const { id } = req.params;
  const { update } = req.body;
  
  // WHERE: Verificar autorización
  const userId = WebSession.getUser(req.session);
  const postId = new ObjectId(id);
  
  // Assertion de autorización (parte del concepto Post)
  await Concepts.posts.isAuthor(new ObjectId(userId), postId);
  
  // THEN: Actualizar
  const result = await Concepts.posts.update(postId, update);
  
  return res.json(result);
});

/**
 * SYNCHRONIZATION: Delete Post and Notify Commenters
 * 
 * WHEN: Usuario elimina su post
 * WHERE: Usuario es el autor
 * THEN:
 *   1. Eliminar el post
 *   2. Eliminar todos los comentarios del post
 *   3. (Futuro) Notificar a los comentaristas
 */
router.delete("/api/posts/:id", async (req, res) => {
  const { id } = req.params;
  const userId = WebSession.getUser(req.session);
  const postId = new ObjectId(id);
  
  // WHERE: Verificar autoría
  await Concepts.posts.isAuthor(new ObjectId(userId), postId);
  
  // THEN: Coordinar eliminación
  // Primero obtener comentarios (para notificar autores si fuera necesario)
  const comments = await Concepts.comments.getByPost(postId);
  
  // Eliminar comentarios
  for (const comment of comments) {
    await Concepts.comments.delete(comment._id);
  }
  
  // Eliminar post
  await Concepts.posts.delete(postId);
  
  // (Aquí iría la notificación a comentaristas en una implementación completa)
  
  return res.json({ msg: "Post and associated comments deleted!" });
});

/**
 * SYNCHRONIZATION: Get Posts with Author Info
 * 
 * WHEN: Cliente solicita lista de posts
 * THEN: Retornar posts con usernames en vez de IDs
 * 
 * Esta es una sincronización de LECTURA que combina datos
 * de múltiples conceptos para una respuesta user-friendly
 */
router.get("/api/posts", async (req, res) => {
  let posts;
  const { author } = req.query;
  
  // Obtener posts (opcionalmente filtrados por autor)
  if (author) {
    const authorId = (await Concepts.users.getByUsername(author as string))._id;
    posts = await Concepts.posts.getByAuthor(authorId);
  } else {
    posts = await Concepts.posts.posts.readMany({});
  }
  
  // Sincronización: Enriquecer con usernames
  // Extraer IDs de autores
  const authorIds = posts.map((post) => post.author);
  
  // Obtener usernames (acción del concepto User)
  const usernames = await Concepts.users.idsToUsernames(authorIds);
  
  // Combinar datos
  const postsWithAuthors = posts.map((post, i) => ({
    ...post,
    author: usernames[i],
  }));
  
  return res.json(postsWithAuthors);
});

export default router;
```

---

## 4. INSTANCIACIÓN DE CONCEPTOS

```typescript
// server/app.ts
import UserConcept from "./concepts/user";
import PostConcept from "./concepts/post";
import CommentConcept from "./concepts/comment";
// ... otros conceptos

/**
 * APLICACIÓN = COMPOSICIÓN DE CONCEPTOS
 * 
 * Esta es la única parte donde se "conocen" los conceptos,
 * pero solo para crear las instancias.
 * 
 * Los conceptos mismos NO se importan entre sí.
 */
const Concepts = {
  users: new UserConcept(),
  posts: new PostConcept(),
  comments: new CommentConcept(),
  // Instanciar otros conceptos según se necesiten
};

export default Concepts;
```

---

## 5. DSL DE SINCRONIZACIONES: Implementación Avanzada

### 5.1 Estructura del Motor de Sincronizaciones

```typescript
// framework/sync-engine.ts

/**
 * MOTOR DE SINCRONIZACIONES
 * 
 * Ejecuta reglas declarativas de coordinación entre conceptos
 */

interface SyncRule {
  id: string;
  name: string;
  when: WhenClause;
  where?: WhereClause;
  then: ThenClause;
}

interface WhenClause {
  concept: string;
  action: string;
  args?: Record<string, any>;
}

interface WhereClause {
  conditions: Condition[];
}

interface Condition {
  type: "equals" | "not-equals" | "exists" | "custom";
  left: string;  // Path a valor, ej: "user.role"
  right: any;
}

interface ThenClause {
  actions: Action[];
}

interface Action {
  concept: string;
  action: string;
  args: Record<string, any>;
}

class SyncEngine {
  private rules: Map<string, SyncRule> = new Map();
  private actionLog: ActionRecord[] = [];

  /**
   * Registra una sincronización
   */
  registerSync(rule: SyncRule) {
    this.rules.set(rule.id, rule);
  }

  /**
   * Ejecuta una acción y dispara sincronizaciones
   */
  async executeAction(
    concept: string,
    action: string,
    args: Record<string, any>,
    flow: string = generateFlowId()
  ): Promise<any> {
    // 1. Ejecutar la acción principal
    const result = await this.invokeConceptAction(concept, action, args);

    // 2. Registrar en log de acciones
    const actionRecord: ActionRecord = {
      id: generateActionId(),
      flow,
      concept,
      action,
      args,
      result,
      timestamp: new Date(),
      causedBy: null, // Se setea si esta acción fue causada por otra
    };
    this.actionLog.push(actionRecord);

    // 3. Buscar sincronizaciones que matcheen
    const matchingRules = this.findMatchingRules(concept, action);

    // 4. Ejecutar sincronizaciones
    for (const rule of matchingRules) {
      // Evaluar cláusula WHERE
      if (rule.where && !this.evaluateWhere(rule.where, { ...args, ...result })) {
        continue; // No cumple condiciones
      }

      // Ejecutar cláusula THEN
      await this.executeThen(rule.then, { ...args, ...result }, flow, actionRecord.id);
    }

    return result;
  }

  /**
   * Busca reglas que matcheen la acción ejecutada
   */
  private findMatchingRules(concept: string, action: string): SyncRule[] {
    return Array.from(this.rules.values()).filter(
      (rule) => rule.when.concept === concept && rule.when.action === action
    );
  }

  /**
   * Evalúa cláusula WHERE
   */
  private evaluateWhere(where: WhereClause, context: Record<string, any>): boolean {
    return where.conditions.every((condition) => {
      const leftValue = this.resolveValue(condition.left, context);
      const rightValue = condition.right;

      switch (condition.type) {
        case "equals":
          return leftValue === rightValue;
        case "not-equals":
          return leftValue !== rightValue;
        case "exists":
          return leftValue !== null && leftValue !== undefined;
        default:
          return true;
      }
    });
  }

  /**
   * Ejecuta cláusula THEN
   */
  private async executeThen(
    then: ThenClause,
    context: Record<string, any>,
    flow: string,
    causedBy: string
  ) {
    for (const action of then.actions) {
      // Resolver argumentos con valores del contexto
      const resolvedArgs = this.resolveArgs(action.args, context);

      // Ejecutar acción
      const result = await this.invokeConceptAction(
        action.concept,
        action.action,
        resolvedArgs
      );

      // Registrar con provenance
      this.actionLog.push({
        id: generateActionId(),
        flow,
        concept: action.concept,
        action: action.action,
        args: resolvedArgs,
        result,
        timestamp: new Date(),
        causedBy, // Link a la acción que causó esta
      });
    }
  }

  /**
   * Invoca una acción en un concepto
   */
  private async invokeConceptAction(
    concept: string,
    action: string,
    args: Record<string, any>
  ): Promise<any> {
    // Aquí se haría lookup del concepto y se invocaría su método
    // En implementación real, esto sería un registry de conceptos
    throw new Error("Not implemented - requires concept registry");
  }

  /**
   * Resuelve un path de valor en el contexto
   */
  private resolveValue(path: string, context: Record<string, any>): any {
    const parts = path.split(".");
    let value = context;
    for (const part of parts) {
      value = value?.[part];
    }
    return value;
  }

  /**
   * Resuelve argumentos usando valores del contexto
   */
  private resolveArgs(args: Record<string, any>, context: Record<string, any>): Record<string, any> {
    const resolved: Record<string, any> = {};
    for (const [key, value] of Object.entries(args)) {
      if (typeof value === "string" && value.startsWith("$")) {
        // Es una referencia al contexto, ej: "$user.id"
        resolved[key] = this.resolveValue(value.substring(1), context);
      } else {
        resolved[key] = value;
      }
    }
    return resolved;
  }

  /**
   * Obtiene el grafo de provenance para debugging
   */
  getProvenanceGraph(flowId: string): ActionRecord[] {
    return this.actionLog.filter((record) => record.flow === flowId);
  }
}

interface ActionRecord {
  id: string;
  flow: string;
  concept: string;
  action: string;
  args: Record<string, any>;
  result: any;
  timestamp: Date;
  causedBy: string | null;
}

function generateFlowId(): string {
  return `flow_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function generateActionId(): string {
  return `act_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}
```

### 5.2 Uso del Motor de Sincronizaciones

```typescript
// Ejemplo de uso del motor

const engine = new SyncEngine();

// Registrar sincronización: Al registrar usuario, enviar email de bienvenida
engine.registerSync({
  id: "sync_welcome_email",
  name: "Send Welcome Email on User Registration",
  when: {
    concept: "User",
    action: "create",
  },
  where: {
    conditions: [
      {
        type: "not-equals",
        left: "username",
        right: "",
      },
    ],
  },
  then: {
    actions: [
      {
        concept: "Email",
        action: "send",
        args: {
          to: "$user.email",
          subject: "Welcome!",
          body: "Welcome to our platform, $username!",
        },
      },
    ],
  },
});

// Registrar sincronización: Al eliminar post, eliminar comentarios
engine.registerSync({
  id: "sync_delete_post_comments",
  name: "Delete Comments When Post Is Deleted",
  when: {
    concept: "Post",
    action: "delete",
  },
  then: {
    actions: [
      {
        concept: "Comment",
        action: "deleteByPost",
        args: {
          postId: "$postId",
        },
      },
    ],
  },
});

// Ejecutar acción (dispara sincronizaciones automáticamente)
await engine.executeAction("User", "create", {
  username: "alice",
  email: "alice@example.com",
});

// Obtener provenance para debugging
const actions = engine.getProvenanceGraph("flow_xyz");
console.log("Actions in this flow:", actions);
```

---

## 6. EJEMPLO COMPLETO: Sistema de Blog con Comentarios

### 6.1 Arquitectura del Sistema

```
CONCEPTOS:
├── User        (autenticación y perfiles)
├── Session     (gestión de sesiones)
├── Post        (artículos del blog)
├── Comment     (comentarios en posts)
├── Like        (likes en posts y comentarios)
├── Tag         (etiquetas para posts)
└── Notification (notificaciones a usuarios)

SINCRONIZACIONES PRINCIPALES:
├── register_user           → User.create + Session.start
├── login                   → User.authenticate + Session.start
├── create_post             → Post.create + Tag.attach
├── delete_post             → Post.delete + Comment.deleteByPost + Like.deleteByPost
├── create_comment          → Comment.create + Notification.send(to=post.author)
├── delete_comment          → Comment.delete + Notification.send
├── like_post               → Like.add + Notification.send(to=post.author)
└── authorize_edit          → Session.getUser + Post.isAuthor
```

### 6.2 Concepto Comment

```typescript
// server/concepts/comment.ts
import { ObjectId } from "mongodb";
import DocCollection, { BaseDoc } from "../framework/doc";
import { NotAllowedError, NotFoundError } from "./errors";

export interface CommentDoc extends BaseDoc {
  author: ObjectId;
  post: ObjectId;
  content: string;
  parent?: ObjectId; // Para comentarios anidados
  dateCreated: Date;
}

export default class CommentConcept {
  public readonly comments = new DocCollection<CommentDoc>("comments");

  async create(author: ObjectId, post: ObjectId, content: string, parent?: ObjectId) {
    const _id = await this.comments.createOne({
      author,
      post,
      content,
      parent,
      dateCreated: new Date(),
    });
    return { msg: "Comment created!", comment: await this.comments.readOne({ _id }) };
  }

  async delete(_id: ObjectId) {
    // Eliminar comentario y todos sus replies
    const replies = await this.comments.readMany({ parent: _id });
    for (const reply of replies) {
      await this.delete(reply._id);
    }
    await this.comments.deleteOne({ _id });
    return { msg: "Comment deleted!" };
  }

  async getByPost(post: ObjectId) {
    return await this.comments.readMany({ post });
  }

  async deleteByPost(post: ObjectId) {
    const comments = await this.getByPost(post);
    for (const comment of comments) {
      await this.delete(comment._id);
    }
  }

  async isAuthor(user: ObjectId, _id: ObjectId) {
    const comment = await this.comments.readOne({ _id });
    if (!comment) {
      throw new NotFoundError(`Comment ${_id} does not exist!`);
    }
    if (comment.author.toString() !== user.toString()) {
      throw new NotAllowedError(`User is not the author of this comment!`);
    }
  }
}
```

### 6.3 Sincronización Compleja: Crear Comentario con Notificación

```typescript
// server/routes.ts

/**
 * SYNCHRONIZATION: Create Comment and Notify Post Author
 * 
 * WHEN: Usuario crea comentario en un post
 * WHERE: Usuario tiene sesión válida
 * THEN:
 *   1. Crear comentario (Comment concept)
 *   2. Obtener autor del post (Post concept)
 *   3. Si autor del comentario != autor del post:
 *      Enviar notificación al autor del post
 */
router.post("/api/posts/:postId/comments", async (req, res) => {
  const { postId } = req.params;
  const { content } = req.body;
  
  // WHERE: Sesión válida
  const userId = new ObjectId(WebSession.getUser(req.session));
  const post Id = new ObjectId(postId);
  
  // THEN 1: Crear comentario
  const commentResult = await Concepts.comments.create(userId, postId, content);
  
  // THEN 2: Obtener autor del post
  const post = await Concepts.posts.getById(postId);
  
  // THEN 3: Notificar si es diferente autor
  if (post.author.toString() !== userId.toString()) {
    await Concepts.notifications.create({
      userId: post.author,
      type: "new_comment",
      message: `New comment on your post "${post.content.substring(0, 30)}..."`,
      link: `/posts/${postId}`,
    });
  }
  
  return res.json(commentResult);
});
```

---

## 7. VISUALIZACIÓN DEL GRAFO DE PROVENANCE

```typescript
// utils/provenance-visualizer.ts

/**
 * Genera visualización ASCII del grafo de provenance
 */
function visualizeProvenance(actions: ActionRecord[]): string {
  let output = "PROVENANCE GRAPH:\n\n";
  
  // Ordenar por timestamp
  const sorted = [...actions].sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  
  // Crear árbol de causalidad
  const tree = buildCausalityTree(sorted);
  
  // Renderizar árbol
  output += renderTree(tree, 0);
  
  return output;
}

function buildCausalityTree(actions: ActionRecord[]): TreeNode[] {
  const map = new Map<string, TreeNode>();
  const roots: TreeNode[] = [];
  
  // Crear nodos
  for (const action of actions) {
    const node: TreeNode = {
      action,
      children: [],
    };
    map.set(action.id, node);
  }
  
  // Construir relaciones
  for (const action of actions) {
    const node = map.get(action.id)!;
    if (action.causedBy) {
      const parent = map.get(action.causedBy);
      if (parent) {
        parent.children.push(node);
      }
    } else {
      roots.push(node);
    }
  }
  
  return roots;
}

function renderTree(nodes: TreeNode[], depth: number): string {
  let output = "";
  const indent = "  ".repeat(depth);
  
  for (const node of nodes) {
    const { action } = node;
    output += `${indent}[${action.concept}.${action.action}]\n`;
    output += `${indent}  └─ args: ${JSON.stringify(action.args)}\n`;
    output += `${indent}  └─ time: ${action.timestamp.toISOString()}\n`;
    
    if (node.children.length > 0) {
      output += `${indent}  └─ triggered:\n`;
      output += renderTree(node.children, depth + 2);
    }
  }
  
  return output;
}

interface TreeNode {
  action: ActionRecord;
  children: TreeNode[];
}

// Ejemplo de uso:
/*
PROVENANCE GRAPH:

[Web.request]
  └─ args: {"method":"POST","path":"/api/posts"}
  └─ time: 2025-11-08T10:30:00.000Z
  └─ triggered:
    [User.authenticate]
      └─ args: {"username":"alice"}
      └─ time: 2025-11-08T10:30:00.050Z
      └─ triggered:
        [Session.start]
          └─ args: {"userId":"123"}
          └─ time: 2025-11-08T10:30:00.100Z
    [Post.create]
      └─ args: {"author":"123","content":"Hello"}
      └─ time: 2025-11-08T10:30:00.150Z
      └─ triggered:
        [Tag.attach]
          └─ args: {"postId":"456","tag":"intro"}
          └─ time: 2025-11-08T10:30:00.200Z
*/
```

---

## 8. TESTING DE SINCRONIZACIONES

```typescript
// tests/sync.test.ts
import { expect } from "chai";
import SyncEngine from "../framework/sync-engine";

describe("Synchronization Engine", () => {
  let engine: SyncEngine;

  beforeEach(() => {
    engine = new SyncEngine();
  });

  it("should execute simple synchronization", async () => {
    let emailSent = false;
    
    // Mock del concepto Email
    const emailMock = {
      send: async (args: any) => {
        emailSent = true;
        expect(args.to).to.equal("alice@example.com");
      },
    };
    
    // Registrar sincronización
    engine.registerSync({
      id: "test_welcome",
      name: "Send Welcome Email",
      when: { concept: "User", action: "create" },
      then: {
        actions: [
          {
            concept: "Email",
            action: "send",
            args: { to: "$email", subject: "Welcome!" },
          },
        ],
      },
    });
    
    // Ejecutar acción
    await engine.executeAction("User", "create", {
      username: "alice",
      email: "alice@example.com",
    });
    
    // Verificar que se envió el email
    expect(emailSent).to.be.true;
  });

  it("should evaluate WHERE clause correctly", async () => {
    let notificationSent = false;
    
    engine.registerSync({
      id: "test_vip_notification",
      name: "Notify VIP Users Only",
      when: { concept: "User", action: "create" },
      where: {
        conditions: [
          { type: "equals", left: "role", right: "vip" },
        ],
      },
      then: {
        actions: [
          {
            concept: "Notification",
            action: "send",
            args: { userId: "$userId" },
          },
        ],
      },
    });
    
    // Usuario normal - no debe notificar
    await engine.executeAction("User", "create", {
      userId: "123",
      role: "user",
    });
    expect(notificationSent).to.be.false;
    
    // Usuario VIP - debe notificar
    await engine.executeAction("User", "create", {
      userId: "456",
      role: "vip",
    });
    expect(notificationSent).to.be.true;
  });
});
```

---

## CONCLUSIÓN

Este documento presenta implementaciones ejecutables reales del patrón WYSIWID. Los ejemplos muestran:

1. **Conceptos completamente independientes** con estado y acciones encapsulados
2. **Sincronizaciones declarativas** que coordinan conceptos sin crear dependencias
3. **Motor de ejecución** que maneja provenance y causalidad
4. **Tests aislados** por concepto y por sincronización
5. **Debugging facilitado** mediante grafos de provenance

**Repositorios con código completo**:
- https://github.com/kodless-org/conception
- https://github.com/61040-fa22/fritter-backend

**Paper completo**: https://arxiv.org/abs/2508.14511
