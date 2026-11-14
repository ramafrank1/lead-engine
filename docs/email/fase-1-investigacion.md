# Fase 1: investigación, herramientas y recomendación

Fecha: 2026-10-29. Precios sacados de búsquedas web (la mayoría de blogs de terceros) y, en el caso de Mailerfind, de su API vía MCP. **Antes de pagar, confirmar cada precio en la web oficial.**

---

## 1. Objetivo (resumen)

1. De lunes a sábado, encontrar negocios con capital (rubros de ticket alto) que no tengan web o la tengan mala, en Argentina, EE.UU. y otros países de habla inglesa.
2. Calificarlos (0–100), conseguir un email de empresa publicado y **verificarlo** antes de enviar.
3. Mandar entre 30 y 50 emails en frío por día, personalizados por rubro, país e idioma, de 9 a 12 en la hora del destinatario, desde dominios secundarios con warmup y cumpliendo la ley de cada país.
4. Hacer 3 seguimientos (días 3, 7 y 12), cortar la secuencia si responden, pasar a blacklist a quien pide la baja.
5. Clasificar las respuestas con IA, avisarte al instante cuando haya un interesado (con un borrador que revisás vos) y mandarte reportes diarios y semanales.

---

## 2. Hallazgos que cambian el plan

1. **Ya existe el Lead Engine** (`Desktop/captar leads`): buscador de Google Places, CSV, blacklist, control de costos y Supabase, con 19 tests. Conviene **reutilizar ese código** (buscador, calificación, blacklist, Supabase) y sumarle el envío, en lugar de construir todo dos veces.
2. **Los negocios sin web casi nunca tienen el email en Google Maps.** Maps no muestra emails; los scrapers los sacan *de la web del negocio*. Entonces:
   - "Web mala" → Maps + extracción de email desde su web (Outscraper/Apify).
   - "Sin web / solo redes" (la prioridad máxima) → el email suele estar en la **bio de Instagram**, y eso es justo lo que hace bien Mailerfind (análisis de Instagram por hashtag, ubicación o palabra clave).
3. **Argentina: la Disposición DNPDP 4/2009** exige poner la palabra **"publicidad" en el encabezado** de los emails publicitarios no solicitados e informar el derecho de baja (art. 27 Ley 25.326). Baja la tasa de apertura. No encontré confirmación de que se haya derogado. **Lo tenés que decidir vos** (ver sección 7). No soy abogado: es lo que dicen las fuentes.
4. **Canadá y Australia (y Nueva Zelanda):** se puede escribir solo a emails *publicados de forma visible* por el negocio, sin un aviso de "no queremos publicidad" al lado y **con un mensaje relacionado con su actividad**. La carga de la prueba es tuya: hay que guardar la **evidencia** (URL donde estaba el email, fecha y captura). El sistema puede hacerlo.
5. **Reino Unido:** se puede escribir en frío a **empresas (Ltd, PLC, LLP)**. A los *sole traders* y a las sociedades simples (partnerships) **no**, porque se tratan como personas. Hay que filtrar por forma jurídica (Companies House tiene API gratis). Desde 2025, las multas de PECR llegan a £17,5 M.
6. **Google Places (términos):** solo se puede guardar el `place_id` para siempre; el resto (nombre, teléfono, web) no se puede guardar a largo plazo. Para una base de prospección eso molesta. Outscraper o Apify no tienen esa restricción de Google en sus términos (el riesgo de scrapear lo asume el proveedor).
7. **El plan Starter de Mailerfind tiene un tope de 4.000 emails por mes.** Con 4 pasos por lead, 50 nuevos por día da unos 4.800 emails por mes y 40 por día da unos 3.800. **Alcanza para la rampa y hasta ~40 nuevos por día**; para pasar de ahí hace falta subir de plan o cambiar a Instantly.
8. Tu cuenta de Mailerfind hoy: sin plan, 0 créditos de análisis, 100 créditos de IA, sin casillas conectadas. Hay un **cupón Pre-Black Friday del 40 %** vigente hasta el 24/11/2026.

---

## 3. Tabla comparativa

### 3.1 Búsqueda de negocios

| Herramienta | Precio | Límites | API / MCP | Datos EE.UU. | Datos AR | Pros | Contras |
|---|---|---|---|---|---|---|---|
| **Google Places API (New)** | 1.000 llamadas/mes gratis (SKU Enterprise), después pago | Máx. 60 resultados por búsqueda | API oficial; no hay MCP oficial | Excelente | Excelente | Oficial, datos frescos, detecta "sin web" | No da emails; no se pueden guardar los datos; ya integrado en el Lead Engine |
| **Outscraper** | ~US$3/1.000 lugares + ~US$3/1.000 dominios para emails; 500 gratis por mes en cada servicio | Pago por uso, sin mensualidad | API REST; no encontré MCP oficial | Muy buena | Buena | Saca emails y redes desde la web; los créditos no vencen | Sin verificación incluida; costo por capas |
| **Apify (actors de Google Maps)** | ~US$2–5/1.000 lugares + enriquecimiento aparte; US$5 gratis por mes | Según el actor | API + **MCP oficial** (tenés el plugin, falta autorizarlo con /mcp) | Muy buena | Buena | Flexible, muchos actors | Calidad variable según el actor; precios cambian |
| **Apollo.io** | Free limitado; pagos desde ~US$49/usuario | Créditos de exportación | API + MCP (plugin disponible, falta autorizarlo) | **Excelente** para empresas medianas | **Pobre** para pymes locales | Emails de dueños y decisores en EE.UU. | Flojo para contractors chicos y negocios AR; más caro |
| **Mailerfind** | Starter: US$97 (o **US$47 precio LATAM**), −40 % hasta el 24/11 | 10.000 créditos de análisis, 2.500 perfiles por análisis | **MCP conectado y funcionando** | Media (Maps) | **Muy buena** vía Instagram | Encuentra emails de negocios **sin web** en bios de IG | Menos control fino sobre la calificación |

### 3.2 Búsqueda y verificación de emails

| Herramienta | Precio aprox. | Comentario |
|---|---|---|
| **MillionVerifier** | ~US$37 por 10.000 (créditos que no vencen) | El más barato; ideal para listas de pymes. **Recomendado.** |
| ZeroBounce | ~US$70–80 por 10.000 | Mejor detección de spam traps; opción "pro" |
| NeverBounce | ~US$50–80 por 10.000 | Bien para la API en tiempo real |
| Hunter.io / Snov.io / Findymail | Desde ~US$30–50 por mes | Buscan emails *de personas* por dominio. Para tu caso (info@, contacto@ publicados) aportan poco y empujan a usar emails personales, que vos querés evitar |
| Mailerfind | Incluido en el plan | Tiene validación propia; igual conviene pasar todo por MillionVerifier |

### 3.3 Envío en frío

| Herramienta | Precio | Casillas / warmup | Horario por zona y seguimientos | API / MCP | Comentario |
|---|---|---|---|---|---|
| **Mailerfind Starter** | US$47 LATAM (~US$28 con el cupón, verificar en el checkout) | 10 casillas, warmup incluido, 4.000 emails por mes | Secuencias (5), campañas programadas, bandeja unificada | **MCP ya conectado** | Búsqueda + envío + bandeja en uno. Su red de warmup es más chica que la de Instantly |
| **Instantly Growth** | US$47 por mes (US$37,6 anual) | **Casillas y warmup ilimitados**; 1.000 contactos y 5.000 emails por mes | Sí, por zona horaria, con rotación | **MCP oficial** (`mcp.instantly.ai`) + API v2 | La mejor entregabilidad del rango; los créditos de leads van aparte |
| Smartlead Basic | US$39 por mes | Según la fuente, 6 casillas o ilimitadas; 6.000 emails por mes | Sí | API buena; **sin MCP oficial** | Muy técnico; los add-ons suben el costo |
| Lemlist / Woodpecker | ~US$60–80+ por mes | Warmup incluido o como add-on | Sí | API | Más caros para lo que necesitás |
| **Gmail/Workspace directo por API** | US$0 extra | Sin warmup ni rotación | Hay que programar todo | Gmail API | **No recomendado:** sin warmup, si la casilla se quema perdés todo, y hay que construir la baja y los rebotes a mano. Nunca desde `tu-email-personal@gmail.com` |

### 3.4 Casillas

| Opción | Precio | Comentario |
|---|---|---|
| **Google Workspace Business Starter** | ~US$7 por usuario anual / US$8,4 mensual | La mejor entregabilidad. **Recomendado** |
| Zoho Mail Lite | ~US$1 por usuario | Barato, pero hay reportes de bloqueos con volumen. Sirve como respaldo |
| Casillas de Mailerfind/Instantly (llave en mano) | A consultar | Cómodo, pero más caro por casilla |

---

## 4. Recomendación

### Opción económica (objetivo: menos de US$100 por mes)

| Pieza | Herramienta | Costo mensual estimado |
|---|---|---|
| Leads "sin web / solo redes" (sobre todo AR) | **Mailerfind** (análisis de Instagram) | incluido |
| Leads "web mala" + EE.UU./UK | **Outscraper** (Maps + Emails & Contacts), pago por uso, orquestado desde el Lead Engine | US$15–30 |
| Calificación (PageSpeed, HTTPS, celular, copyright, reseñas) | Código propio (Lead Engine) + PageSpeed API (gratis) | US$0 |
| Verificación | **MillionVerifier** (pack de 10.000, rinde ~4–5 meses) | ~US$8 prorrateado |
| Envío, warmup, secuencias, bandeja | **Mailerfind Starter** (MCP) | US$28–47 |
| Casillas | **3 casillas de Google Workspace** en 2 dominios (2 + 1) | ~US$25 |
| Dominios | 2 `.com` (~US$11 por año cada uno) | ~US$2 |
| Redacción y clasificación con IA | API de Claude (Haiku para clasificar, Sonnet para redactar) | US$5–10 |
| Base de datos | **Supabase** (plan gratis, ya lo usás) | US$0 |
| Automatización diaria y reportes | **GitHub Actions** (cron en la nube) + bot de **Telegram** | US$0 |
| **Total** | | **~US$85–125** |

Queda debajo de US$100 con el cupón de Mailerfind y 3 casillas. Con 3 casillas a 20 por día cada una hay 60 envíos por día de capacidad (te sobran para 50).

**Por qué Mailerfind como base:** ya está conectado por MCP, cubre la búsqueda en Instagram (donde están los emails de los negocios sin web) y el envío en un solo plan. **Plan B:** si a las 2 semanas el warmup de Mailerfind da mal (inbox placement bajo), se cambia el envío a **Instantly Growth** (mismo precio, MCP oficial, warmup ilimitado) y Mailerfind queda solo para buscar.

### Opción "pro" (para escalar a 100+ por día)

- Envío: **Instantly Hypergrowth** o **Smartlead Pro**, con 8–10 casillas en 4–5 dominios.
- Leads EE.UU.: **Apollo** para conseguir dueños y decisores, más Outscraper.
- Verificación: **ZeroBounce** (spam traps y scoring).
- Costo estimado: **US$250–400 por mes**.

---

## 5. Arquitectura propuesta

```
GitHub Actions (cron, lun–sáb 04:00 ART)
  └─ Lead Engine (Python)
       ├─ Rotación rubro × país (config/rotacion.yaml)
       ├─ Outscraper / Mailerfind → leads crudos
       ├─ Calificación 0–100 (PageSpeed, HTTPS, celular, reseñas, rubro)
       ├─ Filtros legales por país (forma jurídica en UK, evidencia en CA/AU/NZ)
       ├─ Blacklist + deduplicado (Supabase)
       ├─ MillionVerifier → solo "valid" (los catch-all van aparte, a menor volumen)
       ├─ Claude → email 1 + 3 seguimientos desde templates/{idioma}/{rubro}.md
       └─ Mailerfind API → carga leads en la campaña del país (zona horaria y ventana 9–12)

Mailerfind (envía solo, 9–12 en la hora local, lun–sáb, 3–8 min entre envíos por casilla)

GitHub Actions (cada 15 min, 8–20 ART)
  └─ Lee la bandeja de Mailerfind → Claude clasifica
       ├─ interesado / pide info → Telegram con resumen + borrador (no se responde solo)
       ├─ baja / no interesado   → blacklist permanente
       ├─ no ahora               → reprogramar a 60 días
       └─ rebote > 3 % o quejas  → `prospect pause` automático + alerta

13:00 ART reporte diario · lunes reporte semanal (Telegram + email)
CLI: prospect status | prospect pause | prospect resume
```

**Horario:** recomiendo la **hora local del destinatario** (es lo que pediste). La contra es que Australia y Nueva Zelanda caen entre las 19 y las 23 h ART, y EE.UU. Pacific entre las 13 y las 16 h ART. Como envía la herramienta, no te afecta.

**Feriados:** tabla por país con la librería `holidays` de Python. Ese día no se cargan leads de ese país.

---

## 6. Cumplimiento por país (lo que configura el sistema)

| País | Regla clave | Cómo lo cumple el sistema |
|---|---|---|
| EE.UU. (CAN-SPAM) | Asunto veraz, identificación, **dirección postal física**, baja en ≤10 días hábiles | Firma con dirección, link de baja + "respondé 'no'", blacklist inmediata |
| Argentina (Ley 25.326, art. 27 + Disp. 4/2009) | Informar el derecho de baja; **"publicidad" en el encabezado** | Leyenda de baja en cada email; lo de "publicidad" queda **a tu decisión** |
| Reino Unido (PECR + UK GDPR) | Solo empresas (Ltd/PLC/LLP), nunca sole traders ni partnerships; identificación y baja | Chequeo en Companies House; si no se confirma la forma jurídica, se descarta |
| Canadá (CASL) | Email publicado, sin aviso de "no spam", relacionado con su actividad; identificación + dirección + baja en ≤10 días hábiles | Guardar la evidencia (URL, fecha, captura) en Supabase; solo info@/contacto publicados |
| Australia (Spam Act 2003) | Ídem (publicación visible y relacionada) + baja funcional en ≤5 días hábiles | Igual que Canadá |
| Nueva Zelanda (UEMA 2007) | Consentimiento inferido por publicación visible, parecido a Australia | Igual que Canadá (verificar en Fase 3) |
| Irlanda (S.I. 336/2011) | B2B a empresas permitido con baja; las personas, con más restricciones | Solo empresas (verificar en Fase 3) |

**Propuesta:** arrancar con **AR + EE.UU. + UK (solo empresas)** y sumar **CA/AU/NZ/IE en una segunda tanda**, cuando el registro de evidencia esté probado. Si no querés esperar, se pueden incluir desde el día 1 con la evidencia obligatoria.

---

## 7. Decisiones que necesito de vos

1. **¿Unificamos con el Lead Engine** (`Desktop/captar leads`) o este proyecto va aparte? Recomiendo unificar.
2. **"publicidad" en el asunto de los emails a Argentina:** (a) ponerlo para cumplir al pie de la letra, (b) no ponerlo y aceptar el riesgo, o (c) consultarlo con un abogado. Recomiendo (a) o (c).
3. **CA/AU/NZ/IE:** ¿desde el día 1 o en una segunda tanda? Recomiendo la segunda tanda.
4. **Mailerfind como motor de envío** (con Instantly como plan B), ¿OK?

## 8. Lo que necesito de vos (para la Fase 2)

- [ ] **Dirección postal física** para la firma (puede ser una casilla postal o una dirección comercial virtual, no hace falta que sea tu casa).
- [ ] **WhatsApp** para la firma (¿el [tu WhatsApp]?).
- [ ] Elegir y **comprar 2 dominios** (te guío; Cloudflare Registrar o Namecheap).
- [ ] **Google Workspace**: alta y 3 casillas "Ramiro Frank" (te guío).
- [ ] **Plan de Mailerfind** (Starter, idealmente con el cupón antes del 24/11). Conectar las casillas.
- [ ] Cuentas y claves: **Outscraper**, **MillionVerifier**, **API de Anthropic**, **Supabase** (proyecto + service key), **bot de Telegram** (token + tu chat id), **PageSpeed API key** (gratis, Google Cloud).
- [ ] **Portfolio en inglés**: ¿ramirofrank.pages.dev ya tiene la versión EN? (Según mis notas, es ES/EN.) Link directo a la versión en inglés y, si es posible, a cada caso.
- [ ] Permiso para mencionar a **BulkGym, Sinergia, Mayorista Leo, la distribuidora y la concesionaria** como casos, con links.
- [ ] Precios orientativos (ARS/USD) si querés que aparezcan en los emails (recomiendo **no** poner precios en el primer email).
- [ ] Repositorio en GitHub (privado) para que corran las automatizaciones.

---

## Fuentes

- Mailerfind: planes y límites leídos de su API vía MCP (29/10/2026).
- Instantly: [precios (Cleanlist)](https://www.cleanlist.ai/blog/2026-09-01-instantly-pricing-guide), [MarketBetter](https://marketbetter.ai/blog/instantly-pricing-breakdown-2026/), [MCP oficial (help center)](https://help.instantly.ai/en/articles/12980002-instantly-mcp-model-context-protocol)
- Smartlead: [precios (smartlead.ai)](https://www.smartlead.ai/pricing.md), [SendKit](https://sendkit.ai/smartlead-pricing), [Reply.io sobre la API](https://reply.io/blog/smartlead-api/)
- Outscraper: [costo de enriquecimiento](https://outscraper.com/google-maps-scraper-pricing-enrichment-cost/), [SyncGTM](https://syncgtm.com/blog/outscraper-review-2026)
- Apify: [Google Maps pay-per-event](https://help.apify.com/en/articles/10774732-google-maps-scraper-is-going-to-pay-per-event-pricing), [guía 2026](https://use-apify.com/blog/best-google-maps-scrapers-2026)
- Verificadores: [ZoomInfo: MillionVerifier vs ZeroBounce](https://pipeline.zoominfo.com/sales/millionverifier-vs-zerobounce), [BounceZero](https://bouncezero.io/best-email-verifier-2026)
- Casillas: [precios de Google Workspace](https://www.emailvendorselection.com/google-workspace-pricing/), [precios de Zoho Mail (PDF)](https://www.zoho.com/mail/images/mail-pricing-usd.pdf)
- CASL: [Bennett Jones](https://www.bennettjones.com/Insights/Blogs/2016/11/CRTC-Assesses-Conspicuous-Publication-Basis-of-Implied-Consent-in-CASL-Enforcement-Decision), [Prospeo](https://prospeo.io/s/casl-cold-email)
- Spam Act de Australia: [ALRC](https://www.alrc.gov.au/publication/for-your-information-australian-privacy-law-and-practice-alrc-report-108/73-other-telecommunications-privacy-issues/spam-act/), [Ashurst](https://www.ashurst.com/en/insights/acma-goes-ham-on-spam-is-your-business-in-breach-of-the-spam-act)
- PECR (UK): [ICO, marketing B2B](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/business-to-business-marketing/)
- Argentina: [Marval, Disp. 4/2009](https://www.marval.com/publicacion/proteccion-de-datos-personales----derecho-de-bloqueo-5534), [abogados.com.ar, opt-out](https://abogados.com.ar/index.php/ejercicio-del-derecho-de-retiro-o-bloqueo-opt-out/2805), [Diario Judicial](https://www.diariojudicial.com/news-23105-publicidad-pero-con-previo-aviso)
