# Operação dos laboratórios — o que rodar quando

Guia por **situação**, não por arquivo. Cada playbook tem no próprio cabeçalho
a explicação detalhada e o histórico das decisões; aqui está só o mapa.

Todos os comandos pressupõem:

```bash
cd ~/ansible-labs
export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible_vault_pass
```

Sem essa variável, qualquer playbook que leia o vault falha com
`Decryption failed`. O caminho não fica no `ansible.cfg` porque o arquivo é
versionado e um `vault_password_file` inexistente é erro fatal de
configuração — quebraria o CI e a máquina de quem clonasse o repositório.

---

## O dia a dia

| Situação | Comando |
|---|---|
| Ligar um laboratório remotamente | `ansible-playbook acordar.yml -e alvo=lab4` |
| Desligar, avisando quem estiver usando | `ansible-playbook desligar.yml -e alvo=lab4 -e atraso=300` |
| Ver quem está usando antes de desligar | `ansible-playbook desligar.yml -e alvo=lab4 -t verificar` |
| Aplicar o estado declarado | `ansible-playbook estado.yml -e alvo=lab4` |
| Ver o que mudaria, sem mudar | `ansible-playbook estado.yml -e alvo=lab4 --check --diff` |

O `estado.yml` aceita tags para as partes rápidas, quando não se quer esperar
a instalação de pacotes:

- `-t energia` — plano de energia, suspensão, monitor, desligamento diário
- `-t navegadores` — política do Firefox
- `-t aparencia` — papel de parede
- `-t sessao` — logon automático
- `-t pacotes` — software (a parte demorada)

---

## Quando algo não responde

Máquina que não responde pode estar **desligada** ou **mal configurada**, e as
duas produzem o mesmo silêncio. A distinção importa porque as soluções são
opostas: uma volta sozinha na próxima aula, a outra nunca volta.

```bash
ansible-playbook alcance.yml -e alvo=lab4            # o laboratório inteiro
ansible-playbook alcance.yml -e alvo=lab4 --limit 411
```

Ele sonda portas TCP do controlador e classifica. Não usa ping: o firewall do
Windows bloqueia ICMP por padrão em vários perfis.

Foi um caso desses que manteve o **lab5 inteiro fora da automação por tempo
indeterminado** — o inventário o declarava na porta 5986 com transporte
`basic`, o listener HTTPS não existia mais, e nada nunca acusou nada.

---

## Auditoria semanal

Roda sozinha, por `systemd`, em horários escolhidos para coincidir com aulas
— a auditoria só avalia quem está ligado.

| Quando | Labs |
|---|---|
| terça, 15h | lab2, lab6 |
| quarta, 10h | lab1 |
| quarta, 15h | lab4, lab5 |

```bash
systemctl list-timers 'ansible-auditoria*'     # ver o agendamento
ansible-playbook auditoria.yml -e alvo=lab4 -e enviar_email=false   # à mão
ansible-playbook auditoria.yml -t instalar_agendamento -K           # reinstalar
```

**A agenda caduca na virada do semestre.** O Mapa de Salas é refeito e as
disciplinas trocam de laboratório; o agendamento continua no horário velho,
agora vazio, e nada dá erro. O relatório avisa quando a cobertura cai abaixo
de 50%, mas conferir na virada é mais barato que descobrir depois. A skill
`mapa-de-salas` responde qual laboratório tem aula quando.

---

## Inventário e conferência

| Para saber | Comando |
|---|---|
| O que está instalado, e em quantas máquinas | `ansible-playbook inventario_software.yml -e alvo=lab4` |
| Uso de disco e o que dá para recuperar | `ansible-playbook disco.yml -e alvo=lab4` |
| Onde o espaço está, de verdade (demorado) | `ansible-playbook disco.yml -e alvo=lab4 -e detalhado=true` |
| Se a planilha bate com a realidade | `ansible-playbook conferir_planilha.yml -e alvo=lab4` |

O `conferir_planilha.yml` precisa do CSV da aba exportado para
`inventario/planilha-<lab>.csv`. A exportação é manual de propósito: publicar
a planilha na web a tornaria acessível a quem tivesse o link, e ela contém
patrimônios e endereços MAC.

---

## Wake-on-LAN

Funciona, com dois limites que custaram tempo para descobrir:

**O pacote sai do `ppgte-server`, não do controlador.** O controlador está em
`10.102.226.x` e as estações em `10.102.227.0/24`; broadcast dirigido entre
sub-redes é descartado pelo roteador. O `ppgte-server` (`10.102.227.245`) está
dentro do segmento. É o padrão desde 09/09/2026 — se ele cair, o WoL para.

**Não sobrevive a corte de energia.** A placa de rede só responde ao pacote
mágico se continuar energizada em standby. Desligamento por software preserva
isso; disjuntor, queda ou régua desligada, não. Depois de um fim de semana com
corte, é preciso ir ao laboratório apertar o botão.

Antes de coletar MACs, as máquinas precisam estar ligadas:

```bash
ansible-playbook coletar_macs.yml -e alvo=lab4
ansible-playbook macs_planilha.yml -e alvo=todos   # colunas para colar na planilha
```

---

## Instalar ou remover software

O estado declarado cobre o que é padrão do laboratório. Para demanda pontual:

```bash
ansible-playbook site.yaml -e local=lab4 -t apache_netbeans
ansible-playbook site.yaml -e local=lab4 -t tomcat
ansible-playbook postgresql_pgadmin.yml -e local=lab4
ansible-playbook remover_pacote.yml -e alvo=lab4 -e pacote=X          # prévia
ansible-playbook remover_pacote.yml -e alvo=lab4 -e pacote=X -t remover
```

O `remover_pacote.yml` recusa remover pacote que esteja declarado em
`group_vars` — o `estado.yml` o reinstalaria na execução seguinte, e a máquina
ficaria oscilando entre dois estados sem explicação aparente.

---

## Observabilidade — Prometheus e Grafana

A base é o Mac mini **mm2**, em **10.102.227.250**, IP fixo. Prometheus e
Grafana rodam em Docker, com o compose em `~/observabilidade-labs/`.

Não confundir com o **mm01**, outro Mac mini, destinado a assumir como
controlador Ansible. São máquinas diferentes com papéis diferentes.

```
~/observabilidade-labs/
  docker-compose.yml
  prometheus.yml          ← montado como ARQUIVO em /etc/prometheus/prometheus.yml
  targets/                ← montado como PASTA  em /etc/prometheus/targets
    prometheus-targets-lab1.json
    prometheus-targets-lab2.json
    prometheus-targets-lab3.json
```

Grafana em `http://10.102.227.250:3000`, Prometheus em `:9090`.

### Instalar o agente nas estações

```bash
# Windows — lab1, lab2, lab4, lab5, lab6
ansible-playbook windows_exporter.yml -e alvo=lab1

# macOS — lab3
ansible-playbook node_exporter.yml -e alvo=lab3

# só verificar, sem instalar nada
ansible-playbook windows_exporter.yml -e alvo=lab1 -t verificar
```

Cada execução grava `inventario/prometheus-targets-<lab>.json`, a partir do
**inventário** e não de quem respondeu — estação apagada continua sendo alvo
legítimo e aparece como `down`, que é a informação certa. Gerar só com quem
respondeu faria a máquina desligada sumir do monitoramento em vez de aparecer
fora do ar.

### Levar os alvos para o Mac mini

```bash
# na máquina de trabalho
scp ~/ansible-labs/inventario/prometheus-targets-*.json emanoel@10.102.227.250:/tmp/

# no Mac mini
cd ~/observabilidade-labs
sudo mv /tmp/prometheus-targets-*.json targets/
sudo chown 65534:65534 targets/*.json
sudo chmod 644 targets/*.json
```

O `65534` é o UID `nobody`, com que o processo do Prometheus roda dentro do
contêiner. Sem permissão de leitura ele **não falha** — reporta zero alvos,
que na tela é idêntico a "arquivo não encontrado".

Não é preciso editar o `prometheus.yml` nem reiniciar: o `file_sd_configs` usa
glob e relê sozinho a cada 5 minutos.

```yaml
  - job_name: 'laboratorios'
    file_sd_configs:
      - files:
          - '/etc/prometheus/targets/*.json'
        refresh_interval: 5m
```

### Conferir

```bash
docker exec prometheus ls -l /etc/prometheus/targets/    # o contêiner enxerga?
curl -s localhost:9090/api/v1/targets \
  | grep -o '"health":"[a-z]*"' | sort | uniq -c          # quantos up?
```

Os dois degraus separam causas que dão o mesmo sintoma: o primeiro isola
problema de volume, o segundo de configuração ou de rede.

### Painéis

Data source do Grafana: URL **`http://prometheus:9090`** — o nome do serviço na
rede do Docker, nunca `localhost`, que ali seria o próprio contêiner do
Grafana. Painéis prontos: **1860** (Node Exporter Full, lab3) e **14694**
(Windows Exporter, demais laboratórios).

### Quatro armadilhas desta montagem

**Volume de arquivo único esconde a pasta ao lado.** O `prometheus.yml` é
montado como arquivo, não como diretório: o contêiner enxerga só ele dentro de
`/etc/prometheus/`. Qualquer coisa que você ponha em `/etc/prometheus/` do
*host* fica invisível. Por isso `targets/` tem montagem própria no compose.

**A linha de comando do serviço vence o arquivo de configuração.** O MSI do
`windows_exporter` grava o `ENABLED_COLLECTORS` no `ImagePath` do serviço, e
argumento de linha de comando tem precedência sobre o `config.yaml`. Em
21/09/2026 isso custou três rodadas: o arquivo estava correto e era ignorado,
enquanto o serviço morria com a lista congelada no dia da instalação. O
playbook hoje reescreve o `ImagePath` deixando só o `--config.file`.

**Nome de coletor muda entre versões.** `cs` e `logon` existiam e foram
removidos na 0.31; cada um derrubou o serviço na partida com `unknown
collector <nome>`, um de cada vez. Ao trocar a versão do MSI, leia a lista do
próprio binário antes de aplicar:

```bash
ansible lab1 --limit 112 -m win_shell -a '& "C:\Program Files\windows_exporter\windows_exporter.exe" --help'
```

A primeira linha de `--collectors.enabled` traz os padrões daquela versão —
válidos por definição.

**Subir agora não é sobreviver a um reinício.** As três máquinas do piloto
Windows subiram em 18/09 e estavam mortas em 21/09, porque o `cs` só derrubava
o serviço na partida seguinte. O teste que vale é depois de um boot, não logo
após instalar. No lab3 isso está coberto por o serviço ser LaunchDaemon com
`RunAtLoad`, e não `brew services` — que morre no logout do usuário.

### Diagnóstico que quebra impasse

Quando o serviço morre calado, rode o binário em **primeiro plano**: ele
escreve no console o erro que, como serviço, se perde.

```bash
ansible lab1 --limit 112 -m win_shell -a '
$exe = "C:\Program Files\windows_exporter\windows_exporter.exe"
$p = Start-Process -FilePath $exe -ArgumentList "--config.file=""C:\Program Files\windows_exporter\config.yaml""" `
     -NoNewWindow -PassThru -RedirectStandardOutput C:\Temp\we_out.txt -RedirectStandardError C:\Temp\we_err.txt
Start-Sleep -Seconds 6
if (-not $p.HasExited) { "AINDA RODANDO"; $p.Kill() } else { "SAIU com codigo " + $p.ExitCode }
Get-Content C:\Temp\we_out.txt,C:\Temp\we_err.txt -EA SilentlyContinue
'
```

Se em primeiro plano funciona e como serviço não, o problema não é o binário
nem a configuração — é como o serviço foi registrado. No lab3, o equivalente é
`tail -n 15 /var/log/node_exporter.err`.

---

## Três armadilhas que já custaram caro

**O Ansible conecta como `suporte`; quem usa a máquina é o `aluno`.** Todo
instalador resolve o perfil pelo token de segurança com que roda, não pelas
variáveis de ambiente. Software que grava no perfil do usuário vai para o
perfil errado e fica invisível ao aluno. Aconteceu com o Arduino, com o papel
de parede e com a configuração do NetBeans. A saída é instalar para todos os
usuários quando o instalador permitir (`estado_pacotes_args`) ou escrever
direto na chave do aluno (tag `aparencia`).

**Ausência não é conformidade.** Máquina desligada não é avaliada, e um
relatório com duas máquinas vistas e "0 divergências" parece boa notícia sem
ser. Sempre olhe a cobertura antes da conclusão.

**Presente em uma máquina não é padrão do laboratório.** Listas declaradas
derivadas de relatórios sem contagem promoveram a padrão o que era resíduo de
um disco remanejado — e o `estado.yml` propagou para as 25 outras. Hoje o
inventário conta em quantas máquinas cada pacote está, e
`estado_pacotes_pontuais` registra o que foi instalação deliberada numa
máquina só, para a revisão seguinte não refazer a pergunta.
