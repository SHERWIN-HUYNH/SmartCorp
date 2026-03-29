export interface UserNode {
  id: string;
  name: string;
  initials: string;
  email: string;
  status: 'Active' | 'On Leave' | 'Restricted';
  avatarColor: string; // e.g., 'bg-blue-100 text-blue-700'
}

export interface DocumentNode {
  id: string;
  name: string;
  type: 'file' | 'security' | 'handbook' | 'schema';
  uploadedBy: {
    name: string;
    avatarUrl?: string;
  };
  dateAdded: string;
}

export interface RoleNode {
  id: string;
  title: string;
  description: string;
  userCount: number;
  docCount: number;
  category: string;
  isCore?: boolean;
  users: UserNode[]; // Edge linking Role to Users
  documents: DocumentNode[]; // Edge linking Role to Documents
}
