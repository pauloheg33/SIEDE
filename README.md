# SIEDE - Sistema de Evidências SME

Sistema para gestão de evidências e eventos da Secretaria Municipal de Educação.

## 🚀 Tecnologias

- **Frontend:** React 18 + TypeScript + Vite
- **Backend:** Supabase (Auth, Database, Storage)
- **Hosting:** GitHub Pages

## 📁 Estrutura

```
├── frontend/          # Aplicação React
│   ├── src/
│   │   ├── components/   # Componentes reutilizáveis
│   │   ├── pages/        # Páginas da aplicação
│   │   ├── store/        # Estado global (Zustand)
│   │   ├── lib/          # Supabase client e API
│   │   └── types/        # Tipos TypeScript
│   └── public/
├── supabase/
│   └── migration.sql     # Schema do banco de dados
└── .github/workflows/    # CI/CD para GitHub Pages
```

## 🔧 Configuração

### 1. Supabase

1. Crie um projeto em [supabase.com](https://supabase.com)
2. Execute o SQL em `supabase/migration.sql` no SQL Editor
3. Copie a URL e Anon Key do projeto

### 2. GitHub Secrets

Configure os seguintes secrets no repositório:

- `VITE_SUPABASE_URL` - URL do projeto Supabase
- `VITE_SUPABASE_ANON_KEY` - Chave anônima do Supabase

### 3. GitHub Pages

Em Settings → Pages, selecione "GitHub Actions" como source.

## 🌐 Deploy

O deploy é automático via GitHub Actions ao fazer push na branch `main`.

**URL:** https://pauloheg33.github.io/SIEDE/

## 📋 Funcionalidades

- ✅ Autenticação de usuários
- ✅ Gestão de eventos (CRUD)
- ✅ Upload de fotos e documentos
- ✅ Controle de presença
- ✅ Notas e observações
- ✅ Diferentes tipos de eventos (Formação, Premiação, Encontro)
- ✅ Controle de status (Planejado, Realizado, Arquivado)

## 👥 Perfis de Usuário

- **ADMIN** - Acesso total
- **TEC_FORMACAO** - Técnico de Formação
- **TEC_ACOMPANHAMENTO** - Técnico de Acompanhamento
