# PAINEL.md — Desenho do painel de gestão (Subprojeto B)

Desenho funcional do **motor de reservas e gestão** da Casa Angelina: o que o painel terá,
tela por tela e funcionalidade por funcionalidade. Base: `INFORMACOES.md` (seções 9 a 12) +
transcrição da reunião (timestamps citados).

> **Fase futura.** Não é estático, depende de channel manager com mensalidade e roda fora do
> GitHub Pages. Este documento define **escopo e funcionalidades** para guiar a escolha de
> ferramenta e a construção. Ainda não define stack técnica nem implementa nada.

> **Atualização 2026-07-24:** channel manager definido = **Beds24** (~R$200/mês), revertendo a
> Smoobu (~R$400/mês) por **custo**. Cadastro concluído; Airbnb conectado, Booking conectado
> aguardando aceite da Beds24. Beds24 tem API v2 documentada + webhooks. **TripAdvisor descartado**
> pelo cliente (não entra como canal); **pagamento = sinal online (PIX) + resto no check-in**
> (APP Max descartada; gateway tendendo Mercado Pago/PagSeguro). Tarifas e condições dos 4 quartos
> extraídas em `docs/TARIFAS.md`.

## 1. Objetivo do painel

Central única de gestão dos donos. Quatro metas de negócio que tudo serve:
1. **Reservas diretas** (menos dependência de Airbnb/Booking).
2. **Menos taxas** (pagamento direto ~3,9% vs 15% a 18%).
3. **Zero overbooking** (sincronização bidirecional de datas).
4. **Autonomia total** dos donos (editar tudo sem depender do desenvolvedor), com treinamento
   e vídeos tutoriais.

Princípio de produto: superar sites simples feitos por IA, entregando algo completo,
profissional e fácil de operar.

## 2. Perfis de usuário

| Perfil | Quem | Acesso |
|---|---|---|
| **Administrador** | Edmundo, Bruno (donos) | Tudo: reservas, preços, fotos, pacotes, relatórios, configurações. |
| **Operador** | Eventual recepção/apoio | Reservas e hóspedes, sem configurações sensíveis nem financeiro. `[a confirmar necessidade]` |
| **Parceiro** | Donos de outras casas (fase marketplace) | Apenas a própria propriedade. |
| **Hóspede** | Visitante do site | Não acessa o painel; interage pelo fluxo de reserva no site. |

## 3. Mapa de módulos (telas)

```
Painel Casa Angelina
├── 1. Dashboard (visão geral)
├── 2. Calendário (reservas + disponibilidade)
├── 3. Reservas
├── 4. Hóspedes
├── 5. Tarifas e temporadas
├── 6. Pacotes e serviços
├── 7. Avaliações
├── 8. Conteúdo do site (fotos, textos, comodidades)
├── 9. Pagamentos e financeiro
├── 10. Integrações (canais)
├── 11. Relatórios
├── 12. Propriedades (multi-casa / marketplace)
└── 13. Configurações e usuários
```

## 4. Funcionalidades por módulo

### 4.1 Dashboard
- Resumo do dia: chegadas, saídas, casa ocupada ou livre.
- Próximas reservas e ocupação do mês (taxa de ocupação).
- Avisos: pagamentos pendentes, avaliações a solicitar, mensalidade do channel manager.
- Atalhos para "nova reserva" e "bloquear datas".

### 4.2 Calendário (núcleo operacional) — (09:24)
- **Visão única consolidada** de todos os canais (site, Airbnb, Booking) em um só calendário.
- Cada data mostra **origem** da reserva (cor/etiqueta por canal) e datas bloqueadas.
- **Bloqueio bidirecional automático:** reserva no site bloqueia Airbnb e Booking, e vice-versa.
- Bloqueio manual de datas (manutenção, uso próprio).
- Visões por mês e por temporada; arrastar para criar/editar reserva.

### 4.3 Reservas (CRUD) — (15:55)
- Criar, editar e excluir reservas manualmente.
- Campos: hóspede, check-in, check-out, nº de pessoas, canal de origem, valor, status,
  pacotes adicionados, observações/pedidos especiais.
- Status: pré-reserva, confirmada, paga, hospedada, finalizada, cancelada.
- Aplicar regras da casa automaticamente (check-in 13:00, check-out 10:30 a 11:30, mínimo de
  noites por temporada, sem pets, crianças a partir de 12 anos).
- Vincular pagamento e enviar confirmação ao hóspede.

### 4.4 Hóspedes — (15:55)
- Cadastro com dados de contato e e-mail.
- Histórico de estadias por hóspede.
- Base para disparo automático de avaliação.
- Exportação simples (LGPD: consentimento e dados mínimos).

### 4.5 Tarifas e temporadas — (36:03)
- Preço da diária por **período/temporada** (alta temporada, réveillon, carnaval, feiras,
  datas específicas).
- Mínimo de noites por período.
- Regras de variação de preço (fim de semana, feriados).
- Sincronizar tarifas com os canais quando suportado pela ferramenta.

### 4.6 Pacotes e serviços — (13:07)
- Cadastrar pacotes: nome, descrição, itens, preço, foto, **ativo/inativo**.
- Pacotes-alvo: romântico, lua de mel, aniversário, decoração, réveillon, refeições na casa.
- Marcar serviços de custo adicional (transfer, spa, passeios) como add-ons da reserva.
- Pacotes ativos aparecem automaticamente na página Pacotes do site.

### 4.7 Avaliações — (15:55)
- **Disparo automático** de pedido de avaliação por e-mail ao fim da estadia.
- **Avaliação não é portável entre plataformas.** Cada plataforma só mostra avaliação escrita
  dentro dela; não existe API que importe review do Booking para Google/TripAdvisor/Airbnb.
  Copiar o texto e postar como se fosse o hóspede é fraude (derruba/pune o perfil). O caminho é
  **pedir ao hóspede real** que avalie nos perfis novos.
- **Quem pode avaliar muda por plataforma** (define a estratégia de coleta):
  - Booking / Airbnb: só quem reservou por eles (review verificada por reserva).
  - **Google Meu Negócio**: qualquer pessoa com conta Google, sem reserva. Mais fácil de
    encher e **prioritário para ranqueamento**.
- Estado atual dos perfis: Booking tem avaliações (Comodidades 9,3 / casais 8,9); Google e Airbnb
  estão **zerados** (perfis novos). TripAdvisor descartado pelo cliente.
- Estratégia: o painel dispara o pedido com **link direto do Google** para os hóspedes anteriores
  (começando pelos que já avaliaram bem no Booking).
- Acompanhar status (enviado, respondido) por canal.
- O selo/widget de avaliação só vai ao site **depois** que o perfil tiver nota (ex.: 5 a 10
  reviews); perfil zerado no site passa desconfiança.

### 4.8 Conteúdo do site (autonomia) — (09:24)
- Editar **fotos** (galeria, ambientes, hero) sem mexer em código.
- Editar textos de seções, comodidades, FAQ.
- Editar políticas (regras da casa, cancelamento).
- Publicar mudanças refletindo no site.

### 4.9 Pagamentos e financeiro — (05:03)
- Pagamento direto integrado (Mercado Pago / PagSeguro, ~3,9%): sinal online + resto no check-in.
- **Trava de disponibilidade:** o pagamento direto só fecha data efetivamente bloqueada no
  calendário único, para nunca gerar overbooking (ressalva técnica da reunião).
- Registro de valor, taxa e status por reserva.
- Visão de receita por canal e comparativo de taxas (direto vs Airbnb vs Booking).
- Controle do custo recorrente do channel manager.

### 4.10 Integrações (canais) — (03:01, 23:37, 22:49)
Esta tela **não é um formulário de chaves de Booking/Airbnb** (eles não entregam chave ao dono;
ver 7.2). É um **dashboard de status com semáforos e botões de "Conectar"/autorizar**:
- **Channel manager** (núcleo, = Beds24): 1 token/conta (API v2). Destrava Airbnb + Booking de uma vez.
- Status por canal com semáforo: `conectado` / `desconectado` / `erro`, e log de bloqueios.
- Botão "Conectar" que leva o cliente direto ao fluxo de autorização (OAuth/extranet) quando
  o canal estiver desconectado. O cliente **autoriza**, não cola chave.
- **Gateway de pagamento**: access token (Mercado Pago / PagSeguro). Status ativo/inativo.
- **Google**: ID do Analytics, Search Console, link do Meu Negócio.
- **Links públicos** (só para os CTAs do site, sem segredo): Instagram, Booking, Airbnb.
- O painel **mostra status, nunca o valor das chaves** (mascaradas/criptografadas; ver 7.4).

### 4.11 Relatórios
- Ocupação por período, receita por canal, taxa média, ticket médio.
- Desempenho de pacotes.
- Avaliações coletadas.
- Exportação CSV.

### 4.12 Propriedades (multi-casa / marketplace) — (46:50)
- Cadastro de **múltiplas propriedades** (já nasce preparado, começa com a Casa Angelina).
- Cada casa com seus quartos, tarifas, fotos, pacotes e calendário próprios.
- Visão consolidada para o administrador; visão restrita para parceiros.
- Caminho para o **marketplace regional** (várias casas no mesmo site).

### 4.13 Configurações e usuários
- Dados da empresa, canais de contato, regras da casa padrão.
- Gestão de usuários e permissões (admin, operador, parceiro).
- Modelos de e-mail (confirmação, pedido de avaliação).
- Preferências de notificação.

## 5. Fluxos principais

**Reserva pelo site (direta):**
1. Hóspede escolhe datas no site → 2. Sistema checa o calendário único → 3. Mostra preço da
temporada e pacotes → 4. Pagamento direto (~3,9%) → 5. Data bloqueada no site, Airbnb e Booking
→ 6. Confirmação por e-mail → 7. Ao fim da estadia, pedido de avaliação automático.

**Reserva via plataforma (Airbnb/Booking):**
1. Reserva entra na plataforma → 2. Channel manager bloqueia a data no site e no outro canal →
3. Aparece no calendário com a origem marcada → 4. Mesmo fluxo de avaliação ao fim.

**Bloqueio manual:** admin marca datas no calendário → propaga para todos os canais.

## 6. Modelo de dados (entidades)

| Entidade | Campos principais | Observações |
|---|---|---|
| **Propriedade** | id, nome, descrição, endereço, comodidades, políticas, fotos | Multi-propriedade desde o início. |
| **Quarto/Suíte** | id, propriedade_id, nome, capacidade, camas, comodidades | 4 quartos vendidos individualmente; casa inteira no Réveillon/Carnaval (ver `TARIFAS.md`). |
| **Tarifa** | id, propriedade_id, período/temporada, valor diária, mínimo de noites | Preço por temporada. |
| **Disponibilidade** | data, propriedade_id, status, origem | Sincronizada bidirecionalmente. |
| **Reserva** | id, propriedade_id, hóspede_id, check-in, check-out, pessoas, canal, valor, status, pacotes, observações | CRUD manual + automático. |
| **Hóspede** | id, nome, contato, e-mail, histórico | Base para avaliações. |
| **Pacote** | id, propriedade_id, nome, descrição, itens, preço, ativo | Cadastrável e ativável. |
| **Avaliação** | id, reserva_id, canal, status | Pedido automático por e-mail. |
| **Pagamento** | id, reserva_id, provedor, valor, taxa, status | ~3,9% direto. |
| **Usuário** | id, nome, papel, propriedades acessíveis | Admin, operador, parceiro. |

## 7. Integrações externas

### 7.1 Mapa de integrações

| Integração | Função | Status |
|---|---|---|
| Channel manager (**Beds24**) | Sincroniza Airbnb + Booking + site (núcleo) | **Definido: Beds24** (~R$200/mês; trocou a Smoobu por custo, 2026-07-24). Airbnb conectado; Booking aguardando aceite. |
| Airbnb | Canal + sincronização | Cadastro a regularizar (nome/telefone/código). |
| Booking | Canal + sincronização | Conta existente (tem avaliações). ID propriedade `10779110`. |
| Mercado Pago / PagSeguro | Sinal online (~3,9%) + maquininha no check-in | A escolher; APP Max descartada. |
| Google Meu Negócio | Avaliações (preferencial) | Perfil novo, otimizar e encher. |
| Google Analytics + Search Console | Métricas e SEO | Tags por Fabiano. |
| Meta API / Google Ads | Tracking de anúncios | Tracking pelo cliente; alinhar IDs. |

### 7.2 Como conectam (arquitetura) — decisão tomada

**OTAs não dão chave de API para o dono.** Booking e Airbnb só liberam conectividade para
**parceiros certificados** (channel managers/PMS). Airbnb fechou a API pública; Booking exige
programa de certificação. Virar parceiro direto é inviável para a operação. Logo:

- **Não existe "campo de chave do Booking/Airbnb" no painel** — não há chave para o dono colar.
- Quem segura as conexões com as OTAs é **o channel manager**. O painel fala com **uma coisa
  só**: a API do channel manager (1 token por cliente) + o gateway de pagamento (1 chave).
- A conexão de cada OTA é feita por **autorização do dono** (OAuth/handshake no extranet da
  própria conta dele), uma vez, não por chave copiada. É clicar em "autorizar".

```
Painel  ──API──►  Channel Manager (Beds24)  ──conectividade──►  Booking
                                            ──conectividade──►  Airbnb
Painel  ──API──►  Gateway de pagamento (Mercado Pago / PagSeguro)
```

**TripAdvisor descartado pelo cliente (2026-06-24)** — não entra como canal de venda.

### 7.3 Painel replicável (template para o nicho)

O painel nasce para ser **copiado para outros clientes do mesmo nicho** (pousadas/temporada):

- **Padronizar UM channel manager** para todos os clientes: **Beds24** (~R$200/mês, mais barato
  que a Smoobu ~R$400). O template integra **uma vez** contra a API v2 dele + um gateway.
- **Abstrair atrás de uma interface de provider** (ex.: `ChannelManager.getCalendar()`,
  `.blockDates()`), para trocar de ferramenta depois sem reescrever o painel.
- **Onboarding de cliente novo:** (1) criar a conta dele no channel manager; (2) fazer com ele
  as autorizações de Booking/Airbnb (por chamada de tela); (3) colar token do
  channel manager + chaves do gateway nas configurações; (4) no ar com o mesmo código.
- Objetivo de facilidade: o cliente quase não toca em chave. O provisionamento inicial é seu;
  o que exige o cliente é só o clique de **autorizar** na conta dele (não dá para fazer por ele).

### 7.4 Segurança das credenciais (regra dura)

- **Nenhuma chave/secret no site estático** (subprojeto A). Token de channel manager e gateway
  são backend (subprojeto B). O site de apresentação carrega apenas **links públicos**.
- **Secrets criptografados no servidor**, nunca expostos no front. O painel mostra **status**,
  não o valor da chave (mascarado).

## 8. Decisões técnicas

### Tomadas
- **Arquitetura de integrações:** painel fala só com o channel manager (1 token) + gateway
  (1 chave); sem campo de chave de OTA; OTAs conectadas por autorização do dono (ver 7.2).
- **Painel replicável:** padronizar um channel manager e abstrair atrás de interface de
  provider; integrações viram dashboard de status, não formulário de chaves (ver 7.3).
- **Segurança:** nenhum secret no site estático; secrets criptografados no servidor (ver 7.4).
- **Channel manager:** **Beds24** (~R$200/mês; trocou a Smoobu ~R$400 por custo, 2026-07-24).
- **TripAdvisor descartado** pelo cliente.
- **Pagamento:** sinal online (PIX obrigatório) + resto no check-in (maquininha/PIX presencial);
  o split é lógica do painel, não do gateway. APP Max descartada.

### Em aberto
- **% do sinal** a cobrar online; PIX via Beds24+Stripe (curto prazo) x Mercado Pago no painel próprio.
- Escolha final do **gateway** (Mercado Pago x PagSeguro).
- Stack e hospedagem do painel (fora do GitHub Pages).
- Fluxo de pagamento que respeite a trava de disponibilidade.

## 9. Custos recorrentes a alinhar com o cliente
- Mensalidade do channel manager.
- Taxas de pagamento (~3,9%).
- Cliente ciente para planejamento financeiro.

## 10. Sequência sugerida de construção
1. Regularizar acessos (Airbnb, Google Meu Negócio) e iniciar coleta de avaliações no Google
   com os hóspedes anteriores.
2. Configurar o channel manager (Beds24) e escolher o gateway (Mercado Pago x PagSeguro).
3. Modelar dados multi-propriedade.
4. Calendário único + sincronização bidirecional.
5. Tarifas por temporada + reservas/hóspedes (CRUD).
6. Pagamento direto integrado à trava de disponibilidade.
7. Avaliações automáticas + pacotes.
8. Edição de conteúdo do site + relatórios.
9. Treinamento e vídeos tutoriais.
10. Expansão multi-casa / marketplace.
