# Docker Setup para Dashboard Trafego

## 📋 Pré-requisitos

- Docker instalado ([download aqui](https://www.docker.com/products/docker-desktop))
- Docker Compose (incluído no Docker Desktop)

## 🚀 Como Usar

### 1. Build da Imagem Docker

```bash
docker build -t dashboard_trafego:latest .
```

Ou usando Docker Compose:

```bash
docker-compose build
```

### 2. Executar o Container

#### Opção 1: Com Docker Compose (Recomendado)

```bash
docker-compose up -d
```

Para ver os logs:

```bash
docker-compose logs -f dashboard
```

Para parar:

```bash
docker-compose down
```

#### Opção 2: Com Docker Direto

```bash
docker run -d \
  --name dashboard_trafego \
  -p 8501:8501 \
  -v "$(pwd)/reports_salvos:/app/reports_salvos" \
  -v "$(pwd)/.streamlit:/app/.streamlit" \
  --restart unless-stopped \
  dashboard_trafego:latest
```

### 3. Acessar a Aplicação

Após o container estar rodando, acesse:

```
http://localhost:8501
```

## 📁 Estrutura de Volumes

- `./reports_salvos:/app/reports_salvos` - Dados persistentes de relatórios
- `./.streamlit:/app/.streamlit` - Configurações e secrets

## 🔑 Variáveis de Ambiente

As credenciais da Meta devem estar configuradas em `.streamlit/secrets.toml`:

```toml
META_APP_ID = "seu_app_id"
META_APP_SECRET = "seu_app_secret"
```

## 🛑 Parar e Remover

```bash
# Parar container
docker-compose down

# Remover imagem
docker rmi dashboard_trafego:latest

# Remover volume (dados)
docker volume prune
```

## 📊 Health Check

O container possui health check automático. Para verificar:

```bash
docker ps
```

O status deve aparecer como "healthy".

## 🐛 Troubleshooting

### Container não inicia
```bash
docker-compose logs dashboard
```

### Porta 8501 já está em uso
```bash
# Altere em docker-compose.yml:
ports:
  - "8502:8501"  # Mapeie para outra porta
```

### Permissões de arquivo
Se tiver problemas com `reports_salvos`, verifique as permissões:

```bash
docker exec dashboard_trafego chmod 777 /app/reports_salvos
```

## 📦 Reconstruir Imagem

Se adicionar novas dependências ao `requirements.txt`:

```bash
docker-compose build --no-cache
docker-compose up -d
```
