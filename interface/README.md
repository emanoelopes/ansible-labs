# Ansible Labs Interface

Interfaces TUI (Text User Interface) e GUI Web para facilitar a execução de playbooks Ansible.

## Instalação

### Opção 1: Usando ambiente virtual (Recomendado)

Para sistemas com Python gerenciado externamente (Debian/Ubuntu):

```bash
# Configurar ambiente virtual e instalar dependências
./setup_venv.sh

# Ativar o ambiente virtual
source venv/bin/activate

# Agora você pode executar as interfaces
python run_web.py
python run_tui.py
```

### Opção 2: Instalação manual

1. Criar ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Instalar dependências:
```bash
pip install -r requirements.txt
```

## Uso

### Interface Web (GUI)

Inicie o servidor web que inclui a API e a interface web:

```bash
python run_web.py
```

Ou com opções personalizadas:
```bash
python run_web.py --host 0.0.0.0 --port 8000
```

Acesse no navegador:
- Interface Web: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Interface TUI (Terminal)

Primeiro, certifique-se de que a API está rodando (use `run_web.py`).

Em outro terminal, inicie a TUI:

```bash
python run_tui.py
```

Ou com API em URL diferente:
```bash
ANSIBLE_LABS_API_URL=http://outro-servidor:8000 python run_tui.py
```

## Funcionalidades

### Interface Web
- Seleção visual de hosts e grupos
- Seleção de playbooks e tags
- Visualização de logs em tempo real
- Design moderno e responsivo

### Interface TUI
- Navegação por teclado
- Seleção de hosts/grupos
- Seleção de playbooks e tags
- Visualização de execução com logs
- Funciona via SSH (servidor remoto)

## Estrutura

```
interface/
├── api/              # Backend FastAPI
│   ├── main.py       # API principal
│   ├── models.py     # Modelos Pydantic
│   └── ansible_runner.py  # Wrapper para executar Ansible
├── tui/              # Interface TUI (Textual)
│   ├── main.py       # Aplicação TUI principal
│   └── screens/      # Telas da TUI
├── web/              # Interface Web
│   ├── static/       # CSS e JavaScript
│   └── templates/    # Templates HTML
└── utils/            # Utilitários
    ├── inventory_parser.py   # Parser de inventory.ini
    └── playbook_parser.py   # Parser de playbooks YAML
```

## API Endpoints

- `GET /api/inventory/groups` - Lista grupos
- `GET /api/inventory/hosts` - Lista hosts
- `GET /api/playbooks` - Lista playbooks
- `GET /api/tags` - Lista tags
- `POST /api/execute` - Executa playbook
- `GET /api/executions/{id}` - Status da execução
- `GET /api/executions` - Lista execuções
- `DELETE /api/executions/{id}` - Cancela execução

## Preparação para LLM

Endpoints placeholder para futura integração:
- `POST /api/llm/suggest` - Sugestões de LLM
- `POST /api/llm/explain` - Explicações de LLM

## Notas

- Os logs são salvos em `interface/logs/`
- A API roda na porta 8000 por padrão
- A TUI funciona via SSH e localmente
- A interface web é acessível via navegador


