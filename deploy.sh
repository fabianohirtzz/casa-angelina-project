#!/usr/bin/env bash
# Deploy do site real da Casa Angelina para a subpasta protegida /preview/ na ErEhost.
#
# Uso:
#   ./deploy.sh                 -> paginas + css + js + images (rapido; SEM videos)
#   ./deploy.sh --with-videos   -> inclui os videos (~73MB, sobem devagar)
#   ./deploy.sh --auth          -> (re)envia apenas .htaccess + .htpasswd do preview
#
# Credenciais ficam em .ftpauth (NUNCA commitado, NUNCA sobe para o FTP).
# Allowlist: nunca envia docs/, *.md, qa-*, .git, manutencao.html, prototipo-mapa.html, .ftp*.
# Resiliente: curl com --retry; um arquivo que falhar nao aborta o lote (relatorio no fim).
set -uo pipefail
cd "$(dirname "$0")"
set -a; . ./.ftpauth; set +a
REMOTE_SUB="preview"

up() { # up <arquivo-local> <caminho-remoto-relativo-ao-preview>
  local remote="${2// /%20}"   # codifica espacos para a URL do FTP
  curl -s --ftp-create-dirs --connect-timeout 30 \
       --retry 5 --retry-delay 2 --retry-all-errors \
       -T "$1" --user "$FTP_USER:$FTP_PASS" "ftp://$FTP_HOST/$REMOTE_SUB/$remote"
}

send_auth() {
  echo "-> auth (.htaccess + .htpasswd)"
  up ".deploy/preview.htaccess" ".htaccess" && echo "  ok .htaccess" || echo "  FALHOU .htaccess"
  up ".deploy/preview.htpasswd" ".htpasswd" && echo "  ok .htpasswd" || echo "  FALHOU .htpasswd"
}

WITH_VIDEOS=0; ONLY_AUTH=0
for a in "$@"; do
  case "$a" in
    --with-videos) WITH_VIDEOS=1;;
    --auth) ONLY_AUTH=1;;
  esac
done

if [ "$ONLY_AUTH" = 1 ]; then send_auth; exit 0; fi

send_auth

# Paginas reais (exclui manutencao e prototipo) + assets
FILES=$(ls -1 *.html | grep -viE '^(manutencao|prototipo-mapa)\.html$')
FILES="$FILES
$(find css js -type f)
$(find images -type f -not -path 'images/avaliacoes/*' -not -name '*.psd' -not -name '*.txt' -not \( -path 'images/quartos/*' -name '*.png' \))"
[ "$WITH_VIDEOS" = 1 ] && FILES="$FILES
$(find videos -type f)"

n=0; fail=0; failed_list=""
while IFS= read -r f; do
  [ -z "$f" ] && continue
  f="${f#./}"; f="${f//\\//}"
  n=$((n+1))
  if up "$f" "$f"; then
    printf '  [%d] ok %s\n' "$n" "$f"
  else
    printf '  [%d] FALHOU %s\n' "$n" "$f"
    fail=$((fail+1)); failed_list="$failed_list$f"$'\n'
  fi
done <<< "$FILES"

echo "----"
echo "Enviados: $((n-fail))/$n  |  Falhas: $fail  |  videos: $([ $WITH_VIDEOS = 1 ] && echo sim || echo nao)"
if [ "$fail" -gt 0 ]; then
  echo "Arquivos que falharam:"; printf '%s' "$failed_list"
  exit 1
fi
echo "DEPLOY OK"
