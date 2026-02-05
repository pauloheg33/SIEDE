# 🚀 Guia de Deploy

## Backend - Render

### 1. Preparação

1. Crie uma conta em [render.com](https://render.com)
2. Instale o PostgreSQL localmente para testar

### 2. PostgreSQL Database

1. No dashboard do Render, clique em "New +"
2. Selecione "PostgreSQL"
3. Configure:
   - Name: `evidencias-sme-db`
   - Database: `evidencias_sme`
   - User: (automático)
   - Region: escolha a mais próxima
   - PostgreSQL Version: 15
   - Instance Type: Free
4. Clique em "Create Database"
5. Copie a "Internal Database URL" (será usada como `DATABASE_URL`)

### 3. Storage (Cloudflare R2)

#### Opção 1: Cloudflare R2 (Recomendado)

1. Acesse [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Vá em R2 > Create bucket
3. Nome: `evidencias-sme`
4. Clique em "Create bucket"
5. Vá em "Settings" > "R2 API Tokens"
6. Crie um token com permissões de leitura/escrita
7. Copie:
   - Access Key ID
   - Secret Access Key
   - Endpoint URL (formato: `https://account-id.r2.cloudflarestorage.com`)

#### Opção 2: Backblaze B2

1. Acesse [Backblaze B2](https://www.backblaze.com/b2/)
2. Crie um bucket público ou privado
3. Gere uma Application Key
4. Configure endpoint S3-compatible

#### Opção 3: AWS S3

1. Acesse [AWS Console](https://console.aws.amazon.com/s3/)
2. Crie um bucket
3. Configure IAM user com permissões S3
4. Gere Access Key

### 4. Web Service (Backend API)

1. No dashboard do Render, clique em "New +"
2. Selecione "Web Service"
3. Conecte seu repositório GitHub
4. Configure:
   - Name: `evidencias-sme-api`
   - Region: mesma do database
   - Branch: `main`
   - Root Directory: `backend`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Instance Type: Free

5. Configure as Environment Variables (clique em "Advanced"):

```
DATABASE_URL=<seu-postgresql-internal-url>
SECRET_KEY=<gere-uma-chave-aleatoria-segura>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
FRONTEND_URL=https://<seu-usuario>.github.io
S3_ENDPOINT_URL=<seu-r2-endpoint>
S3_ACCESS_KEY_ID=<seu-r2-access-key>
S3_SECRET_ACCESS_KEY=<seu-r2-secret-key>
S3_BUCKET_NAME=evidencias-sme
S3_REGION=auto
ENVIRONMENT=production
```

**Importante**: Para gerar o `SECRET_KEY`, use:
```python
import secrets
print(secrets.token_urlsafe(32))
```

6. Clique em "Create Web Service"
7. Aguarde o deploy (primeira vez pode demorar 5-10 minutos)
8. Copie a URL do serviço (ex: `https://evidencias-sme-api.onrender.com`)

### 5. Verificação do Backend

1. Acesse `https://sua-api.onrender.com/docs`
2. Teste o endpoint `/health`
3. Verifique os logs no dashboard do Render

---

## Frontend - GitHub Pages

### 1. Preparação do Repositório

1. Crie um repositório no GitHub (público ou privado)
2. Faça push do código:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/seu-usuario/evidencias-sme.git
git push -u origin main
```

### 2. Configurar GitHub Pages

1. Vá em Settings > Pages
2. Source: Deploy from a branch
3. Branch: selecione `gh-pages` (será criada automaticamente)
4. Clique em Save

### 3. Configurar Secrets

1. Vá em Settings > Secrets and variables > Actions
2. Clique em "New repository secret"
3. Adicione:
   - Name: `VITE_API_URL`
   - Value: `https://sua-api.onrender.com` (URL do backend)
4. Clique em "Add secret"

### 4. Verificar Workflow

1. O arquivo `.github/workflows/deploy.yml` já está configurado
2. Faça um push para `main`:

```bash
git add .
git commit -m "Configure deploy"
git push
```

3. Vá em Actions > Deploy to GitHub Pages
4. Aguarde o workflow completar
5. O site estará disponível em `https://seu-usuario.github.io/evidencias-sme`

### 5. Atualizar CORS no Backend

1. No Render, abra seu Web Service
2. Edite a variável `FRONTEND_URL`:
   - `FRONTEND_URL=https://seu-usuario.github.io`
3. Salve e aguarde o redeploy

### 6. Testar a Aplicação

1. Acesse `https://seu-usuario.github.io/evidencias-sme`
2. Cadastre um novo usuário
3. Faça login
4. Teste criar um evento

---

## Alternativas de Deploy

### Backend

#### Fly.io

```bash
# Instalar CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
cd backend
fly launch
fly deploy
```

#### Railway

1. Acesse [railway.app](https://railway.app)
2. Conecte GitHub
3. Deploy automático ao fazer push

#### Heroku

```bash
# Login
heroku login

# Criar app
cd backend
heroku create evidencias-sme-api

# Adicionar PostgreSQL
heroku addons:create heroku-postgresql:mini

# Deploy
git push heroku main
```

### Frontend

#### Vercel

```bash
# Instalar CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

#### Netlify

```bash
# Instalar CLI
npm i -g netlify-cli

# Deploy
cd frontend
npm run build
netlify deploy --prod --dir=dist
```

---

## Troubleshooting

### Backend não inicia

1. Verifique os logs no Render
2. Confirme que todas as env vars estão configuradas
3. Teste localmente:
```bash
cd backend
pip install -r requirements.txt
# Configure .env local
alembic upgrade head
uvicorn app.main:app --reload
```

### Erro de CORS

1. Verifique `FRONTEND_URL` no backend
2. Confirme que não há barra final na URL
3. Teste com curl:
```bash
curl -H "Origin: https://seu-usuario.github.io" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS https://sua-api.onrender.com/auth/login
```

### Upload de arquivos falha

1. Verifique credenciais do S3/R2
2. Confirme que o bucket existe
3. Teste permissões:
```python
from app.storage import storage_service
storage_service.upload_file(b"test", "test.txt", "text/plain")
```

### Migration não roda

1. Conecte ao banco:
```bash
psql postgresql://user:pass@host/db
```

2. Rode migration manualmente:
```bash
cd backend
alembic upgrade head
```

3. Se necessário, reset:
```bash
alembic downgrade base
alembic upgrade head
```

---

## Manutenção

### Backup do Banco

```bash
# Render
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

### Atualizar Dependências

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt

# Frontend
cd frontend
npm update
npm audit fix
```

### Monitoramento

- Render: Dashboard > Metrics
- Logs: Dashboard > Logs
- Uptime: Configure em Dashboard > Settings > Health Check Path: `/health`
