# Herramientas Disponibles Del Agente

Este documento resume las herramientas configuradas para el agente Roblox de este proyecto y ejemplos de uso.

Reglas base del agente:

- No inventar features, sistemas, assets o cambios que no fueron pedidos.
- Si hay duda o ambiguedad, preguntar antes de actuar.
- Usar RAG antes de dar recomendaciones tecnicas Roblox.
- Para cambios en Roblox Studio, inspeccionar antes, cambiar lo minimo y verificar despues.
- Los templates de genero son contexto opcional, no una lista de features obligatorias.

## Agente Principal

Archivo:

- `.opencode/agent/roblox-dev.md`

Uso:

- Agente principal para Roblox, Luau, Studio MCP, arquitectura, debugging, UI, seguridad, performance y generos de juego.

Ejemplos:

```text
/roblox Revisa este sistema de guardado y dime si puede perder datos
```

```text
/roblox Estoy haciendo un obby de backrooms con linterna y puertas falsas
```

```text
/roblox Inspecciona el place abierto y dime por que el boton de compra no funciona
```

## Skills Internas

### roblox-agent-rag

Archivo:

- `.opencode/skills/roblox-agent-rag/SKILL.md`

Uso:

- Consultar la base de conocimiento local antes de responder preguntas tecnicas Roblox.
- Citar fuentes como `creator_hub`, `engine_api`, `devforum`, `github`, `examples`.

Ejemplos:

```powershell
python -m rag query "RemoteEvent server authoritative validation" --score -k 8
```

```powershell
python -m rag query "ProfileStore session locking autosave UpdateAsync" --score -k 8
```

### roblox-agent-workflows

Archivo:

- `.opencode/skills/roblox-agent-workflows/SKILL.md`

Uso:

- UI QA.
- Playtest Runner.
- Spatial QA.
- Before/After Verification.
- Reglas para no convertir templates de genero en features automaticas.

Ejemplos:

```text
/ui-qa Revisa si el HUD actual es usable en mobile
```

```text
/playtest-qa Valida que al tocar la zona de recompensa se sume dinero una sola vez
```

```text
/spatial-qa Busca una posicion segura para un spawn cerca del lobby
```

### roblox-agent-audits

Archivo:

- `.opencode/skills/roblox-agent-audits/SKILL.md`

Uso:

- Security Audit.
- Performance Audit.
- Debug Loop.
- Code Review.
- Publish Checklist.
- Monetization Audit.
- Sharp Edges.
- Guia por generos: obby, tycoon, simulator, RPG, horror, battle royale.

Ejemplos:

```text
/security-audit Revisa todos los remotes relacionados con compras e inventario
```

```text
/performance-audit Revisa por que el juego se siente pesado en mobile
```

```text
/monetization-audit Revisa mi ProcessReceipt y los GamePasses
```

## Comandos OpenCode

Los comandos estan en `.opencode/command/`.

### General

| Comando | Uso | Ejemplo |
|---|---|---|
| `/roblox` | Entrada general para cualquier tarea Roblox | `/roblox Explica como proteger este RemoteEvent` |

### QA Y Validacion Studio

| Comando | Uso | Ejemplo |
|---|---|---|
| `/ui-qa` | Crear, revisar o validar UI Roblox | `/ui-qa Revisa el shop UI para mobile` |
| `/playtest-qa` | Validar comportamiento runtime con playtest/logs | `/playtest-qa Comprueba que el checkpoint guarde al morir` |
| `/spatial-qa` | Revisar suelo, colisiones, spawns, posicionamiento | `/spatial-qa Verifica si este NPC tiene espacio para moverse` |

### Auditorias

| Comando | Uso | Ejemplo |
|---|---|---|
| `/security-audit` | Auditar remotes, client trust y datos expuestos | `/security-audit Busca remotes sin validacion` |
| `/performance-audit` | Auditar lag, memoria, red, mobile y scripts | `/performance-audit Revisa loops y conexiones sin limpiar` |
| `/debug-loop` | Depurar errores con maximo 5 iteraciones | `/debug-loop Arregla este error de nil en DataService` |
| `/code-review` | Review de organizacion, arquitectura, calidad, seguridad y performance | `/code-review Revisa src/server/Services` |
| `/publish-checklist` | Checklist antes de publicar o lanzar update | `/publish-checklist Estoy por publicar, revisa bloqueadores` |
| `/monetization-audit` | Revisar GamePasses, Developer Products, Premium y ProcessReceipt | `/monetization-audit Revisa si este Developer Product esta bien concedido` |

### Generos

Estos comandos usan templates como contexto opcional. No agregan sistemas extra si no se piden.

| Comando | Uso | Ejemplo |
|---|---|---|
| `/obby` | Obbys, stages, hazards, checkpoints si se piden | `/obby Crea un obby de backrooms con linterna y puertas falsas` |
| `/tycoon` | Plot claiming, droppers, collectors, buttons si se piden | `/tycoon Crea solo el sistema de reclamar parcelas` |
| `/simulator` | Loops de coleccion, upgrades, zonas si se piden | `/simulator Haz un loop de recoger energia y venderla` |
| `/rpg` | Stats, quests, NPCs, combate, inventario si se piden | `/rpg Crea un sistema basico de quests sin combate` |
| `/horror` | Atmosfera, sonido, chase, eventos si se piden | `/horror Agrega luces parpadeantes y ambiente de pasillo` |
| `/battle-royale` | Match lifecycle, loot, storm, eliminaciones si se piden | `/battle-royale Crea solo el contador de jugadores vivos` |

Ejemplo de alcance correcto:

```text
/obby Estoy haciendo un obby de backrooms con linterna y puertas falsas
```

Resultado esperado:

- Si falta una decision clave, el agente pregunta.
- Puede crear o proponer linterna y puertas falsas.
- No agrega tienda, skip-stage, GamePasses, coins, pets o leaderboard salvo que se pida.

## Herramientas Roblox Studio MCP

Estas herramientas permiten inspeccionar y modificar el Studio abierto. Antes de modificar un place con varias ventanas abiertas, se debe confirmar el Studio activo.

### Estado Y Studio

| Herramienta | Uso | Ejemplo |
|---|---|---|
| `Roblox_Studio_list_roblox_studios` | Listar instancias abiertas de Studio | Verificar si hay varios places abiertos |
| `Roblox_Studio_set_active_studio` | Seleccionar Studio activo | Usar el `studio_id` correcto antes de modificar |
| `Roblox_Studio_get_studio_state` | Ver modo actual y DataModels disponibles | Saber si estamos en Edit, Client o Server |
| `Roblox_Studio_start_stop_play` | Iniciar o detener Play | Probar un cambio y volver a Edit |

Ejemplo:

```text
Antes de tocar el place, lista los Studios abiertos y confirma cual usar.
```

### Exploracion Del DataModel

| Herramienta | Uso | Ejemplo |
|---|---|---|
| `Roblox_Studio_search_game_tree` | Explorar jerarquia con filtros | Buscar todos los `RemoteEvent` |
| `Roblox_Studio_inspect_instance` | Ver propiedades, atributos e hijos | Inspeccionar `Workspace.Baseplate` |
| `Roblox_Studio_execute_luau` | Ejecutar Luau en Studio | Hacer queries que no tengan herramienta especifica |

Ejemplos:

```text
Busca todos los scripts bajo ServerScriptService y dime cuales usan MarketplaceService.
```

```lua
local remotes = {}
for _, inst in game:GetDescendants() do
    if inst:IsA("RemoteEvent") or inst:IsA("RemoteFunction") then
        table.insert(remotes, inst:GetFullName())
    end
end
return remotes
```

### Scripts

| Herramienta | Uso | Ejemplo |
|---|---|---|
| `Roblox_Studio_script_search` | Buscar scripts por nombre | Encontrar `DataService` |
| `Roblox_Studio_script_grep` | Buscar texto en todos los scripts | Buscar `OnServerEvent` |
| `Roblox_Studio_script_read` | Leer scripts completos o por rango | Leer `ServerScriptService.GameServer` |
| `Roblox_Studio_multi_edit` | Editar scripts de forma atomica | Crear o modificar un `ModuleScript` |

Ejemplos:

```text
/security-audit Busca todos los OnServerEvent y revisa si validan tipos y cooldowns
```

```text
/debug-loop Lee el stack trace, abre el script afectado y aplica el fix minimo
```

### Assets Y Creator Store

| Herramienta | Uso | Ejemplo |
|---|---|---|
| `Roblox_Studio_search_asset` | Buscar assets en Creator Store o inventarios | Buscar modelo de arbol gratuito |
| `Roblox_Studio_insert_asset` | Insertar asset por ID | Insertar un modelo aprobado por el usuario |
| `Roblox_Studio_upload_image` | Subir imagenes a Roblox Asset Server | Subir iconos generados/aprobados |
| `Roblox_Studio_store_image` | Convertir imagen local a URI interna | Usar una imagen local como referencia |

Reglas:

- No inventar asset IDs.
- Pedir confirmacion antes de insertar assets externos ambiguos.
- Si el asset pertenece a otro owner, pedir consentimiento explicito antes de insertarlo.

Ejemplo:

```text
Busca 3 modelos de linterna, muéstrame opciones y no insertes nada hasta que confirme.
```

### Captura, Input Y Playtest

| Herramienta | Uso | Ejemplo |
|---|---|---|
| `Roblox_Studio_screen_capture` | Capturar pantalla de Studio | Verificar escena/UI visualmente |
| `Roblox_Studio_get_console_output` | Leer consola de Studio | Ver errores despues de playtest |
| `Roblox_Studio_user_keyboard_input` | Simular teclado en Client | Probar inputs durante playtest |
| `Roblox_Studio_user_mouse_input` | Simular mouse en Client | Clickear botones UI |
| `Roblox_Studio_character_navigation` | Mover personaje a una posicion/instancia | Probar zonas o triggers |

Ejemplo:

```text
/playtest-qa Inicia Play, camina hasta la zona de recompensa, revisa logs y detén Play
```

### Generacion Y Procedural

| Herramienta | Uso | Ejemplo |
|---|---|---|
| `Roblox_Studio_generate_procedural_model` | Crear modelos proceduralmente con atributos | Crear una puerta configurable |
| `Roblox_Studio_generate_mesh` | Generar mesh por prompt | Crear un prop simple |
| `Roblox_Studio_generate_material` | Generar MaterialVariant | Crear material de pared humeda |

Reglas:

- Usar solo si el usuario pidio crear un objeto/material/mesh.
- No generar assets extra solo por genero.

Ejemplo:

```text
Crea una puerta falsa procedural para el obby, con atributo para cambiar color y tamaño.
```

### Documentacion Roblox

| Herramienta | Uso | Ejemplo |
|---|---|---|
| `Roblox_Studio_http_get` | Consultar docs oficiales permitidas | Revisar API de `MarketplaceService` |
| `Roblox_Studio_skill` | Cargar skills especificas Roblox MCP | Device simulator, docs, profiling, scene analysis |

Skills Roblox MCP disponibles:

- `rbx-docs-search`: buscar documentacion Roblox.
- `rbx-device-simulator-lua`: probar UI en dispositivos/orientaciones.
- `rbx-perf-profiling`: analizar MicroProfiler/LibMP.
- `rbx-scene-analysis`: analizar escena, memoria, instancias y assets.

Ejemplo:

```text
Consulta la documentacion oficial de TextService antes de proponer filtrado de texto.
```

## Herramientas Locales Del Proyecto

### RAG

Comandos:

```powershell
python -m rag query "<consulta>" --score -k 8
python -m rag stats
```

Ejemplos:

```powershell
python -m rag query "DataStore ProfileStore session locking BindToClose" --score -k 8
```

```powershell
python -m rag query "RemoteEvent OnServerEvent validation rate limiting exploit prevention" --score -k 8
```

### Orquestador

Comando:

```powershell
python -m orchestrator "<consulta>" --verbose
```

Ejemplos:

```powershell
python -m orchestrator "como protejo un RemoteEvent de compra" --verbose
```

```powershell
python -m orchestrator "revisa patrones de performance para mobile" --verbose
```

### Memoria

El proyecto incluye modulo `memory/` para reglas, casos y notas persistentes. Usar cuando el usuario pida recordar una regla o consultar decisiones pasadas.

Ejemplos de regla para guardar:

```text
Recuerda que este proyecto no usa React Luau ni Roact.
```

```text
Recuerda que los RemoteEvents deben ser server-authoritative y validar tipos.
```

## Flujos Recomendados

### Crear O Modificar Algo En Studio

1. Confirmar alcance si hay duda.
2. Inspeccionar el objeto/servicio afectado.
3. Aplicar solo el cambio pedido.
4. Verificar con readback, logs, screenshot o playtest.
5. Responder que se cambio y como se verifico.

Ejemplo:

```text
Agrega una puerta falsa en el pasillo principal del obby de backrooms.
```

### Auditar Seguridad

1. Buscar remotes.
2. Leer handlers server-side.
3. Revisar validacion, autorizacion y cooldowns.
4. Reportar hallazgos por severidad.
5. Pedir confirmacion antes de fixes amplios.

Ejemplo:

```text
/security-audit Revisa compras, inventario y recompensas por exploits
```

### Optimizar Performance

1. Escanear scripts y escena.
2. Reportar patrones problematicos.
3. Separar fixes mecanicos de cambios arquitectonicos.
4. Verificar despues de modificar.

Ejemplo:

```text
/performance-audit El juego baja FPS cuando entran muchos jugadores
```

### Usar Templates De Genero Sin Inventar

1. Identificar el genero como contexto.
2. Extraer solo patrones relevantes a lo pedido.
3. Preguntar si falta una decision bloqueante.
4. No agregar sistemas tipicos del genero sin permiso.

Ejemplo:

```text
/horror Haz que el pasillo tenga luces parpadeantes y sonido ambiente, sin monstruo todavia
```

Resultado esperado:

- Agrega luces y sonido ambiente.
- No agrega monstruo, jumpscare, tienda, historia o inventario.

## Checklist Rapido De No Inventar

Antes de ejecutar o proponer cambios, el agente debe revisar:

- ¿El usuario pidio esta feature explicitamente?
- ¿Esta decision cambia gameplay, monetizacion, datos o arquitectura?
- ¿Hay riesgo de afectar datos reales, compras, teleports o servicios externos?
- ¿Hay multiples opciones razonables?
- ¿Falta informacion para hacerlo bien?

Si la respuesta es si a cualquiera de las preguntas de riesgo, preguntar antes de actuar.
