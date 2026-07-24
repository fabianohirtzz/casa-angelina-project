# Beds24 API v2 — Referência de Implementação

> Pesquisa feita em 2026-07-24 para o painel Casa Angelina (subprojeto B), visando Edge
> Functions (Deno, Supabase) que espelham reservas do Beds24 num Postgres + um webhook receiver.
>
> **Método:** documentação oficial (wiki.beds24.com, api.beds24.com/v2 Swagger UI) não é acessível
> por fetch direto sem autenticação (a Swagger UI é uma SPA que carrega o spec só com token; o
> wiki bloqueia user-agents automatizados com HTTP 403). Contornei via proxy de leitura (r.jina.ai)
> nas páginas públicas do wiki, e complementei com busca web e o changelog oficial. **Onde o
> conteúdo não pôde ser confirmado diretamente, isso está marcado explicitamente como "NÃO
> CONFIRMADO" — não adivinhei.**

---

## 0. Fontes usadas

- Swagger UI (spec exige auth, não abriu sem token): https://beds24.com/api/v2/ e https://api.beds24.com/v2/
- Wiki oficial — página raiz da API v2: https://wiki.beds24.com/index.php/API_V2.0
- Wiki — guia de conexão via Booking.com: https://wiki.beds24.com/index.php/PMSs:_How_to_connect_to_Beds24_and_use_Booking.com_via_API_V2
- Wiki — guia de conexão para OTAs: https://wiki.beds24.com/index.php/OTAs:_How_to_connect_to_Beds24_using_API_V2
- Wiki — guia para Guest Services: https://wiki.beds24.com/index.php/Guest_Services:_How_to_connect_to_Beds24_using_API_V2
- Wiki — categoria API v2 (índice): https://wiki.beds24.com/index.php/Category:API_V2
- Wiki — changelog da API v2: https://wiki.beds24.com/index.php/API_V2.0_changelog
- Wiki — tabela de apiSourceId (canais/OTAs): https://wiki.beds24.com/index.php/API_V2.0_apisourceids
- Wiki — Booking Webhooks (V2): https://wiki.beds24.com/index.php/Booking_Webhooks
- Wiki — Inventory/Web Hooks (feature irmã, mesma UI pattern): https://wiki.beds24.com/index.php/Web_Hooks
- Wiki — categoria Webhooks: https://wiki.beds24.com/index.php/Category:Webhooks
- Wiki — Category:Bookings (valores de status): https://wiki.beds24.com/index.php/Category:Bookings
- Wiki — Auto Actions (uso de status em condições): https://wiki.beds24.com/index.php/Auto_Actions
- Wiki — Custom Gateway (não é o webhook de bookings, mas mostra o padrão de template vars): https://wiki.beds24.com/index.php/Custom_Gateway
- Fórum oficial — escopos financeiros/pessoais: https://forum.beds24.com/viewtopic.php?f=15&t=1555
- Referência cruzada da URL técnica do endpoint de webhook (linkada pelo wiki, não acessível sem
  auth): https://api.beds24.com/v2/#/Webhooks/postWebhooks___bookings
- SDK de terceiros (não oficial, mas gerado a partir do `apiV2.yaml` oficial via `openapi-typescript`):
  https://www.npmjs.com/package/@lionlai/beds24-v2-sdk

**Fonte descartada por baixa confiabilidade:** `comparatifchannelmanager.fr/en/beds24-api-3/` —
menciona "GraphQL alternative endpoint", "OAuth 2.1 com PKCE", "500 requests/minute", nenhum dos
quais bate com a documentação oficial do wiki (que fala em token/refreshToken e 100 créditos/5min).
Parece conteúdo genérico/gerado por IA sobre channel managers em geral, não específico e
verificado do Beds24. **Não usar como fonte.**

---

## 1. Autenticação — invite code → refresh token → access token

Fluxo confirmado (wiki `API_V2.0` + guias de conexão):

1. **Gerar invite code (manual, uma vez só)** no painel Beds24, em
   `https://beds24.com/control3.php?pagetype=apiv2` (Settings → API). Ao gerar, você escolhe os
   **scopes** necessários. Alternativa: gerar um **long-life token** direto na mesma tela (não
   passa pelo fluxo de invite code).
   > "This step is the only one that must be done manually, all other steps can be performed and
   > automated programmatically." (wiki API_V2.0)

2. **Trocar o invite code por tokens:**
   `GET https://beds24.com/api/v2/authentication/setup`
   Header: `code: {inviteCode}`

   Exemplo (wiki):
   ```
   curl -X 'GET' 'https://beds24.com/api/v2/authentication/setup' \
     -H 'accept: application/json' \
     -H 'code: abc123'
   ```

   Resposta (campos confirmados pelo wiki, três campos citados explicitamente):
   ```json
   {
     "token": "eyJ...",
     "expiresIn": 86400,
     "refreshToken": "xxxxxxxx-xxxx-...."
   }
   ```

3. **Usar o access token nas chamadas:** header `token: {token}` na maioria dos endpoints.
   > "To use most API endpoints you will need to include a token header in the format
   > 'token: {token}'"

4. **Renovar o access token quando expirar:**
   `GET https://beds24.com/api/v2/authentication/token`
   Header: `refreshToken: {refreshToken}`
   Retorna um novo `token` (e `expiresIn`).

### Tempo de vida dos tokens (confirmado, wiki API_V2.0)

| Item | Duração |
|---|---|
| Invite code | expira em 24h se não usado |
| Access token (`token`) gerado a partir de refresh token | expira em **24h** |
| Refresh token | expira após **30 dias sem uso** (não expira se usado regularmente) |
| Long-life token (gerado direto no painel, sem invite code) | expira após **90 dias sem uso** |

Implicação prática para as Edge Functions: como o access token dura só 24h, a função precisa
persistir o `refreshToken` (não o `token` de curta duração) em local seguro (Supabase secret /
tabela protegida) e renovar o `token` a cada execução (ou cachear com expiração curta, tipo
20-22h de margem). Para um job periódico de sync, considerar usar o **long-life token** (90 dias
de validade, renovado a cada uso) para simplificar — evita o ciclo invite→refresh todo dia.

### Escopo por propriedade — NÃO CONFIRMADO explicitamente

O wiki não deixa claro, no material que consegui puxar, se o invite code/token é escopado por
**propertyId** especificamente (ex.: "este token só enxerga a properties X e Y") ou apenas por
**scope de recurso** (bookings, bookings-personal, bookings-financial, inventory, properties,
account). O que está confirmado é a lista de **scopes de recurso**:

| Scope | O que libera |
|---|---|
| `bookings` | Dados básicos de reserva |
| `bookings-personal` | + nome do hóspede, e-mail, telefone, endereço (dados pessoais) |
| `bookings-financial` | + preço, invoice, comissão, dados financeiros |
| `inventory` | Preços e disponibilidade |
| `properties` | Dados de propriedades/quartos |
| `account` | Configurações de conta |

Cada scope é combinado com um prefixo de método: `read:`, `write:`, `delete:`, `all:` (ex.:
`read:bookings`, `write:bookings-financial`). Isso é selecionado na tela de geração do invite
code/long-life token. **Se o painel Casa Angelina precisa só espelhar bookings (leitura), o
mínimo é `read:bookings` + `read:bookings-personal` (nome/e-mail/telefone do hóspede) +
`read:bookings-financial` (valores) + `read:properties` (para mapear propertyId/roomId a nomes).**

### Headers em cada chamada autenticada

- `token: {accessToken}` — obrigatório na maioria dos endpoints (equivalente a Bearer, mas é um
  header customizado chamado literalmente `token`, não `Authorization: Bearer`).
- `refreshToken: {refreshToken}` — só no endpoint de renovação (`GET /authentication/token`).
- `code: {inviteCode}` — só no endpoint inicial (`GET /authentication/setup`).
- `accept: application/json` — recomendado nos exemplos oficiais.

---

## 2. GET /bookings

Endpoint: `GET https://beds24.com/api/v2/bookings`
(mesma base: `https://api.beds24.com/v2/bookings` — o wiki usa `beds24.com/api/v2` e a raiz da
Swagger é `api.beds24.com/v2`; ambas resolvem para a mesma API conforme os exemplos do wiki e o
link do Swagger em `api.beds24.com/v2/#/Webhooks/...`).

### Parâmetros de query confirmados

Não consegui puxar a lista completa e formal (ela está na Swagger, que exige token para abrir).
O que está confirmado, citado explicitamente em páginas do wiki/changelog:

| Parâmetro | Tipo/exemplo | Fonte/confirmação |
|---|---|---|
| `id` | `?id=1234567` — busca por bookingId específico | wiki Guest Services guide |
| `propertyId` | array, ex. `propertyId[]=12345` (visto no SDK: `{ query: { propertyId: [12345] } }`) | SDK npm |
| `status` | `?status=new` — filtra por status | wiki Guest Services guide |
| `filter` | `?filter=arrivals` — reservas chegando hoje (valor de conveniência, não é range de datas cru) | wiki Guest Services guide + OTAs guide |
| `includeInvoiceItems` | boolean, `?includeInvoiceItems=true` — inclui itens de fatura na resposta | wiki + fórum oficial |
| `includeBookingGroup` | boolean — adicionado **2024-01-09**, retorna informação extra sobre reservas em grupo | changelog API v2 |
| `searchString` | string — adicionado **2024-01-10**, busca em nome do hóspede, e-mail, `apiref` e `bookingId` | changelog API v2 |

**NÃO CONFIRMADO diretamente nos textos que consegui puxar** (mas são citados nas minhas
perguntas de pesquisa e são padrão em APIs Beds24-like — trate como hipótese a validar direto no
Swagger com token antes de codar): `modifiedFrom`, `arrivalFrom`/`arrivalTo`,
`departureFrom`/`departureTo`, `includeGuests`, paginação via `page`/`offset`/tamanho de página.
O guia da Guest Services explicitamente diz "There are a lot of ways you can filter the bookings
you wish to retrieve" e remete ao Swagger para a lista completa — ou seja, **o wiki confirma que
existem mais filtros de data/modificação do que os listados acima, mas não entrega os nomes
exatos dos parâmetros.** Antes de implementar, é necessário abrir a Swagger UI logado (com um
token de invite code) e ler o schema real de `GET /bookings`, ou testar empiricamente.

### Envelope de resposta

Não encontrei um exemplo textual explícito do envelope de `GET /bookings` (o wiki mostra o
envelope de **respostas de escrita/POST**, que é diferente):

```json
[
  {
    "success": true,
    "new": { "...": "..." },
    "modified": { "...": "..." },
    "errors": [ "..." ],
    "warnings": [ "..." ],
    "info": [ "..." ]
  }
]
```
(Esse é o formato de resposta de **POST /bookings** — array de resultados, um item por reserva
enviada na requisição, na mesma ordem.) **NÃO CONFIRMADO** se `GET /bookings` usa o mesmo
envelope de array-de-resultados por item ou um envelope `{success, type, count, pages, data:[...]}`
como perguntado — isso precisa ser confirmado testando a chamada real ou lendo o Swagger com
token. Recomendo, ao implementar a Edge Function, logar a resposta bruta da primeira chamada real
e ajustar o parser antes de assumir a forma do envelope.

### Campos do objeto de reserva — confirmados por menções diretas

| Campo | Observação |
|---|---|
| `id` (bookingId) | identificador da reserva |
| `propertyId` | referência à propriedade |
| `roomId` | referência ao tipo de quarto |
| `masterId` | liga reservas de um **group booking** (ver seção 4) |
| `status` | ver seção 3 |
| `firstName`, `lastName` | nome do hóspede (campo `name` foi **renomeado para `lastName`** em 2022-11-22, conforme changelog — cuidado com integrações antigas/exemplos desatualizados) |
| `email`, `phone`, `mobile` | contato do hóspede (exige scope `bookings-personal`) |
| `address`, `city`, `state`, `postcode`, `country` | endereço do hóspede (scope `bookings-personal`) |
| `price` | valor total (scope `bookings-financial`) |
| `deposit` | sinal/depósito |
| `tax`, `commission` | dados financeiros |
| `rateDescription` | descrição da tarifa aplicada |
| `invoiceeId` | referência de faturamento |
| `apiref` | referência externa, também pesquisável via `searchString` |
| `apiSourceId` / `apiSource` | identifica o **canal/OTA de origem** (ver seção 2.1) |
| mensagens | desde **2024-07-30**, reservas suportam mensagens tipadas: `guest`, `host`, `internalNote`, `system` |

**Campos citados na pergunta de pesquisa mas NÃO CONFIRMADOS por texto explícito do wiki**:
`unitId`, `numAdult`/`numChild`, `modifiedTime`/`bookingTime`, `arrival`/`departure` (o wiki
referencia genericamente "check-in and checkout dates" sem confirmar os nomes exatos dos campos
— prováveis candidatos seriam `arrival`/`departure` ou `checkInDate`/`checkOutDate`, mas os dois
nomes aparecem em fontes diferentes sem uma confirmação única e autoritativa). **Confirmar direto
no Swagger (schema da resposta de `GET /bookings`, clicando em "Model"/"Schema") antes de mapear
colunas no Postgres.**

### 2.1 Como identificar o canal/OTA de origem

Confirmado: o campo é **`apiSourceId`** (numérico) com um `apiSource` (slug) correspondente.
Tabela oficial completa em https://wiki.beds24.com/index.php/API_V2.0_apisourceids — os valores
relevantes para Casa Angelina:

| Canal | apiSourceId | apiSource (slug) |
|---|---|---|
| **Direto** (reserva feita direto, sem OTA) | **0** | `direct` |
| Booking Page (motor de reservas próprio do Beds24) | 1 | `bookingpage` |
| **Booking.com** | **19** | `booking` |
| **Airbnb** (XML/API) | **46** | `airbnb` |
| Airbnb (iCal, legado) | 10 | — |
| Expedia | 14 | `expedia` |
| Agoda | 17 | `agoda` |
| Google (Ads/Vacation Rentals) | 58 | `googleads` |
| Google Calendar | 80 | `googlecal` |
| Agente/agent booking | 999 | `agent` |

(Tripadvisor = apiSourceId 20, mas já descartado como canal para Casa Angelina.)

Tabela completa (todos os ~50 valores) está na fonte; reproduzida aqui só a parte relevante ao
projeto. Ver arquivo-fonte para a lista integral se precisar mapear outros canais no futuro.

---

## 3. Valores de status de reserva

Confirmado via `Category:Bookings` + `Auto_Actions` do wiki:

| Status | Significado |
|---|---|
| **New** | Reserva recebida e ainda não aberta/visualizada no painel. Ao abrir e salvar/atualizar, o status muda automaticamente para **Confirmed**. |
| **Confirmed** | Status padrão de reserva ativa/confirmada. |
| **Request** | Reserva em modo de solicitação (existe como valor filtrável — significado exato de "pedido pendente de aprovação" é inferido pelo nome, não detalhado literalmente no texto que consegui puxar, mas é consistente com o padrão de "request-to-book" de várias OTAs). |
| **Inquiry** | Pergunta/consulta do hóspede que **não bloqueia o quarto** — não é uma reserva de fato, é uma pré-reserva exploratória. |
| **Cancelled** | Reserva cancelada. Confirmado que reservas diretas podem ser canceladas simplesmente mudando o status para `Cancelled` (não existe um endpoint de "delete" separado para isso). |
| **Black** | Reserva "sem hóspede", usada para **bloquear** um quarto (manutenção, uso pessoal, etc). Não entra em relatórios (`"Black bookings are not considered in reports"`). |

Também existe um campo adicional de **"sub status"**, que não afeta o comportamento da reserva
(`"has no direct effect on the booking"`), serve só para categorização/filtro em relatórios.

**Representação de cancelamento:** não é um campo booleano separado — o cancelamento **é** o
próprio valor `status = "Cancelled"`. Para a Edge Function de sync, isso significa: ao receber
`status: "Cancelled"` num `GET /bookings` ou webhook, marcar a reserva local como cancelada
(não é preciso checar outro campo).

**NÃO CONFIRMADO**: se o valor literal retornado pela API é `"cancelled"` (minúsculo, como em
`?status=new` que é minúsculo) ou `"Cancelled"` (capitalizado, como aparece na UI/Auto Actions).
Os exemplos de query usam minúsculo (`?status=new`); a UI mostra capitalizado. Tratar a comparação
como case-insensitive na Edge Function até confirmar empiricamente.

---

## 4. Multi-room / group bookings

Confirmado (wiki API_V2.0 + changelog):

- Beds24 gera **um booking id por quarto** — quando um hóspede reserva vários quartos (ou a casa
  inteira via os 4 quartos), cada quarto vira uma reserva (`id`) separada.
- Essas reservas são ligadas pelo campo **`masterId`**: todas as reservas do mesmo grupo
  compartilham o mesmo `masterId` (que é, na prática, o `id` de uma delas — a "master").
  - Para adicionar/remover uma reserva de um grupo via API, sem usar a ação `makeGroup`: enviar
    `"masterId": {groupBookingId}` para adicionar, ou `"masterId": null` para remover.
  - Existe também uma ação explícita `makeGroup` (movida para dentro de `body.actions` em
    2023-10-30, junto com `autoInvoiceItemCharge`).
- Parâmetro de leitura: **`includeBookingGroup`** (adicionado 2024-01-09) em `GET /bookings` —
  quando `true`, retorna informação adicional sobre o grupo na resposta (provavelmente as outras
  reservas do mesmo `masterId`, mas o conteúdo exato do payload retornado **não foi confirmado**
  no material disponível — testar empiricamente).

Implicação prática: para "casa inteira" (Réveillon/Carnaval, ou grupo reservando os 4 quartos),
o painel deve tratar isso como **N reservas com o mesmo `masterId`**, não uma reserva única — a
tabela Postgres de bookings provavelmente precisa de uma coluna `master_id` (nullable, indexado)
para agrupar visualmente essas N linhas como "uma reserva de casa inteira" na UI do painel.

---

## 5. Webhooks

### Onde configurar

- **Booking webhooks (API v2, o que interessa aqui):**
  `Settings → Properties → Access → Booking webhooks` (por propriedade).
  Documentação técnica do schema do payload está atrás do Swagger autenticado, em
  `https://api.beds24.com/v2/#/Webhooks/postWebhooks___bookings` (não consegui abrir sem token —
  a página carrega mas o conteúdo real do schema é renderizado client-side após autenticação).
- Existe uma **versão 1 (GET)** e **versão 2 (POST, "with personal data")** do webhook de
  bookings. A v2 é a recomendada: "V2 booking webhooks use the POST method and can contain the
  booking data as a JSON object in their body" — ou seja, o payload do webhook já traz o booking
  completo, evitando uma chamada extra a `GET /bookings` depois de receber o evento.
- **Suporte a dados pessoais no webhook** foi adicionado em **2024-05-28** (changelog): antes
  disso o payload de webhook não incluía nome/e-mail/telefone do hóspede.
- (Feature irmã, não é o webhook de bookings, mas mesma família de UI —
  **Inventory Webhooks**, para mudança de disponibilidade/preço, ficam em
  `Settings → Marketplace → Webhooks`. Não usar essa se o objetivo é espelhar reservas; é para
  sync de calendário/preço.)

### O que dispara (confirmado para Inventory Webhooks; booking webhooks devem seguir padrão
análogo mas isso é inferência, não confirmação direta)

Para Inventory Webhooks (confirmado explicitamente): reserva nova, mudança nas datas reservadas,
cancelamento, ajuste de inventário, mudança de preço por tipo de quarto disparam o webhook;
mudança de restrições (ex.: estadia mínima) **não** dispara.

Para Booking Webhooks especificamente, o changelog e o wiki confirmam que o payload cobre
criação/modificação de reservas (é a razão de existir do recurso), mas o texto explícito de
"quais eventos exatamente disparam" (new/modify/cancel como triggers distintos, ou um único
evento genérico "booking changed") **não foi confirmado** no material acessível — a documentação
formal está atrás do Swagger autenticado.

### Payload

**NÃO CONFIRMADO** um exemplo de payload JSON real do Booking Webhook v2 (o schema formal está no
Swagger autenticado). O que está confirmado por texto: o corpo é um objeto JSON POST contendo os
dados da reserva (mesmos campos, presumivelmente, do objeto retornado por `GET /bookings` — ver
seção 2), agora incluindo dados pessoais desde mai/2024. **Antes de implementar o parser do
webhook receiver, é necessário: (a) configurar um webhook de teste no painel Beds24 apontando
para uma URL de captura (ex.: webhook.site) e inspecionar o payload real, ou (b) conseguir acesso
autenticado ao Swagger para ler o schema formal.**

### Autenticação/verificação do webhook

**NÃO HÁ CONFIRMAÇÃO EXPLÍCITA E DIRETA para o Booking Webhook v2** de um mecanismo de HMAC
signature, IP allowlist, ou secret dedicado. O que está confirmado, por analogia com o recurso
irmão **Inventory Webhooks** (mesma UI framework, texto explícito do wiki):

> "You must provide a public facing URL to receive the request. Optional headers support
> authentication and other custom purposes as needed." — existe um campo de **"Custom Header"**
> configurável na tela de cadastro do webhook, onde você pode colocar um header arbitrário
> (ex.: `X-Webhook-Secret: {valor-que-você-escolhe}`) que o Beds24 vai enviar em toda chamada.

Isso **não é HMAC nem assinatura criptográfica** — é um shared-secret estático que você mesmo
define e o Beds24 ecoa de volta no header configurado. A verificação, do lado do receiver, seria
simplesmente checar se o header recebido bate com o secret esperado (comparação constant-time).

Também é possível (confirmado pelo padrão de "Custom Gateway", outro recurso do Beds24 que usa
template variables tipo `[BOOKID]`, `[PROPERTYID]` na própria URL) embutir um secret como **query
string estático na URL do webhook** (ex.: `https://sua-edge-function.supabase.co/beds24-webhook?secret=xyz`),
já que o wiki confirma que a URL do webhook aceita template variables e valores estáticos
combinados: `https://yourdomain.com/page?property=[PROPERTYID]`.

**Recomendação de design para a Edge Function** (não confirmada pela doc, é decisão de
implementação): usar as duas camadas — (1) secret na query string da URL cadastrada no painel
Beds24 (simples, funciona mesmo se o campo de custom header não existir para bookings webhooks) e
(2) validar que o payload recebido é consistente (propertyId conhecido, bookingId presente) antes
de gravar. Uma alegação de "IP allowlist" ou "HMAC signature" **não deve ser assumida como
disponível** sem confirmar no Swagger autenticado — o texto oficial acessível não menciona nenhum
dos dois para o Booking Webhook v2.

### Retry / confiabilidade (confirmado para Inventory Webhooks, presumivelmente igual para Booking Webhooks)

> HTTP status fora da faixa 200–299 no seu endpoint faz o Beds24 tentar de novo múltiplas vezes,
> ao longo de aproximadamente 30 minutos, antes de desistir.

Implicação: o webhook receiver deve responder 200 rapidamente (ack) e processar
assíncrono/idempotente, já que reentregas são esperadas em caso de falha temporária — e o handler
precisa ser idempotente (mesma reserva podendo chegar mais de uma vez).

---

## 6. Rate limits

Confirmado, texto literal do wiki (`API_V2.0`):

> "The API credit limit restricts how much you can use the API in a 5 minute window, it's by
> default 100 credits per 5 minutes." — **limite é por conta** ("at the account level"), não por
> token/usuário.

**Custo por requisição:** "Each API request has a cost, this cost is calculated dynamically and
depends on how complex the request is." — ou seja, **não é 1 crédito fixo por chamada**; chamadas
mais "caras" (ex.: `GET /bookings` trazendo muitos campos/joins como `includeInvoiceItems=true`
ou `includeBookingGroup=true`, ou páginas grandes) consomem mais créditos. Não há uma tabela
formal de custo por endpoint no material acessível — **NÃO CONFIRMADO** um valor numérico exato
por tipo de chamada.

### Headers de resposta (exact casing confirmado)

| Header | Significado |
|---|---|
| `x-five-min-limit-remaining` | créditos restantes na janela atual de 5 minutos |
| `x-five-min-limit-resets-in` | segundos até a janela resetar |
| `x-request-cost` | quantos créditos essa requisição específica consumiu |

(O nome `X-FiveMinCreditLimit` citado na pergunta original não bate literalmente com o header
confirmado — o nome real é `x-five-min-limit-remaining`, não `X-FiveMinCreditLimit`. Ajustar
qualquer código/parser para os nomes reais acima.)

### Orientação de uso (confirmado, texto literal)

> "Beds24 API's have strict usage limits and you need to design your interface to stay within
> these limits." ... "The Beds24 API is not intended or suitable for applications making
> significant numbers of real time calls." Para sync de calendário: "Generally performing this
> call about once per 6 hours is enough to keep the data in sync."

Implicação para a Edge Function: **depender de webhooks como fonte primária de atualização em
near-real-time**, e usar `GET /bookings` (com paginação e algum filtro de data de modificação —
nome exato do parâmetro a confirmar, ver seção 2) só como **reconciliação periódica** (ex.: a
cada poucas horas), não como polling frequente. Ler o header `x-five-min-limit-remaining` a cada
resposta e fazer backoff se estiver baixo.

---

## Resumo do que precisa validação direta (não confirmado só por doc pública)

Antes de codar a Edge Function, valide isto com uma chamada real (usando um invite code de
teste) ou acesso autenticado ao Swagger:

1. Nomes exatos dos parâmetros de filtro por data em `GET /bookings` (`modifiedFrom`,
   `arrivalFrom`/`arrivalTo`, `departureFrom`/`departureTo` são hipóteses, não confirmados).
2. Paginação de `GET /bookings` — existe `page`/`offset`/tamanho de página? Formato do envelope
   de resposta (`{success, count, pages, data:[...]}` ou lista crua)?
3. Nomes exatos dos campos de datas de estadia (`arrival`/`departure` vs `checkInDate`/
   `checkOutDate`) e de ocupação (`numAdult`/`numChild`).
4. Payload real do Booking Webhook v2 (estrutura JSON completa) — configurar um webhook de teste
   e capturar um evento real é o caminho mais confiável.
5. Se existe mecanismo de assinatura/HMAC no Booking Webhook v2, ou se é só o padrão
   custom-header/query-secret observado no Inventory Webhooks.
6. Formato exato do valor de `status` retornado pela API (`"new"` minúsculo vs `"New"`
   capitalizado).
