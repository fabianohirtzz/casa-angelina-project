create or replace function casa_angelina.is_member(p_property_id uuid)
returns boolean
language sql
stable
security definer
set search_path = casa_angelina, public
as $$
  select exists (
    select 1 from casa_angelina.app_users au
    where au.user_id = auth.uid()
      and au.property_id = p_property_id
  );
$$;

alter table casa_angelina.properties          enable row level security;
alter table casa_angelina.rooms               enable row level security;
alter table casa_angelina.guests              enable row level security;
alter table casa_angelina.reservations        enable row level security;
alter table casa_angelina.calendar_blocks     enable row level security;
alter table casa_angelina.app_users           enable row level security;
alter table casa_angelina.beds24_webhook_events enable row level security;
alter table casa_angelina.sync_state          enable row level security;

drop policy if exists properties_select_member on casa_angelina.properties;
create policy properties_select_member on casa_angelina.properties
  for select to authenticated using (casa_angelina.is_member(id));

drop policy if exists rooms_select_member on casa_angelina.rooms;
create policy rooms_select_member on casa_angelina.rooms
  for select to authenticated using (casa_angelina.is_member(property_id));

drop policy if exists guests_select_member on casa_angelina.guests;
create policy guests_select_member on casa_angelina.guests
  for select to authenticated using (casa_angelina.is_member(property_id));

drop policy if exists reservations_select_member on casa_angelina.reservations;
create policy reservations_select_member on casa_angelina.reservations
  for select to authenticated using (casa_angelina.is_member(property_id));

drop policy if exists calendar_blocks_select_member on casa_angelina.calendar_blocks;
create policy calendar_blocks_select_member on casa_angelina.calendar_blocks
  for select to authenticated using (casa_angelina.is_member(property_id));

drop policy if exists app_users_select_self on casa_angelina.app_users;
create policy app_users_select_self on casa_angelina.app_users
  for select to authenticated using (user_id = auth.uid());

-- beds24_webhook_events e sync_state: sem policy => nenhum acesso de anon/authenticated.

grant usage on schema casa_angelina to authenticated;
grant select on
  casa_angelina.properties,
  casa_angelina.rooms,
  casa_angelina.guests,
  casa_angelina.reservations,
  casa_angelina.calendar_blocks,
  casa_angelina.app_users
  to authenticated;
