# SIEDE - Sistema de Evidências SME

Sistema para gestão de eventos e evidências da Secretaria Municipal de Educação.

## Funcionalidades

- **Gestão de Eventos**: Formações, premiações, encontros
- **Upload de Fotos**: Galeria com thumbnails automáticos
- **Upload de Documentos**: PDFs, planilhas, documentos
- **Lista de Presença**: Registro de participantes com exportação CSV
- **Observações**: Notas e histórico por evento
- **Controle de Acesso**: 3 níveis (Admin, Técnico Formação, Técnico Acompanhamento)

## Stack Tecnológica

- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: Supabase (Auth, Database, Storage)
- **Hospedagem**: GitHub Pages

## Configuração

### 1. Criar projeto no Supabase

1. Acesse [supabase.com](https://supabase.com) e crie um novo projeto
2. Copie a **URL** e **anon key** do projeto

### 2. Executar migração do banco

1. No Supabase, vá em **SQL Editor**
2. Cole e execute o conteúdo de `supabase/migration.sql`

### 3. Configurar variáveis de ambiente

Crie `.env` na pasta `frontend`:

```env
VITE_SUPABASE_URL=https://seu-projeto.supabase.co
VITE_SUPABASE_ANON_KEY=sua-anon-key
```

### 4. Desenvolvimento local

```bash
cd frontend
npm install
npm run dev
```

Acesse: http://localhost:3000

## Deploy no GitHub Pages

### 1. Configurar Secrets no GitHub

Vá em **Settings > Secrets and variables > Actions** e adicione:

- `VITE_SUPABASE_URL`: URL do seu projeto Supabase
- `VITE_SUPABASE_ANON_KEY`: Anon key do Supabase

### 2. Habilitar GitHub Pages

Vá em **Settings > Pages** e configure:
- **Source**: GitHub Actions

O deploy será automático a cada push na branch `main`.

## Estrutura do Projeto

```
├── frontend/
│   ├── src/
│   │   ├── components/    # Componentes reutilizáveis
│   │   ├── lib/           # Supabase client e API
│   │   ├── pages/         # Páginas da aplicação
│   │   ├── store/         # Zustand stores
│   │   ├── styles/        # CSS global
│   │   └── types/         # TypeScript types
│   └── package.json
├── supabase/
│   └── migration.sql      # Schema do banco de dados
└── .github/
    └── workflows/
        └── deploy.yml     # CI/CD para GitHub Pages
```

## Primeiro Acesso

1. Registre um usuário na aplicação
2. No Supabase, vá em **Table Editor > users**
3. Altere o campo `role` do usuário para `ADMIN`
4. Faça logout e login novamente

## Licença

MIT
