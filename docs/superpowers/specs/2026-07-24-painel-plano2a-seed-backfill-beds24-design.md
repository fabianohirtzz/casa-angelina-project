# Plano 2a — Seed + espelhamento Beds24 (backfill local)

**Data:** 2026-07-24
**Sub-projeto:** B (motor de reservas & gestão) — fatia 1, parte A do espelhamento
**Base:** `docs/superpowers/specs/2026-07-24-painel-fundacao-dados-beds24-sync-design.md` (spec da fatia 1)
**Depende de:** Plano 1 (schema `casa_angelina` + RLS) — concluído e aplicado.

Este documento resolve as "decisões em aberto" do §7 do spec da fatia 1 para o recorte
**local-first**: popular o Supabase com dados reais do Beds24 por um script Python local, antes
de montar qualquer infraestrutura de Edge Functions.

## 1. Objetivo e escopo

Espelhar o Beds24 → Supabase (`casa_angelina.*`) por um **script Python local** que reusa o
harness `tools/db` do Plano 1 (conexão direta ao Postgres como superuser — escreve por baixo do
RLS, que é o comportamento correto para um backfill de backend).

**Dentro do Plano 2a:**
- Seed da propriedade Casa Angelina + os 4 quartos, com os `beds24_*_id` reais.
- Cliente Beds24 (autenticação por invite code → refresh token → access token).
- Lib de mapeamento (Beds24 booking JSON → nossas linhas) + upsert idempotente.
- Backfill paginado de `GET /bookings`, com cursor em `sync_state`.
- Testes: unit do mapeamento (fixtures) + integração de idempotência do backfill.

**Fora (vai para o Plano 2b):**
- Webhook em tempo real e reconciliação por cron como **Edge Functions** (Deno). Exigem Supabase
  CLI/deploy, endpoint público e configuração de webhook no painel Beds24.

## 2. Arquitetura

```
Beds24 (API v2)  ──GET /properties, GET /bookings──►  script Python local (tools/beds24/)
                                                          │  mapeia + upsert
                                                          ▼
                                        Supabase Postgres — casa_angelina.* (conexão direta)
```

- **Conexão ao banco:** reusa `tools/db/apply.py:db_url()` (lê `SUPABASE_DB_URL` do `.supabaseauth`,
  conecta como `postgres`, fura o RLS). Não usa a `service_role` REST key nesta fatia (essa fica
  para as Edge Functions do 2b).
- **Segredos:** o refresh token do Beds24 vive em **`.beds24auth`** (gitignored, mesmo padrão do
  `.supabaseauth`). Nada de token no git nem em código.

## 3. Autenticação no Beds24 (API v2)

Fluxo (base na pesquisa `docs/superpowers/references/beds24-api-v2-research.md`):
1. O dono gera um **invite code** no painel Beds24 (Account → API / `control3.php?pagetype=apiv2`)
   com escopos de leitura: `read:bookings`, `read:properties`, `read:inventory`.
2. Primeira execução: o script troca o code por um **refresh token** via
   `GET /authentication/setup` (header `code:`) e **persiste o refresh token** em `.beds24auth`.
3. Execuções seguintes: o script gera um **access token** curto (~24 h) via
   `GET /authentication/token` (header `refreshToken:`), usado no header `token:` de cada chamada.

O passo manual (gerar o invite code no painel) será instruído ao dono na hora da task de execução
que precisar do token. O refresh token desliza (~30 dias); se expirar, gera-se novo invite code.

## 4. Fluxo do backfill

1. **Seed** (idempotente): garante `properties` (1 linha) + `rooms` (4 linhas) com os ids reais.
2. **Probe:** uma chamada pequena a `GET /bookings` grava o JSON cru num arquivo de scratch
   (gitignored). A doc pública do Beds24 não fecha os nomes exatos de campos de data/ocupação nem
   o shape do envelope de paginação — o mapeamento final é travado contra esse JSON real.
3. **Paginação:** percorre todas as reservas (parâmetros confirmados no probe), aplicando o mapa.
4. **Upsert idempotente** por reserva.
5. **Cursor:** grava `backfill_cursor` / `last_backfill_at` em `sync_state`.

## 5. Mapa de dados (Beds24 → `casa_angelina`)

| Beds24 | Nosso |
|---|---|
| status `New` / `Confirmed` | `reservations.status = confirmed` |
| status `Request` / `Inquiry` | `reservations.status = pending` |
| status `Cancelled` | `reservations.status = cancelled` (não deleta) |
| status `Black` (bloqueio do dono) | linha em **`calendar_blocks`** (`source = beds24`), não é reserva |
| `apiSourceId` 0 / 19 / 46 | `channel` = `direct` / `booking` / `airbnb` (fallback `manual`) |
| `masterId` | `group_ref` (liga casa inteira / multi-quarto) |
| booking id (um por quarto) | `beds24_booking_id` |
| `roomId` | resolve `room_id` por `rooms.beds24_room_id` |
| email / telefone | resolve ou cria `guest` (por email/phone dentro da property) |
| `modifiedTime` | `beds24_modified_at` (guarda da idempotência) |
| payload cru | `reservations.raw_payload` (jsonb) |

Comparação de status é **case-insensitive** (a doc não confirma o casing exato retornado).
Os valores de `apiSourceId` (0/19/46) são confirmados no probe antes de virarem código final.

## 6. Seed (data-driven, não hardcoded)

O script busca `GET /properties` (traz a propriedade e seus roomTypes com os **ids reais** do
Beds24), faz upsert em `properties`/`rooms` casando cada roomType com os 4 nomes canônicos
(ver memória `casa-angelina-quartos`): Quarto Duplo com Varanda, Quarto Triplo com Vista para a
Piscina, Quarto Superior com Cama King-size 1, Quarto Superior com Cama King-size 2. O script
**imprime os ids descobertos** para o dono confirmar, evitando gravar id errado. Se o nome no
Beds24 não casar exato, o script para e reporta em vez de adivinhar.

## 7. Idempotência

- Upsert casa por `beds24_booking_id`. Atualiza a linha **só se** `modifiedTime` do payload for
  mais novo que o `beds24_modified_at` gravado. Nunca duplica nem sobrescreve com dado velho.
- Cancelamento vira `status = cancelled` (não deleta).
- Seed e backfill re-executáveis (upsert em tudo).

## 8. Testes / verificação

- **Unit (núcleo, TDD):** a função pura de mapeamento (booking JSON → dict das nossas linhas),
  com fixtures capturadas no probe. Cobre: os 4 caminhos de status, `Black` → `calendar_blocks`,
  `apiSourceId` → channel, `masterId` → `group_ref`, resolve de room e de guest, guarda de
  `modifiedTime`. Não toca a rede.
- **Integração:** roda o backfill real uma vez; confere a contagem contra o Beds24 e a
  **idempotência** (segunda rodada = 0 duplicatas, nenhuma linha alterada).

## 9. Estrutura de arquivos (proposta)

- `tools/beds24/auth.py` — invite code → refresh token → access token (lê/grava `.beds24auth`).
- `tools/beds24/client.py` — chamadas `GET /properties`, `GET /bookings` (paginação, rate-limit).
- `tools/beds24/mapping.py` — funções puras de mapeamento (Beds24 → nossas linhas). Testável isolado.
- `tools/beds24/upsert.py` — upsert idempotente (usa a conexão do harness).
- `tools/beds24/seed.py` — seed data-driven da property + 4 rooms.
- `tools/beds24/backfill.py` — orquestra probe → paginação → upsert → cursor.
- `tools/beds24/test_mapping.py` — unit do mapeamento (fixtures).
- `tools/beds24/test_backfill.py` — integração/idempotência.

## 10. Ainda em aberto (travados na execução, via probe)

- Nomes exatos de campos de data/ocupação e o shape do envelope de paginação de `GET /bookings`.
- Confirmar que `apiSourceId` é 0/19/46 (Direct/Booking/Airbnb).
- Casing exato dos status retornados (mitigado por comparação case-insensitive).
- Formato do refresh: confirmar TTL do access token e o header exato de refresh no probe de auth.

## Depois deste plano

**Plano 2b:** webhook (Edge Function pública, protegida por segredo) + reconcile (cron) reusando
a mesma lib de mapeamento/upsert. Pré-requisitos: Supabase CLI + deploy de Edge Functions,
endpoint público, e configuração do webhook no painel Beds24 (Settings → Properties → Access →
Booking webhooks).
