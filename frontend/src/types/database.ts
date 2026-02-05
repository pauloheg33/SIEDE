export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          name: string
          email: string
          role: 'ADMIN' | 'TEC_FORMACAO' | 'TEC_ACOMPANHAMENTO'
          is_active: boolean
          created_at: string
        }
        Insert: {
          id?: string
          name: string
          email: string
          role?: 'ADMIN' | 'TEC_FORMACAO' | 'TEC_ACOMPANHAMENTO'
          is_active?: boolean
          created_at?: string
        }
        Update: {
          id?: string
          name?: string
          email?: string
          role?: 'ADMIN' | 'TEC_FORMACAO' | 'TEC_ACOMPANHAMENTO'
          is_active?: boolean
          created_at?: string
        }
      }
      events: {
        Row: {
          id: string
          title: string
          type: 'FORMACAO' | 'PREMIACAO' | 'ENCONTRO' | 'OUTRO'
          status: 'PLANEJADO' | 'REALIZADO' | 'ARQUIVADO'
          start_at: string
          end_at: string | null
          location: string | null
          audience: string | null
          description: string | null
          tags: string[]
          schools: string[]
          created_by: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          title: string
          type: 'FORMACAO' | 'PREMIACAO' | 'ENCONTRO' | 'OUTRO'
          status?: 'PLANEJADO' | 'REALIZADO' | 'ARQUIVADO'
          start_at: string
          end_at?: string | null
          location?: string | null
          audience?: string | null
          description?: string | null
          tags?: string[]
          schools?: string[]
          created_by: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          title?: string
          type?: 'FORMACAO' | 'PREMIACAO' | 'ENCONTRO' | 'OUTRO'
          status?: 'PLANEJADO' | 'REALIZADO' | 'ARQUIVADO'
          start_at?: string
          end_at?: string | null
          location?: string | null
          audience?: string | null
          description?: string | null
          tags?: string[]
          schools?: string[]
          created_by?: string
          created_at?: string
          updated_at?: string
        }
      }
      event_files: {
        Row: {
          id: string
          event_id: string
          kind: 'PHOTO' | 'DOC'
          filename: string
          mime: string
          size: number
          url: string
          thumbnail_url: string | null
          uploaded_by: string
          created_at: string
        }
        Insert: {
          id?: string
          event_id: string
          kind: 'PHOTO' | 'DOC'
          filename: string
          mime: string
          size: number
          url: string
          thumbnail_url?: string | null
          uploaded_by: string
          created_at?: string
        }
        Update: {
          id?: string
          event_id?: string
          kind?: 'PHOTO' | 'DOC'
          filename?: string
          mime?: string
          size?: number
          url?: string
          thumbnail_url?: string | null
          uploaded_by?: string
          created_at?: string
        }
      }
      attendance: {
        Row: {
          id: string
          event_id: string
          person_name: string
          person_role: string | null
          school: string | null
          present: boolean
          created_at: string
        }
        Insert: {
          id?: string
          event_id: string
          person_name: string
          person_role?: string | null
          school?: string | null
          present?: boolean
          created_at?: string
        }
        Update: {
          id?: string
          event_id?: string
          person_name?: string
          person_role?: string | null
          school?: string | null
          present?: boolean
          created_at?: string
        }
      }
      event_notes: {
        Row: {
          id: string
          event_id: string
          text: string
          created_by: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          event_id: string
          text: string
          created_by: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          event_id?: string
          text?: string
          created_by?: string
          created_at?: string
          updated_at?: string
        }
      }
    }
  }
}
