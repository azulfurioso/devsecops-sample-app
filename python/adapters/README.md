adapters es la capa que traduce entre:
- Tu aplicación (casos de uso, dominio) y el mundo externo (frameworks, librerías, I/O)
- Son la frontera técnica entre tu app y el mundo. Absorben complejidad, ruido y dependencias externas.
- No decide reglas de negocio.
- No orquesta el sistema.
- Solo adapta.
- Son traductores entre tu core y el exterior.

Como decidir si algo es adapter?
¿Esto habla con algo externo o técnico?
- ✔ Sí → adapter
- ❌ No → core (use case / domain)

Adaptar Entrada (input):
- CLI
- HTTP controllers (FastAPI, Flask)
- mensajes de una cola
- archivos de entrada
- Convierten: args / JSON / flags  →  datos limpios

Adaptar Salida (output):
- persistencia (SQLite, YAML, Mongo)
- APIs externas
- feeds RSS
- servicios cloud
- Convierten: interfaces del core  →  llamadas técnicas
