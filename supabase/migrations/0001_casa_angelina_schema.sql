create schema if not exists casa_angelina;

create table if not exists casa_angelina.properties (
  id uuid primary key default gen_random_uuid(),
  beds24_property_id text unique not null,
  name text not null,
  slug text unique not null,
  timezone text not null default 'America/Bahia',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists casa_angelina.rooms (
  id uuid primary key default gen_random_uuid(),
  property_id uuid not null references casa_angelina.properties(id) on delete cascade,
  beds24_room_id text unique not null,
  name text not null,
  slug text not null,
  capacity int not null check (capacity > 0),
  sort_order int not null default 0,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (property_id, slug)
);

create table if not exists casa_angelina.guests (
  id uuid primary key default gen_random_uuid(),
  property_id uuid not null references casa_angelina.properties(id) on delete cascade,
  full_name text,
  email text,
  phone text,
  country text,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists guests_property_email_idx on casa_angelina.guests (property_id, email);
create index if not exists guests_property_phone_idx on casa_angelina.guests (property_id, phone);

create table if not exists casa_angelina.reservations (
  id uuid primary key default gen_random_uuid(),
  property_id uuid not null references casa_angelina.properties(id) on delete cascade,
  room_id uuid not null references casa_angelina.rooms(id),
  guest_id uuid references casa_angelina.guests(id),
  beds24_booking_id text,
  group_ref text,
  channel text not null check (channel in ('booking','airbnb','direct','manual')),
  status text not null check (status in ('confirmed','pending','cancelled','no_show')),
  check_in date not null,
  check_out date not null,
  num_guests int check (num_guests is null or num_guests > 0),
  total_amount numeric(12,2),
  currency text not null default 'BRL',
  raw_payload jsonb,
  beds24_modified_at timestamptz,
  synced_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (check_out > check_in),
  unique (beds24_booking_id, room_id)
);
create index if not exists reservations_property_dates_idx on casa_angelina.reservations (property_id, check_in, check_out);
create index if not exists reservations_room_dates_idx on casa_angelina.reservations (room_id, check_in, check_out);
create index if not exists reservations_group_ref_idx on casa_angelina.reservations (group_ref);

create table if not exists casa_angelina.calendar_blocks (
  id uuid primary key default gen_random_uuid(),
  property_id uuid not null references casa_angelina.properties(id) on delete cascade,
  room_id uuid not null references casa_angelina.rooms(id),
  start_date date not null,
  end_date date not null,
  reason text,
  source text not null check (source in ('beds24','manual')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (end_date > start_date)
);

create table if not exists casa_angelina.app_users (
  user_id uuid primary key references auth.users(id) on delete cascade,
  property_id uuid not null references casa_angelina.properties(id) on delete cascade,
  role text not null check (role in ('admin','operador')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists casa_angelina.beds24_webhook_events (
  id bigint generated always as identity primary key,
  event_type text,
  beds24_booking_id text,
  payload jsonb,
  received_at timestamptz not null default now(),
  processed_at timestamptz,
  status text not null default 'received' check (status in ('received','processed','error')),
  error text
);

create table if not exists casa_angelina.sync_state (
  key text primary key,
  value jsonb,
  updated_at timestamptz not null default now()
);
