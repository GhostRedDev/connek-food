-- Purpose: schema inicial del contexto identity + RLS + trigger auto-create org al signup.
-- Depends on: auth.users (provista por Supabase Auth automáticamente).

-- ─── Extensiones ─────────────────────────────────────────────────
create extension if not exists "uuid-ossp";

-- ─── organizations ───────────────────────────────────────────────
create table if not exists public.organizations (
    id          uuid        primary key default uuid_generate_v4(),
    name        varchar(120) not null,
    slug        varchar(60)  not null unique,
    plan        varchar(20)  not null default 'free',
    created_at  timestamptz  not null default now()
);

comment on table public.organizations is 'Restaurantes o grupos de restaurantes (un tenant).';

-- ─── memberships ─────────────────────────────────────────────────
create table if not exists public.memberships (
    id              uuid        primary key default uuid_generate_v4(),
    user_id         uuid        not null,    -- referencia lógica a auth.users.id
    organization_id uuid        not null references public.organizations(id) on delete cascade,
    role            varchar(20) not null default 'owner',
    created_at      timestamptz not null default now(),
    constraint uq_user_org unique (user_id, organization_id),
    constraint ck_memberships_role check (role in ('owner', 'manager', 'host', 'super_admin'))
);

create index if not exists ix_memberships_user_id         on public.memberships (user_id);
create index if not exists ix_memberships_organization_id on public.memberships (organization_id);

comment on table public.memberships is 'Vincula auth.users con organizations + role.';

-- ─── RLS: organizations ──────────────────────────────────────────
alter table public.organizations enable row level security;

drop policy if exists "members read their orgs" on public.organizations;
create policy "members read their orgs"
on public.organizations for select
to authenticated
using (
    id in (select organization_id from public.memberships where user_id = auth.uid())
);

drop policy if exists "authenticated insert orgs" on public.organizations;
create policy "authenticated insert orgs"
on public.organizations for insert
to authenticated
with check (true);  -- al crear org, el use case agrega membership owner inmediatamente

drop policy if exists "owners update their orgs" on public.organizations;
create policy "owners update their orgs"
on public.organizations for update
to authenticated
using (
    id in (
        select organization_id from public.memberships
        where user_id = auth.uid() and role = 'owner'
    )
);

drop policy if exists "owners delete their orgs" on public.organizations;
create policy "owners delete their orgs"
on public.organizations for delete
to authenticated
using (
    id in (
        select organization_id from public.memberships
        where user_id = auth.uid() and role = 'owner'
    )
);

-- ─── RLS: memberships ────────────────────────────────────────────
alter table public.memberships enable row level security;

drop policy if exists "users read their memberships" on public.memberships;
create policy "users read their memberships"
on public.memberships for select
to authenticated
using (
    user_id = auth.uid()
    or organization_id in (select organization_id from public.memberships where user_id = auth.uid())
);

drop policy if exists "owners manage memberships of their orgs" on public.memberships;
create policy "owners manage memberships of their orgs"
on public.memberships for all
to authenticated
using (
    organization_id in (
        select organization_id from public.memberships
        where user_id = auth.uid() and role = 'owner'
    )
)
with check (
    organization_id in (
        select organization_id from public.memberships
        where user_id = auth.uid() and role = 'owner'
    )
);

-- ─── Trigger: al signup, auto-crear Organization "Mi Restaurante" + Membership owner ─
create or replace function public.handle_new_user_create_org()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
    new_org_id uuid;
    org_name   text;
    org_slug   text;
begin
    org_name := coalesce(
        new.raw_user_meta_data->>'organization_name',
        'Mi Restaurante'
    );
    -- Slug único: base + sufijo corto del user_id si colisiona.
    org_slug := lower(regexp_replace(org_name, '[^a-zA-Z0-9]+', '-', 'g'));
    org_slug := trim(both '-' from org_slug);
    if length(org_slug) = 0 then org_slug := 'mi-restaurante'; end if;
    if exists (select 1 from public.organizations where slug = org_slug) then
        org_slug := org_slug || '-' || substr(new.id::text, 1, 8);
    end if;

    insert into public.organizations (name, slug)
    values (org_name, org_slug)
    returning id into new_org_id;

    insert into public.memberships (user_id, organization_id, role)
    values (new.id, new_org_id, 'owner');

    return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute function public.handle_new_user_create_org();

comment on function public.handle_new_user_create_org() is
    'Auto-crea Organization + Membership(owner) cuando un user nuevo signup en Supabase Auth.';
