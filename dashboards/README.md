# Dashboards do Grafana

Cópia versionada dos painéis vivos no Grafana (`http://10.102.227.250:3000`,
ver `docs/operacao.md`). O Grafana é a fonte da verdade — isto aqui é
backup e histórico, não o que é servido.

O nome do arquivo precisa começar com 'dashboard' (`dashboard-<nome>.json`)
— é a exceção que o `.gitignore` abre no `*.json` genérico do repositório.
Sem isso, `git add` aceita silenciosamente mas o arquivo nunca entra no
commit.

## Atualizar o arquivo depois de editar um painel na UI

```bash
curl -s -u admin:'<senha>' http://10.102.227.250:3000/api/dashboards/uid/<uid> \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d['dashboard'], indent=2, ensure_ascii=False))" \
  > dashboards/dashboard-<nome>.json
```

## Publicar este arquivo de volta no Grafana

```bash
curl -s -u admin:'<senha>' -X POST http://10.102.227.250:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d "{\"dashboard\": $(cat dashboards/dashboard-<nome>.json), \"overwrite\": true}"
```

O `datasource.uid` dentro do JSON (`ffyxh5kcfjhtsd`, a data source
"prometheus") é específico desta instância do Grafana. Importar este
arquivo numa instância nova exige ajustar esse uid antes — senão os
painéis sobem sem dado, apontando para uma data source que não existe lá.

## dashboard-visao-labs.json

"Laboratórios — Visão geral": máquinas ligadas, CPU, disco, ociosidade,
conexões web e tráfego de rede, por laboratório (lab1–lab6). As métricas de
ociosidade/conexões vêm do `atividade_estacao.yml` — só aparecem nos labs
onde ele já rodou.
