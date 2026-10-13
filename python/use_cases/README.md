Application / Use Cases
- Determines the behavior of the app
- The use cases interact with and depend on the entities, but they know nothing about the layers further out.
- They don't care if it's a web page or an iPhone app.
- They don't care if the data is stored in the cloud or in a local SQLite database.

Entities + Use Cases -> "core"
Entities definen el “qué”, los casos de uso definen el “cómo”.
Ambos juntos son el core.


❓ Si mañana cambio RSS, SQLite, CLI y Web…
¿esto sigue existiendo?
- ✔ Sí → Core
- ❌ No → Adapter / Framework
