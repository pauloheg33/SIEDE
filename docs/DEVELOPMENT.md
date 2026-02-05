# 💻 Guia de Desenvolvimento

## Setup do Ambiente

### Requisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Git
- Editor de código (VSCode recomendado)

### Extensões VSCode Recomendadas

- Python
- Pylance
- ESLint
- Prettier
- GitLens
- Thunder Client (testar API)

## Desenvolvimento Backend

### Setup Inicial

```bash
cd backend

# Criar venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Copiar .env
cp .env.example .env
# Editar .env com suas configurações

# Criar banco local
createdb evidencias_sme

# Rodar migrations
alembic upgrade head

# Iniciar server
uvicorn app.main:app --reload --port 8000
```

### Estrutura de Código

```
app/
├── routers/          # Controllers (endpoints)
├── models.py         # SQLAlchemy models
├── schemas.py        # Pydantic schemas (validação)
├── auth.py           # Autenticação/autorização
├── storage.py        # Serviço de storage
├── audit.py          # Logs de auditoria
├── config.py         # Configurações
├── database.py       # Conexão DB
└── main.py           # FastAPI app
```

### Criar Nova Migration

```bash
# Após alterar models.py
alembic revision --autogenerate -m "Descrição da mudança"

# Aplicar
alembic upgrade head

# Reverter
alembic downgrade -1
```

### Adicionar Novo Endpoint

1. Criar schema em `schemas.py`:

```python
class NovoSchema(BaseModel):
    campo: str
    
    class Config:
        from_attributes = True
```

2. Adicionar rota em `routers/`:

```python
@router.post("/endpoint", response_model=NovoSchema)
def criar_item(
    data: NovoSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Lógica aqui
    return item
```

3. Incluir router em `main.py`:

```python
from app.routers import novo_router
app.include_router(novo_router.router)
```

### Testar API

#### Com Thunder Client (VSCode)

1. Instale extensão Thunder Client
2. Crie request:
   - Method: POST
   - URL: http://localhost:8000/auth/login
   - Body (JSON):
   ```json
   {
     "email": "test@example.com",
     "password": "password123"
   }
   ```
3. Salve o token
4. Use token em outros requests (Header `Authorization: Bearer <token>`)

#### Com curl

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Com token
curl http://localhost:8000/events \
  -H "Authorization: Bearer <seu-token>"
```

#### Com Python requests

```python
import requests

# Login
response = requests.post('http://localhost:8000/auth/login', json={
    'email': 'test@example.com',
    'password': 'password123'
})
token = response.json()['access_token']

# Usar token
headers = {'Authorization': f'Bearer {token}'}
events = requests.get('http://localhost:8000/events', headers=headers)
print(events.json())
```

### Debugging

#### VSCode launch.json

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload"
      ],
      "jinja": true,
      "justMyCode": true
    }
  ]
}
```

#### Logs

```python
import logging

logger = logging.getLogger(__name__)

@router.get("/endpoint")
def minha_rota():
    logger.info("Info log")
    logger.error("Error log")
```

---

## Desenvolvimento Frontend

### Setup Inicial

```bash
cd frontend

# Instalar dependências
npm install

# Copiar .env
cp .env.example .env
# Editar VITE_API_URL

# Iniciar dev server
npm run dev
```

### Estrutura de Código

```
src/
├── components/       # Componentes reutilizáveis
├── pages/           # Páginas/rotas
├── lib/             # Utilitários (API client)
├── store/           # Estado global (Zustand)
├── styles/          # CSS
├── types/           # Tipos TypeScript
├── App.tsx          # App principal
└── main.tsx         # Entry point
```

### Criar Nova Página

1. Criar arquivo em `pages/`:

```tsx
// pages/NovaPagina.tsx
import Layout from '@/components/Layout/Layout';

export default function NovaPagina() {
  return (
    <Layout>
      <h1>Nova Página</h1>
    </Layout>
  );
}
```

2. Adicionar rota em `App.tsx`:

```tsx
import NovaPagina from '@/pages/NovaPagina';

// Em Routes
<Route
  path="/nova-pagina"
  element={
    <ProtectedRoute>
      <NovaPagina />
    </ProtectedRoute>
  }
/>
```

### Criar Novo Componente

```tsx
// components/MeuComponente/MeuComponente.tsx
interface Props {
  titulo: string;
  onAction: () => void;
}

export default function MeuComponente({ titulo, onAction }: Props) {
  return (
    <div className="meu-componente">
      <h2>{titulo}</h2>
      <button onClick={onAction}>Ação</button>
    </div>
  );
}
```

```css
/* components/MeuComponente/MeuComponente.css */
.meu-componente {
  padding: 1rem;
  border: 1px solid var(--border);
}
```

### Consumir API

```tsx
import { useState, useEffect } from 'react';
import { eventsAPI } from '@/lib/api';
import { Event } from '@/types';

function MinhaPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      const { data } = await eventsAPI.list();
      setEvents(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Carregando...</div>;

  return (
    <div>
      {events.map(event => (
        <div key={event.id}>{event.title}</div>
      ))}
    </div>
  );
}
```

### Estado Global (Zustand)

```tsx
// store/eventStore.ts
import { create } from 'zustand';
import { Event } from '@/types';

interface EventStore {
  events: Event[];
  selectedEvent: Event | null;
  setEvents: (events: Event[]) => void;
  selectEvent: (event: Event) => void;
}

export const useEventStore = create<EventStore>((set) => ({
  events: [],
  selectedEvent: null,
  setEvents: (events) => set({ events }),
  selectEvent: (event) => set({ selectedEvent: event }),
}));

// Usar em componente
function MyComponent() {
  const { events, setEvents } = useEventStore();
}
```

### Forms com React Hook Form

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  title: z.string().min(3, 'Mínimo 3 caracteres'),
  email: z.string().email('Email inválido'),
});

type FormData = z.infer<typeof schema>;

function MyForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (data: FormData) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('title')} />
      {errors.title && <span>{errors.title.message}</span>}
      
      <button type="submit">Enviar</button>
    </form>
  );
}
```

### Toasts

```tsx
import { toast } from 'react-toastify';

// Sucesso
toast.success('Operação realizada!');

// Erro
toast.error('Algo deu errado');

// Info
toast.info('Informação');

// Warning
toast.warning('Atenção');
```

---

## Boas Práticas

### Backend

1. **Sempre use Pydantic schemas** para validação
2. **Use type hints** em todas as funções
3. **Adicione docstrings** nos endpoints
4. **Log ações importantes** com auditoria
5. **Trate erros** adequadamente:

```python
try:
    # código
except SpecificError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

6. **Use transactions** para múltiplas operações:

```python
try:
    db.add(obj1)
    db.add(obj2)
    db.commit()
except Exception:
    db.rollback()
    raise
```

7. **Teste endpoints** antes de commitar

### Frontend

1. **Use TypeScript** corretamente (evite `any`)
2. **Componentize** código repetitivo
3. **Use CSS variables** para temas
4. **Otimize re-renders** com `useMemo`/`useCallback`
5. **Trate loading states**:

```tsx
if (loading) return <Loading />;
if (error) return <Error />;
return <Content />;
```

6. **Valide forms** com Zod
7. **Feedback visual** com toasts
8. **Mobile-first** CSS

---

## Git Workflow

### Branches

```bash
# Feature
git checkout -b feature/nome-da-feature

# Bugfix
git checkout -b fix/nome-do-bug

# Hotfix
git checkout -b hotfix/descricao
```

### Commits

Siga [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: adiciona upload de fotos"
git commit -m "fix: corrige erro de autenticação"
git commit -m "docs: atualiza README"
git commit -m "refactor: simplifica lógica de eventos"
git commit -m "test: adiciona testes de API"
```

### Pull Requests

1. Crie branch
2. Faça mudanças
3. Commit e push
4. Abra PR no GitHub
5. Descreva mudanças
6. Aguarde review

---

## Testes

### Backend (pytest)

```bash
pip install pytest pytest-cov

# Criar test_api.py
pytest
pytest --cov=app
```

```python
def test_login():
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json()
```

### Frontend (Vitest)

```bash
npm install -D vitest @testing-library/react

# Criar *.test.tsx
npm run test
```

```tsx
import { render, screen } from '@testing-library/react';
import Login from '@/pages/Login';

test('renders login form', () => {
  render(<Login />);
  expect(screen.getByText('Entrar')).toBeInTheDocument();
});
```

---

## Performance

### Backend

1. **Use indexes** no banco
2. **Pagination** em listagens
3. **Cache** com Redis (opcional)
4. **Async** onde possível
5. **Optimize queries** (select only needed fields)

### Frontend

1. **Code splitting** com lazy load:

```tsx
const EventDetail = lazy(() => import('@/pages/EventDetail'));
```

2. **Optimize images** (thumbnails)
3. **Virtualize** listas longas
4. **Debounce** buscas
5. **Service Worker** para cache (PWA)

---

## Debugging Comum

### "Token expired"
- Refresh token automático está implementado
- Verifique `localStorage` no DevTools

### "CORS error"
- Verifique `FRONTEND_URL` no backend
- Confirme que não há barra final

### "Database locked"
- Use PostgreSQL em produção (não SQLite)

### "Module not found"
- Frontend: `npm install`
- Backend: `pip install -r requirements.txt`

### "Port already in use"
- Backend: `lsof -ti:8000 | xargs kill`
- Frontend: `lsof -ti:3000 | xargs kill`
