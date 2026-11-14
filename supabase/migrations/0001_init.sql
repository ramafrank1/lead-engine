-- Lead Engine: esquema inicial.
-- Política de datos de Google: de Places solo se guarda el place_id para siempre (en `leads`).
-- El resto (nombre, teléfono, web, rating...) vive en `place_cache` y se borra a los N días.
-- Los datos "verificados" (los confirmás vos o salen de la web/redes del propio negocio) van en `leads`.

create type pipeline_status as enum (
  'nuevo', 'contactado', 'respondio', 'demo_pedida', 'demo_enviada',
  'reunion', 'propuesta', 'ganado', 'perdido', 'descartado'
);

create table leads (
  id              bigint generated always as identity primary key,
  place_id        text unique,
  source          text not null default 'maps' check (source in ('maps', 'instagram', 'radar', 'manual')),
  rubro           text not null,
  zona            text not null,
  web_status      text check (web_status in ('none', 'social', 'own')),
  score           int not null default 0,
  score_reason    text,
  heat            int not null default 0,
  pipeline_status pipeline_status not null default 'nuevo',
  -- datos verificados (propios, no de Google)
  verified_name   text,
  verified_wa     text,   -- +549...
  verified_email  text,
  instagram       text,
  facebook        text,
  notes           text,
  reactivated     boolean not null default false,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create index leads_status_idx on leads (pipeline_status, score desc);

-- Copia temporal de Places. `wa_phone` y `domain` se guardan normalizados para deduplicar.
create table place_cache (
  place_id   text primary key,
  data       jsonb not null,
  wa_phone   text,
  domain     text,
  fetched_at timestamptz not null default now()
);
create index place_cache_phone_idx on place_cache (wa_phone);
create index place_cache_domain_idx on place_cache (domain);

create table audits (
  id                  bigint generated always as identity primary key,
  lead_id             bigint not null references leads (id) on delete cascade,
  url                 text not null,
  https               boolean,
  mobile_friendly     boolean,
  performance_mobile  int,
  performance_desktop int,
  seo_score           int,
  accessibility_score int,
  copyright_year      int,
  cms                 text,
  has_whatsapp        boolean,
  has_form            boolean,
  problems            jsonb not null default '[]',
  summary             text,
  pdf_path            text,
  created_at          timestamptz not null default now()
);

-- Las demos se hacen solo cuando el lead dice que sí.
create table demos (
  id           bigint generated always as identity primary key,
  lead_id      bigint not null references leads (id) on delete cascade,
  slug         text unique,
  template     text,
  url          text,
  colors       jsonb,
  logo_url     text,
  copy         jsonb,
  version      int not null default 1,
  requested_at timestamptz not null default now(),
  published_at timestamptz,
  expires_at   timestamptz,
  status       text not null default 'pedida' check (status in ('pedida', 'activa', 'expirada', 'convertida'))
);

-- Sin IPs: solo user agent, ciudad aproximada y métricas de lectura.
create table demo_views (
  id          bigint generated always as identity primary key,
  demo_id     bigint not null references demos (id) on delete cascade,
  event       text not null check (event in ('open', 'scroll', 'click_whatsapp', 'time')),
  user_agent  text,
  country     text,
  city        text,
  referrer    text,
  duration_s  int,
  scroll_max  int,
  created_at  timestamptz not null default now()
);

create table messages (
  id          bigint generated always as identity primary key,
  lead_id     bigint not null references leads (id) on delete cascade,
  channel     text not null check (channel in ('whatsapp', 'email', 'instagram')),
  kind        text not null default 'primer_contacto',
  variant     text,
  body        text not null,
  link        text,
  sent        boolean not null default false,
  sent_at     timestamptz,
  replied     boolean not null default false,
  replied_at  timestamptz,
  created_at  timestamptz not null default now()
);

create table followups (
  id            bigint generated always as identity primary key,
  lead_id       bigint not null references leads (id) on delete cascade,
  due_on        date not null,
  kind          text not null check (kind in ('dia3', 'dia7', 'dia14', 'custom', 'resena', 'reactivacion')),
  suggested_msg text,
  done          boolean not null default false,
  cancelled     boolean not null default false
);
create index followups_due_idx on followups (due_on) where not done and not cancelled;

create table opportunities (
  id          bigint generated always as identity primary key,
  source      text not null,
  external_id text,
  title       text not null,
  description text,
  url         text,
  budget      text,
  posted_at   timestamptz,
  relevance   int,
  draft       text,
  status      text not null default 'nueva' check (status in ('nueva', 'descartada', 'propuesta_enviada', 'ganada', 'perdida')),
  created_at  timestamptz not null default now(),
  unique (source, external_id)
);

create table deals (
  id         bigint generated always as identity primary key,
  lead_id    bigint not null references leads (id) on delete cascade,
  service    text not null check (service in ('landing', 'catalogo', 'catalogo_panel', 'sistema_gestion', 'chatbot_ia', 'mantenimiento')),
  amount     numeric(12, 2),
  currency   text not null default 'ARS' check (currency in ('ARS', 'USD')),
  status     text not null default 'propuesto' check (status in ('propuesto', 'ganado', 'perdido')),
  closed_on  date,
  delivered_on date,
  created_at timestamptz not null default now()
);

-- Opt-out permanente: lo respetan todos los módulos. Nunca se borra con el lead.
create table blacklist (
  id         bigint generated always as identity primary key,
  kind       text not null check (kind in ('phone', 'domain', 'place_id')),
  value      text not null,
  reason     text,
  created_at timestamptz not null default now(),
  unique (kind, value)
);

-- Consumo de APIs por día, para el tope de costos.
create table api_usage (
  day   date not null,
  api   text not null,
  calls int not null default 0,
  primary key (day, api)
);

create or replace function touch_updated_at() returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end $$;

create trigger leads_touch before update on leads
  for each row execute function touch_updated_at();
