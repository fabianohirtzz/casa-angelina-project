# Casa Angelina — Projeto de Site

## O que é
Site da **Casa Angelina**, casa de hospedagem (pousada) em **Trancoso, Bahia**. Objetivo de
negócio: valorizar a casa e o ambiente natural, gerar **reservas diretas** (reduzindo
dependência e taxas de Airbnb/Booking) e dar autonomia de gestão aos donos. Público: viajantes
em busca de hospedagem exclusiva e experiência em Trancoso.

### Modelo de hospedagem (atualizado 2026-06-22)
A casa funciona em **duas formas** (a regra antiga "sempre alugada inteira" foi descartada):
- **Quartos individuais** — na maior parte do ano cada quarto é reservado separadamente; as
  áreas comuns (piscina, jardim, café da manhã) são compartilhadas com os outros hóspedes.
- **Casa inteira** — disponível **só no Réveillon e no Carnaval** (datas exatas a confirmar);
  no resto do ano, um grupo tem a casa inteira **reservando os quatro quartos juntos**.
- **Quartos:** 4 dormitórios. Cada um acomoda 2 pessoas, exceto o Triplo (3 pessoas, 1 cama de
  casal + 1 de solteiro). A casa inteira acomoda **até 12 pessoas**. Há 2 unidades do Superior
  King-size; Triplo e Superiores têm 30 m² cada.

## Cliente & contatos
- **Segmento:** pousada / hospedagem exclusiva (quartos individuais e casa inteira).
- **Localização:** Trancoso, Bahia.
- **Instagram:** https://www.instagram.com/casangelinatrancoso
- **Booking:** https://www.booking.com/hotel/br/casa-angelina.pt-br.html
- **Airbnb:** *(a confirmar — cadastro atual está com nome incorreto, em ajuste pelo cliente)*
- **WhatsApp:** +55 73 99961-9953 *(confirmado pelo cliente — link wa.me: 5573999619953)*
- **Interlocutores:** Edmundo Alves, Bruno Eduardo (donos/parceiros).

## Identidade visual (nova paleta — 2026-06-19)
Mudança de paleta no briefing: **saiu o azul antigo**, entram **tons de verde** que valorizam
a **madeira natural**, a piscina e a mata ao redor. Sensação de natureza e aconchego.

| Token | Hex | Uso |
|---|---|---|
| **Verde escuro** | `#567332` | Títulos, destaques, elementos de ênfase. |
| **Verde claro** | `#d0f0aa` | Backgrounds de seção, textos sobre escuro, botões, ícones. |
| Neutros | *(a definir na design skill)* | Creme/off-white e texto escuro para legibilidade. |

- **Tipografia atual (página de manutenção):** Cormorant Garamond (serifada) + Jost. Reavaliar
  na design skill se mantém esse par para o site definitivo.
- **Paleta antiga (descontinuada):** `#c8df51` limão / `#627e02` oliva — ainda presente na
  página de manutenção; será substituída pela nova paleta ao reconstruir.
- **Fotos/vídeos:** plano de material profissional com **drone**; fotos de alta qualidade são
  decisivas para conversão. Material ideal antes do fim do desenvolvimento.

## Design
- **Design skill:** `casa-angelina-design` (nível de usuário, `~/.claude/skills/`). Acionar
  sempre que tocar UI/copy/motion do projeto. Tema "Trancoso botânico": claro/creme, verdes
  da marca, line-art botânico do logo, foto protagonista, motion suave.
- **Paleta:** verde escuro `#567332` (títulos/ink) + verde claro `#d0f0aa` (fills/botões),
  base creme `#f5efe4`, verde profundo `#2f3d1c` (âncoras/rodapé). Tipografia Cormorant Garamond + Jost.

## Stack
- **Atual:** HTML/CSS/JS estático (one-page de manutenção), publicado em GitHub Pages.
- **Site definitivo:** **multi-página** estático (HTML/CSS/JS), foco em apresentação + CTAs de
  reserva. Sitemap: Home, A casa, Acomodações, Galeria, Pacotes, Trancoso, Contato (ver design skill LAYOUT.md).

## Escopo — dois subprojetos independentes
> Pelo freela-method, escopos de tipos diferentes são tratados como subprojetos separados.

### A) Site de apresentação (FOCO ATUAL — entra no GitHub Pages)
Front-end estático: hero com vídeo/fotos, a casa e os ambientes, galeria (incl. drone),
suítes/acomodações, **pacotes extras** (romântico, lua de mel, réveillon, decoração),
localização/Trancoso, FAQ, integração Instagram, contato e **CTAs de reserva**
(Booking / Airbnb / WhatsApp). SEO on-page e tags de Analytics/Search Console prontos.

### B) Motor de reservas & gestão (FASE FUTURA — backend, fora do GitHub Pages)
Não é estático; depende de ferramenta de sincronização (channel manager) com mensalidade.
Itens levantados no briefing:
- **Reservas diretas integradas** com Airbnb e Booking, com **bloqueio automático de datas**
  nos dois sentidos (site ↔ plataformas) para evitar overbooking.
- **Redução de taxas:** pagamento direto (~3,9% Mercado Pago/PagSeguro/APP Max) vs ~15% Airbnb / ~18% Booking.
- **Painel único:** calendário consolidado, gestão de hóspedes, preços por temporada/diária
  variável, fotos, pets/políticas — com treinamento e vídeos tutoriais.
- **Hóspedes & avaliações:** CRUD de reservas; pedido de avaliação automático por e-mail
  ao fim da estadia, direcionando ao **Google Meu Negócio** (preferência p/ ranqueamento).
- **Expansão/marketplace:** novas suítes e outras casas/parceiros → marketplace regional.

## Hospedagem & repositório
- **Preview (durante o desenvolvimento):** **GitHub Pages** — https://fabianohirtzz.github.io/casa-angelina-project/
  - Fluxo: **commitar sempre** para visualizar as alterações no Pages. Preview com `noindex`.
- **Host final (só após aprovação do cliente):** **ErEhost** (cliente). Página de manutenção
  já publicada em `http://casaangelina.com.br` (2026-06-19).
  - FTP: host `ftp.casaangelina.com.br`, login cai direto na `public_html`.
  - Pendente: **SSL/HTTPS** (cPanel → SSL/TLS Status → Run AutoSSL). HTTPS hoje dá falha de certificado.
- **Repo:** https://github.com/fabianohirtzz/casa-angelina-project.git (conta `fabianohirtzz`).

## Integrações
- CTAs: Booking, Instagram, WhatsApp (Airbnb a confirmar).
- **Analytics/Search Console:** Fabiano entrega tags configuradas; cliente faz o tracking de
  anúncios (Google Ads / Meta) — alinhar IDs.
- Reservas/pagamentos/channel manager: subprojeto B (futuro).

## Regras do projeto (copy — padrão Freela)
Sem travessões, sem emojis, números concretos, português do Brasil.

## Fluxo de trabalho
1. Construir o site de apresentação seção por seção, **commits pequenos**, sempre empurrando
   para o GitHub para visualizar no Pages.
2. **Só depois de aprovado pelo cliente**, subir na ErEhost (FTP / `public_html`).

## Estado atual
- **Fase:** Design → Copy/conteúdo do **site de apresentação** (subprojeto A) mapeada. Briefing
  consolidado, nova paleta e dados do Booking registrados.
- **Entregue:** página de manutenção (one-page, vídeo de fundo, CTAs, `noindex`) no GitHub Pages
  e na ErEhost.
- **Docs de conteúdo:** `docs/INFORMACOES.md` (dossiê de fatos), `docs/COPY.md` (copy completa
  das 7 páginas), `docs/PAINEL.md` (desenho funcional do subprojeto B).
- **Decididas:** design skill `casa-angelina-design`; site **multi-página**; modelo de
  hospedagem **quartos individuais + casa inteira no Réveillon/Carnaval ou reservando tudo**
  (até 12 pessoas); WhatsApp confirmado (+55 73 99961-9953).
- **Decisões em aberto:** datas exatas de Réveillon/Carnaval; link/nome do Airbnb; preços (por
  quarto e casa inteira) e itens dos pacotes; endereço/mapa; e-mail; política de cancelamento;
  ensaio de fotos/drone. Próximo: montar a Home.
- **Assets:** `images/casa1..7.png`, `images/logo*.png`, `images/favicon.png`, `videos/video-desktop.mp4`, `videos/video-mobile.mp4`.
