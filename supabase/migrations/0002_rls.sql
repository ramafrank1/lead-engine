-- RLS en todas las tablas. El pipeline (Python) se conecta como `postgres` y no pasa por RLS.
-- El panel web entra con supabase-js y solo ve datos si su usuario está en `app_owner`.

create table app_owner (
  user_id uuid primary key references auth.users (id) on delete cascade
);
alter table app_owner enable row level security;
create policy owner_self on app_owner for select to authenticated using (user_id = auth.uid());

create or replace function is_owner() returns boolean
  language sql stable security definer set search_path = public as $$
  select exists (select 1 from app_owner where user_id = auth.uid());
$$;

do $$
declare t text;
begin
  foreach t in array array[
    'leads', 'place_cache', 'audits', 'demos', 'demo_views', 'messages',
    'followups', 'opportunities', 'deals', 'blacklist', 'api_usage'
  ] loop
    execute format('alter table %I enable row level security', t);
    execute format(
      'create policy owner_all on %I for all to authenticated using (is_owner()) with check (is_owner())', t
    );
  end loop;
end $$;

-- Después de crear tu usuario en Supabase Auth, corré (con tu UUID):
-- insert into app_owner (user_id) values ('<tu-uuid>');
