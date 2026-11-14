# Fase 2: Gmail nuevo + Google Cloud (costo US$0)

Tiempo total: unos 40 minutos, más 14 días de "calentamiento" manual de la cuenta.
Los pasos marcados con 👤 los hacés vos (crear cuentas y aceptar términos). El resto ya está programado.

---

## Paso 1 👤 Crear la cuenta de Gmail de envío

1. Abrí una **ventana de incógnito** (así no se mezcla con tu cuenta personal) y entrá a https://accounts.google.com/signup
2. Nombre: **Ramiro Frank**. Dirección: algo profesional y fácil de leer, por ejemplo:
   `ramirofrank.web@gmail.com`, `ramiro.frank.dev@gmail.com` o `hola.ramirofrank@gmail.com`.
   Evitá números al azar: parecen spam.
3. Poné **tu número de celular** y un **email de recuperación** (tu `tu-email-personal@gmail.com`).
4. Activá la **verificación en 2 pasos**: https://myaccount.google.com/signinoptions/two-step-verification
5. Subí una **foto de perfil** (la misma del portfolio). Las cuentas con foto y nombre real generan más confianza.
6. Creá **una sola** cuenta. Abrir varias para esquivar límites va contra las reglas de Google y es la forma más rápida de que te las cierren a todas.

## Paso 2 👤 Calentamiento manual (14 días, mientras se programa el resto)

Una cuenta nueva que de golpe le escribe a desconocidos es la señal clásica de spam. Durante 2 semanas usala como una persona real:

| Días | Qué hacer (5–10 minutos por día) |
|---|---|
| 1–3 | Mandá 3–5 emails a amigos, familia o clientes conocidos **pidiéndoles que te respondan**. Suscribite a 3–4 newsletters de tu rubro (por ejemplo, de diseño web o de IA). |
| 4–7 | Respondé los emails que te lleguen. Abrí y marcá como "importante" algunas newsletters. Si algo cae en Spam, marcá "No es spam". |
| 8–14 | 5–8 emails por día a gente conocida, con conversaciones de ida y vuelta. Mandate emails a tu cuenta personal y contestalos. |

**No mandes nada en frío todavía.** El envío automático arranca recién en la Fase 5, con 10 por día.

## Paso 3 👤 Proyecto de Google Cloud

Si todavía no creaste el proyecto del Lead Engine, seguí antes la sección **"1. Google"** del [README](../../README.md): proyecto `lead-engine`, facturación, Places API (New), PageSpeed y el tope de 40 búsquedas por día.

Usá **tu cuenta personal** para Google Cloud (es la dueña del proyecto y de la facturación). La cuenta nueva solo se usa para enviar.

**Alerta de gasto (recomendado):** *Facturación → Presupuestos y alertas → Crear presupuesto* de **US$1**, con aviso al 50 % y al 100 %. Si alguna vez algo cobra, te enterás enseguida.

## Paso 4 👤 Activar la Gmail API

1. https://console.cloud.google.com/ → arriba, elegí el proyecto **lead-engine**.
2. *APIs y servicios → Biblioteca* → buscá **Gmail API** → **Habilitar**.

## Paso 5 👤 Pantalla de consentimiento (Google Auth Platform)

1. Menú → **Google Auth Platform** (o *APIs y servicios → Pantalla de consentimiento de OAuth*) → **Comenzar**.
2. **Información de la app:** nombre `Lead Engine`, correo de asistencia: tu email personal.
3. **Público:** **Externo**.
4. **Información de contacto:** tu email personal. Aceptá la política de datos de usuario → **Crear**.
5. Entrá a **Público** y tocá **Publicar app** → confirmá ("En producción").
   - **Por qué:** si la app queda en "Prueba", el permiso **vence cada 7 días** y el envío automático se corta.
   - **No hace falta mandarla a verificación.** Al autorizar vas a ver "Google no verificó esta app": es normal, porque la app es tuya y la usás solo vos.

## Paso 6 👤 Credenciales OAuth

1. **Google Auth Platform → Clientes → Crear cliente**.
2. Tipo de aplicación: **App de escritorio**. Nombre: `lead-engine-cli` → **Crear**.
3. Copiá el **ID de cliente** y el **Secreto del cliente** y pegalos en el `.env` del Lead Engine
   (todavía no existe: creálo con `copy .env.example .env` dentro de `Desktop\captar leads`):
   ```
   GMAIL_CLIENT_ID=xxxxxxxx.apps.googleusercontent.com
   GMAIL_CLIENT_SECRET=GOCSPX-xxxxxxxx
   ```
   No los mandes por chat ni los subas a git (`.env` ya está en `.gitignore`).

## Paso 7 👤 Tus datos para la firma

En el mismo `.env`:
```
OWNER_WHATSAPP=+54 9 11 ...
OWNER_POSTAL_ADDRESS=Calle 123, Bella Vista (1661), Buenos Aires, Argentina
```
La dirección postal es **obligatoria para EE.UU.** (CAN-SPAM). Puede ser una casilla postal o una dirección comercial; no hace falta que sea tu casa.

## Paso 8 Autorizar y probar

En PowerShell, dentro de `Desktop\captar leads`:

```powershell
.venv\Scripts\activate
pip install -e ".[dev]"
lead gmail-auth
```

- Se abre el navegador → elegí la **cuenta NUEVA** → "Google no verificó esta app" → **Configuración avanzada → Ir a Lead Engine (no seguro)** → marcá el permiso → **Continuar**.
- El token queda guardado solo en `.env` (`GMAIL_REFRESH_TOKEN`). Si por error entrás con tu cuenta personal, el comando la rechaza.

Después:

```powershell
lead gmail-check
lead gmail-check --enviar-prueba tu-email-personal@gmail.com
```

El primero confirma la conexión y avisa si falta algún dato de la firma. El segundo manda **un** email de prueba a tu cuenta personal: fijate si llegó a Recibidos o a Spam y abrí *⋮ → Mostrar original*. Tienen que decir **SPF: PASS** y **DKIM: PASS**.

## Paso 9 (opcional, ya que estás) 👤 Bot de Telegram

1. En Telegram hablale a **@BotFather** → `/newbot` → nombre `Lead Engine Ramiro` → copiá el token en `TELEGRAM_BOT_TOKEN`.
2. Mandale cualquier mensaje a tu bot y abrí `https://api.telegram.org/bot<TOKEN>/getUpdates`: el número de `"chat":{"id": ...}` va en `TELEGRAM_CHAT_ID`.

---

## Listo cuando…

- [ ] Existe la cuenta nueva, con 2 pasos, foto y recuperación.
- [ ] Arrancó el calentamiento (anotá la fecha: el envío en frío empieza después del día 14).
- [ ] La app de Google Cloud está **En producción**, con la Gmail API habilitada.
- [ ] `lead gmail-check` dice "Conectado" con la cuenta nueva.
- [ ] El email de prueba llegó a Recibidos con SPF y DKIM en PASS.

## Si algo falla

| Mensaje | Solución |
|---|---|
| `Faltan GMAIL_CLIENT_ID y GMAIL_CLIENT_SECRET` | Paso 6: pegalos en `.env` sin espacios ni comillas. |
| `access_denied` o "La app está en prueba" | Paso 5.5: publicá la app, o agregá la cuenta nueva en *Público → Usuarios de prueba*. |
| `No se pudo renovar el acceso a Gmail (400)` | El token venció o lo revocaste: publicá la app y corré `lead gmail-auth` de nuevo. |
| `Gmail API ... 403 accessNotConfigured` | Paso 4: falta habilitar la Gmail API en ese proyecto. |
| Acentos raros en la terminal | `chcp 65001` o usá Windows Terminal. |
