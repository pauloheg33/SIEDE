# ⚡ Início Rápido - Evidências SME

Guia para rodar o projeto localmente em **menos de 10 minutos**.

## 📋 Pré-requisitos

Instale antes de começar:

- **Python 3.11+**: [python.org/downloads](https://www.python.org/downloads/)
- **Node.js 18+**: [nodejs.org](https://nodejs.org/)
- **PostgreSQL 14+**: [postgresql.org/download](https://www.postgresql.org/download/)
- **Git**: [git-scm.com](https://git-scm.com/)

## 🚀 Setup em 5 Passos

### 1️⃣ Clone o Repositório

```bash
git clone https://github.com/seu-usuario/evidencias-sme.git
cd evidencias-sme
```

### 2️⃣ Configure o Backend

```bash
# Entre na pasta do backend
cd backend

# Crie ambiente virtual
python -m venv venv

# Ative o ambiente (Windows)
venv\Scripts\activate

# Ative o ambiente (Linux/Mac)
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
copy .env.example .env   # Windows
cp .env.example .env     # Linux/Mac

# Edite o .env com suas configurações
# Mínimo necessário:
# DATABASE_URL=postgresql://postgres:senha@localhost:5432/evidencias_sme
# SECRET_KEY=sua-chave-secreta-aqui
# FRONTEND_URL=http://localhost:3000
```

### 3️⃣ Configure o Banco de Dados

```bash
# Crie o banco (PostgreSQL deve estar rodando)
# Windows (psql)
psql -U postgres -c "CREATE DATABASE evidencias_sme;"

# Linux/Mac
createdb evidencias_sme

# Rode as migrations
alembic upgrade head
```

### 4️⃣ Inicie o Backend

```bash
# Ainda em backend/
uvicorn app.main:app --reload

# Backend rodando em: http://localhost:8000
# Documentação em: http://localhost:8000/docs
```

### 5️⃣ Configure e Inicie o Frontend

**Novo terminal:**

```bash
# Entre na pasta do frontend
cd frontend

# Instale dependências
npm install

# Configure variáveis de ambiente
copy .env.example .env   # Windows
cp .env.example .env     # Linux/Mac

# O .env já vem configurado para localhost:8000

# Inicie o servidor
npm run dev

# Frontend rodando em: http://localhost:3000
```

## ✅ Teste a Aplicação

1. Abra [http://localhost:3000](http://localhost:3000)
2. Clique em "Cadastre-se"
3. Preencha:
   - Nome: Seu Nome
   - Email: seu@email.com
   - Senha: senha123456
4. Clique em "Cadastrar"
5. Você será redirecionado para o Dashboard
6. Crie seu primeiro evento!

## 🐛 Troubleshooting

### Backend não inicia

**Erro: "No module named 'app'"**
```bash
# Certifique-se de estar na pasta backend/
cd backend
```

**Erro: "Database connection failed"**
```bash
# Verifique se PostgreSQL está rodando
# Windows: abra Services.msc e procure por PostgreSQL
# Linux/Mac:
sudo service postgresql status

# Verifique DATABASE_URL no .env
```

**Erro: "Permission denied"**
```bash
# Linux/Mac - dê permissão ao PostgreSQL
sudo -u postgres psql
CREATE DATABASE evidencias_sme;
\q
```

### Frontend não inicia

**Erro: "Cannot find module"**
```bash
# Delete node_modules e reinstale
rm -rf node_modules package-lock.json   # Linux/Mac
rmdir /s node_modules & del package-lock.json   # Windows
npm install
```

**Erro: "Port 3000 is already in use"**
```bash
# Mate o processo na porta 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:3000 | xargs kill
```

### CORS Error

Se aparecer erro de CORS no console do navegador:

1. Verifique se o backend está rodando
2. Confirme `FRONTEND_URL=http://localhost:3000` no backend/.env
3. Reinicie o backend

## 🎯 Próximos Passos

Agora que está rodando localmente:

1. **Explore a API**: [http://localhost:8000/docs](http://localhost:8000/docs)
2. **Leia a documentação**: [docs/](docs/)
3. **Configure Storage**: Para upload de fotos, configure S3/R2 (ver [DEPLOY.md](docs/DEPLOY.md))
4. **Customize**: Altere cores em `frontend/src/styles/global.css`

## 📚 Documentação Completa

- [README.md](README.md) - Visão geral do projeto
- [docs/API.md](docs/API.md) - Documentação da API
- [docs/DEPLOY.md](docs/DEPLOY.md) - Guia de deploy em produção
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) - Guia de desenvolvimento

## 💡 Dicas

**Atalhos úteis:**

```bash
# Backend - Criar novo usuário admin direto no banco
psql evidencias_sme
UPDATE users SET role = 'ADMIN' WHERE email = 'seu@email.com';
\q

# Backend - Reset banco (CUIDADO: apaga tudo!)
alembic downgrade base
alembic upgrade head

# Frontend - Build para produção
npm run build

# Frontend - Preview da build
npm run preview
```

**VSCode:**

Abra o projeto com:
```bash
code .
```

Extensões recomendadas:
- Python
- Pylance
- ESLint
- Prettier

## 🆘 Precisa de Ajuda?

1. Verifique os [Issues](https://github.com/seu-usuario/evidencias-sme/issues)
2. Leia a [documentação completa](docs/)
3. Abra um novo Issue descrevendo o problema

---

**Pronto! Agora você tem o Evidências SME rodando localmente!** 🎉
