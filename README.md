# Lead Engine

Sistema para encontrar pymes con mala o nula presencia web, puntuarlas, contactarlas por WhatsApp
(el envío lo hacés vos) y hacerles una demo **solo si dicen que sí**. El plan completo está en
[docs/plan.md](docs/plan.md).

Estado: **Fase 1** — cazador de leads de Google Maps.
**Canal email (en construcción):** prospección por email en frío para AR, EE.UU. y UK con costo US$0
(Gmail API + GitHub Actions). Plan en [docs/email/fase-1-plan-gratis.md](docs/email/fase-1-plan-gratis.md);
configuración de Gmail y Google Cloud en [docs/email/fase-2-gmail-google-cloud.md](docs/email/fase-2-gmail-google-cloud.md).

## Instalación (una sola vez)

Necesitás Python 3.11 o más nuevo (`py --version`). En PowerShell, dentro de esta carpeta:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
```

Después abrí `.env` y completá lo que haga falta (ver abajo). Cada vez que abras una terminal nueva,
activá el entorno con `.venv\Scripts\activate`.

## Claves que necesitás

### 1. Google (obligatorio para buscar leads)
1. Entrá a https://console.cloud.google.com/ y creá un proyecto `lead-engine`.
2. **Facturación:** Google pide una tarjeta aunque no te cobre. Con los topes de abajo no salís del plan gratis.
3. *APIs y servicios → Biblioteca:* habilitá **Places API (New)** y **PageSpeed Insights API**.
4. *Credenciales → Crear credenciales → Clave de API.* Restringila a esas dos APIs y pegala en `GOOGLE_API_KEY`.
5. Recomendado: en *Places API (New) → Cuotas*, poné un máximo de 40 solicitudes de Text Search por día.
   Así, aunque el programa fallara, Google no te cobra nunca.

### 2. Supabase (para guardar los leads)
Sin `DATABASE_URL` el sistema corre en **modo prueba**: busca, puntúa y exporta el CSV, pero no guarda nada.
1. Creá un proyecto en https://supabase.com (plan free) llamado `lead-engine`.
2. *SQL Editor:* pegá y ejecutá, en orden, `supabase/migrations/0001_init.sql` y `0002_rls.sql`.
3. *Project Settings → Database → Connection string → Session pooler:* copiá la URI en `DATABASE_URL`
   (reemplazá `[YOUR-PASSWORD]` por la contraseña de la base).

## Uso

```powershell
lead opciones                                       # rubros y zonas disponibles
lead hunt --rubro corralones --zona "San Miguel" --max 60
lead hunt --rubro constructoras --zona pilar --csv-con-datos-google
lead blacklist "+54 9 11 5555-4444"                 # opt-out para siempre
lead purge-cache                                    # borra datos de Google viejos
lead gmail-auth                                     # autoriza la cuenta de Gmail de envío (una vez)
lead gmail-check --enviar-prueba vos@gmail.com      # verifica la conexión y manda una prueba
```

Cada `hunt` muestra una tabla con los mejores leads, guarda en la base y deja un CSV en `out/`.
Las búsquedas de un rubro, las zonas y los pesos del score se cambian en `config/*.yaml`, sin tocar código.

## Cómo se calcula el score (0–100)
Sin web +40 · solo redes/Linktree +35 · reseñas hasta +20 (logarítmico) · rating ≥ 4.2 +10 ·
rubro de ticket alto +10 · celular +10 · sin teléfono −30 · cercanía a Bella Vista hasta +5.
El motivo queda escrito, por ejemplo: "Sin web, 230 reseñas, 4.6★, constructora, celular".

## Costos y topes
`config/limites.yaml` define cuántas llamadas por día y por mes puede hacer cada API. Si se alcanza
un tope, el comando frena con un aviso. Por defecto: 40 búsquedas por día y 950 por mes de Places
(el cupo gratis es de 1.000 por mes). Una búsqueda trae hasta 20 negocios.

## Términos de Google (importante)
Las políticas de Places permiten guardar **para siempre solo el `place_id`**. Por eso:
- nombre, teléfono, web y rating van a una copia temporal (`place_cache`) que `lead purge-cache` borra
  a los `PLACES_CACHE_DAYS` días (30 por defecto);
- el CSV, por defecto, solo trae datos propios y el link a Maps. `--csv-con-datos-google` agrega
  nombre, teléfono y web: usalo para trabajar en el momento y no lo acumules;
- cuando mostrás datos de Google hay que atribuirlos ("Datos: Google Maps").

## Tests

```powershell
pytest -q
```

## Si ves acentos raros en la terminal
Ejecutá `chcp 65001` antes de usar `lead`, o usá Windows Terminal.
