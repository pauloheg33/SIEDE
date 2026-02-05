import axios from 'axios';
import type {
  User,
  Event,
  EventFile,
  Attendance,
  EventNote,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  EventCreateRequest,
  AttendanceCreateRequest,
  NoteCreateRequest,
  FileKind,
} from '@/types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          throw new Error('No refresh token');
        }

        const { data } = await axios.post<TokenResponse>(`${API_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);

        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  register: (data: RegisterRequest) => api.post<User>('/auth/register', data),
  login: (data: LoginRequest) => api.post<TokenResponse>('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  getMe: () => api.get<User>('/auth/me'),
};

// Users
export const usersAPI = {
  list: () => api.get<User[]>('/users'),
  create: (data: RegisterRequest) => api.post<User>('/users', data),
  update: (id: string, data: Partial<User>) => api.put<User>(`/users/${id}`, data),
  changeRole: (id: string, role: string) => api.patch<User>(`/users/${id}/role`, null, { params: { role } }),
  deactivate: (id: string) => api.patch<User>(`/users/${id}/deactivate`),
};

// Events
export const eventsAPI = {
  list: (params?: Record<string, any>) => api.get<Event[]>('/events', { params }),
  get: (id: string) => api.get<Event>(`/events/${id}`),
  create: (data: EventCreateRequest) => api.post<Event>('/events', data),
  update: (id: string, data: Partial<EventCreateRequest>) => api.put<Event>(`/events/${id}`, data),
  delete: (id: string) => api.delete(`/events/${id}`),
};

// Files
export const filesAPI = {
  list: (eventId: string, kind?: FileKind) => 
    api.get<EventFile[]>(`/events/${eventId}/files`, { params: { kind } }),
  upload: (eventId: string, files: File[], kind: FileKind) => {
    const formData = new FormData();
    files.forEach((file) => formData.append('files', file));
    return api.post<EventFile[]>(`/events/${eventId}/files`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      params: { kind },
    });
  },
  delete: (eventId: string, fileId: string) => api.delete(`/events/${eventId}/files/${fileId}`),
};

// Attendance
export const attendanceAPI = {
  list: (eventId: string) => api.get<Attendance[]>(`/events/${eventId}/attendance`),
  create: (eventId: string, data: AttendanceCreateRequest) => 
    api.post<Attendance>(`/events/${eventId}/attendance`, data),
  importCSV: (eventId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/events/${eventId}/attendance/import`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  exportCSV: (eventId: string) => 
    api.get(`/events/${eventId}/attendance/export/csv`, { responseType: 'blob' }),
  exportPDF: (eventId: string) => 
    api.get(`/events/${eventId}/attendance/export/pdf`, { responseType: 'blob' }),
  delete: (eventId: string, attendanceId: string) => 
    api.delete(`/events/${eventId}/attendance/${attendanceId}`),
};

// Notes
export const notesAPI = {
  list: (eventId: string) => api.get<EventNote[]>(`/events/${eventId}/notes`),
  create: (eventId: string, data: NoteCreateRequest) => 
    api.post<EventNote>(`/events/${eventId}/notes`, data),
  update: (eventId: string, noteId: string, data: NoteCreateRequest) => 
    api.put<EventNote>(`/events/${eventId}/notes/${noteId}`, data),
  delete: (eventId: string, noteId: string) => 
    api.delete(`/events/${eventId}/notes/${noteId}`),
};

export default api;
