# PROMPT PARA CLAUDE CODE — Sistema de prospección por email en frío (Argentina + países de habla inglesa)

## 0. Contexto

Soy Ramiro, de Bella Vista (Buenos Aires, Argentina). Desarrollo **páginas web, catálogos con panel de administración, sistemas de gestión a medida y chatbots con IA** para negocios y profesionales. Trabajo con Claude Code.

- Portfolio: https://ramirofrank.pages.dev/
- Proyectos para mostrar: BulkGym (gimnasio), Sinergia (logística), Mayorista Leo (mayorista de bebidas), una distribuidora con catálogo + panel de admin de precios/productos, y una concesionaria con catálogo de vehículos, consultas y financiación.

**Objetivo:** un sistema que **todos los días, de lunes a sábado**, busque negocios con potencial (que necesiten web o sistema y que manejen buen capital), consiga su email, les mande un **email en frío personalizado según el rubro y el país** ofreciendo mis servicios con el link a mi portfolio, y haga los seguimientos. Meta: **30 a 50 emails nuevos por día**, enviados **entre las 9:00 y las 12:00, nunca los domingos**.

Ya usé el **MCP de Mailerfind** y funcionó. Usalo como opción base, pero investigá otras herramientas de prospección y envío, compará y recomendame la mejor combinación.

---

## 1. Cómo quiero que trabajes

1. Arrancá en **modo plan**. Investigá las herramientas (sección 3), proponé la arquitectura y el costo mensual, y **esperá mi OK**.
2. Antes de **pagar, crear cuentas o comprar dominios**, pedime confirmación. Yo hago esos pasos; vos me guiás paso a paso.
3. Instalá y configurá vos lo que se pueda: MCP servers, SDKs, scripts, conexión por API.
4. Claves solo en `.env` (con un `.env.example`), nunca en el código.
5. Si una herramienta, API o función que menciono no existe o cambió, verificalo y avisame. No inventes endpoints.
6. Hacé una **prueba controlada** antes de activar el envío real: 5 emails a mis propias casillas, revisión de spam score y de cómo se ven.

---

## 2. Mercados y rubros

### Mercados
- **Argentina** (prioridad: GBA y CABA; después Córdoba, Rosario, Mendoza). Emails en **español rioplatense**, precios en ARS o USD.
- **Estados Unidos** (prioridad Florida, Texas y California por volumen de pymes; después el resto). Emails en **inglés**, precios en USD.
- **Otros países de habla inglesa:** Reino Unido, Canadá, Australia, Irlanda, Nueva Zelanda. En inglés, adaptado a cada país (moneda, ortografía UK/US).
- Opcional fase 2: resto de Latinoamérica y España, en español neutro.
- Distribución inicial del volumen (configurable): 40 % Argentina, 40 % EE.UU., 20 % otros de habla inglesa.

### Rubros (con buen capital y que necesitan web o sistema)
Corralones y materiales de construcción, constructoras y desarrolladoras, inmobiliarias, concesionarias de autos/motos/maquinaria, mayoristas y distribuidoras, estudios contables y jurídicos, clínicas odontológicas y estéticas, centros médicos privados, gimnasios y centros deportivos, empresas de logística y transporte, talleres y servicios automotores premium, agro (maquinaria, insumos, acopio), fábricas e industrias pymes, ferreterías industriales, empresas de seguridad, constructoras de piletas, amoblamientos/cocinas a medida, aberturas, energía solar, catering y salones de eventos, hoteles y cabañas. **En EE.UU./UK sumá:** roofing, HVAC, plumbing, remodeling/contractors, landscaping, real estate agents, auto dealers, dental practices, law firms, med spas.

Agregá los rubros que creas rentables y justificalos. Rotá los rubros día a día para no saturar uno.

### Criterios de calificación del lead (puntaje 0–100)
- **Sin web:** prioridad máxima. **Web vieja o mala:** sin HTTPS, no adaptada a celular, lenta (PageSpeed), copyright viejo, sin formulario ni WhatsApp. **Solo redes/Linktree:** muy bueno.
- Señales de capital: muchas reseñas, buen rating, varias sucursales, rubro de ticket alto, flota o stock visible.
- **Tiene email verificable** (requisito obligatorio para enviar).
- Descartá negocios cerrados, franquicias de grandes cadenas (la web la maneja la central), duplicados y la blacklist.

---

## 3. Herramientas: investigá, compará y recomendá

Investigá las opciones vigentes hoy y armame una tabla comparativa (precio mensual, límites, API/MCP disponible, calidad de datos de EE.UU. y de Argentina, pros y contras):

- **Búsqueda de negocios:** Google Places API (oficial), Apify (actors de Google Maps), Outscraper, Apollo.io (fuerte en EE.UU.), el propio Mailerfind.
- **Búsqueda y verificación de emails:** Mailerfind, Hunter.io, Snov.io, Apollo, Findymail, NeverBounce/ZeroBounce/MillionVerifier. **Todo email se verifica antes de enviarse.**
- **Envío en frío (con warmup, rotación de casillas, programación por horario y seguimientos automáticos):** Mailerfind, Instantly, Smartlead, Lemlist, Woodpecker. Evaluá también si conviene enviar desde Gmail/Google Workspace directo por API (más simple pero más riesgoso para volumen).
- Revisá si existe **MCP server** de cada herramienta para usarla directo desde Claude Code; si no, integralas por API.

Recomendame **una combinación concreta** con presupuesto bajo (ideal menos de USD 100/mes al inicio) y una opción "pro" para escalar.

---

## 4. Infraestructura de envío (entregabilidad; obligatorio)

- **No enviar desde mi dominio principal.** Comprar 1–2 dominios secundarios parecidos (por ejemplo `ramirofrank-web.com`, `getramirofrank.com`) que redirijan a mi portfolio.
- 2–3 casillas por dominio (Google Workspace o Zoho), con nombre real: "Ramiro Frank".
- Configurar **SPF, DKIM y DMARC** y verificarlos. Tracking domain personalizado si la herramienta lo usa.
- **Warmup de 2–3 semanas** antes de mandar volumen. Rampa: semana 1 → 10/día total, semana 2 → 20, semana 3 → 30–40, semana 4 → 50.
- Máximo **~20–25 emails por casilla por día**; repartir los 30–50 entre casillas.
- **Portfolio: link, no adjunto.** Los adjuntos en el primer email mandan a spam. Primer email: link a mi portfolio (o a un caso del rubro). Si el lead responde, ahí se manda el **PDF del portfolio adjunto** (preparalo en español y en inglés).
- Primer email en **texto plano o HTML mínimo**, sin imágenes pesadas, máximo 1–2 links, sin palabras gatillo de spam.
- Monitorear diariamente: rebotes (frenar si supera 3 %), quejas de spam y reputación de dominio. Si algo se dispara, **pausar automáticamente y avisarme**.

---

## 5. Los emails

### Secuencia por lead
1. **Email 1 (día 0):** primer contacto.
2. **Seguimiento 1 (día 3):** corto, agrega valor (un dato sobre su web o su rubro).
3. **Seguimiento 2 (día 7):** caso de un proyecto similar del portfolio.
4. **Cierre (día 12):** "último email, ¿lo dejo acá?".
- Si responde, la secuencia se corta.

### Reglas de redacción
- **Personalizado por rubro, país e idioma:** el dolor del rubro (ejemplos: inmobiliaria → captar consultas de propiedades; corralón → catálogo y presupuestos por WhatsApp; concesionaria → catálogo de stock y financiación; constructora → mostrar obras y conseguir licitaciones/clientes; contractor de EE.UU. → más quotes desde Google).
- Mencioná **un dato real del negocio**: nombre, ciudad y la situación de su web ("vi que no tienen web", "su web no se ve bien en el celular", "tienen 200 reseñas excelentes en Google pero ninguna web donde mostrarlas"). Nunca inventes datos.
- Cortos: **60–110 palabras**. Asunto de 2–6 palabras, natural, sin clickbait ni mayúsculas.
- Estructura: observación personalizada → qué hago y qué gana el negocio → prueba (proyecto similar del portfolio) → CTA simple ("¿Te muestro una idea de cómo quedaría?" / "Worth a quick look?").
- **Servicios a ofrecer** (elegir los 1–2 más relevantes por rubro, no todos juntos): web profesional, catálogo online con panel de administración, sistema de gestión a medida (stock, turnos, clientes, presupuestos), chatbot con IA para atención 24/7, mantenimiento mensual.
- Usá **spintax o variaciones generadas** para que no salgan todos iguales. Armá 3 variantes por rubro por idioma y medí cuál responde mejor (A/B).
- En inglés: tono natural de nativo, no traducción literal. Vendé el valor (remote developer, fast delivery, competitive USD pricing) sin sonar a "agencia offshore barata".
- Plantillas guardadas en `/templates/{idioma}/{rubro}.md`, editables por mí.

### Firma y cumplimiento legal (obligatorio en todos los emails)
- Nombre, servicio, link al portfolio, WhatsApp, **dirección postal física** (requisito de CAN-SPAM en EE.UU.; te la paso yo).
- **Opción de baja clara** en cada email ("Si no te interesa, respondé 'no' y no te escribo más" + link de unsubscribe de la herramienta).
- Cumplir **CAN-SPAM (EE.UU.)**, **Ley 25.326 (Argentina)**, **PECR/UK GDPR (Reino Unido)**, **CASL (Canadá)** y la **Spam Act (Australia)**. Investigá las reglas específicas de B2B en cada país y configurá el sistema para cumplirlas. Por ejemplo, en Canadá y Australia solo se puede escribir a emails publicados de forma visible por el negocio y relacionados con su actividad; en UK no se puede escribir en frío a emails personales de sole traders. Si en algún país no se puede cumplir, excluilo y avisame.
- Solo emails **de empresa/genéricos publicados** (info@, contacto@, ventas@ o el del dueño publicado en su web/Google). Nada de emails personales comprados.
- **Blacklist permanente:** quien pida la baja o responda negativamente no vuelve a recibir nada, nunca.

---

## 6. Horario de envío

- **Lunes a sábado, de 9:00 a 12:00, en la hora local del destinatario** (Argentina en hora ART; EE.UU. según la zona del lead: Eastern, Central, Mountain o Pacific; UK, Australia, etc. en su hora). Si conviene hacerlo en mi horario de Argentina, explicame el trade-off y lo decido.
- **Domingos: nada.** Excluí también los feriados nacionales de cada país.
- Envíos espaciados aleatoriamente (cada 3–8 min por casilla), no en ráfaga.

---

## 7. Flujo diario automatizado

1. **Búsqueda (a la madrugada o el día anterior):** según la rotación de rubro/país, buscar negocios, calificarlos, sacar emails y verificarlos. Generar **un 20 % más de leads** que el cupo del día por si algunos fallan.
2. **Redacción:** generar el email 1 personalizado de cada lead y cargarlo en la herramienta de envío con su secuencia.
3. **Envío:** la herramienta envía en la ventana 9–12 respetando los límites.
4. **Respuestas:**
   - Clasificar cada respuesta con IA: interesado / pide info / no ahora / no interesado / baja / rebote / respuesta automática.
   - **Interesado o pide info:** avisarme por **Telegram o email al instante** con el resumen y un **borrador de respuesta** en su idioma (con el PDF del portfolio adjunto). **No responder solo a los interesados; esa respuesta la reviso yo.**
   - Baja / no interesado: blacklist automática.
   - "No ahora": reprogramar el contacto en 60 días.
5. **Reporte diario (13:00 ART) por Telegram o email:** enviados, aperturas (si se mide), respuestas, interesados, rebotes, y salud de casillas y dominios.
6. **Reporte semanal (lunes):** qué rubros, países y variantes responden mejor, más los ajustes recomendados para la semana.

### Dónde corre
Proponé lo más confiable para que funcione **sin que yo tenga la compu prendida**: el scheduler de la herramienta de envío para los emails, y GitHub Actions/cron en la nube (o tareas programadas) para la búsqueda diaria y los reportes.

---

## 8. Base de datos y seguimiento

Supabase (ya lo uso) o una Google Sheet, lo que recomiendes, con estas tablas/columnas: lead, rubro, país, ciudad, web, situación de la web, score, email, verificado, idioma, variante enviada, fecha de envío, estado de la secuencia, respuesta, clasificación, próximo paso y notas. Más una tabla de **blacklist** y otra de **métricas diarias**.

Un comando simple para mí: `prospect status` (resumen del día) y `prospect pause` / `prospect resume` (frenar todo al instante).

---

## 9. Fases

1. **Fase 1:** investigación de herramientas + tabla comparativa + recomendación + costos. Espero OK.
2. **Fase 2:** guía para comprar dominios y crear casillas, configuración de SPF/DKIM/DMARC, arranque del warmup. *(Mientras corre el warmup se avanza con lo demás.)*
3. **Fase 3:** buscador de leads + calificación + emails verificados. Prueba: 50 leads reales de Argentina y 50 de EE.UU. para que los revise.
4. **Fase 4:** plantillas por rubro e idioma + generación personalizada. Me mostrás 10 emails de ejemplo (5 ES, 5 EN) para aprobar.
5. **Fase 5:** integración con la herramienta de envío, secuencias, horarios, blacklist y prueba controlada a mis casillas.
6. **Fase 6:** clasificación de respuestas + alertas + reportes + automatización diaria. Arranque con la rampa de volumen.

En cada fase: README en español, paso a paso y claro para alguien que no es dev senior.

---

## 10. Lo primero que hacés

1. Resumime el objetivo en 5 líneas para confirmar que entendiste.
2. Investigá las herramientas de la sección 3 y traeme la tabla comparativa y la recomendación.
3. Listá todo lo que necesitás de mí: cuentas, claves, dirección postal, versión en inglés del portfolio, etc.
4. Esperá mi OK para arrancar la Fase 2.
