# Painel — Fatia 1: Fundação de dados + espelhamento Beds24 → Supabase

**Data:** 2026-07-24
**Sub-projeto:** B (motor de reservas & gestão) — primeira fatia
**Base funcional:** `docs/PAINEL.md` (modelo de dados seção 6, integrações seção 7)

## 1. Objetivo e escopo

Construir a **fundação de dados** do painel no Supabase (schema `casa_angelina`) e o
**espelhamento Beds24 → Supabase** que a mantém populada. É a base que destrava todas as
fatias seguintes do painel.

**Neste spec (fatia 1):**
- Schema `casa_angelina` (8 tabelas) com RLS.
- Edge Functions de sincronização: backfill inicial, webhook em tempo real, reconciliação por cron.
- Seed da propriedade Casa Angelina + 4 quartos com seus ids do Beds24.
- Testes de RLS, idempotência e cobertura da sincronização.

**Fora deste spec (fatias futuras):**
- Tela de calendário e telas do painel (leem o que esta fatia construiu).
- Reserva direta pelo site + pagamento (gateway indefinido).
- CRM/avaliações, editor de conteúdo, relatórios, multi-propriedade/marketplace.

## 2. Arquitetura

Beds24 é a **fonte da verdade** de reservas/disponibilidade (ele sincroniza Airbnb + Booking).
O Supabase é um **espelho consultável**. Nesta fatia o fluxo é só de entrada (Beds24 → Supabase).

```
Beds24 (dono das reservas Airbnb + Booking)
   │  1. webhook (reserva criada/alterada/cancelada)
   │  2. backfill inicial (GET /bookings, paginado)
   │  3. reconciliação periódica (cron)
   ▼
Edge Functions (Supabase, Deno) — seguram o token Beds24, escrevem com service_role
   ▼
Supabase Postgres — schema casa_angelina.* (RLS ligado)
   ▲
   │  leitura autenticada (dono logado, só-leitura via RLS) — fatia seguinte
Painel (UI estática)
```

**Acesso do painel (decisão: híbrido):** a UI (fatia futura) lê o Supabase direto (Supabase
Auth + RLS só-leitura); toda escrita e integração com o Beds24 passa por Edge Functions.

**Princípios de fundamento:**
1. **Fonte da verdade = Beds24.** Escrita que afeta disponibilidade real vai ao Beds24 (fatias futuras).
2. **Idempotência.** Webhooks podem repetir/chegar fora de ordem; upsert por `beds24_booking_id` +
   timestamp de modificação, com log de eventos.
3. **Isolamento no projeto compartilhado (HD360).** Auth é compartilhado; acesso é gated por
   tabela de membros (`app_users`) via RLS. HD360 usa o schema `public`; Casa Angelina usa
   `casa_angelina` (não colidem).

## 3. Schema `casa_angelina`

Tipos: `uuid` com `gen_random_uuid()` como pk; `timestamptz` com `now()`; datas como `date`.
`created_at`/`updated_at` em todas as tabelas de domínio.

### 3.1 `properties`
| coluna | tipo | notas |
|---|---|---|
| id | uuid pk | |
| beds24_property_id | text unique not null | id da propriedade no Beds24 |
| name | text not null | |
| slug | text unique not null | |
| timezone | text not null default 'America/Bahia' | |

Nasce com 1 linha (Casa Angelina). Abstração pronta para multi-propriedade sem migração.

### 3.2 `rooms`
| coluna | tipo | notas |
|---|---|---|
| id | uuid pk | |
| property_id | uuid fk → properties(id) | |
| beds24_room_id | text unique not null | room type no Beds24 |
| name | text not null | nome oficial do quarto |
| slug | text not null | |
| capacity | int not null | |
| sort_order | int default 0 | |
| active | boolean default true | |

`unique(property_id, slug)`. Seed com os 4 quartos (ver `casa-angelina-quartos`).

### 3.3 `guests`
| coluna | tipo | notas |
|---|---|---|
| id | uuid pk | |
| property_id | uuid fk | |
| full_name | text | |
| email | text | |
| phone | text | |
| country | text | |
| notes | text | |

Dado sensível (LGPD). Índices em `(property_id, email)` e `(property_id, phone)` para dedupe.

### 3.4 `reservations`
| coluna | tipo | notas |
|---|---|---|
| id | uuid pk | |
| property_id | uuid fk | |
| room_id | uuid fk → rooms(id) | |
| guest_id | uuid fk → guests(id), null | |
| beds24_booking_id | text, null | null p/ reservas diretas futuras |
| group_ref | text, null | liga reservas de casa inteira / booking multi-quarto |

`unique(beds24_booking_id, room_id)` (seguro tanto se o Beds24 der 1 id por quarto quanto 1 id
por grupo). O upsert casa por essa chave composta.
| channel | text not null | check: booking, airbnb, direct, manual |
| status | text not null | check: confirmed, pending, cancelled, no_show |
| check_in | date not null | |
| check_out | date not null | check `check_out > check_in` |
| num_guests | int | |
| total_amount | numeric(12,2) | |
| currency | text default 'BRL' | |
| raw_payload | jsonb | booking cru do Beds24 |
| beds24_modified_at | timestamptz, null | usado na idempotência |
| synced_at | timestamptz | |

### 3.5 `calendar_blocks`
| coluna | tipo | notas |
|---|---|---|
| id | uuid pk | |
| property_id | uuid fk | |
| room_id | uuid fk | |
| start_date | date | |
| end_date | date | check `end_date > start_date` |
| reason | text | |
| source | text | check: beds24, manual |

Disponibilidade é **derivada** de `reservations` + `calendar_blocks` (sem tabela data-a-data).

### 3.6 `app_users`
| coluna | tipo | notas |
|---|---|---|
| user_id | uuid pk fk → auth.users(id) | |
| property_id | uuid fk | |
| role | text | check: admin, operador |

Resolve o isolamento no Auth compartilhado + base de papéis. Quem não está aqui, o RLS bloqueia.

### 3.7 `beds24_webhook_events`
| coluna | tipo | notas |
|---|---|---|
| id | bigint identity pk | |
| event_type | text | |
| beds24_booking_id | text | |
| payload | jsonb | |
| received_at | timestamptz default now() | |
| processed_at | timestamptz, null | |
| status | text default 'received' | check: received, processed, error |
| error | text, null | |

Log de idempotência, auditoria e replay. Sem acesso de cliente (só service_role).

### 3.8 `sync_state`
| coluna | tipo | notas |
|---|---|---|
| key | text pk | ex.: 'backfill_cursor', 'last_reconcile_at' |
| value | jsonb | |
| updated_at | timestamptz default now() | |

## 4. Espelhamento (Edge Functions)

Todas em Deno, no Supabase, com `service_role` (fura o RLS por ser backend confiável).

**Auth no Beds24 (API v2):** invite code (gerado no painel Beds24) → refresh token (secret da
função) → access tokens curtos por chamada. Nenhum token no front.

**Funções:**
- `beds24-backfill` (disparo manual/admin): pagina `GET /bookings`, upsert, cursor em `sync_state`.
- `beds24-webhook` (endpoint público, protegido por segredo): valida segredo → grava em
  `beds24_webhook_events` → upsert.
- `beds24-reconcile` (cron, pg_cron/agendador): puxa o que mudou desde a última sincronização,
  upsert. Rede de segurança para webhooks perdidos.
- lib compartilhada: cliente Beds24 (auth/refresh) + lógica de upsert.

**Lógica de upsert (idempotência):**
- Casa por `beds24_booking_id`. Atualiza só se `beds24_modified_at` do payload for mais novo que
  o `synced_at`/`beds24_modified_at` gravado. Nunca duplica nem sobrescreve com dado velho.
- Resolve `guest` (acha por email/phone ou cria) e `room` (por `beds24_room_id`).
- Booking multi-quarto / casa inteira → uma reserva por quarto com o mesmo `group_ref`.
- Cancelamento → `status = cancelled` (não deleta).

**Seed inicial:** cria a `property` Casa Angelina + os 4 `rooms` com os `beds24_room_id` reais.

**Secrets (Edge Functions):** `BEDS24_REFRESH_TOKEN`, `BEDS24_WEBHOOK_SECRET`,
`SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_URL`. Nunca no repo nem no front.

## 5. Segurança e RLS

- **RLS ligado em todas as tabelas** `casa_angelina.*`.
- Função `casa_angelina.is_member(p_property_id uuid) returns boolean` (security definer): checa
  se `auth.uid()` está em `app_users` para a propriedade.
- **Policies:**
  - `anon`: **nenhuma** policy → zero acesso (LGPD).
  - `authenticated` + membro: **SELECT** em `properties`, `rooms`, `guests`, `reservations`,
    `calendar_blocks`, e a própria linha de `app_users`. Nenhuma escrita de cliente nesta fatia.
  - `beds24_webhook_events` e `sync_state`: sem acesso de cliente (só `service_role`).
  - `service_role`: fura o RLS (Edge Functions).
- **Config no dashboard:** adicionar `casa_angelina` em *Settings → API → Exposed schemas*;
  `grant usage on schema casa_angelina` e `grant select` nas tabelas para `authenticated` (o RLS
  filtra as linhas por cima).

## 6. Testes / verificação

- **Migração** roda limpa e é re-executável (idempotente).
- **RLS:** anon lê `guests`/`reservations` → negado; membro → lê; authenticated não-membro
  (simula HD360) → negado.
- **Idempotência:** reenviar o mesmo webhook não duplica; payload com modificação mais antiga é ignorado.
- **Backfill:** contagem de reservas no Supabase bate com o Beds24.
- **Reconciliação:** simular webhook perdido e confirmar que o cron recupera.

## 7. Decisões em aberto (resolver na implementação)

- Mapa exato de status do Beds24 → `status` nosso (confirmed/pending/cancelled/no_show).
- Intervalo do cron de reconciliação (sugestão inicial: a cada 3–6 h).
- Backfill como Edge Function ou script local one-off (ambos usam a mesma lib de upsert).
- Formato exato do payload/segredo do webhook do Beds24 (confirmar na doc da API v2).
- Granularidade de booking no Beds24: 1 id por quarto vs 1 id por grupo (confirma como `group_ref`
  e a chave composta se comportam na prática).
