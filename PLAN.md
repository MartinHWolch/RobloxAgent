# RobloxAgent — Plan de Arquitectura

## Visión General

Agente AI especializado en desarrollo Roblox. No un chat genérico, sino un **desarrollador senior de Roblox** que entiende el ecosistema, la arquitectura y las mejores prácticas.

---

## 1. Base de Conocimiento (Knowledge Base)

Biblioteca curada y estructurada (~2.000–5.000 piezas de alta calidad).

### 1.1 Documentación Oficial
- API Reference
- Creator Hub
- Luau
- Networking
- DataStore / MemoryStore / MessagingService
- UI / Avatar / Animation
- Pathfinding / Terrain / Audio / Physics
- Cloud / Open Cloud / MCP
- DevForum (hilos selectos)

### 1.2 DevForum
Solo contenido de alta calidad:
- Muchos likes
- Respuestas aceptadas
- Escritos por ingenieros de Roblox
- Tutoriales reconocidos
- Mejores prácticas

Ej: *"How should I structure a large Roblox game?"*

### 1.3 GitHub
Repositorios de calidad (librerías, frameworks, utilidades):
- Knit
- Matter
- React Lua
- Fusion
- ProfileStore
- Promise
- Signal / Janitor / Trove
- Cmdr

### 1.4 Ejemplos por Categoría
Cada uno con: explicación, ventajas, desventajas, arquitectura.

| Categoría | Ejemplos |
|-----------|----------|
| Inventory | Sistema, UI, trading |
| Combat | NPC, AI, waves |
| Quests | Quest system, progression |
| Economy | Marketplace, trading, tycoon |
| Games | Tower defense, pet system, fishing, vehicle |
| Systems | Saving, matchmaking, party |
| UI | Loading screen, shop UI, inventory UI |
| Animation | Animation system |
| Infrastructure | ECS, OOP, MVC patterns |

---

## 2. Indexación del Proyecto

El agente debe construir un índice automático del proyecto Roblox.

### 2.1 Estructura
- Workspace
- ReplicatedStorage
- ServerStorage
- ServerScriptService
- StarterGui
- StarterPlayer

### 2.2 Indexar
- ModuleScripts
- LocalScripts
- Scripts
- RemoteEvents / BindableEvents
- Attributes
- Tags

### 2.3 Relaciones
```
InventoryController
       ↓
InventoryService
       ↓
   DataService
       ↓
  ProfileStore
```

---

## 3. Memoria Permanente

Reglas fijas del proyecto que persisten entre sesiones.

Ejemplos:
- "Este proyecto usa React Lua. No usar Fusion."
- "Arquitectura MVC."
- "RemoteEvents siempre prefijo `REM_`."
- "DataStores usan ProfileStore."
- "NPCs usan ECS."
- "No usar `Wait()`. Siempre `task.wait()`."
- "No crear Singletons."

---

## 4. RAG (Retrieval-Augmented Generation)

No enviar todo en el prompt. Buscar solo lo relevante.

Ejemplo:
> "Haz un sistema de mascotas."

El agente busca automáticamente:
- Pet System
- Inventory
- DataStore
- Marketplace
- UI
- Animation

Y solo envía eso al modelo.

### Vector DB
- Qdrant / ChromaDB / Postgres + pgvector
- Documento → Fragmentos → Embedding → Vector DB
- Búsqueda semántica (no por palabras clave)

---

## 5. Aprendizaje Continuo

Cada vez que el agente:
- Implementa una funcionalidad
- Corrige un bug
- Refactoriza
- Recibe feedback ("esto estuvo bien/mal")

→ se guarda como **caso resuelto** en la memoria.

Con el tiempo, consulta su propio historial de soluciones exitosas.

---

## Arquitectura General

```
                 GPT
                  │
          Orquestador
     ┌────────────┼────────────┐
     │            │            │
     ▼            ▼            ▼
 Proyecto      RAG        MCP Roblox
  Index      Knowledge      Oficial
     │            │            │
     └────────────┼────────────┘
                  │
            Genera Plan
                  │
            Ejecuta Cambios
```

---

## Stack Propuesto

- **Vector DB:** Qdrant o ChromaDB
- **Embeddings:** OpenAI text-embedding-3-small o similar
- **Orquestador:** Python (LangChain / LlamaIndex) o TypeScript
- **Roblox MCP:** Open Cloud API + Roblox MCP
- **Memoria:** SQLite + vector embeddings
