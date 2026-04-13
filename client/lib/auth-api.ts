const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api';

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: string;
  role_id?: string | null;
  state: string;
  created_at: string;
}

export interface LoginResponse {
  user: AuthUser;
  token_type: string;
}
export interface SignupPayload {
  email: string;
  name: string;
  password: string;
}

export interface UploadDocumentsPayload {
  files: File[];
  effectiveDate: string;
  roleIds: string[];
}

export interface UploadDocumentsResponse {
  message: string;
  uploaded: number;
  duplicates: number;
  failed: number;
  items: UploadDocumentItemResult[];
}

export interface UploadDocumentItemResult {
  filename: string;
  status: 'uploaded' | 'duplicate' | 'failed';
  detail: string;
  documentId?: string;
  taskId?: string;
}

export interface RoleOption {
  id: string;
  name: string;
  description?: string | null;
}

export interface RoleManagementRole {
  id: string;
  name: string;
  description?: string | null;
  created_at?: string | null;
  user_count: number;
  doc_count: number;
  category: string;
  is_system: boolean;
}

export interface RoleManagementUser {
  id: string;
  name: string;
  email: string;
  state: string;
  created_at?: string | null;
}

export interface RoleManagementDocument {
  id: string;
  filename: string;
  status: string;
  uploaded_by: string;
  effective_date?: string | null;
  created_at?: string | null;
}

export interface RoleManagementRoleDetail extends RoleManagementRole {
  users: RoleManagementUser[];
  documents: RoleManagementDocument[];
}

export interface RoleManagementListResponse {
  items: RoleManagementRole[];
  total: number;
}

export interface RoleCreatePayload {
  name: string;
  description?: string | null;
}

export interface RoleUpdatePayload {
  name?: string;
  description?: string | null;
}

export interface RoleDeleteResponse {
  message: string;
  role_id: string;
}

export interface RoleManagementUsersResponse {
  items: RoleManagementUser[];
  total: number;
}

export interface RoleManagementDocumentsResponse {
  items: RoleManagementDocument[];
  total: number;
}

export interface PrecheckDocumentResponse {
  duplicate: boolean;
  existing_document?: {
    id: string;
    filename: string;
    status: string;
    created_at: string;
  } | null;
}

export interface DocumentUploadResponse {
  upload_token: string;
  filename: string;
  file_url: string;
  file_hash: string;
  file_size_bytes: number;
  mime_type?: string | null;
}

export interface ConfirmDocumentUploadResponse {
  message: string;
  task_id?: string | null;
  document: {
    id: string;
    filename: string;
    status: string;
  };
}

export type DocumentStatus = 'pending' | 'processing' | 'ready' | 'failed' | 'deleted';

export interface DocumentRecord {
  id: string;
  filename: string;
  file_url: string;
  file_size_bytes?: number | null;
  mime_type?: string | null;
  file_hash: string;
  effective_date?: string | null;
  status: DocumentStatus;
  error_message?: string | null;
  deleted_at?: string | null;
  created_at: string;
  updated_at?: string | null;
  role_ids: string[];
}

export interface DocumentsListResponse {
  items: DocumentRecord[];
  total: number;
}

export interface DocumentStatsResponse {
  total: number;
  pending: number;
  processing: number;
  ready: number;
  failed: number;
  deleted: number;
}

export interface DeleteDocumentResponse {
  message: string;
  document_id: string;
}

export type ProcessingQueueStatus = 'pending' | 'processing' | 'failed';

export interface ProcessingQueueItem {
  id: string;
  filename: string;
  file_size_bytes?: number | null;
  mime_type?: string | null;
  status: ProcessingQueueStatus;
  error_message?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface ProcessingQueueResponse {
  items: ProcessingQueueItem[];
  total: number;
}

export class AuthApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'AuthApiError';
    this.status = status;
  }
}

function getErrorMessage(payload: unknown, fallback: string): string {
  if (!payload || typeof payload !== 'object') {
    return fallback;
  }

  const detail = (payload as { detail?: unknown }).detail;
  if (typeof detail === 'string') {
    return detail;
  }
  if (detail && typeof detail === 'object') {
    const message = (detail as { message?: unknown }).message;
    if (typeof message === 'string') {
      return message;
    }
  }
  return fallback;
}

function bufferToHex(buffer: ArrayBuffer): string {
  return Array.from(new Uint8Array(buffer))
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('');
}

async function computeSha256(file: File): Promise<string> {
  const bytes = await file.arrayBuffer();
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return bufferToHex(digest);
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Login failed. Please try again.'), response.status);
  }

  return response.json() as Promise<LoginResponse>;
}

export async function signup(payload: SignupPayload): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Login failed. Please try again.'), response.status);
  }

  return response.json() as Promise<LoginResponse>;
}

export async function getCurrentUser(): Promise<AuthUser> {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: 'GET',
    credentials: 'include',
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Unauthorized.'), response.status);
  }

  return response.json() as Promise<AuthUser>;
}

export async function listRoles(): Promise<RoleOption[]> {
  const response = await fetch(`${API_BASE_URL}/documents/roles`, {
    method: 'GET',
    credentials: 'include',
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Failed to load role list.'), response.status);
  }

  return response.json() as Promise<RoleOption[]>;
}

export async function listRoleManagementRoles(): Promise<RoleManagementListResponse> {
  const response = await fetch(`${API_BASE_URL}/roles`, {
    method: 'GET',
    credentials: 'include',
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Failed to load role management list.'), response.status);
  }

  return response.json() as Promise<RoleManagementListResponse>;
}

export async function getRoleManagementRole(roleId: string): Promise<RoleManagementRoleDetail> {
  const response = await fetch(`${API_BASE_URL}/roles/${roleId}`, {
    method: 'GET',
    credentials: 'include',
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Failed to load role details.'), response.status);
  }

  return response.json() as Promise<RoleManagementRoleDetail>;
}

export async function getRoleManagementUsers(
  roleId: string,
  options?: { search?: string; state?: string; limit?: number; offset?: number },
): Promise<RoleManagementUsersResponse> {
  const query = new URLSearchParams();
  if (options?.search) {
    query.set('search', options.search);
  }
  if (options?.state) {
    query.set('state', options.state);
  }
  if (typeof options?.limit === 'number') {
    query.set('limit', String(options.limit));
  }
  if (typeof options?.offset === 'number') {
    query.set('offset', String(options.offset));
  }

  const response = await fetch(
    `${API_BASE_URL}/roles/${roleId}/users${query.toString() ? `?${query.toString()}` : ''}`,
    {
      method: 'GET',
      credentials: 'include',
    },
  );

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Failed to load role users.'), response.status);
  }

  return response.json() as Promise<RoleManagementUsersResponse>;
}

export async function assignUserToRole(roleId: string, userId: string): Promise<RoleManagementUser> {
  const response = await fetch(`${API_BASE_URL}/roles/${roleId}/users/${userId}`, {
    method: 'PUT',
    credentials: 'include',
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Failed to assign user to role.'), response.status);
  }

  return response.json() as Promise<RoleManagementUser>;
}

export async function removeUserFromRole(roleId: string, userId: string): Promise<RoleManagementUser> {
  const response = await fetch(`${API_BASE_URL}/roles/${roleId}/users/${userId}`, {
    method: 'DELETE',
    credentials: 'include',
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Failed to remove user from role.'), response.status);
  }

  return response.json() as Promise<RoleManagementUser>;
}

export async function getRoleManagementDocuments(
  roleId: string,
  options?: {
    search?: string;
    status?: string;
    includeDeleted?: boolean;
    limit?: number;
    offset?: number;
  },
): Promise<RoleManagementDocumentsResponse> {
  const query = new URLSearchParams();
  if (options?.search) {
    query.set('search', options.search);
  }
  if (options?.status) {
    query.set('status', options.status);
  }
  if (options?.includeDeleted) {
    query.set('include_deleted', 'true');
  }
  if (typeof options?.limit === 'number') {
    query.set('limit', String(options.limit));
  }
  if (typeof options?.offset === 'number') {
    query.set('offset', String(options.offset));
  }

  const response = await fetch(
    `${API_BASE_URL}/roles/${roleId}/documents${query.toString() ? `?${query.toString()}` : ''}`,
    {
      method: 'GET',
      credentials: 'include',
    },
  );

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Failed to load role documents.'), response.status);
  }

  return response.json() as Promise<RoleManagementDocumentsResponse>;
}

export async function grantDocumentToRole(
  roleId: string,
  documentId: string,
): Promise<RoleManagementDocument> {
  const response = await fetch(`${API_BASE_URL}/roles/${roleId}/documents/${documentId}`, {
    method: 'PUT',
    credentials: 'include',
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Failed to grant document access.'), response.status);
  }

  return response.json() as Promise<RoleManagementDocument>;
}

export async function revokeDocumentFromRole(
  roleId: string,
  documentId: string,
): Promise<RoleManagementDocument> {
  const response = await fetch(`${API_BASE_URL}/roles/${roleId}/documents/${documentId}`, {
    method: 'DELETE',
    credentials: 'include',
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Failed to revoke document access.'), response.status);
  }

  return response.json() as Promise<RoleManagementDocument>;
}

export async function createRole(payload: RoleCreatePayload): Promise<RoleManagementRole> {
  const response = await fetch(`${API_BASE_URL}/roles`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorPayload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(errorPayload, 'Failed to create role.'), response.status);
  }

  return response.json() as Promise<RoleManagementRole>;
}

export async function updateRole(roleId: string, payload: RoleUpdatePayload): Promise<RoleManagementRole> {
  const response = await fetch(`${API_BASE_URL}/roles/${roleId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorPayload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(errorPayload, 'Failed to update role.'), response.status);
  }

  return response.json() as Promise<RoleManagementRole>;
}

export async function deleteRole(roleId: string): Promise<RoleDeleteResponse> {
  const response = await fetch(`${API_BASE_URL}/roles/${roleId}`, {
    method: 'DELETE',
    credentials: 'include',
  });

  if (!response.ok) {
    const errorPayload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(errorPayload, 'Failed to delete role.'), response.status);
  }

  return response.json() as Promise<RoleDeleteResponse>;
}

export async function getProcessingQueue(includeFailed = false): Promise<ProcessingQueueResponse> {
  const query = new URLSearchParams();
  if (includeFailed) {
    query.set('include_failed', 'true');
  }

  const response = await fetch(
    `${API_BASE_URL}/documents/queue${query.toString() ? `?${query.toString()}` : ''}`,
    {
      method: 'GET',
      credentials: 'include',
    },
  );

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Failed to load processing queue.'), response.status);
  }

  return response.json() as Promise<ProcessingQueueResponse>;
}

export async function listDocuments(options?: {
  status?: DocumentStatus;
  includeDeleted?: boolean;
}): Promise<DocumentsListResponse> {
  const query = new URLSearchParams();
  if (options?.status) {
    query.set('status', options.status);
  }
  if (options?.includeDeleted) {
    query.set('include_deleted', 'true');
  }

  const response = await fetch(`${API_BASE_URL}/documents${query.toString() ? `?${query.toString()}` : ''}`, {
    method: 'GET',
    credentials: 'include',
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Failed to load documents.'), response.status);
  }

  return response.json() as Promise<DocumentsListResponse>;
}

export async function getDocumentDetail(documentId: string): Promise<DocumentRecord> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    method: 'GET',
    credentials: 'include',
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Failed to load document details.'), response.status);
  }

  return response.json() as Promise<DocumentRecord>;
}

export async function getDocumentStats(): Promise<DocumentStatsResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/stats`, {
    method: 'GET',
    credentials: 'include',
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Failed to load document stats.'), response.status);
  }

  return response.json() as Promise<DocumentStatsResponse>;
}

export async function updateDocumentPermissions(documentId: string, roleIds: string[]): Promise<DocumentRecord> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}/permissions`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({
      role_ids: roleIds,
    }),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Failed to update document permissions.'), response.status);
  }

  return response.json() as Promise<DocumentRecord>;
}

export async function retryDocumentIngestion(documentId: string): Promise<ConfirmDocumentUploadResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}/retry`, {
    method: 'POST',
    credentials: 'include',
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Failed to retry document ingestion.'), response.status);
  }

  return response.json() as Promise<ConfirmDocumentUploadResponse>;
}

export async function deleteDocument(documentId: string): Promise<DeleteDocumentResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    method: 'DELETE',
    credentials: 'include',
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Failed to delete document.'), response.status);
  }

  return response.json() as Promise<DeleteDocumentResponse>;
}

export async function precheckDocument(fileHash: string): Promise<PrecheckDocumentResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/precheck`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ file_hash: fileHash }),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Precheck failed.'), response.status);
  }

  return response.json() as Promise<PrecheckDocumentResponse>;
}

export async function uploadDocumentFile(file: File): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: 'POST',
    credentials: 'include',
    body: formData,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new AuthApiError(getErrorMessage(payload, 'Upload failed. Please try again.'), response.status);
  }

  return response.json() as Promise<DocumentUploadResponse>;
}

export async function confirmDocumentUpload(payload: {
  uploadToken: string;
  roleIds: string[];
  effectiveDate?: string;
  clientFileHash?: string;
}): Promise<ConfirmDocumentUploadResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/confirm`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({
      upload_token: payload.uploadToken,
      role_ids: payload.roleIds,
      effective_date: payload.effectiveDate || null,
      client_file_hash: payload.clientFileHash || null,
    }),
  });

  if (!response.ok) {
    const errorPayload = await response.json().catch(() => null);
    throw new AuthApiError(
      getErrorMessage(errorPayload, 'Confirm upload failed. Please try again.'),
      response.status,
    );
  }

  return response.json() as Promise<ConfirmDocumentUploadResponse>;
}

export async function uploadDocuments(payload: UploadDocumentsPayload): Promise<UploadDocumentsResponse> {
  const items: UploadDocumentItemResult[] = [];
  let uploaded = 0;
  let duplicates = 0;
  let failed = 0;

  for (const file of payload.files) {
    try {
      const fileHash = await computeSha256(file);
      const precheck = await precheckDocument(fileHash);

      if (precheck.duplicate) {
        duplicates += 1;
        items.push({
          filename: file.name,
          status: 'duplicate',
          detail: `Duplicate: ${precheck.existing_document?.filename || file.name}`,
          documentId: precheck.existing_document?.id,
        });
        continue;
      }

      const uploadedFile = await uploadDocumentFile(file);
      const confirmed = await confirmDocumentUpload({
        uploadToken: uploadedFile.upload_token,
        roleIds: payload.roleIds,
        effectiveDate: payload.effectiveDate,
        clientFileHash: fileHash,
      });

      uploaded += 1;
      items.push({
        filename: file.name,
        status: 'uploaded',
        detail: confirmed.message,
        documentId: confirmed.document.id,
        taskId: confirmed.task_id || undefined,
      });
    } catch (error) {
      failed += 1;
      items.push({
        filename: file.name,
        status: 'failed',
        detail: error instanceof Error ? error.message : 'Upload failed.',
      });
    }
  }

  const message = `Uploaded ${uploaded}, duplicates ${duplicates}, failed ${failed}.`;
  return {
    message,
    uploaded,
    duplicates,
    failed,
    items,
  };
}



