import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import Layout from '@/components/Layout/Layout';
import { eventsAPI, filesAPI, attendanceAPI, notesAPI } from '@/lib/api';
import { Event, EventFile, Attendance, EventNote, EventType, EventStatus, FileKind } from '@/types';
import { 
  ArrowLeft, Edit, Trash2, Calendar, MapPin, Users, 
  Image, FileText, ClipboardList, MessageSquare, 
  Upload, Download, Plus, X, Check, FileSpreadsheet
} from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { toast } from 'react-toastify';
import './EventDetail.css';

const EVENT_TYPE_LABELS: Record<EventType, string> = {
  [EventType.FORMACAO]: 'Formação',
  [EventType.PREMIACAO]: 'Premiação',
  [EventType.ENCONTRO]: 'Visita de Acompanhamento',
  [EventType.OUTRO]: 'Outro',
};

const EVENT_STATUS_LABELS: Record<EventStatus, string> = {
  [EventStatus.PLANEJADO]: 'Planejado',
  [EventStatus.REALIZADO]: 'Realizado',
  [EventStatus.ARQUIVADO]: 'Arquivado',
};

type TabType = 'overview' | 'photos' | 'report' | 'documents' | 'attendance' | 'notes';

export default function EventDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [event, setEvent] = useState<Event | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  
  // Photos
  const [photos, setPhotos] = useState<EventFile[]>([]);
  const [uploadingPhotos, setUploadingPhotos] = useState(false);
  const [selectedPhoto, setSelectedPhoto] = useState<EventFile | null>(null);
  
  // Documents
  const [documents, setDocuments] = useState<EventFile[]>([]);
  const [uploadingDocs, setUploadingDocs] = useState(false);
  
  // Attendance
  const [attendance, setAttendance] = useState<Attendance[]>([]);
  const [showAddAttendee, setShowAddAttendee] = useState(false);
  const [newAttendee, setNewAttendee] = useState({
    person_name: '',
    person_role: '',
    school: '',
    present: true,
  });
  
  // Notes
  const [notes, setNotes] = useState<EventNote[]>([]);
  const [newNote, setNewNote] = useState('');
  const [savingNote, setSavingNote] = useState(false);

  useEffect(() => {
    if (id) {
      loadEvent();
    }
  }, [id]);

  useEffect(() => {
    if (id && event) {
      loadTabData();
    }
  }, [activeTab, id, event]);

  const loadEvent = async () => {
    try {
      setLoading(true);
      const data = await eventsAPI.get(id!);
      setEvent(data);
    } catch (error) {
      toast.error('Erro ao carregar evento');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const loadTabData = async () => {
    try {
      switch (activeTab) {
        case 'photos':
          const photosData = await filesAPI.list(id!, FileKind.PHOTO);
          setPhotos(photosData);
          break;
        case 'documents':
          const docsData = await filesAPI.list(id!, FileKind.DOC);
          setDocuments(docsData);
          break;
        case 'attendance':
          const attendanceData = await attendanceAPI.list(id!);
          setAttendance(attendanceData);
          break;
        case 'notes':
          const notesData = await notesAPI.list(id!);
          setNotes(notesData);
          break;
      }
    } catch (error) {
      console.error('Error loading tab data:', error);
    }
  };

  const handleDeleteEvent = async () => {
    if (!window.confirm('Tem certeza que deseja excluir este evento?')) return;
    
    try {
      await eventsAPI.delete(id!);
      toast.success('Evento excluído com sucesso');
      navigate('/dashboard');
    } catch (error) {
      toast.error('Erro ao excluir evento');
    }
  };

  // Photo handlers
  const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files?.length) return;

    try {
      setUploadingPhotos(true);
      await filesAPI.upload(id!, Array.from(files), FileKind.PHOTO);
      toast.success('Fotos enviadas com sucesso!');
      loadTabData();
    } catch (error) {
      toast.error('Erro ao enviar fotos');
    } finally {
      setUploadingPhotos(false);
      e.target.value = '';
    }
  };

  const handleDeletePhoto = async (fileId: string) => {
    if (!window.confirm('Excluir esta foto?')) return;
    
    try {
      await filesAPI.delete(id!, fileId);
      toast.success('Foto excluída');
      setPhotos(photos.filter(p => p.id !== fileId));
      setSelectedPhoto(null);
    } catch (error) {
      toast.error('Erro ao excluir foto');
    }
  };

  // Document handlers
  const handleDocUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files?.length) return;

    try {
      setUploadingDocs(true);
      await filesAPI.upload(id!, Array.from(files), FileKind.DOC);
      toast.success('Documentos enviados com sucesso!');
      loadTabData();
    } catch (error) {
      toast.error('Erro ao enviar documentos');
    } finally {
      setUploadingDocs(false);
      e.target.value = '';
    }
  };

  const handleDeleteDoc = async (fileId: string) => {
    if (!window.confirm('Excluir este documento?')) return;
    
    try {
      await filesAPI.delete(id!, fileId);
      toast.success('Documento excluído');
      setDocuments(documents.filter(d => d.id !== fileId));
    } catch (error) {
      toast.error('Erro ao excluir documento');
    }
  };

  // Attendance handlers
  const handleAddAttendee = async () => {
    if (!newAttendee.person_name.trim()) {
      toast.error('O nome é obrigatório');
      return;
    }

    try {
      await attendanceAPI.create(id!, newAttendee);
      toast.success('Participante adicionado');
      setNewAttendee({ person_name: '', person_role: '', school: '', present: true });
      setShowAddAttendee(false);
      loadTabData();
    } catch (error) {
      toast.error('Erro ao adicionar participante');
    }
  };

  const handleDeleteAttendee = async (attendeeId: string) => {
    if (!window.confirm('Remover este participante?')) return;
    
    try {
      await attendanceAPI.delete(id!, attendeeId);
      setAttendance(attendance.filter(a => a.id !== attendeeId));
    } catch (error) {
      toast.error('Erro ao remover participante');
    }
  };

  const handleExportCSV = async () => {
    try {
      const blob = await attendanceAPI.exportCSV(id!);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `frequencia-${event?.title.replace(/\s+/g, '-')}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      toast.error('Erro ao exportar');
    }
  };

  // Notes handlers
  const handleAddNote = async () => {
    if (!newNote.trim()) return;

    try {
      setSavingNote(true);
      await notesAPI.create(id!, { text: newNote });
      toast.success('Observação adicionada');
      setNewNote('');
      loadTabData();
    } catch (error) {
      toast.error('Erro ao adicionar observação');
    } finally {
      setSavingNote(false);
    }
  };

  const handleDeleteNote = async (noteId: string) => {
    if (!window.confirm('Excluir esta observação?')) return;
    
    try {
      await notesAPI.delete(id!, noteId);
      setNotes(notes.filter(n => n.id !== noteId));
    } catch (error) {
      toast.error('Erro ao excluir observação');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  if (loading) {
    return (
      <Layout>
        <div className="loading">
          <div className="spinner" />
          <p>Carregando evento...</p>
        </div>
      </Layout>
    );
  }

  if (!event) return null;

  return (
    <Layout>
      {/* Header */}
      <div className="event-detail-header">
        <div className="header-left">
          <button className="btn btn-ghost" onClick={() => navigate('/dashboard')}>
            <ArrowLeft size={20} />
            Voltar
          </button>
          <div className="event-info">
            <div className="event-badges">
              <span className="badge badge-primary">{EVENT_TYPE_LABELS[event.type]}</span>
              <span className="badge badge-secondary">{EVENT_STATUS_LABELS[event.status]}</span>
            </div>
            <h1>{event.title}</h1>
          </div>
        </div>
        <div className="header-actions">
          <Link to={`/events/${id}/edit`} className="btn btn-secondary">
            <Edit size={18} />
            Editar
          </Link>
          <button className="btn btn-danger" onClick={handleDeleteEvent}>
            <Trash2 size={18} />
            Excluir
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <Calendar size={18} />
          Visão Geral
        </button>
        <button 
          className={`tab ${activeTab === 'photos' ? 'active' : ''}`}
          onClick={() => setActiveTab('photos')}
        >
          <Image size={18} />
          Fotos
        </button>
        {event.type === EventType.ENCONTRO && (
          <button 
            className={`tab ${activeTab === 'report' ? 'active' : ''}`}
            onClick={() => setActiveTab('report')}
          >
            <FileSpreadsheet size={18} />
            Relatório
          </button>
        )}
        <button 
          className={`tab ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents')}
        >
          <FileText size={18} />
          Documentos
        </button>
        <button 
          className={`tab ${activeTab === 'attendance' ? 'active' : ''}`}
          onClick={() => setActiveTab('attendance')}
        >
          <ClipboardList size={18} />
          Frequência
        </button>
        <button 
          className={`tab ${activeTab === 'notes' ? 'active' : ''}`}
          onClick={() => setActiveTab('notes')}
        >
          <MessageSquare size={18} />
          Observações
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="info-grid">
              <div className="info-card">
                <Calendar size={24} />
                <div>
                  <label>Data/Hora</label>
                  <p>
                    {format(new Date(event.start_at), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                    {event.end_at && ` - ${format(new Date(event.end_at), "HH:mm", { locale: ptBR })}`}
                  </p>
                </div>
              </div>
              
              {event.location && (
                <div className="info-card">
                  <MapPin size={24} />
                  <div>
                    <label>Local</label>
                    <p>{event.location}</p>
                  </div>
                </div>
              )}
              
              {event.audience && (
                <div className="info-card">
                  <Users size={24} />
                  <div>
                    <label>Público-Alvo</label>
                    <p>{event.audience}</p>
                  </div>
                </div>
              )}
            </div>

            {event.description && (
              <div className="description-card">
                <h3>Descrição</h3>
                <p>{event.description}</p>
              </div>
            )}

            {event.tags && event.tags.length > 0 && (
              <div className="tags-section">
                <h3>Tags</h3>
                <div className="tags-list">
                  {event.tags.map((tag, i) => (
                    <span key={i} className="tag">{tag}</span>
                  ))}
                </div>
              </div>
            )}

            {event.schools && event.schools.length > 0 && (
              <div className="schools-section">
                <h3>Escolas Vinculadas</h3>
                <ul>
                  {event.schools.map((school, i) => (
                    <li key={i}>{school}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Photos Tab */}
        {activeTab === 'photos' && (
          <div className="photos-tab">
            <div className="tab-header">
              <h3>Galeria de Fotos</h3>
              <label className="btn btn-primary">
                <Upload size={18} />
                {uploadingPhotos ? 'Enviando...' : 'Enviar Fotos'}
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handlePhotoUpload}
                  disabled={uploadingPhotos}
                  style={{ display: 'none' }}
                />
              </label>
            </div>

            {photos.length === 0 ? (
              <div className="empty-state">
                <Image size={48} />
                <p>Nenhuma foto adicionada</p>
              </div>
            ) : (
              <div className="photos-grid">
                {photos.map((photo) => (
                  <div 
                    key={photo.id} 
                    className="photo-item"
                    onClick={() => setSelectedPhoto(photo)}
                  >
                    <img 
                      src={photo.thumbnail_url || photo.url} 
                      alt={photo.filename}
                    />
                    <button 
                      className="delete-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeletePhoto(photo.id);
                      }}
                    >
                      <X size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Lightbox */}
            {selectedPhoto && (
              <div className="lightbox" onClick={() => setSelectedPhoto(null)}>
                <button className="close-btn" onClick={() => setSelectedPhoto(null)}>
                  <X size={24} />
                </button>
                <img src={selectedPhoto.url} alt={selectedPhoto.filename} />
              </div>
            )}
          </div>
        )}

        {/* Report Tab - Only for Visita de Acompanhamento */}
        {activeTab === 'report' && event.type === EventType.ENCONTRO && (
          <div className="report-tab">
            <div className="tab-header">
              <h3>Relatório de Visita de Acompanhamento</h3>
            </div>
            <div className="report-placeholder">
              <FileSpreadsheet size={48} />
              <h4>Relatório de Acompanhamento</h4>
              <p>Em breve você poderá preencher o relatório de acompanhamento aqui.</p>
              <p className="text-muted">Esta funcionalidade será implementada em breve.</p>
            </div>
          </div>
        )}

        {/* Documents Tab */}
        {activeTab === 'documents' && (
          <div className="documents-tab">
            <div className="tab-header">
              <h3>Documentos</h3>
              <label className="btn btn-primary">
                <Upload size={18} />
                {uploadingDocs ? 'Enviando...' : 'Enviar Documentos'}
                <input
                  type="file"
                  multiple
                  accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.png,.jpg,.jpeg"
                  onChange={handleDocUpload}
                  disabled={uploadingDocs}
                  style={{ display: 'none' }}
                />
              </label>
            </div>

            {documents.length === 0 ? (
              <div className="empty-state">
                <FileText size={48} />
                <p>Nenhum documento adicionado</p>
              </div>
            ) : (
              <div className="documents-list">
                {documents.map((doc) => (
                  <div key={doc.id} className="document-item">
                    <FileText size={24} />
                    <div className="doc-info">
                      <span className="doc-name">{doc.filename}</span>
                      <span className="doc-meta">
                        {formatFileSize(doc.size)} • {doc.uploader?.name || 'Usuário'}
                      </span>
                    </div>
                    <div className="doc-actions">
                      <a 
                        href={doc.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="btn btn-icon"
                      >
                        <Download size={18} />
                      </a>
                      <button 
                        className="btn btn-icon btn-danger"
                        onClick={() => handleDeleteDoc(doc.id)}
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Attendance Tab */}
        {activeTab === 'attendance' && (
          <div className="attendance-tab">
            <div className="tab-header">
              <h3>Lista de Presença ({attendance.length})</h3>
              <div className="header-buttons">
                <button className="btn btn-secondary" onClick={handleExportCSV}>
                  <Download size={18} />
                  Exportar CSV
                </button>
                <button 
                  className="btn btn-primary"
                  onClick={() => setShowAddAttendee(true)}
                >
                  <Plus size={18} />
                  Adicionar
                </button>
              </div>
            </div>

            {showAddAttendee && (
              <div className="add-attendee-form">
                <input
                  type="text"
                  className="form-input"
                  placeholder="Nome *"
                  value={newAttendee.person_name}
                  onChange={(e) => setNewAttendee({ ...newAttendee, person_name: e.target.value })}
                />
                <input
                  type="text"
                  className="form-input"
                  placeholder="Função/Cargo"
                  value={newAttendee.person_role}
                  onChange={(e) => setNewAttendee({ ...newAttendee, person_role: e.target.value })}
                />
                <input
                  type="text"
                  className="form-input"
                  placeholder="Escola"
                  value={newAttendee.school}
                  onChange={(e) => setNewAttendee({ ...newAttendee, school: e.target.value })}
                />
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={newAttendee.present}
                    onChange={(e) => setNewAttendee({ ...newAttendee, present: e.target.checked })}
                  />
                  Presente
                </label>
                <div className="form-actions">
                  <button className="btn btn-secondary" onClick={() => setShowAddAttendee(false)}>
                    Cancelar
                  </button>
                  <button className="btn btn-primary" onClick={handleAddAttendee}>
                    Adicionar
                  </button>
                </div>
              </div>
            )}

            {attendance.length === 0 ? (
              <div className="empty-state">
                <ClipboardList size={48} />
                <p>Nenhum participante registrado</p>
              </div>
            ) : (
              <table className="attendance-table">
                <thead>
                  <tr>
                    <th>Nome</th>
                    <th>Função</th>
                    <th>Escola</th>
                    <th>Presença</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {attendance.map((a) => (
                    <tr key={a.id}>
                      <td>{a.person_name}</td>
                      <td>{a.person_role || '-'}</td>
                      <td>{a.school || '-'}</td>
                      <td>
                        {a.present ? (
                          <span className="presence-yes"><Check size={16} /> Sim</span>
                        ) : (
                          <span className="presence-no"><X size={16} /> Não</span>
                        )}
                      </td>
                      <td>
                        <button 
                          className="btn btn-icon btn-danger"
                          onClick={() => handleDeleteAttendee(a.id)}
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* Notes Tab */}
        {activeTab === 'notes' && (
          <div className="notes-tab">
            <div className="add-note">
              <textarea
                className="form-textarea"
                placeholder="Adicionar observação..."
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                rows={3}
              />
              <button 
                className="btn btn-primary"
                onClick={handleAddNote}
                disabled={savingNote || !newNote.trim()}
              >
                {savingNote ? 'Salvando...' : 'Adicionar Observação'}
              </button>
            </div>

            {notes.length === 0 ? (
              <div className="empty-state">
                <MessageSquare size={48} />
                <p>Nenhuma observação registrada</p>
              </div>
            ) : (
              <div className="notes-list">
                {notes.map((note) => (
                  <div key={note.id} className="note-card">
                    <div className="note-header">
                      <span className="note-author">{note.author?.name || 'Usuário'}</span>
                      <span className="note-date">
                        {format(new Date(note.created_at), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                      </span>
                    </div>
                    <p className="note-text">{note.text}</p>
                    <button 
                      className="btn btn-icon btn-danger"
                      onClick={() => handleDeleteNote(note.id)}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
}
