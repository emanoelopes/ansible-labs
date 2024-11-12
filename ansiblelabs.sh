#!/bin/bash
echo Verificar se existe imagem ansible labs
docker image inspect ansiblelabs:latest > /dev/null 2>&1 && echo yes || echo no
if [ -z "$(docker images -q ansiblelabs:latest 2> /dev/null)" ]; then
  docker build -t ansiblelabs .
  docker-compose up -d
fi
docker run -d \
  --name=ansiblelabs \
  -e PUID=1000 \
  -e PGID=1000 \
  -e TZ=Etc/UTC \
  -e ALLOWED_HOSTS= `#optional` \
  -e APPRISE_ENABLED=False `#optional` \
  -e CSRF_TRUSTED_ORIGINS= `#optional` \
  -e DEBUG=True `#optional` \
  -e DEFAULT_FROM_EMAIL= `#optional` \
  -e EMAIL_HOST= `#optional` \
  -e EMAIL_PORT= `#optional` \
  -e EMAIL_HOST_USER= `#optional` \
  -e EMAIL_HOST_PASSWORD= `#optional` \
  -e EMAIL_USE_TLS= `#optional` \
  -e INTEGRATIONS_ALLOW_PRIVATE_IPS= `#optional` \
  -e PING_EMAIL_DOMAIN= `#optional` \
  -e RP_ID= `#optional` \
  -e SECRET_KEY= `#optional` \
  -e SITE_LOGO_URL= `#optional` \
  -p 8025:8025 \
  -p 2525:2525 `#optional` \
  -v ansible-labs:/home/emanoel/ansible-labs \
  --restart unless-stopped \
  ansiblelabs:latest
