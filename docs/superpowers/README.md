# Painel Casa Angelina (subprojeto B) — índice de plano e estado

Ponto de entrada único para retomar o trabalho do painel em qualquer sessão.

## Documentos

- **Design / spec (fatia 1):** [`specs/2026-07-24-painel-fundacao-dados-beds24-sync-design.md`](specs/2026-07-24-painel-fundacao-dados-beds24-sync-design.md)
  — schema `casa_angelina`, espelhamento Beds24, RLS, testes.
- **Plano 1 (PRONTO para executar):** [`plans/2026-07-24-painel-schema-rls.md`](plans/2026-07-24-painel-schema-rls.md)
  — schema (8 tabelas) + RLS + testes. Executável já, só com o acesso ao banco.
- **Base funcional:** `../PAINEL.md` (13 módulos, modelo de dados, fluxos).

## Estado atual (2026-07-24)

- Site de apresentação **pronto e publicado** em `casaangelina.com.br/preview/` (protegido por
  senha; manutenção pública no root). Deploy via `../../deploy.sh`.
- Channel manager = **Beds24** (API v2). Airbnb conectado; Booking aguardando aceite.
- Supabase (projeto **compartilhado do HD360**, ref `euzmbswywwhmicjlszqw`): acesso validado
  (anon key + conexão direta ao Postgres por IPv6). Schema `casa_angelina` **ainda não criado**.
- Decisões: Beds24 é a fonte da verdade e o Supabase espelha; acesso do painel é híbrido
  (UI lê direto com RLS, escrita/integração via Edge Functions); isolamento por schema + membros.

## Como executar o Plano 1 (subagent-driven)

Numa sessão nova do Claude Code, a partir da raiz do projeto:

```
claude "Execute o plano docs/superpowers/plans/2026-07-24-painel-schema-rls.md usando a skill superpowers:subagent-driven-development — um subagente por task, com revisao entre elas. Contexto no spec docs/superpowers/specs/2026-07-24-painel-fundacao-dados-beds24-sync-design.md. Credenciais do banco em .supabaseauth (local). Pare para meu checkpoint depois de cada migracao aplicada ao banco."
```

Depois da migração, no dashboard do Supabase: **Settings → API → Exposed schemas** → adicionar
`casa_angelina`.

## Plano 2 (pendente — ainda não escrito)

Espelhamento Beds24 → Supabase em Edge Functions (backfill, webhook, reconcile) + seed da
propriedade/quartos com os `beds24_*_id` reais. **Pré-requisitos que faltam:**
- **`service_role` key** do Supabase (Settings → API) — guardar no `.supabaseauth`.
- **Invite code / refresh token** da API v2 do Beds24 (gerar no painel Beds24).
- Setup de deploy de Edge Functions (Supabase CLI).

## Segredos (todos gitignored, local only)

- `.ftpauth` — FTP da ErEhost + senha do preview.
- `.supabaseauth` — URL, anon key e senha temporária do banco Supabase.
- `.deploy/` — hash da senha do preview (basic auth).
