# Fase 1 (revisada): plan con costo US$0

Fecha: 2026-10-29. Reemplaza la recomendación de `fase-1-investigacion.md`. La parte legal sigue igual.

---

## 1. Lo que se puede hacer gratis y lo que no

| Pieza | ¿Gratis? | Cómo |
|---|---|---|
| Buscar negocios | ✅ | Google Places API: 1.000 llamadas gratis por mes, hasta 20 negocios por llamada. Pide tarjeta para activar la facturación, pero con un **tope de cuota** no cobra nunca. Ya está integrado en el Lead Engine. Outscraper (500 lugares + 500 emails gratis por mes) y Apify (US$5 de crédito por mes) quedan como extras. |
| Sacar el email | ✅ | Script propio que lee la web del negocio (inicio, /contacto) y busca `mailto:` e info@. Gratis e ilimitado. |
| Calificar la web | ✅ | PageSpeed Insights API (gratis), chequeo de HTTPS, celular, año del copyright, formulario y WhatsApp. |
| Verificar el email | ⚠️ parcial | Chequeo propio de sintaxis + registro MX + lista de dominios descartables, gratis. La verificación por SMTP desde tu casa no funciona bien (los ISP bloquean el puerto 25). Los créditos gratis de alta de MillionVerifier y otros sirven para empezar, no para siempre. Riesgo: más rebotes, por eso hay que ir con menos volumen. |
| Redactar los emails | ✅ | Plantillas con spintax por rubro e idioma (3 variantes cada una), completadas con datos reales del lead. IA opcional: **Gemini Flash-Lite, plan gratis** (~500 pedidos por día según fuentes no oficiales; lo confirmo en la consola). |
| Clasificar las respuestas | ✅ | Reglas (palabras clave para "no", "baja", rebote, respuesta automática) + Gemini gratis para los casos dudosos. |
| Enviar | ⚠️ con límites | **Gmail por API** (gratis), desde una cuenta de Gmail dedicada. Sin dominio propio no hay SPF/DKIM propios, pero Gmail ya firma los emails de gmail.com. |
| Warmup automático | ❌ | No hay warmup gratis que valga la pena. Se reemplaza por una **rampa lenta manual** y emails muy personalizados que generen respuestas. |
| Dominio secundario | ❌ | Ningún dominio que sirva para mail es gratis (~US$10 por año). Sin dominio, se envía desde @gmail.com. |
| Casillas con dominio propio | ❌ | Zoho Free permite 5 casillas con dominio, pero **sin IMAP/SMTP**, así que no se pueden automatizar. Además necesita el dominio. |
| Link de baja | ✅ | Página en Cloudflare Pages + Supabase (gratis): un clic y queda en la blacklist. |
| Base de datos | ✅ | Supabase (plan gratis). |
| Automatización sin la compu prendida | ✅ | GitHub Actions: 2.000 minutos gratis por mes en repos privados, de sobra. |
| Alertas y reportes | ✅ | Bot de Telegram (gratis). |

**Proveedores de envío masivo gratis (Brevo, Resend, SendGrid, Mailgun):** descartados. Sus términos **prohíben el email en frío** y te cierran la cuenta.

---

## 2. El costo real de hacerlo gratis: volumen

Sin dominio propio ni warmup, **30–50 emails en frío por día desde Gmail es demasiado**: Google suspende cuentas por envíos a desconocidos con pocas respuestas. Lo prudente:

| Semana | Emails nuevos por día (total) | Seguimientos |
|---|---|---|
| 1–2 | 10 | sí |
| 3–4 | 15 | sí |
| 5 en adelante | 20–25 (techo) | sí |

Con los seguimientos, son unos 60–90 envíos por día en total. Para llegar a 40–50 nuevos por día sin pagar habría que usar 2 cuentas de Gmail, y aun así es arriesgado. **La puerta de salida barata** sería un dominio de ~US$10 por año + Zoho Mail Lite (~US$1 por mes) o Workspace. Queda anotado por si más adelante querés escalar.

Reglas que aplica el sistema para cuidar la cuenta:
- **Nunca desde `tu-email-personal@gmail.com`**: si se quema, perdés tu email personal. Crear una cuenta nueva, por ejemplo `ramirofrank.web@gmail.com`, a tu nombre.
- Pausa automática si los rebotes superan el 3 % o si Gmail devuelve errores de límite.
- Texto plano, 1 link (portfolio), sin adjuntos ni imágenes, sin pixel de apertura (no medimos aperturas; medimos respuestas).
- Envíos espaciados al azar cada 4–10 minutos, solo de 9 a 12 en la hora local, de lunes a sábado, sin feriados.

---

## 3. Arquitectura US$0

```
GitHub Actions (cron)
 ├─ 04:00 ART lun–sáb · BUSCAR
 │    Lead Engine: Places API → leer la web → email → PageSpeed → puntaje
 │    → filtros legales por país → blacklist/deduplicado (Supabase)
 │    → verificación propia (sintaxis + MX + descartables)
 │    → email 1 con plantilla + spintax (+ Gemini opcional)
 │    → fila en Supabase con estado "listo"
 │
 ├─ cada 10 min, ventana por zona horaria · ENVIAR
 │    toma 1 lead "listo" o 1 seguimiento vencido → Gmail API → guarda el thread_id
 │    respeta el cupo diario, la pausa global y el espaciado aleatorio
 │
 ├─ cada 15 min, 8–20 ART · RESPUESTAS
 │    Gmail API lee las respuestas → reglas + Gemini clasifican
 │    interesado → Telegram con resumen + borrador (como borrador de Gmail, lo mandás vos)
 │    baja / no → blacklist · no ahora → +60 días · rebote → marcar
 │
 ├─ 13:00 ART · reporte diario a Telegram
 └─ lunes · reporte semanal (rubro, país, variante, % de respuesta)

Cloudflare Pages: /baja?t=<token> → Supabase blacklist
CLI local: prospect status | pause | resume  (pause/resume también por Telegram)
```

---

## 4. Mercados con el plan gratis

| Mercado | Situación |
|---|---|
| **Argentina** | ✅ Arranca primero. Places tiene muy buena cobertura. La decisión de "publicidad" en el asunto sigue pendiente. |
| **EE.UU.** | ✅ Places + webs de contractors, dentistas, etc. Hace falta la dirección postal (CAN-SPAM). |
| **Reino Unido** | ✅ Solo empresas: chequeo gratis con la API de Companies House. |
| Canadá / Australia / NZ / Irlanda | ⏸ Segunda tanda, con registro de evidencia (URL + fecha + captura de la página, guardada gratis en Supabase Storage). |

Con 20–25 nuevos por día, el reparto 40/40/20 da unos 10 AR, 10 EE.UU. y 5 UK.

---

## 5. Lo que necesito de vos (todo gratis)

- [ ] **Cuenta de Gmail nueva** para enviar (la creás vos) y, con ella, un proyecto de Google Cloud con la Gmail API activada (te guío paso a paso).
- [ ] **Google Cloud: Places API + PageSpeed API**, con la facturación activada y un **tope de cuota** (te guío; con el tope no se cobra nada).
- [ ] **Clave gratis de Gemini** (Google AI Studio). Ojo: en el plan gratis, Google puede usar los datos para mejorar sus modelos. Se le mandan datos públicos del negocio y el texto de las respuestas. Si no te gusta, usamos solo plantillas y reglas.
- [ ] **Supabase**: proyecto + service key (¿el mismo del Lead Engine?).
- [ ] **Bot de Telegram**: token + tu chat id.
- [ ] **Clave de Companies House** (gratis) para el Reino Unido.
- [ ] **Repo privado en GitHub**.
- [ ] **Dirección postal** para la firma (obligatoria para EE.UU.) y el **WhatsApp**.
- [ ] Link del portfolio en inglés y OK para nombrar a los clientes como casos.

## 6. Decisiones pendientes

1. ¿Unificamos con el Lead Engine? (Recomendado: sí. Ya tiene Places, blacklist, control de costos y Supabase, y también lo armamos con costo cero.)
2. ¿Aceptás arrancar con 10 por día y llegar a un techo de 20–25 por día, en lugar de 30–50?
3. "publicidad" en el asunto para Argentina.
4. Gemini gratis: ¿sí o solo plantillas?

Fuentes: [Zoho Mail, pricing (PDF)](https://www.zoho.com/mail/images/mail-pricing-usd.pdf), [Geekflare: email gratis con dominio](https://geekflare.com/free-email-hosting-on-custom-domain/), [límites gratis de Gemini (ScriptByAI)](https://www.scriptbyai.com/gemini-api-free-tier-limits/), [Yingtu: Gemini free tier 2026](https://yingtu.ai/en/blog/google-gemini-api-free-tier-limits-2026).
