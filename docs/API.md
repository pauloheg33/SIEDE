# 📡 Documentação da API

Base URL: `https://sua-api.onrender.com` (produção) ou `http://localhost:8000` (desenvolvimento)

Documentação interativa: `/docs` (Swagger UI) ou `/redoc` (ReDoc)

## Autenticação

Todos os endpoints (exceto `/auth/register` e `/auth/login`) requerem autenticação via JWT Bearer token.

Header:
```
Authorization: Bearer <access_token>
```

## Endpoints

### 🔐 Autenticação

#### POST /auth/register

Cadastrar novo usuário.

**Request Body:**
```json
{
  "name": "João Silva",
  "email": "joao@example.com",
  "password": "senha123456"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "name": "João Silva",
  "email": "joao@example.com",
  "role": "TEC_ACOMPANHAMENTO",
  "is_active": true,
  "created_at": "2026-02-05T10:00:00Z"
}
```

**Errors:**
- `400` - Email já cadastrado
- `422` - Dados inválidos

---

#### POST /auth/login

Fazer login e obter tokens.

**Request Body:**
```json
{
  "email": "joao@example.com",
  "password": "senha123456"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Errors:**
- `401` - Email ou senha incorretos
- `403` - Usuário inativo

---

#### POST /auth/refresh

Renovar access token usando refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Errors:**
- `401` - Token inválido ou expirado

---

#### POST /auth/logout

Fazer logout (cliente deve descartar tokens).

**Response:** `200 OK`
```json
{
  "message": "Logged out successfully"
}
```

---

#### GET /auth/me

Obter dados do usuário atual.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "João Silva",
  "email": "joao@example.com",
  "role": "TEC_ACOMPANHAMENTO",
  "is_active": true,
  "created_at": "2026-02-05T10:00:00Z"
}
```

**Errors:**
- `401` - Não autenticado

---

### 👥 Usuários (Admin apenas)

#### GET /users

Listar todos os usuários.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "João Silva",
    "email": "joao@example.com",
    "role": "TEC_ACOMPANHAMENTO",
    "is_active": true,
    "created_at": "2026-02-05T10:00:00Z"
  }
]
```

**Errors:**
- `403` - Sem permissão (não é admin)

---

#### POST /users

Criar novo usuário (admin).

**Request Body:**
```json
{
  "name": "Maria Santos",
  "email": "maria@example.com",
  "password": "senha123456"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "name": "Maria Santos",
  "email": "maria@example.com",
  "role": "TEC_ACOMPANHAMENTO",
  "is_active": true,
  "created_at": "2026-02-05T10:00:00Z"
}
```

---

#### PUT /users/{user_id}

Atualizar usuário.

**Request Body:**
```json
{
  "name": "Maria Santos Silva",
  "email": "maria.silva@example.com",
  "role": "TEC_FORMACAO",
  "is_active": true
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "Maria Santos Silva",
  "email": "maria.silva@example.com",
  "role": "TEC_FORMACAO",
  "is_active": true,
  "created_at": "2026-02-05T10:00:00Z"
}
```

---

#### PATCH /users/{user_id}/role?role=ADMIN

Alterar papel do usuário.

**Query Params:**
- `role`: ADMIN | TEC_FORMACAO | TEC_ACOMPANHAMENTO

**Response:** `200 OK`

---

#### PATCH /users/{user_id}/deactivate

Ativar/desativar usuário.

**Response:** `200 OK`

---

### 📅 Eventos

#### GET /events

Listar eventos com filtros opcionais.

**Query Params:**
- `type` (opcional): FORMACAO | PREMIACAO | ENCONTRO | OUTRO
- `status` (opcional): PLANEJADO | REALIZADO | ARQUIVADO
- `start_date` (opcional): ISO datetime
- `end_date` (opcional): ISO datetime
- `search` (opcional): busca no título

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "title": "Formação de Gestores",
    "type": "FORMACAO",
    "status": "PLANEJADO",
    "start_at": "2026-02-10T09:00:00Z",
    "location": "Auditório Central",
    "created_by": "uuid",
    "created_at": "2026-02-05T10:00:00Z",
    "creator": {
      "id": "uuid",
      "name": "João Silva",
      "email": "joao@example.com",
      "role": "TEC_FORMACAO",
      "is_active": true,
      "created_at": "2026-02-01T10:00:00Z"
    }
  }
]
```

---

#### POST /events

Criar novo evento.

**Request Body:**
```json
{
  "title": "Formação de Gestores 2026",
  "type": "FORMACAO",
  "status": "PLANEJADO",
  "start_at": "2026-02-10T09:00:00Z",
  "end_at": "2026-02-10T17:00:00Z",
  "location": "Auditório Central",
  "audience": "Gestores escolares",
  "description": "Formação focada em gestão pedagógica",
  "tags": ["gestão", "liderança"],
  "schools": ["Escola A", "Escola B"]
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "title": "Formação de Gestores 2026",
  "type": "FORMACAO",
  "status": "PLANEJADO",
  "start_at": "2026-02-10T09:00:00Z",
  "end_at": "2026-02-10T17:00:00Z",
  "location": "Auditório Central",
  "audience": "Gestores escolares",
  "description": "Formação focada em gestão pedagógica",
  "tags": ["gestão", "liderança"],
  "schools": ["Escola A", "Escola B"],
  "created_by": "uuid",
  "created_at": "2026-02-05T10:00:00Z",
  "updated_at": "2026-02-05T10:00:00Z",
  "creator": { /* ... */ }
}
```

---

#### GET /events/{event_id}

Obter detalhes de um evento.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "title": "Formação de Gestores 2026",
  "type": "FORMACAO",
  "status": "PLANEJADO",
  "start_at": "2026-02-10T09:00:00Z",
  "end_at": "2026-02-10T17:00:00Z",
  "location": "Auditório Central",
  "audience": "Gestores escolares",
  "description": "Formação focada em gestão pedagógica",
  "tags": ["gestão", "liderança"],
  "schools": ["Escola A", "Escola B"],
  "created_by": "uuid",
  "created_at": "2026-02-05T10:00:00Z",
  "updated_at": "2026-02-05T10:00:00Z",
  "creator": { /* ... */ }
}
```

**Errors:**
- `404` - Evento não encontrado

---

#### PUT /events/{event_id}

Atualizar evento (apenas criador ou admin).

**Request Body:** (campos opcionais)
```json
{
  "title": "Novo título",
  "status": "REALIZADO"
}
```

**Response:** `200 OK`

**Errors:**
- `403` - Sem permissão
- `404` - Evento não encontrado

---

#### DELETE /events/{event_id}

Deletar evento (apenas admin).

**Response:** `204 No Content`

**Errors:**
- `403` - Apenas admin pode deletar
- `404` - Evento não encontrado

---

### 📁 Arquivos

#### POST /events/{event_id}/files?kind=PHOTO

Upload de arquivos (múltiplos).

**Query Params:**
- `kind`: PHOTO | DOC

**Request:** `multipart/form-data`
- `files`: arquivo(s)

**Response:** `201 Created`
```json
[
  {
    "id": "uuid",
    "event_id": "uuid",
    "kind": "PHOTO",
    "filename": "foto.jpg",
    "mime": "image/jpeg",
    "size": 1024000,
    "url": "https://storage.com/uuid_foto.jpg",
    "thumbnail_url": "https://storage.com/uuid_thumb_foto.jpg",
    "uploaded_by": "uuid",
    "created_at": "2026-02-05T10:00:00Z",
    "uploader": { /* ... */ }
  }
]
```

**Limits:**
- Max size: 10MB por arquivo
- Photos: JPEG, PNG, GIF, WebP
- Docs: PDF, DOCX, XLSX, ZIP

**Errors:**
- `400` - Tipo de arquivo inválido
- `400` - Arquivo muito grande
- `403` - Sem permissão

---

#### GET /events/{event_id}/files?kind=PHOTO

Listar arquivos de um evento.

**Query Params:**
- `kind` (opcional): PHOTO | DOC

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "event_id": "uuid",
    "kind": "PHOTO",
    "filename": "foto.jpg",
    "mime": "image/jpeg",
    "size": 1024000,
    "url": "https://storage.com/uuid_foto.jpg",
    "thumbnail_url": "https://storage.com/uuid_thumb_foto.jpg",
    "uploaded_by": "uuid",
    "created_at": "2026-02-05T10:00:00Z",
    "uploader": { /* ... */ }
  }
]
```

---

#### DELETE /events/{event_id}/files/{file_id}

Deletar arquivo.

**Response:** `204 No Content`

**Errors:**
- `403` - Sem permissão
- `404` - Arquivo não encontrado

---

### 📋 Frequência

#### GET /events/{event_id}/attendance

Listar frequência de um evento.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "event_id": "uuid",
    "person_name": "Maria Silva",
    "person_role": "Diretora",
    "school": "Escola Municipal A",
    "present": true,
    "created_at": "2026-02-05T10:00:00Z"
  }
]
```

---

#### POST /events/{event_id}/attendance

Adicionar participante.

**Request Body:**
```json
{
  "person_name": "Maria Silva",
  "person_role": "Diretora",
  "school": "Escola Municipal A",
  "present": true
}
```

**Response:** `201 Created`

---

#### POST /events/{event_id}/attendance/import

Importar frequência via CSV.

**Request:** `multipart/form-data`
- `file`: arquivo CSV

**CSV Format:**
```csv
person_name,person_role,school,present
Maria Silva,Diretora,Escola A,true
João Santos,Coordenador,Escola B,true
```

**Response:** `201 Created`
```json
{
  "message": "Imported 2 attendance records"
}
```

**Errors:**
- `400` - Arquivo não é CSV
- `400` - Colunas inválidas

---

#### GET /events/{event_id}/attendance/export/csv

Exportar frequência como CSV.

**Response:** `200 OK`
- Content-Type: `text/csv`
- Content-Disposition: `attachment; filename=frequencia_evento.csv`

---

#### GET /events/{event_id}/attendance/export/pdf

Exportar frequência como PDF.

**Response:** `200 OK`
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename=frequencia_evento.pdf`

---

#### DELETE /events/{event_id}/attendance/{attendance_id}

Deletar registro de frequência.

**Response:** `204 No Content`

---

### 📝 Observações

#### GET /events/{event_id}/notes

Listar observações de um evento.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "event_id": "uuid",
    "text": "Evento teve ótima participação",
    "created_by": "uuid",
    "created_at": "2026-02-05T10:00:00Z",
    "updated_at": "2026-02-05T10:00:00Z",
    "author": { /* ... */ }
  }
]
```

---

#### POST /events/{event_id}/notes

Criar observação.

**Request Body:**
```json
{
  "text": "Evento teve ótima participação"
}
```

**Response:** `201 Created`

---

#### PUT /events/{event_id}/notes/{note_id}

Atualizar observação (apenas autor ou admin).

**Request Body:**
```json
{
  "text": "Texto atualizado"
}
```

**Response:** `200 OK`

---

#### DELETE /events/{event_id}/notes/{note_id}

Deletar observação (apenas autor ou admin).

**Response:** `204 No Content`

---

## Códigos de Status

- `200` - OK
- `201` - Created
- `204` - No Content
- `400` - Bad Request (dados inválidos)
- `401` - Unauthorized (não autenticado)
- `403` - Forbidden (sem permissão)
- `404` - Not Found
- `422` - Unprocessable Entity (validação falhou)
- `500` - Internal Server Error

## Rate Limiting

- Login: 5 requisições / minuto
- Outros endpoints: 100 requisições / minuto

## Paginação

Atualmente não implementada. Todas as listagens retornam todos os registros.

MVP 2 incluirá:
```
GET /events?page=1&per_page=20
```

## Filtros Avançados

MVP 2 incluirá busca avançada:
```
GET /events?q=formação&tags=gestão,liderança&schools=Escola A
```

## Webhooks

Não implementado. Pode ser adicionado em versões futuras para notificar sistemas externos de eventos importantes.

## Versionamento

API não versionada atualmente. Mudanças breaking incluirão versionamento:
```
/api/v2/events
```
