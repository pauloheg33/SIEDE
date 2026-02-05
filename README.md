# 📚 Evidências SME

Sistema web para Secretaria Municipal de Educação registrar e organizar eventos (formações, premiações, encontros etc.) e agrupar evidências por evento: descrição, fotos, documentos, frequência, observações e histórico.

## 🏗️ Arquitetura

### Frontend
- **Framework**: React 18 + Vite + TypeScript
- **Roteamento**: React Router v6
- **Estado**: Zustand
- **Estilização**: CSS moderno com variáveis
- **Ícones**: Lucide React
- **Deploy**: GitHub Pages

### Backend
- **Framework**: Python FastAPI
- **Banco de dados**: PostgreSQL
- **ORM**: SQLAlchemy + Alembic
- **Autenticação**: JWT (access + refresh tokens)
- **Autorização**: RBAC (Role-Based Access Control)
- **Storage**: S3 compatível (Cloudflare R2, Backblaze B2, AWS S3)
- **Deploy**: Render / Fly.io / Railway

### Segurança
- Senhas: bcrypt
- Tokens JWT com refresh
- CORS configurável
- Rate limiting
- Validação de uploads
- Auditoria completa

## 👥 Perfis e Permissões

### ADMIN
- Gerencia usuários (criar, editar, desativar, alterar papel)
- Pode ver/editar/excluir qualquer evento e qualquer evidência
- Acesso total ao sistema

### TEC_FORMACAO
- Cria eventos relacionados a formações
- Gerencia evidências dos eventos que criou
- Visualiza eventos de outros usuários
- Edita apenas eventos próprios

### TEC_ACOMPANHAMENTO (padrão)
- Cria eventos de acompanhamento/visitas/encontros
- Gerencia evidências dos eventos que criou
- Visualiza eventos de outros usuários
- Edita apenas eventos próprios

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Conta em serviço S3 compatível (Cloudflare R2, Backblaze B2, etc.)

### Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais

# Rodar migrations
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

O backend estará disponível em `http://localhost:8000`
Documentação da API: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o .env com a URL da API

# Iniciar servidor de desenvolvimento
npm run dev
```

O frontend estará disponível em `http://localhost:3000`

## 📦 Estrutura do Projeto

```
/
├── backend/
│   ├── alembic/              # Migrations
│   │   ├── versions/         # Arquivos de migration
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── app/
│   │   ├── routers/          # Endpoints da API
│   │   │   ├── auth.py       # Autenticação
│   │   │   ├── users.py      # Usuários
│   │   │   ├── events.py     # Eventos
│   │   │   ├── files.py      # Arquivos
│   │   │   ├── attendance.py # Frequência
│   │   │   └── notes.py      # Observações
│   │   ├── models.py         # Modelos do banco
│   │   ├── schemas.py        # Schemas Pydantic
│   │   ├── auth.py           # Lógica de autenticação
│   │   ├── storage.py        # Serviço de storage
│   │   ├── audit.py          # Auditoria
│   │   ├── config.py         # Configurações
│   │   ├── database.py       # Conexão com DB
│   │   └── main.py           # App principal
│   ├── requirements.txt
│   ├── Dockerfile
│   └── render.yaml
│
├── frontend/
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   │   └── Layout/       # Layout principal
│   │   ├── pages/            # Páginas
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   └── Dashboard.tsx
│   │   ├── lib/              # Utilitários
│   │   │   └── api.ts        # Cliente da API
│   │   ├── store/            # Estado global (Zustand)
│   │   │   └── authStore.ts
│   │   ├── styles/           # Estilos
│   │   │   └── global.css
│   │   ├── types/            # Tipos TypeScript
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── vite-env.d.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── index.html
│
├── .github/
│   └── workflows/
│       └── deploy.yml        # CI/CD GitHub Actions
│
└── docs/
    ├── API.md                # Documentação da API
    ├── DEPLOY.md             # Guia de deploy
    └── DEVELOPMENT.md        # Guia de desenvolvimento
```

## 🔗 Endpoints da API

### Autenticação
- `POST /auth/register` - Cadastrar novo usuário
- `POST /auth/login` - Fazer login
- `POST /auth/refresh` - Renovar token
- `POST /auth/logout` - Fazer logout
- `GET /auth/me` - Dados do usuário atual

### Usuários (Admin apenas)
- `GET /users` - Listar usuários
- `POST /users` - Criar usuário
- `PUT /users/{id}` - Atualizar usuário
- `PATCH /users/{id}/role` - Alterar papel
- `PATCH /users/{id}/deactivate` - Ativar/desativar

### Eventos
- `GET /events` - Listar eventos (com filtros)
- `POST /events` - Criar evento
- `GET /events/{id}` - Detalhes do evento
- `PUT /events/{id}` - Atualizar evento
- `DELETE /events/{id}` - Deletar evento (admin)

### Arquivos
- `POST /events/{id}/files` - Upload de arquivos
- `GET /events/{id}/files` - Listar arquivos
- `DELETE /events/{id}/files/{fileId}` - Deletar arquivo

### Frequência
- `GET /events/{id}/attendance` - Listar frequência
- `POST /events/{id}/attendance` - Adicionar participante
- `POST /events/{id}/attendance/import` - Importar CSV
- `GET /events/{id}/attendance/export/csv` - Exportar CSV
- `GET /events/{id}/attendance/export/pdf` - Exportar PDF
- `DELETE /events/{id}/attendance/{attendanceId}` - Deletar registro

### Observações
- `GET /events/{id}/notes` - Listar observações
- `POST /events/{id}/notes` - Criar observação
- `PUT /events/{id}/notes/{noteId}` - Atualizar observação
- `DELETE /events/{id}/notes/{noteId}` - Deletar observação

## 🗄️ Modelo de Dados

### users
- `id` (UUID)
- `name` (string)
- `email` (string, unique)
- `password_hash` (string)
- `role` (enum: ADMIN, TEC_FORMACAO, TEC_ACOMPANHAMENTO)
- `is_active` (boolean)
- `created_at` (datetime)

### events
- `id` (UUID)
- `title` (string)
- `type` (enum: FORMACAO, PREMIACAO, ENCONTRO, OUTRO)
- `status` (enum: PLANEJADO, REALIZADO, ARQUIVADO)
- `start_at` (datetime)
- `end_at` (datetime, nullable)
- `location` (string, nullable)
- `audience` (string, nullable)
- `description` (text, nullable)
- `tags` (json array)
- `schools` (json array)
- `created_by` (UUID, FK users)
- `created_at` (datetime)
- `updated_at` (datetime)

### event_files
- `id` (UUID)
- `event_id` (UUID, FK events)
- `kind` (enum: PHOTO, DOC)
- `filename` (string)
- `mime` (string)
- `size` (integer)
- `url` (string)
- `thumbnail_url` (string, nullable)
- `uploaded_by` (UUID, FK users)
- `created_at` (datetime)

### attendance
- `id` (UUID)
- `event_id` (UUID, FK events)
- `person_name` (string)
- `person_role` (string, nullable)
- `school` (string, nullable)
- `present` (boolean)
- `created_at` (datetime)

### event_notes
- `id` (UUID)
- `event_id` (UUID, FK events)
- `text` (text)
- `created_by` (UUID, FK users)
- `created_at` (datetime)
- `updated_at` (datetime)

### audit_logs
- `id` (UUID)
- `user_id` (UUID, FK users)
- `action` (string)
- `entity` (string)
- `entity_id` (string)
- `metadata` (json)
- `created_at` (datetime)

## 🚢 Deploy

### Backend (Render)

1. Crie uma conta em [render.com](https://render.com)
2. Crie um PostgreSQL database
3. Crie um Web Service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Configure as variáveis de ambiente:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `FRONTEND_URL`
   - `S3_*` (credenciais do storage)

### Frontend (GitHub Pages)

1. Configure o repositório no GitHub
2. Ative GitHub Pages em Settings > Pages
3. Configure os secrets:
   - `VITE_API_URL`: URL do backend no Render
4. Faça push para `main` - o deploy é automático

## 🔒 Variáveis de Ambiente

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/evidencias_sme
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
FRONTEND_URL=https://your-username.github.io
S3_ENDPOINT_URL=https://your-account.r2.cloudflarestorage.com
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=evidencias-sme
S3_REGION=auto
ENVIRONMENT=development
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 📝 MVP 1 - Primeira Entrega

✅ Cadastro/login/roles  
✅ Criar/listar/editar evento  
✅ Upload fotos + galeria com thumbnails  
✅ Upload documentos  
✅ Frequência simples (manual + export CSV/PDF)  
✅ Deploy frontend (GitHub Pages)  
✅ Deploy backend (Render)  

## 🔜 MVP 2 - Segunda Entrega

- Import CSV frequência
- Auditoria completa (visualização)
- Busca avançada e filtros
- Página de detalhes de evento com abas
- Gallery com lightbox
- Upload com drag-and-drop
- Gestão de usuários (admin)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é proprietário da Secretaria Municipal de Educação.

## 👨‍💻 Desenvolvimento

Para mais informações sobre desenvolvimento, consulte:
- [docs/API.md](docs/API.md) - Documentação completa da API
- [docs/DEPLOY.md](docs/DEPLOY.md) - Guia detalhado de deploy
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) - Guia de desenvolvimento

## 🐛 Problemas e Sugestões

Use a aba [Issues](https://github.com/seu-usuario/evidencias-sme/issues) do GitHub para reportar problemas ou sugerir melhorias.
