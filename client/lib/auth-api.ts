const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api';

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: string;
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
  processCode: string;
  version: string;
  effectiveDate: string;
  roles: string[];
  useLlamaParse: boolean;
}

export interface UploadDocumentsResponse {
  message?: string;
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
  return fallback;
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

export async function uploadDocuments(payload: UploadDocumentsPayload): Promise<UploadDocumentsResponse> {
  const formData = new FormData();

  payload.files.forEach((file) => {
    formData.append('files', file);
  });
  formData.append('process_code', payload.processCode);
  formData.append('version', payload.version);
  formData.append('effective_date', payload.effectiveDate);
  payload.roles.forEach((role) => {
    formData.append('roles', role);
  });
  formData.append('use_llamaparse', String(payload.useLlamaParse));
  for (const [key, value] of formData.entries()) {
    console.log(key, value);
  }
  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: 'POST',
    credentials: 'include',
    body: formData,
  });

  if (!response.ok) {
    const errorPayload = await response.json().catch(() => null);
    throw new AuthApiError(
      getErrorMessage(errorPayload, 'Upload failed. Please try again.'),
      response.status,
    );
  }

  return response.json().catch(() => ({ message: 'Upload submitted successfully.' })) as Promise<UploadDocumentsResponse>;
}



