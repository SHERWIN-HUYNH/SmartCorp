'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  Database,
  Edit2,
  Eye,
  File,
  FileText,
  Filter,
  RefreshCw,
  Search,
  Settings,
  Trash2,
} from 'lucide-react';

import {
  deleteDocument,
  listDocuments,
  listRoles,
  retryDocumentIngestion,
  type DocumentRecord,
  type DocumentStatus,
  type RoleOption,
  updateDocumentPermissions,
} from '@/lib/auth-api';

function formatFileSize(bytes?: number | null): string {
  if (!bytes || bytes <= 0) {
    return 'Unknown size';
  }

  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function resolveTypeLabel(document: DocumentRecord): string {
  const filename = document.filename.toLowerCase();
  const mimeType = document.mime_type?.toLowerCase() || '';

  if (mimeType.includes('pdf') || filename.endsWith('.pdf')) {
    return 'PDF Document';
  }
  if (mimeType.includes('word') || filename.endsWith('.docx') || filename.endsWith('.doc')) {
    return 'Word Document';
  }
  if (mimeType.includes('json') || filename.endsWith('.json')) {
    return 'JSON Data';
  }
  if (mimeType.includes('markdown') || filename.endsWith('.md')) {
    return 'Markdown';
  }
  return 'File';
}

function resolveStatusLabel(status: DocumentStatus): string {
  if (status === 'ready') {
    return 'Indexed';
  }
  if (status === 'processing') {
    return 'Processing';
  }
  if (status === 'pending') {
    return 'Pending';
  }
  if (status === 'failed') {
    return 'Failed';
  }
  return 'Deleted';
}

function statusBadgeClass(status: DocumentStatus): string {
  if (status === 'ready') {
    return 'bg-emerald-100 text-emerald-700';
  }
  if (status === 'processing' || status === 'pending') {
    return 'bg-amber-100 text-amber-700';
  }
  if (status === 'failed') {
    return 'bg-error-container/20 text-error';
  }
  return 'bg-slate-200 text-slate-600';
}

const PAGE_SIZE = 20;

export function DocumentTable() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [roles, setRoles] = useState<RoleOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);

  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | DocumentStatus>('all');

  const [openPopoverId, setOpenPopoverId] = useState<string | null>(null);
  const [draftRoleIds, setDraftRoleIds] = useState<string[]>([]);
  const [savingPermissions, setSavingPermissions] = useState(false);
  const [retryingId, setRetryingId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const roleNameById = useMemo(() => {
    const map: Record<string, string> = {};
    roles.forEach((role) => {
      map[role.id] = role.name;
    });
    return map;
  }, [roles]);

  const totalPages = useMemo(() => {
    return Math.max(1, Math.ceil(totalCount / PAGE_SIZE));
  }, [totalCount]);

  const pageRange = useMemo(() => {
    if (totalCount === 0) {
      return { start: 0, end: 0 };
    }

    const start = (page - 1) * PAGE_SIZE + 1;
    const end = Math.min(start + documents.length - 1, totalCount);
    return { start, end };
  }, [documents.length, page, totalCount]);

  const loadRoles = useCallback(async () => {
    try {
      const rolesResult = await listRoles();
      setRoles(rolesResult);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Failed to load roles.');
    }
  }, []);

  const loadDocuments = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const documentsResult = await listDocuments({
        includeDeleted: false,
        status: statusFilter === 'all' ? undefined : statusFilter,
        search: debouncedSearchTerm || undefined,
        limit: PAGE_SIZE,
        offset: (page - 1) * PAGE_SIZE,
      });

      const resolvedTotal = documentsResult.total_count ?? documentsResult.total;
      setDocuments(documentsResult.items);
      setTotalCount(resolvedTotal);

      const maxPage = Math.max(1, Math.ceil(resolvedTotal / PAGE_SIZE));
      if (page > maxPage) {
        setPage(maxPage);
      }
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Failed to load documents.');
    } finally {
      setLoading(false);
    }
  }, [debouncedSearchTerm, page, statusFilter]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setDebouncedSearchTerm(searchTerm.trim());
    }, 350);

    return () => window.clearTimeout(timer);
  }, [searchTerm]);

  useEffect(() => {
    setPage(1);
  }, [debouncedSearchTerm, statusFilter]);

  useEffect(() => {
    void loadRoles();
  }, [loadRoles]);

  useEffect(() => {
    void loadDocuments();
  }, [loadDocuments]);

  useEffect(() => {
    const handleClickOutside = () => setOpenPopoverId(null);
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  const openPermissionsPopover = (document: DocumentRecord, event: React.MouseEvent) => {
    event.stopPropagation();
    setOpenPopoverId((current) => (current === document.id ? null : document.id));
    setDraftRoleIds(document.role_ids);
  };

  const toggleDraftRole = (roleId: string) => {
    setDraftRoleIds((prev) =>
      prev.includes(roleId) ? prev.filter((id) => id !== roleId) : [...prev, roleId],
    );
  };

  const savePermissions = async () => {
    if (!openPopoverId || draftRoleIds.length === 0) {
      return;
    }

    setSavingPermissions(true);
    try {
      const updated = await updateDocumentPermissions(openPopoverId, draftRoleIds);
      setDocuments((prev) => prev.map((doc) => (doc.id === updated.id ? updated : doc)));
      setOpenPopoverId(null);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : 'Failed to update permissions.');
    } finally {
      setSavingPermissions(false);
    }
  };

  const handleRetry = async (documentId: string) => {
    setRetryingId(documentId);
    try {
      await retryDocumentIngestion(documentId);
      await loadDocuments();
    } catch (retryError) {
      setError(retryError instanceof Error ? retryError.message : 'Failed to retry ingestion.');
    } finally {
      setRetryingId(null);
    }
  };

  const handleDelete = async (documentId: string) => {
    setDeletingId(documentId);
    try {
      await deleteDocument(documentId);
      await loadDocuments();
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : 'Failed to delete document.');
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <section className="space-y-4 mb-12">
      <div className="bg-surface-container-low p-4 rounded-2xl flex flex-wrap items-center gap-4 shadow-sm border border-outline-variant/10">
        <div className="flex-1 min-w-[300px] relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-outline w-4 h-4" />
          <input
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            className="w-full bg-surface-container-lowest border-none rounded-xl pl-10 pr-4 py-2.5 text-sm focus:ring-2 focus:ring-primary/5 focus:outline-none shadow-sm transition-all"
            placeholder="Search by file name or hash..."
            type="text"
          />
        </div>

        <div className="flex gap-3 items-center">
          <select
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value as 'all' | DocumentStatus)}
            className="bg-surface-container-lowest border-none rounded-xl text-sm font-medium py-2.5 px-4 focus:ring-2 focus:ring-primary/5 focus:outline-none shadow-sm min-w-[120px]"
          >
            <option value="all">Status: All</option>
            <option value="ready">Indexed</option>
            <option value="processing">Processing</option>
            <option value="pending">Pending</option>
            <option value="failed">Failed</option>
          </select>
          <button className="px-4 py-2 bg-surface-container-lowest border border-outline-variant/30 rounded-xl flex items-center gap-2 text-sm font-semibold hover:bg-surface-container-low transition-colors shadow-sm">
            <Filter className="w-4 h-4" />
            Filters
          </button>
          <button
            type="button"
            onClick={() => void loadDocuments()}
            className="px-4 py-2 bg-surface-container-lowest border border-outline-variant/30 rounded-xl flex items-center gap-2 text-sm font-semibold hover:bg-surface-container-low transition-colors shadow-sm"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      <div className="bg-surface-container-lowest rounded-2xl shadow-sm border border-slate-200 overflow-visible">
        <div className="p-6 border-b border-slate-200 flex items-center justify-between">
          <h3 className="font-headline font-bold text-on-surface">Document Index Registry</h3>
          <div className="flex gap-2">
            <button className="p-2 rounded-lg hover:bg-surface-container-low transition-colors text-outline">
              <Eye className="w-5 h-5" />
            </button>
            <button className="p-2 rounded-lg hover:bg-surface-container-low transition-colors text-outline">
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>

        {error && <p className="px-6 pt-4 text-sm text-error">{error}</p>}

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 text-xs font-bold text-outline uppercase tracking-wider border-r border-slate-200/60 last:border-0">Document Name</th>
                <th className="px-6 py-4 text-xs font-bold text-outline uppercase tracking-wider border-r border-slate-200/60 last:border-0">Effective Date</th>
                <th className="px-6 py-4 text-xs font-bold text-outline uppercase tracking-wider border-r border-slate-200/60 last:border-0">Allowed Roles</th>
                <th className="px-6 py-4 text-xs font-bold text-outline uppercase tracking-wider border-r border-slate-200/60 last:border-0">Status</th>
                <th className="px-6 py-4 text-xs font-bold text-outline uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {loading && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-sm text-outline text-center">
                    Loading documents...
                  </td>
                </tr>
              )}

              {!loading && documents.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-sm text-outline text-center">
                    No documents found.
                  </td>
                </tr>
              )}

              {!loading && documents.map((doc) => {
                const typeLabel = resolveTypeLabel(doc);
                const effectiveDateLabel = doc.effective_date
                  ? new Date(doc.effective_date).toLocaleDateString()
                  : 'N/A';

                return (
                  <tr key={doc.id} className="hover:bg-slate-50/50 transition-colors group">
                    <td className="px-6 py-4 border-r border-slate-100 last:border-0 max-w-[320px] w-[320px]">
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-8 h-8 rounded flex items-center justify-center ${
                            typeLabel.includes('PDF')
                              ? 'bg-red-50 text-red-500'
                              : typeLabel.includes('Word')
                                ? 'bg-blue-50 text-blue-500'
                                : 'bg-yellow-50 text-yellow-600'
                          }`}
                        >
                          {typeLabel.includes('PDF') ? (
                            <FileText className="w-4 h-4" />
                          ) : typeLabel.includes('Word') ? (
                            <File className="w-4 h-4" />
                          ) : (
                            <Database className="w-4 h-4" />
                          )}
                        </div>
                        <div className="min-w-0 max-w-[240px] w-[240px]">
                          <p className="text-sm font-bold text-on-surface truncate" title={doc.filename}>{doc.filename}</p>
                          <p className="text-[10px] text-outline">
                            {typeLabel} • {formatFileSize(doc.file_size_bytes)}
                          </p>
                        </div>
                      </div>
                    </td>

                    <td className="px-6 py-4 border-r border-slate-100 last:border-0">
                      <div className="text-[11px]">
                        <p className="font-bold text-on-surface">{effectiveDateLabel}</p>
                        <p className="text-outline">Created {new Date(doc.created_at).toLocaleDateString()}</p>
                      </div>
                    </td>

                    <td className="px-6 py-4 border-r border-slate-100 last:border-0 relative">
                      <div className="relative" onClick={(event) => event.stopPropagation()}>
                        <button
                          className="w-full flex flex-wrap gap-1 p-1 bg-surface-container-low border border-slate-200 rounded-lg hover:border-primary/30 transition-all text-left items-start content-start max-h-[60px] overflow-y-auto"
                          onClick={(event) => openPermissionsPopover(doc, event)}
                        >
                          {doc.role_ids.map((roleId) => (
                            <span key={roleId} className="px-2 py-0.5 bg-primary text-white text-[10px] font-bold rounded shrink-0">
                              {roleNameById[roleId] || roleId.slice(0, 8)}
                            </span>
                          ))}
                          <Edit2 className="w-3.5 h-3.5 ml-auto mt-0.5 text-outline shrink-0" />
                        </button>

                        {openPopoverId === doc.id && (
                          <div className="absolute left-0 top-full mt-2 z-[60] w-56 bg-white rounded-xl shadow-2xl border border-slate-200 p-4 space-y-3 animate-in fade-in zoom-in duration-200">
                            <p className="text-[10px] font-bold text-outline uppercase tracking-widest">
                              Update Permissions
                            </p>
                            <div className="space-y-2 max-h-40 overflow-y-auto pr-2">
                              {roles.map((role) => (
                                <label key={role.id} className="flex items-center gap-2 cursor-pointer">
                                  <input
                                    type="checkbox"
                                    checked={draftRoleIds.includes(role.id)}
                                    onChange={() => toggleDraftRole(role.id)}
                                    className="w-3.5 h-3.5 rounded border-slate-300 text-primary focus:ring-primary shrink-0"
                                  />
                                  <span className="text-xs font-medium text-on-surface">{role.name}</span>
                                </label>
                              ))}
                            </div>
                            <div className="flex gap-2 pt-2 border-t border-slate-100">
                              <button
                                className="flex-1 py-1.5 bg-primary text-white text-[10px] font-bold rounded-lg hover:opacity-90 transition-all disabled:opacity-50"
                                onClick={() => void savePermissions()}
                                disabled={savingPermissions || draftRoleIds.length === 0}
                              >
                                {savingPermissions ? 'Saving...' : 'Save'}
                              </button>
                              <button
                                className="flex-1 py-1.5 bg-slate-100 text-slate-600 text-[10px] font-bold rounded-lg hover:bg-slate-200 transition-colors"
                                onClick={() => setOpenPopoverId(null)}
                              >
                                Cancel
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    </td>

                    <td className="px-6 py-4 border-r border-slate-100 last:border-0">
                      <span
                        className={`px-2 py-1 text-[10px] font-extrabold rounded-full uppercase flex items-center w-fit gap-1 ${statusBadgeClass(doc.status)}`}
                      >
                        <span className="w-1 h-1 rounded-full bg-current"></span>
                        {resolveStatusLabel(doc.status)}
                      </span>
                    </td>

                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        {doc.status === 'failed' ? (
                          <button
                            className="p-2 hover:bg-slate-100 rounded-lg text-outline disabled:opacity-50"
                            onClick={() => void handleRetry(doc.id)}
                            disabled={retryingId === doc.id}
                            title="Retry ingestion"
                          >
                            {retryingId === doc.id ? (
                              <RefreshCw className="w-4 h-4 animate-spin" />
                            ) : (
                              <AlertTriangle className="w-4 h-4" />
                            )}
                          </button>
                        ) : (
                          <button className="p-2 hover:bg-slate-100 rounded-lg text-outline" title="View document details">
                            <Eye className="w-4 h-4" />
                          </button>
                        )}

                        <button
                          className="p-2 hover:bg-error-container/10 text-error rounded-lg disabled:opacity-50"
                          onClick={() => void handleDelete(doc.id)}
                          disabled={deletingId === doc.id}
                          title="Soft delete document"
                        >
                          {deletingId === doc.id ? (
                            <RefreshCw className="w-4 h-4 animate-spin" />
                          ) : (
                            <Trash2 className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="p-6 border-t border-slate-200 bg-slate-50/50 flex items-center justify-between gap-4">
          <p className="text-sm text-outline font-medium">
            Showing <span className="text-on-surface font-bold">{pageRange.start}</span>
            {' - '}
            <span className="text-on-surface font-bold">{pageRange.end}</span> of{' '}
            <span className="text-on-surface font-bold">{totalCount}</span> documents
          </p>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setPage((prev) => Math.max(1, prev - 1))}
              disabled={loading || page <= 1}
              className="px-3 py-1.5 bg-surface-container-lowest border border-outline-variant/30 rounded-lg text-sm font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-surface-container-low transition-colors"
            >
              Previous
            </button>
            <p className="text-sm text-outline">
              Page <span className="font-bold text-on-surface">{page}</span> /{' '}
              <span className="font-bold text-on-surface">{totalPages}</span>
            </p>
            <button
              type="button"
              onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
              disabled={loading || page >= totalPages}
              className="px-3 py-1.5 bg-surface-container-lowest border border-outline-variant/30 rounded-lg text-sm font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-surface-container-low transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
