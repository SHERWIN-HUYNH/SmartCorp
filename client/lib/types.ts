export interface User {
  name: string;
  role: string;
  avatar: string;
}

export interface Query {
  id: string;
  title: string;
  isActive?: boolean;
}

export interface Message {
  id: string;
  role: 'user' | 'ai';
  content: React.ReactNode;
  timestamp?: string;
}

// Interfaces for Nodes and Edges as requested
export interface FlowNode {
  id: string;
  title: string;
  description: string;
  status: 'completed' | 'active' | 'pending';
}

export interface FlowEdge {
  id: string;
  source: string;
  target: string;
}

export interface Source {
  id: string;
  title: string;
  type: 'pdf' | 'table' | 'link';
  url: string;
}
