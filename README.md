# Catálogo de Produtos e Categorias — K3s Cluster

**Grupo 2** — Serviços de Redes para Internet
Professor: Rafael Silva Guimarães

## Descrição

Sistema web para gerenciamento de um catálogo de **Produtos** e **Categorias**, portado do Docker Compose para um cluster **K3s** (Kubernetes leve) com 2 VMs, separação de camadas (dados × aplicação) e coleta centralizada de logs com **Grafana Loki**.

## Integrantes

| Nome | Matrícula |
|------|-----------|
| Marcos Lopes Ribeiro | 20241si036 |
| Rafael Zoppé Santos | 20241si021 |
| Thaynara Zamparini Xavier | 20241si025 |

## Orquestrador

**K3s** — distribuição leve de Kubernetes (Apache 2.0, Rancher/SUSE). Ideal para ambientes com recursos limitados, edge computing e laboratório.

## Entidades

- **Categoria**: id, nome, descricao, criado_em
- **Produto**: id, nome, descricao, preco, estoque, categoria_id, criado_em, atualizado_em

## Topologia do Cluster

```
┌──────────────────────────────────┐      ┌──────────────────────────────────┐
│       VM1  —  Camada de Dados    │      │    VM2  —  Camada de Aplicação   │
│       Papel: Agent (worker)      │      │    Papel: Server (control plane) │
│                                  │      │                                  │
│   ┌────────────┐  ┌───────────┐  │      │  ┌─────────┐   ┌─────────────┐  │
│   │ PostgreSQL │  │   Loki    │  │      │  │  NGINX  │   │   FastAPI   │  │
│   │  porta     │  │  porta    │  │      │  │  porta  │   │  porta 8080 │  │
│   │  5432      │  │  3100     │  │      │  │ 80/443  │   │  (interno)  │  │
│   │ (1 réplica)│  │(1 réplica)│  │      │  │(2 répl.)│   │ (2 répl.)   │  │
│   └────────────┘  └───────────┘  │      │  └─────────┘   └─────────────┘  │
│                                  │      │                                  │
│   (sem portas expostas ao host)  │      │   (NGINX exposto via NodePort)   │
│   Label: tier=data               │      │   Label: tier=app                │
└──────────────┬───────────────────┘      └──────────────┬───────────────────┘
               │                                         │
               └──────────── rede interna do cluster ────┘
                           (K3s pod network / flannel)
```

| Serviço    | Tipo K8s     | Réplicas | VM   | nodeSelector  |
|------------|-------------|----------|------|---------------|
| PostgreSQL | StatefulSet | 1        | VM1  | `tier: data`  |
| Loki       | Deployment  | 1        | VM1  | `tier: data`  |
| NGINX      | Deployment  | 2        | VM2  | `tier: app`   |
| FastAPI    | Deployment  | 2        | VM2  | `tier: app`   |

## Estrutura do Projeto

```
trabalho-docker-servicos-redes/
├── README.md                       # Esta documentação
├── docker-compose.yml              # Compose original (Trabalho 01)
├── .env                            # Variáveis de ambiente (dev local)
├── backend/
│   ├── Dockerfile                  # Imagem do backend
│   ├── requirements.txt            # Dependências Python (inclui httpx)
│   └── app/
│       ├── __init__.py
│       ├── main.py                 # Aplicação FastAPI + middleware de logs
│       ├── database.py             # Conexão com PostgreSQL + suporte a Secret
│       ├── models.py               # Modelos SQLAlchemy
│       ├── logger.py               # ← NOVO: cliente HTTP para envio de logs ao Loki
│       ├── schemas/
│       │   ├── __init__.py
│       │   └── schemas.py
│       └── routes/
│           ├── __init__.py
│           ├── categorias.py
│           └── produtos.py
├── nginx/
│   ├── nginx.conf                  # Configuração do proxy reverso
│   └── html/
│       ├── index.html
│       ├── style.css
│       └── script.js
├── loki/
│   └── loki-config.yaml            # ← NOVO: configuração do Grafana Loki
└── k8s/                            # ← NOVO: manifests Kubernetes
    ├── deploy.sh                   # Script de deploy automatizado
    ├── namespace.yaml
    ├── secret-postgres.yaml
    ├── configmap-nginx.yaml
    ├── configmap-loki.yaml
    ├── pvc-postgres.yaml
    ├── pvc-loki.yaml
    ├── statefulset-postgres.yaml
    ├── service-postgres.yaml
    ├── deployment-loki.yaml
    ├── service-loki.yaml
    ├── deployment-fastapi.yaml
    ├── service-fastapi.yaml
    ├── deployment-nginx.yaml
    └── service-nginx.yaml
```

## Configuração do Ambiente Local (.env e Secrets)

### 1. Arquivo `.env` (Desenvolvimento Local)
Antes de rodar o projeto localmente, certifique-se de que possui o arquivo [.env](file:///c:/Users/marcos/trabalho-docker-servicos-redes/.env) na raiz do projeto configurado da seguinte forma:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=[SEU NÚMERO DE MATRÍCULA]
POSTGRES_DB=catalogo_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

### 2. Kubernetes Secret (`secret-postgres.yaml`)
No Kubernetes, as credenciais confidenciais do banco de dados ficam salvas no arquivo [k8s/secret-postgres.yaml](file:///c:/Users/marcos/trabalho-docker-servicos-redes/k8s/secret-postgres.yaml), codificadas em Base64. 

Para codificar o seu número de matrícula no terminal (Linux, macOS ou WSL), execute:
```bash
echo -n 'SUA_MATRICULA' | base64
```
Substitua o valor resultante no campo `POSTGRES_PASSWORD` do arquivo [k8s/secret-postgres.yaml](file:///c:/Users/marcos/trabalho-docker-servicos-redes/k8s/secret-postgres.yaml).

---

## Pré-requisitos para o Cluster Kubernetes (VMs via Vagrant)

Para simular o ambiente com duas VMs Linux distintas comunicando-se em rede local no Windows de forma totalmente offline e compatível com redes restritivas (como a eduroam da faculdade), utilizaremos **Vagrant** integrado ao hypervisor **Oracle VirtualBox**.

1. **Instalar o Oracle VirtualBox**:
   Abra o PowerShell como Administrador e execute:
   ```powershell
   winget install Oracle.VirtualBox
   ```
   *Após concluir a instalação, **reinicie o computador** para carregar os novos drivers de rede do VirtualBox.*

2. **Instalar o Vagrant**:
   No PowerShell do Windows:
   ```powershell
   winget install HashiCorp.Vagrant
   ```
   *Se o comando `vagrant` não for reconhecido após a instalação, reinicie o seu terminal ou execute `$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")`.*

---

## Instruções de Deploy com Vagrant

Siga os passos abaixo usando o terminal do Windows (PowerShell):

### Passo 1: Obter a Imagem do Backend (Docker Hub)
No Kubernetes, o cluster precisa baixar a imagem do backend de algum repositório. O arquivo [k8s/deployment-fastapi.yaml](file:///c:/Users/marcos/trabalho-docker-servicos-redes/k8s/deployment-fastapi.yaml) está configurado para puxar a imagem `marcosrb/catalogo-backend:latest`.

- **Se você não fez alterações locais no backend:** Não é necessário executar este passo. O cluster K3s irá baixar automaticamente a imagem que já está publicada no seu Docker Hub.
- **Se você realizou alterações locais no backend:** Para que o cluster receba as suas modificações, você precisará gerar uma nova imagem e enviá-la para o Docker Hub:
  ```powershell
  cd backend
  docker build -t marcosrb/catalogo-backend:latest .
  docker push marcosrb/catalogo-backend:latest
  ```

### Passo 2: Criar as Duas VMs no Vagrant
No PowerShell do Windows na pasta raiz do projeto, crie e inicialize as duas máquinas virtuais configuradas no `Vagrantfile`:
```powershell
vagrant up
```
Esse comando criará automaticamente:
- `vm1-dados` com IP estático `192.168.56.11`
- `vm2-app` com IP estático `192.168.56.12` e a pasta do projeto compartilhada em `/home/ubuntu/trabalho`.

### Passo 3: Instalar o K3s e Configurar o Cluster

1. **Na VM2 (Server - Control Plane)**:
   Acesse a máquina virtual:
   ```powershell
   vagrant ssh vm2-app
   ```
   Instale o K3s como servidor principal especificando a interface Host-Only:
   ```bash
   curl -sfL https://get.k3s.io | sh -s - server --node-ip=192.168.56.12 --flannel-iface=enp0s8 --advertise-address=192.168.56.12
   ```
   Exiba e copie o token gerado para conectar o outro nó:
   ```bash
   sudo cat /var/lib/rancher/k3s/server/node-token
   ```
   *Copie o token da tela.* Saia da máquina:
   ```bash
   exit
   ```

2. **Na VM1 (Agent - Worker/Dados)**:
   Acesse a máquina virtual:
   ```powershell
   vagrant ssh vm1-dados
   ```
   Instale o K3s como agent apontando para a VM2 e especificando a interface Host-Only (Substitua `<TOKEN>` pelo token copiado no passo anterior):
   ```bash
   curl -sfL https://get.k3s.io | sh -s - agent --server https://192.168.56.12:6443 --token <TOKEN> --node-ip=192.168.56.11 --flannel-iface=enp0s8
   ```
   Saia da máquina:
   ```bash
   exit
   ```

### Passo 4: Rotular (Label) os Nós
Como o banco de dados deve ir para a `vm1-dados` e a aplicação para a `vm2-app`, precisamos identificá-las no cluster.
1. Acesse a `vm2-app`:
   ```powershell
   vagrant ssh vm2-app
   ```
2. Rode os comandos para adicionar as etiquetas (*labels*) exigidas no projeto:
   ```bash
   sudo kubectl label node vm1-dados tier=data
   sudo kubectl label node vm2-app tier=app
   ```

### Passo 5: Executar o Deploy
No terminal da `vm2-app` (`vagrant ssh vm2-app`), execute o script de deploy:
```bash
sudo bash /home/ubuntu/trabalho/k8s/deploy.sh
```

Ou aplicar manualmente (certifique-se de navegar para a pasta do projeto primeiro):

```bash
cd /home/ubuntu/trabalho
sudo kubectl apply -f k8s/namespace.yaml
sudo kubectl apply -f k8s/secret-postgres.yaml
sudo kubectl apply -f k8s/configmap-loki.yaml
sudo kubectl apply -f k8s/configmap-nginx.yaml

# Criar ConfigMap do frontend
sudo kubectl create configmap nginx-html \
  --from-file=nginx/html/index.html \
  --from-file=nginx/html/style.css \
  --from-file=nginx/html/script.js \
  --namespace=catalogo \
  --dry-run=client -o yaml | sudo kubectl apply -f -

sudo kubectl apply -f k8s/pvc-postgres.yaml
sudo kubectl apply -f k8s/pvc-loki.yaml
sudo kubectl apply -f k8s/statefulset-postgres.yaml
sudo kubectl apply -f k8s/service-postgres.yaml
sudo kubectl apply -f k8s/deployment-loki.yaml
sudo kubectl apply -f k8s/service-loki.yaml
sudo kubectl apply -f k8s/deployment-fastapi.yaml
sudo kubectl apply -f k8s/service-fastapi.yaml
sudo kubectl apply -f k8s/deployment-nginx.yaml
sudo kubectl apply -f k8s/service-nginx.yaml
```

## Verificação do Estado dos Serviços

```bash
# Ver todos os pods e em qual nó estão rodando
sudo kubectl get pods -n catalogo -o wide

# Ver todos os services
sudo kubectl get services -n catalogo

# Verificar os logs de um pod específico
sudo kubectl logs -n catalogo deployment/fastapi

# Descrever um pod com problema
sudo kubectl describe pod -n catalogo <nome-do-pod>

# Verificar se o PostgreSQL está pronto
sudo kubectl get statefulset -n catalogo

# Verificar as réplicas do FastAPI e NGINX
sudo kubectl get deployments -n catalogo
```

## Acessar a Aplicação

| URL | Descrição |
|-----|-----------|
| `http://<IP_DA_VM2>:30080` | Frontend (interface web) |
| `https://<IP_DA_VM2>:30443` | Frontend via HTTPS (certificado autoassinado) |
| `http://<IP_DA_VM2>:30080/api/docs` | Documentação interativa da API (Swagger) |

## Consultar Logs no Loki

O Loki roda internamente no cluster. Para acessá-lo, use `port-forward`:

```bash
# Criar um túnel para o Loki (executar na VM2)
sudo kubectl port-forward svc/loki 3100:3100 -n catalogo &
```

### Listar todos os labels disponíveis

```bash
curl http://localhost:3100/loki/api/v1/labels
```

### Consultar logs do FastAPI dos últimos 10 minutos

```bash
curl -G 'http://localhost:3100/loki/api/v1/query_range' \
  --data-urlencode 'query={service="fastapi"}' \
  --data-urlencode 'start='"$(date -d '10 minutes ago' +%s000000000)"'' \
  --data-urlencode 'end='"$(date +%s000000000)"''
```

### Consultar apenas logs de erro

```bash
curl -G 'http://localhost:3100/loki/api/v1/query_range' \
  --data-urlencode 'query={service="fastapi", level="error"}' \
  --data-urlencode 'start='"$(date -d '1 hour ago' +%s000000000)"'' \
  --data-urlencode 'end='"$(date +%s000000000)"''
```

### Consultar logs de inicialização

```bash
curl -G 'http://localhost:3100/loki/api/v1/query_range' \
  --data-urlencode 'query={service="fastapi", event="startup"}' \
  --data-urlencode 'start='"$(date -d '1 hour ago' +%s000000000)"'' \
  --data-urlencode 'end='"$(date +%s000000000)"''
```

## Demonstrar Isolamento de Rede

Para provar que PostgreSQL, Loki e FastAPI **não** estão acessíveis externamente:

```bash
# De uma máquina FORA do cluster, tentar acessar:

# PostgreSQL — deve falhar (timeout/connection refused, pois o service é ClusterIP e sem IP público)
nc -zv <IP_DA_VM1> 5432

# Loki — deve falhar (não há porta exposta externamente, o service é ClusterIP)
curl http://<IP_DA_VM1>:3100/ready

# FastAPI — deve falhar (não há porta exposta externamente, o service é ClusterIP)
curl http://<IP_DA_VM2>:8080/health

# NGINX — deve funcionar (é o único ponto de entrada exposto via NodePort nas portas 30080/30443 da VM2)
curl http://<IP_DA_VM2>:30080/
```

## Rotas da API

### Categorias

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/api/categorias/` | Listar todas as categorias |
| `GET` | `/api/categorias/{id}` | Obter uma categoria |
| `POST` | `/api/categorias/` | Criar nova categoria |
| `PUT` | `/api/categorias/{id}` | Atualizar categoria |
| `DELETE` | `/api/categorias/{id}` | Remover categoria |

### Produtos

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/api/produtos/` | Listar todos os produtos |
| `GET` | `/api/produtos/?categoria_id=1` | Filtrar por categoria |
| `GET` | `/api/produtos/{id}` | Obter um produto |
| `POST` | `/api/produtos/` | Criar novo produto |
| `PUT` | `/api/produtos/{id}` | Atualizar produto |
| `DELETE` | `/api/produtos/{id}` | Remover produto |

## Exemplos de uso com cURL

```bash
# Criar uma categoria
curl -X POST http://<IP_DA_VM2>:30080/api/categorias/ \
  -H "Content-Type: application/json" \
  -d '{"nome": "Eletrônicos", "descricao": "Dispositivos eletrônicos e gadgets"}'

# Criar um produto
curl -X POST http://<IP_DA_VM2>:30080/api/produtos/ \
  -H "Content-Type: application/json" \
  -d '{"nome": "Smartphone XYZ", "descricao": "Smartphone top de linha", "preco": 2999.90, "estoque": 50, "categoria_id": 1}'

# Listar produtos
curl http://<IP_DA_VM2>:30080/api/produtos/
```

## Tecnologias Utilizadas

- **Python 3.11** + **FastAPI** — Backend REST API
- **PostgreSQL 17** — Banco de dados relacional
- **NGINX** — Proxy reverso e servidor de arquivos estáticos
- **Grafana Loki 3.0.0** — Coleta centralizada de logs
- **K3s** — Orquestrador de containers (Kubernetes leve)
- **Docker** — Containerização
- **SQLAlchemy** — ORM para Python
- **Pydantic** — Validação de dados
- **httpx** — Cliente HTTP para envio de logs
- **HTML/CSS/JavaScript** — Frontend estático
