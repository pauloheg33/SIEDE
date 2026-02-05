-- Supabase SQL Migration for Evidências SME
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- Create custom types
create type user_role as enum ('ADMIN', 'TEC_FORMACAO', 'TEC_ACOMPANHAMENTO');
create type event_type as enum ('FORMACAO', 'PREMIACAO', 'ENCONTRO', 'OUTRO');
create type event_status as enum ('PLANEJADO', 'REALIZADO', 'ARQUIVADO');
create type file_kind as enum ('PHOTO', 'DOC');

-- Create users table (extends auth.users)
create table public.users (
  id uuid references auth.users on delete cascade primary key,
  name text not null,
  email text not null unique,
  role user_role not null default 'TEC_ACOMPANHAMENTO',
  is_active boolean not null default true,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create events table
create table public.events (
  id uuid default uuid_generate_v4() primary key,
  title text not null,
  type event_type not null,
  status event_status not null default 'PLANEJADO',
  start_at timestamp with time zone not null,
  end_at timestamp with time zone,
  location text,
  audience text,
  description text,
  tags text[] default '{}',
  schools text[] default '{}',
  created_by uuid references public.users(id) on delete set null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create event_files table
create table public.event_files (
  id uuid default uuid_generate_v4() primary key,
  event_id uuid references public.events(id) on delete cascade not null,
  kind file_kind not null,
  filename text not null,
  mime text not null,
  size integer not null,
  url text not null,
  thumbnail_url text,
  uploaded_by uuid references public.users(id) on delete set null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create attendance table
create table public.attendance (
  id uuid default uuid_generate_v4() primary key,
  event_id uuid references public.events(id) on delete cascade not null,
  person_name text not null,
  person_role text,
  school text,
  present boolean not null default true,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create event_notes table
create table public.event_notes (
  id uuid default uuid_generate_v4() primary key,
  event_id uuid references public.events(id) on delete cascade not null,
  text text not null,
  created_by uuid references public.users(id) on delete set null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create indexes
create index events_created_by_idx on public.events(created_by);
create index events_status_idx on public.events(status);
create index events_type_idx on public.events(type);
create index event_files_event_id_idx on public.event_files(event_id);
create index attendance_event_id_idx on public.attendance(event_id);
create index event_notes_event_id_idx on public.event_notes(event_id);

-- Enable Row Level Security
alter table public.users enable row level security;
alter table public.events enable row level security;
alter table public.event_files enable row level security;
alter table public.attendance enable row level security;
alter table public.event_notes enable row level security;

-- RLS Policies for users
create policy "Users can view all users" on public.users
  for select using (auth.role() = 'authenticated');

create policy "Users can update own profile" on public.users
  for update using (auth.uid() = id);

create policy "Admins can update any user" on public.users
  for update using (
    exists (
      select 1 from public.users where id = auth.uid() and role = 'ADMIN'
    )
  );

create policy "Allow insert during registration" on public.users
  for insert with check (auth.uid() = id);

-- RLS Policies for events
create policy "Authenticated users can view events" on public.events
  for select using (auth.role() = 'authenticated');

create policy "Authenticated users can create events" on public.events
  for insert with check (auth.role() = 'authenticated');

create policy "Creators and admins can update events" on public.events
  for update using (
    created_by = auth.uid() or
    exists (select 1 from public.users where id = auth.uid() and role = 'ADMIN')
  );

create policy "Creators and admins can delete events" on public.events
  for delete using (
    created_by = auth.uid() or
    exists (select 1 from public.users where id = auth.uid() and role = 'ADMIN')
  );

-- RLS Policies for event_files
create policy "Authenticated users can view files" on public.event_files
  for select using (auth.role() = 'authenticated');

create policy "Authenticated users can upload files" on public.event_files
  for insert with check (auth.role() = 'authenticated');

create policy "Uploaders and admins can delete files" on public.event_files
  for delete using (
    uploaded_by = auth.uid() or
    exists (select 1 from public.users where id = auth.uid() and role = 'ADMIN')
  );

-- RLS Policies for attendance
create policy "Authenticated users can view attendance" on public.attendance
  for select using (auth.role() = 'authenticated');

create policy "Authenticated users can manage attendance" on public.attendance
  for all using (auth.role() = 'authenticated');

-- RLS Policies for event_notes
create policy "Authenticated users can view notes" on public.event_notes
  for select using (auth.role() = 'authenticated');

create policy "Authenticated users can create notes" on public.event_notes
  for insert with check (auth.role() = 'authenticated');

create policy "Authors and admins can update notes" on public.event_notes
  for update using (
    created_by = auth.uid() or
    exists (select 1 from public.users where id = auth.uid() and role = 'ADMIN')
  );

create policy "Authors and admins can delete notes" on public.event_notes
  for delete using (
    created_by = auth.uid() or
    exists (select 1 from public.users where id = auth.uid() and role = 'ADMIN')
  );

-- Create storage buckets
insert into storage.buckets (id, name, public) values ('photos', 'photos', true);
insert into storage.buckets (id, name, public) values ('documents', 'documents', true);

-- Storage policies
create policy "Authenticated users can upload photos"
  on storage.objects for insert
  with check (bucket_id = 'photos' and auth.role() = 'authenticated');

create policy "Anyone can view photos"
  on storage.objects for select
  using (bucket_id = 'photos');

create policy "Uploaders can delete their photos"
  on storage.objects for delete
  using (bucket_id = 'photos' and auth.uid()::text = (storage.foldername(name))[1]);

create policy "Authenticated users can upload documents"
  on storage.objects for insert
  with check (bucket_id = 'documents' and auth.role() = 'authenticated');

create policy "Authenticated users can view documents"
  on storage.objects for select
  using (bucket_id = 'documents' and auth.role() = 'authenticated');

create policy "Uploaders can delete their documents"
  on storage.objects for delete
  using (bucket_id = 'documents' and auth.uid()::text = (storage.foldername(name))[1]);

-- Function to handle new user creation
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.users (id, name, email, role)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'name', split_part(new.email, '@', 1)),
    new.email,
    'TEC_ACOMPANHAMENTO'
  );
  return new;
end;
$$ language plpgsql security definer;

-- Trigger to auto-create user profile on signup
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
