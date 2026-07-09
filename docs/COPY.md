# COPY.md — Copy completa do site (Subprojeto A)

Texto final do site de apresentação da Casa Angelina, página por página, pronto para ir ao
HTML. Fonte: `INFORMACOES.md`. Sitemap: `casa-angelina-design/LAYOUT.md`.

**Convenções:** a palavra entre _underscores_ vai em itálico verde (Cormorant Garamond) no
título. Eyebrow = sobretítulo em caixa alta. Alt = texto alternativo da imagem.
**Regras de copy (Freela):** sem travessões, sem emojis, números concretos, português do Brasil.

Onde o dado ainda não existe, fica `[definir]` (lista completa no fim, seção 10).

> **Modelo de hospedagem (atualizado 2026-06-22 pela cliente):** a casa **não** é sempre
> alugada inteira. Funciona em duas formas:
> 1. **Quartos individuais** — no resto do ano, cada quarto é reservado separadamente. O
>    hóspede usa as áreas comuns (piscina, jardim, café da manhã) junto com quem está nos
>    outros quartos.
> 2. **Casa inteira** — **só** disponível no **Réveillon** e no **Carnaval** (datas exatas
>    `[a confirmar]`). No resto do ano, um grupo pode ter a casa inteira **reservando os quatro
>    quartos juntos**.
>
> Esta copy substitui a antiga premissa "casa sempre alugada inteira". `INFORMACOES.md`,
> `CLAUDE.md` e a memória do projeto ainda trazem a regra antiga e precisam ser atualizados.

---

## 0. Shell compartilhado (todas as páginas)

### Navegação
- **Marca:** logo Casa Angelina.
- **Links:** Home · A casa · Acomodações · Galeria · Pacotes · Trancoso · Contato
- **CTA do nav:** Reservar

### Rodapé
- **Assinatura:** Casa Angelina. Hospedagem exclusiva em Trancoso, Bahia.
- **Frase de marca:** Do quarto à casa inteira, no ritmo de Trancoso.
- **Reservas:** WhatsApp +55 73 99961-9953 · Booking · Airbnb `[link a confirmar]`
- **Redes:** Instagram @casangelinatrancoso
- **Contato:** Trancoso, Bahia `[endereço completo a definir]` · e-mail `[definir]`
- **Legal:** © Casa Angelina. Todos os direitos reservados.

### Botão flutuante (todas as páginas)
- WhatsApp fixo no canto: "Fale com a gente".

### Meta padrão
- `theme-color` #567332 · favicon `images/favicon.png` · `noindex, nofollow` até aprovação.

---

## 1. HOME (`index.html`)

### 1.1 Hero (vídeo/foto full-bleed)
- **Eyebrow:** TRANCOSO, BAHIA
- **Título:** Sua casa em _Trancoso_
- **Lede:** Uma casa de madeira cercada de mata nativa, a 1,8 km do Quadrado. Fique em um dos
  quartos no dia a dia, ou reúna o seu grupo e tenha a casa inteira só para vocês.
- **Botão primário:** Reservar
- **Botão secundário:** Conhecer a casa
- **Alt:** Fachada da Casa Angelina entre o jardim tropical, com piscina e deck de madeira.

### 1.2 Intro band (duas formas de ficar)
- **Eyebrow:** DUAS FORMAS DE FICAR
- **Título:** Um _quarto_ ou a casa _inteira_
- **Corpo:** Na maior parte do ano você reserva um dos quartos e curte a piscina, o jardim e o
  café da manhã da casa. No Réveillon e no Carnaval, e sempre que o seu grupo reserva os quatro
  quartos juntos, a Casa Angelina fica inteira só para vocês. É o conforto de uma casa de
  verdade, no ritmo da Bahia.
- **Bullets:**
  1. Quartos com café da manhã incluso todas as manhãs
  2. Piscina ao ar livre com bar e vista
  3. Casa inteira no Réveillon, no Carnaval ou reservando tudo
  4. A 1,8 km do Quadrado de Trancoso

### 1.3 A casa (preview)
- **Eyebrow:** OS AMBIENTES
- **Título:** Madeira, água e _mata_
- **Corpo:** Da piscina ao jardim, cada canto foi pensado para desacelerar. Conheça a casa
  por dentro.
- **Blocos:**
  - Piscina e deck — Dias longos à beira d'água, cercado de verde.
  - Sala e varanda — Espaço aberto para reunir todo mundo.
  - Jardim e mata — A natureza de Trancoso encostada na casa.
- **Botão:** Ver a casa por dentro (→ `a-casa.html`)
- **Alt:** Piscina com deck de madeira cercada por vegetação tropical.

### 1.4 Quartos individuais (preview)
- **Eyebrow:** ONDE VOCÊ DESCANSA
- **Título:** Quatro quartos para o seu _descanso_
- **Corpo:** Quartos com ar-condicionado, varanda e banheiro privativo, todos com vista para o
  jardim ou para a piscina. Café da manhã incluso todas as manhãs e as áreas da casa à sua
  disposição.
- **Botão:** Ver os quartos (→ `acomodacoes.html`)

### 1.5 Casa inteira (preview)
- **Eyebrow:** SÓ PARA O SEU GRUPO
- **Título:** A casa _inteira_, sem dividir com ninguém
- **Corpo:** No Réveillon e no Carnaval a casa é alugada só inteira. No resto do ano, junte a
  família ou os amigos, reserve os quatro quartos e tenha piscina, jardim e cozinha só para
  vocês, com privacidade total.
- **Botão:** Como reservar a casa inteira (→ `acomodacoes.html`)

### 1.6 Pacotes (preview)
- **Eyebrow:** ALÉM DA HOSPEDAGEM
- **Título:** Pacotes para _ocasiões_ especiais
- **Corpo:** Decoração romântica, lua de mel, réveillon e refeições na casa. Monte a estadia
  do jeito da sua viagem.
- **Botão:** Ver pacotes (→ `pacotes.html`)

### 1.7 Trancoso (teaser full-bleed, banda escura)
- **Eyebrow:** O LUGAR
- **Título:** _Trancoso_ à sua porta
- **Corpo:** O Quadrado a 1,8 km, a praia dos Nativos a 2,6 km, e o pôr do sol que faz o dia
  parar. A Casa Angelina coloca você perto de tudo que faz Trancoso ser Trancoso.
- **Botão:** Descobrir Trancoso (→ `trancoso.html`)
- **Alt:** Vista aérea de drone da região de Trancoso com mata e mar ao fundo. `[foto a definir]`

### 1.8 Prova social `[exibir só após confirmar uso das notas do Booking]`
- **Eyebrow:** QUEM JÁ FICOU
- **Título:** Bem _avaliada_ por quem chega
- **Corpo:** Comodidades com nota 9,3 e 8,9 para viagem a dois no Booking. Casais e famílias
  destacam a localização e o contato com a natureza.
- `[Nota]` Avaliação não é portável: as notas do Booking ficam no Booking. Selo do **Google** no
  site só **depois** que o perfil tiver reviews (hoje zerado). Por ora, prova social usa o texto
  das notas do Booking (decisão do cliente sobre exibir) + depoimentos. (TripAdvisor descartado.)

### 1.9 Instagram strip
- **Eyebrow:** NO DIA A DIA
- **Título:** Acompanhe no _Instagram_
- **Corpo:** Veja a casa, o jardim e Trancoso pelas nossas lentes.
- **Botão:** @casangelinatrancoso (→ Instagram)

### 1.10 Reservas / CTA
- **Eyebrow:** SUA ESTADIA COMEÇA AQUI
- **Título:** Reserve a Casa Angelina _direto_ com a gente
- **Corpo:** Fale pelo WhatsApp para datas, valores e dúvidas, seja para um quarto ou para a
  casa inteira, ou reserve pelos canais parceiros.
- **Botões:** Reservar pelo WhatsApp · Booking · Airbnb `[link a confirmar]`

### Meta da Home
- **Title:** Casa Angelina | Quartos e casa inteira para temporada em Trancoso, Bahia
- **Description:** Hospedagem exclusiva em Trancoso: uma casa de madeira com piscina, jardim e
  café da manhã, a 1,8 km do Quadrado. Reserve um quarto ou a casa inteira direto pelo WhatsApp.

---

## 2. A CASA (`a-casa.html`)

### 2.1 Hero
- **Eyebrow:** A CASA
- **Título:** Uma casa de _madeira_ e luz
- **Lede:** Estrutura de madeira, paredes claras e jardim por todos os lados. Conheça os
  ambientes da Casa Angelina, um por um.
- **Alt:** Fachada e jardim da Casa Angelina sob a luz da tarde.

### 2.2 Tour de ambientes (blocos alternados)
1. **Piscina e deck** — A piscina com deck de madeira é o coração da casa. Cercada pelo verde,
   com bar, espreguiçadeiras e toalhas, é onde os dias começam e terminam sem pressa.
   Alt: Piscina com deck de madeira e espreguiçadeiras no jardim.
2. **Sala e varanda** — Espaço aberto e ventilado, com a varanda integrando a sala ao jardim.
   Lugar de reunir a família e os amigos.
   Alt: Sala de estar integrada à varanda da Casa Angelina.
3. **Cozinha** — Cozinha completa para preparar suas refeições, ou receber a comida pronta em
   casa quando preferir não cozinhar.
   Alt: Cozinha equipada da Casa Angelina.
4. **Os quartos** — Quatro quartos com ar-condicionado, varanda e banheiro privativo, todos
   com vista para o jardim ou para a piscina.
   Alt: Quarto da Casa Angelina com cama de casal e varanda.
5. **Jardim e mata** — A mata nativa de Trancoso encosta na casa. Rede, sombra e o som dos
   pássaros, com área de estar e espaço para piquenique.
   Alt: Jardim com mata nativa e área de estar ao redor da casa.

### 2.3 O que está incluso
- **Eyebrow:** O QUE ESTÁ INCLUSO
- **Título:** Tudo pronto para _relaxar_
- **Inclusos:** Café da manhã todas as manhãs · Cozinha completa para uso · Piscina ao ar livre
  com bar e vista · Ar-condicionado nos quartos · Wi-Fi gratuito em todas as áreas ·
  Estacionamento gratuito e privativo · Banheiro privativo com secador, toalhas e produtos de
  higiene · TV de tela plana com streaming · Serviço de limpeza diário · Recepção e segurança
  24 horas · Jardim, área de estar e espaço para piquenique.
- **Sob consulta:** Refeições entregues na casa · Transfer do aeroporto · Spa e massagem ·
  Passeios e aluguel de bicicleta.

### 2.4 Regras da casa (resumo)
- Check-in a partir das 13:00, check-out das 10:30 às 11:30 · Crianças a partir de 12 anos ·
  Pets não permitidos.

### 2.5 CTA
- **Título:** Quer ver as datas livres?
- **Botão:** Falar no WhatsApp

### Meta de A casa
- **Title:** A casa | Casa Angelina, Trancoso
- **Description:** Conheça a Casa Angelina por dentro: piscina com deck e bar, cozinha
  completa, quatro quartos com varanda e o jardim com mata nativa de Trancoso.

---

## 3. ACOMODAÇÕES (`acomodacoes.html`)

### 3.1 Head
- **Eyebrow:** ACOMODAÇÕES
- **Título:** Um _quarto_ ou a casa _inteira_
- **Lede:** São quatro quartos, todos com ar-condicionado, varanda, banheiro privativo,
  frigobar, Wi-Fi e vista para o jardim ou a piscina. Reserve um quarto para a sua viagem, ou
  os quatro juntos para ter a casa inteira só do seu grupo.

### 3.2 Quartos individuais
- **Eyebrow:** OS QUARTOS
- **Título:** Quatro quartos para _descansar_ bem
- **Corpo:** Cada quarto é reservado separadamente. As áreas comuns, piscina, jardim e café da
  manhã, são compartilhadas com quem está nos outros quartos.

Cards dos quartos:
1. **Quarto Duplo com Varanda** — 1 cama de casal grande, para 2 pessoas. Varanda própria e
   vista para o jardim ou a piscina. `[metragem a confirmar]`
   Alt: Quarto duplo da Casa Angelina com varanda e vista para o jardim.
   Fotos: `images/quartos/Quarto Duplo com Varanda/`
2. **Quarto Triplo com Vista para a Piscina** — 30 m². 1 cama de solteiro e 1 cama de casal
   grande, para 3 pessoas. Varanda térrea com vista para a piscina e o jardim.
   Alt: Quarto triplo da Casa Angelina com vista para a piscina.
   Fotos: `images/quartos/Quarto Triplo com Vista para a Piscina/`
3. **Quarto Superior com Cama King-size** — 30 m². 1 cama de casal extragrande, para 2 pessoas.
   Varanda, frigobar, área de estar e vista para o jardim e a piscina.
   Alt: Quarto superior da Casa Angelina com cama king-size.
   Fotos: `images/quartos/Quarto Superior 1 com Cama King-size/`
4. **Quarto Superior com Cama King-size** — 30 m². 1 cama de casal extragrande, para 2 pessoas.
   Varanda, frigobar, área de estar e vista para o jardim e a piscina. (segunda unidade)
   Alt: Segundo quarto superior da Casa Angelina com cama king-size.
   Fotos: `images/quartos/Quarto Superior 2 com Cama King-size/`

> Cada quarto acomoda 2 pessoas, exceto o Triplo, que acomoda 3 (1 casal + 1 solteiro). Com a
> casa inteira, são até 12 pessoas.

### 3.3 Casa inteira
- **Eyebrow:** SÓ PARA O SEU GRUPO
- **Título:** A casa _inteira_, sem dividir com ninguém
- **Corpo:** Quando a casa é alugada inteira, os quatro quartos, a piscina, o jardim e a
  cozinha são só do seu grupo, com privacidade completa para até 12 pessoas. Há duas formas de
  garantir a casa inteira:
- **Blocos:**
  - **Réveillon e Carnaval** — Nessas datas a casa é alugada só inteira, sem reserva de quartos
    avulsos. Período exato `[a confirmar]`.
  - **O resto do ano** — Junte a família ou os amigos e reserve os quatro quartos juntos para
    ter a casa toda para vocês.
- **Observação:** Fale com a gente pelo WhatsApp para confirmar datas e o valor da casa inteira.

### 3.4 Sempre incluso
- **Eyebrow:** EM TODA RESERVA
- **Título:** Sempre _incluso_
- **Itens:** Café da manhã · Ar-condicionado · Wi-Fi gratuito · Banheiro privativo · Varanda ·
  Frigobar · Vista para o jardim ou a piscina · Roupa de cama e banho · Serviço de limpeza
  diário.

### 3.5 CTA
- **Título:** Garanta as suas datas
- **Botão:** Reservar pelo WhatsApp

### Meta de Acomodações
- **Title:** Acomodações | Casa Angelina, Trancoso
- **Description:** Quatro quartos com ar-condicionado, varanda e vista para a piscina ou o
  jardim. Reserve um quarto, ou a casa inteira para o seu grupo, com café da manhã incluso.

---

## 4. GALERIA (`galeria.html`)

### 4.1 Head
- **Eyebrow:** GALERIA
- **Título:** A casa em _imagens_
- **Lede:** A casa, a piscina, o jardim e Trancoso vistos de perto e do alto.

### 4.2 Grade
- Fotos profissionais da casa e dos ambientes. `[ensaio a definir]`
- Fotos dos quartos já disponíveis em `images/quartos/`.
- Frames de drone em destaque (span largo). `[drone a definir]`
- Alt por imagem, ex.: "Vista aérea da casa e da piscina cercadas pela mata".

### 4.3 CTA
- **Título:** Quer ver tudo pessoalmente?
- **Botão:** Reservar

### Meta de Galeria
- **Title:** Galeria | Casa Angelina, Trancoso
- **Description:** Fotos da Casa Angelina em Trancoso: a casa, a piscina, o jardim e imagens
  aéreas da região.

---

## 5. PACOTES (`pacotes.html`)

### 5.1 Head
- **Eyebrow:** EXPERIÊNCIAS
- **Título:** Pacotes para _celebrar_
- **Lede:** Some à sua estadia o que fizer a viagem valer ainda mais. Decoração, datas
  especiais e serviços extras, do seu jeito.

### 5.2 Cards de pacotes
Cada card: nome, descrição, o que inclui, preço `[definir]`, botão "Quero este pacote" (WhatsApp).

1. **Romântico** — Decoração e clima a dois para uma noite especial em Trancoso. Inclui `[definir]`.
2. **Lua de mel** — Comece a vida de casados com privacidade: decoração especial e os detalhes
   que tornam a viagem inesquecível. Reserve o quarto ou a casa inteira para a ocasião. Inclui `[definir]`.
3. **Réveillon** — A virada do ano em Trancoso, com a casa alugada só inteira para o seu grupo.
   Inclui `[definir]`.
4. **Decoração para datas especiais** — Aniversário, pedido de casamento ou comemoração, com
   decoração sob medida na casa. Inclui `[definir]`.
5. **Refeições na casa** — Almoço ou jantar entregues na casa, sem precisar cozinhar. Inclui
   `[definir]`.

### 5.3 Monte o seu
- **Título:** Não achou o que queria?
- **Corpo:** Conte o que você imagina para a sua estadia e a gente organiza. Fale no WhatsApp.
- **Botão:** Montar meu pacote

### 5.4 CTA
- **Botão:** Falar no WhatsApp

### Meta de Pacotes
- **Title:** Pacotes | Casa Angelina, Trancoso
- **Description:** Pacotes da Casa Angelina em Trancoso: romântico, lua de mel, réveillon,
  decoração e refeições na casa. Monte a sua estadia.

---

## 6. TRANCOSO (`trancoso.html`)

### 6.1 Hero
- **Eyebrow:** O LUGAR
- **Título:** Bem-vindo a _Trancoso_
- **Lede:** Um dos lugares mais especiais da Bahia, entre o Quadrado histórico e praias de
  águas calmas. A Casa Angelina coloca você no meio de tudo.
- **Alt:** Vista de Trancoso com mata e mar.

### 6.2 Intro da região
- **Corpo:** Trancoso reúne o charme do Quadrado, com suas casas coloridas e a igreja
  histórica, e praias de tirar o fôlego logo abaixo das falésias. Restaurantes ficam a poucos
  minutos da casa, e o ritmo é sempre o de quem está de férias.

### 6.3 O que fazer
- O Quadrado e a igreja histórica `[confirmar nome: São João Batista]`
- Praia dos Nativos e Praia de Trancoso
- Praia dos Coqueiros e Praia de Itapororoca
- Pôr do sol no Quadrado
- Gastronomia local, com restaurantes a cerca de 1,1 km da casa

### 6.4 Distâncias (mini-tabela)
- Quadrado: 1,8 km
- Praia dos Nativos: 2,6 km
- Praia de Trancoso: 2,6 km
- Praia dos Coqueiros: 2,9 km
- Praia de Itapororoca: 3,7 km
- Aeroporto de Porto Seguro: 25 km

### 6.5 CTA
- **Título:** Pronto para conhecer Trancoso?
- **Botão:** Reservar a casa

### Meta de Trancoso
- **Title:** Trancoso | Casa Angelina
- **Description:** O que fazer em Trancoso, Bahia: o Quadrado a 1,8 km, praia dos Nativos a
  2,6 km e a Casa Angelina no meio de tudo.

---

## 7. CONTATO (`contato.html`)

### 7.1 Head
- **Eyebrow:** FALE COM A GENTE
- **Título:** Reserve a _Casa Angelina_
- **Lede:** Tire dúvidas e garanta suas datas direto com a gente, para um quarto ou para a casa
  inteira, ou reserve pelos canais parceiros.

### 7.2 Ações de reserva
- **WhatsApp:** +55 73 99961-9953 — botão "Falar no WhatsApp"
- **Booking** — botão "Reservar no Booking"
- **Airbnb** — `[link a confirmar]`
- **Instagram:** @casangelinatrancoso

### 7.3 Mapa
- Embed do Google Maps com a localização. `[endereço/pin a definir]`

### 7.4 FAQ
1. **Como funciona a hospedagem, por quarto ou casa inteira?** Na maior parte do ano os quartos
   são reservados separadamente, e as áreas comuns são compartilhadas com os outros hóspedes.
   No Réveillon e no Carnaval a casa é alugada só inteira. No resto do ano, dá para ter a casa
   inteira reservando os quatro quartos juntos.
2. **Quando consigo a casa inteira?** No Réveillon e no Carnaval `[datas a confirmar]`, ou em
   qualquer época reservando os quatro quartos para o seu grupo.
3. **O café da manhã está incluso?** Sim, todas as manhãs.
4. **Posso cozinhar na casa?** Sim, a cozinha completa está à disposição. Também é possível
   receber refeições prontas na casa.
5. **Quantas pessoas a casa acomoda?** A casa inteira acomoda até 12 pessoas. Cada quarto é
   para 2 pessoas, menos o Triplo, que recebe 3 (1 cama de casal e 1 de solteiro).
6. **Aceita pets?** Não, pets não são permitidos.
7. **Qual o horário de check-in e check-out?** Entrada a partir das 13:00 e saída das 10:30 às
   11:30.
8. **Crianças são bem-vindas?** Sim, a partir de 12 anos. Não há berços nem camas extras
   disponíveis.
9. **Como faço para reservar?** Fale com a gente pelo WhatsApp para confirmar datas e valores,
   ou reserve pelos canais parceiros.
10. **Qual a política de cancelamento?** `[definir]`
11. **Como chego à casa?** A casa fica a 25 km do Aeroporto de Porto Seguro. `[orientações de
    chegada a definir]`

### 7.5 Informações práticas
- Check-in: a partir das 13:00 · Check-out: das 10:30 às 11:30 · Crianças a partir de 12 anos ·
  Sem berços e camas extras · Pets não permitidos · Pedidos especiais aceitos · Idioma:
  português.

### 7.6 Detalhes de contato
- WhatsApp +55 73 99961-9953 · Instagram @casangelinatrancoso · e-mail `[definir]` · Trancoso,
  Bahia `[endereço a definir]`.

### Meta de Contato
- **Title:** Contato e reservas | Casa Angelina, Trancoso
- **Description:** Reserve a Casa Angelina em Trancoso pelo WhatsApp +55 73 99961-9953 ou pelos
  canais parceiros. Tire dúvidas e confira datas e regras da casa.

---

## 8. Microcopy reutilizável
- **CTAs:** Reservar · Reservar pelo WhatsApp · Falar no WhatsApp · Conhecer a casa · Ver a
  casa por dentro · Ver os quartos · Como reservar a casa inteira · Ver pacotes · Descobrir
  Trancoso · Quero este pacote · Montar meu pacote.
- **WhatsApp link:** `https://wa.me/5573999619953`
- **Mensagem pré-preenchida do WhatsApp:** "Olá! Tenho interesse em reservar a Casa Angelina.
  Pode me passar datas e valores?"

---

## 9. Tom e estilo (lembrete para o build)
Calmo, concreto e específico de Trancoso. Vender a sensação do lugar e fatos reais (quartos com
café da manhã, casa inteira no Réveillon e no Carnaval, 1,8 km do Quadrado), nunca "experiência
inesquecível" genérica. Foco em casais e grupos/famílias (lembrando que a regra é a partir de
12 anos). Deixar sempre claras as duas formas de ficar (quarto x casa inteira). Sem travessões,
sem emojis, português do Brasil.

---

## 10. Pendências de conteúdo (o que falta para 100%)
**Falta o cliente fornecer:**
- Datas exatas do Réveillon e do Carnaval em que a casa é alugada só inteira.
- Preços por temporada, por quarto e da casa inteira; valores/itens de cada pacote.
- Endereço completo e pin do Google Maps.
- E-mail de contato.
- Política de cancelamento.
- Texto institucional / história da casa.
- Ensaio fotográfico profissional e imagens/vídeo de drone.
- Metragem do Quarto Duplo com Varanda.

**Decisões em aberto:**
- Link e nome do Airbnb.
- Nome da igreja (São João Batista vs "São Joaquim Batista" do Booking).
- Exibir ou não as notas do Booking (9,3 / 8,9) como prova social.

**Resolvidas nesta atualização (2026-06-22):**
- São quatro quartos, incluindo duas unidades do Superior King-size (pastas em `images/quartos/`).
- Capacidade: cada quarto acomoda 2 pessoas, exceto o Triplo (3 pessoas, 1 casal + 1 solteiro);
  a casa inteira acomoda até 12 pessoas.
- Triplo e os dois Superior King têm 30 m² cada.
- Modelo de hospedagem: quartos individuais no ano todo; casa inteira no Réveillon/Carnaval ou
  reservando os quatro quartos juntos.
