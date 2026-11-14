# Plan de Lead Engine (revisado 2026-10-28)

## Decisiones tomadas
- **Costo US$0/mes.** Textos con plantillas y reglas; la IA es opcional (`AI_PROVIDER`: none, claude-code, ollama, gemini, anthropic).
- **Demos a pedido.** El primer mensaje no lleva demo: ofrece hacerle una gratis. La demo se arma **solo si el negocio dice que sí** (estado `demo_pedida`).
- **Datos de Google (opción A).** Para siempre se guarda solo el `place_id`. Nombre, teléfono, web y rating van a `place_cache` y se borran a los `PLACES_CACHE_DAYS` días. Lo que confirmás vos o sale de la web/redes del negocio va en los campos `verified_*` de `leads`.
- **Radar:** Freelancer por API pública; Upwork y Workana por las alertas que te llegan por email (no tienen RSS); grupos de Facebook en modo manual.

## Embudo
```
nuevo → contactado → respondio → demo_pedida → demo_enviada → reunion → propuesta → ganado / perdido
```

## Fases
1. **Fase 1 (hecha):** setup, migraciones, cazador (Places API), scoring, dedupe, blacklist, tope de costos, CSV.
2. **Fase 2:** auditor web (PageSpeed + chequeos + resumen por reglas) y **diagnóstico express en PDF**, que reemplaza a la demo como gancho del primer mensaje. Mensajes: primer contacto ofreciendo demo, 3 variantes A/B, seguimientos día 3/7/14, links `wa.me`, límite diario.
3. **Fase 3:** panel CRM (Hoy, Kanban, Ficha, Métricas) con login, bot de Telegram (digest 8:30, seguimientos, "X pidió demo") y crons.
4. **Fase 4:** radar de oportunidades y propuestas en PDF.
5. **A pedido:** `lead demo-pedida <id>` arma un brief (datos verificados, logo, colores, rubro) para hacer la demo. Si el volumen lo justifica, recién ahí se construye la fábrica de demos automática con tracking de aperturas.
6. **Después:** prospector "solo redes" y extras (casos de éxito, flyers QR, reactivación, reporte semanal).

## Canal email (decidido 2026-10-30)
- Unificado acá desde `Desktop/captar clientes`. Spec en [email/spec-cold-email.md](email/spec-cold-email.md) y plan US$0 en [email/fase-1-plan-gratis.md](email/fase-1-plan-gratis.md).
- Envío por **Gmail API** desde una cuenta nueva dedicada (nunca `tu-email-personal@gmail.com`). Rampa: 10 por día → techo de 20–25 por día. Mercados: AR + EE.UU. + UK (solo empresas); CA/AU/NZ/IE en una segunda tanda.
- Fase 2 (setup de Gmail y Google Cloud): [email/fase-2-gmail-google-cloud.md](email/fase-2-gmail-google-cloud.md). Comandos `lead gmail-auth` y `lead gmail-check`.
