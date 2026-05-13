# Catálogo de Produtos e Categorias

**Grupo 2** — Serviços de Redes para Internet
Professor: Rafael Silva Guimarães

## Descrição

Sistema web para gerenciamento de um catálogo de **Produtos** e **Categorias**, implementado com uma arquitetura de microserviços orquestrada por Docker Compose.

A aplicação é composta por 3 containers:

| Serviço | Tecnologia | Descrição |
|---------|------------|-----------|
| **nginx** | NGINX Alpine | Proxy reverso + frontend estático |
| **fastapi** | Python 3.11 + FastAPI | API REST com CRUD completo |
| **postgres** | PostgreSQL 17 | Banco de dados relacional |

## Integrantes

| Nome | Matrícula |
|------|-----------|
| Marcos Lopes Ribeiro | 20241si036 |
| Rafael Zoppé Santos | 20241si021 |
| Thaynara Zamparini Xavier | 20241si025 |

## Tema

**Grupo 2** — Catálogo de Produtos e Categorias

### Entidades

- **Categoria**: id, nome, descricao, criado_em
- **Produto**: id, nome, descricao, preco, estoque, categoria_id, criado_em, atualizado_em

## Arquitetura

```
                    ┌─────────────────────┐
                    │      INTERNET       │
                    └────────┬────────────┘
                             │
                      ┌──────┴──────┐
                      │    NGINX    │  Portas 80/443
                      │  (frontend  │
                      │  + proxy)   │
                      └──────┬──────┘
                             │ /api → proxy_pass
                      ┌──────┴──────┐
                      │   FastAPI   │  Porta 8080
                      │  (backend)  │
                      └──────┬──────┘
                             │
                      ┌──────┴──────┐
                      │ PostgreSQL  │  Porta 5432
                      │   (banco)   │
                      └─────────────┘
```

## Como executar

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado
- [Docker Compose](https://docs.docker.com/compose/install/) instalado

### Subir a aplicação

```bash
docker compose up --build
```

### Acessar

| URL | Descrição |
|-----|-----------|
| <http://localhost> | Frontend (interface web) |
| <https://localhost> | Frontend via HTTPS (certificado autoassinado) |
| <http://localhost/api/docs> | Documentação interativa da API (Swagger) |
| <http://localhost/api/redoc> | Documentação alternativa da API (ReDoc) |

### Parar a aplicação

```bash
docker compose down
```

### Parar e remover volumes (limpar dados)

```bash
docker compose down -v
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

### Criar uma categoria

```bash
curl -X POST http://localhost/api/categorias/ \
  -H "Content-Type: application/json" \
  -d '{"nome": "Eletrônicos", "descricao": "Dispositivos eletrônicos e gadgets"}'
```

### Criar um produto

```bash
curl -X POST http://localhost/api/produtos/ \
  -H "Content-Type: application/json" \
  -d '{"nome": "Smartphone XYZ", "descricao": "Smartphone top de linha", "preco": 2999.90, "estoque": 50, "categoria_id": 1}'
```

### Listar produtos

```bash
curl http://localhost/api/produtos/
```

### Atualizar um produto

```bash
curl -X PUT http://localhost/api/produtos/1 \
  -H "Content-Type: application/json" \
  -d '{"preco": 2499.90, "estoque": 45}'
```

### Deletar um produto

```bash
curl -X DELETE http://localhost/api/produtos/1
```

## Estrutura do Projeto

```
trabalho-docker-servicos-redes/
├── docker-compose.yml          # Orquestração dos serviços
├── .env                        # Variáveis de ambiente
├── README.md                   # Documentação
├── backend/
│   ├── Dockerfile              # Imagem do backend
│   ├── requirements.txt        # Dependências Python
│   └── app/
│       ├── __init__.py
│       ├── main.py             # Aplicação FastAPI
│       ├── database.py         # Conexão com PostgreSQL
│       ├── models.py           # Modelos SQLAlchemy
│       ├── schemas/
│       │   ├── __init__.py
│       │   └── schemas.py      # Schemas Pydantic
│       └── routes/
│           ├── __init__.py
│           ├── categorias.py   # Rotas CRUD de categorias
│           └── produtos.py     # Rotas CRUD de produtos
└── nginx/
    ├── Dockerfile              # Imagem do NGINX
    ├── nginx.conf              # Configuração do proxy reverso
    └── html/
        ├── index.html          # Frontend - estrutura HTML
        ├── style.css           # Frontend - estilos
        └── script.js           # Frontend - lógica JavaScript
```

## Tecnologias Utilizadas

- **Python 3.11** + **FastAPI** — Backend REST API
- **PostgreSQL 16** — Banco de dados relacional
- **NGINX** — Proxy reverso e servidor de arquivos estáticos
- **Docker** + **Docker Compose** — Containerização e orquestração
- **SQLAlchemy** — ORM para Python
- **Pydantic** — Validação de dados
- **HTML/CSS/JavaScript** — Frontend estático

## Diferenciais Implementados

- ✅ HTTPS com certificado autoassinado
- ✅ Healthcheck no container do PostgreSQL
- ✅ Documentação automática da API (Swagger/ReDoc)
- ✅ Arquivo `.env` para configurações
- ✅ Frontend moderno com dark mode
- ✅ Filtro de produtos por categoria
- ✅ Tratamento de erros com mensagens amigáveis
