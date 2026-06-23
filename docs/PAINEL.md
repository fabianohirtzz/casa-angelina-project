# PAINEL.md — Desenho do painel de gestão (Subprojeto B)

Desenho funcional do **motor de reservas e gestão** da Casa Angelina: o que o painel terá,
tela por tela e funcionalidade por funcionalidade. Base: `INFORMACOES.md` (seções 9 a 12) +
transcrição da reunião (timestamps citados).

> **Fase futura.** Não é estático, depende de channel manager com mensalidade e roda fora do
> GitHub Pages. Este documento define **escopo e funcionalidades** para guiar a escolha de
> ferramenta e a construção. Ainda não define stack técnica nem implementa nada.

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
- Direcionamento preferencial ao **Google Meu Negócio**; opção também para o site.
- Acompanhar status (enviado, respondido).
- Meta: tentar consolidar avaliações de mais de um canal para otimizar visibilidade.

### 4.8 Conteúdo do site (autonomia) — (09:24)
- Editar **fotos** (galeria, ambientes, hero) sem mexer em código.
- Editar textos de seções, comodidades, FAQ.
- Editar políticas (regras da casa, cancelamento).
- Publicar mudanças refletindo no site.

### 4.9 Pagamentos e financeiro — (05:03)
- Pagamento direto integrado (Mercado Pago / PagSeguro / **APP Max**, ~3,9%).
- **Trava de disponibilidade:** o pagamento direto só fecha data efetivamente bloqueada no
  calendário único, para nunca gerar overbooking (ressalva técnica da reunião).
- Registro de valor, taxa e status por reserva.
- Visão de receita por canal e comparativo de taxas (direto vs Airbnb vs Booking).
- Controle do custo recorrente do channel manager.

### 4.10 Integrações (canais) — (03:01, 23:37, 22:49)
- Conexão com **Airbnb** e **Booking** via channel manager.
- Status da sincronização e log de bloqueios.
- Conexões de pagamento (provedor).
- Google Meu Negócio (avaliações).
- Tags de Google Analytics e Search Console; alinhamento de IDs de tracking (Google/Meta) do
  cliente.

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
| **Quarto/Suíte** | id, propriedade_id, nome, capacidade, camas, comodidades | Casa sempre inteira (4 dormitórios), não vendidos avulsos. |
| **Tarifa** | id, propriedade_id, período/temporada, valor diária, mínimo de noites | Preço por temporada. |
| **Disponibilidade** | data, propriedade_id, status, origem | Sincronizada bidirecionalmente. |
| **Reserva** | id, propriedade_id, hóspede_id, check-in, check-out, pessoas, canal, valor, status, pacotes, observações | CRUD manual + automático. |
| **Hóspede** | id, nome, contato, e-mail, histórico | Base para avaliações. |
| **Pacote** | id, propriedade_id, nome, descrição, itens, preço, ativo | Cadastrável e ativável. |
| **Avaliação** | id, reserva_id, canal, status | Pedido automático por e-mail. |
| **Pagamento** | id, reserva_id, provedor, valor, taxa, status | ~3,9% direto. |
| **Usuário** | id, nome, papel, propriedades acessíveis | Admin, operador, parceiro. |

## 7. Integrações externas

| Integração | Função | Status |
|---|---|---|
| Channel manager | Sincroniza Airbnb + Booking + site (núcleo) | Ferramenta a definir (mensalidade). |
| Airbnb | Canal + sincronização | Cadastro a regularizar (nome/telefone/código). |
| Booking | Canal + sincronização | Conta existente. |
| Mercado Pago / PagSeguro / APP Max | Pagamento direto ~3,9% | APP Max recomendada. |
| Google Meu Negócio | Avaliações (preferencial) | Otimizar perfil. |
| Google Analytics + Search Console | Métricas e SEO | Tags por Fabiano. |
| Meta API / Google Ads | Tracking de anúncios | Tracking pelo cliente; alinhar IDs. |

## 8. Decisões técnicas em aberto
- Escolha do **channel manager** (custo mensal x autonomia).
- Escolha do **provedor de pagamento** (APP Max recomendada).
- Stack e hospedagem do painel (fora do GitHub Pages).
- Fluxo de pagamento que respeite a trava de disponibilidade.

## 9. Custos recorrentes a alinhar com o cliente
- Mensalidade do channel manager.
- Taxas de pagamento (~3,9%).
- Cliente ciente para planejamento financeiro.

## 10. Sequência sugerida de construção
1. Regularizar acessos (Airbnb, Google Meu Negócio).
2. Escolher channel manager e provedor de pagamento.
3. Modelar dados multi-propriedade.
4. Calendário único + sincronização bidirecional.
5. Tarifas por temporada + reservas/hóspedes (CRUD).
6. Pagamento direto integrado à trava de disponibilidade.
7. Avaliações automáticas + pacotes.
8. Edição de conteúdo do site + relatórios.
9. Treinamento e vídeos tutoriais.
10. Expansão multi-casa / marketplace.
