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

import { LucideIcon } from 'lucide-react';

export interface KpiMetric {
  id: string;
  title: string;
  value: string | number;
  changeLabel?: string;
  changeType?: 'positive' | 'warning' | 'neutral' | 'status';
  icon: LucideIcon;
  iconWrapperClass: string;
  iconClass: string;
  statusText?: string;
}

export interface DocumentStat {
  id: string;
  title: string;
  tags: string[];
  icon: LucideIcon;
  iconWrapperClass: string;
  iconClass: string;
  views: number;
  trendPercentage: number;
  trendType: 'up' | 'down' | 'steady';
  sparklinePath: string;
}

export interface ActivityUpdate {
  id: string;
  title: string;
  author: string;
  time: string;
  icon: LucideIcon;
  iconWrapperClass: string;
  iconClass: string;
}

export interface QueueItemData {
  id: string;
  name: string;
  size: string;
  progress: number;
  status: 'uploading' | 'parsing' | 'chunking' | 'embedding' | 'indexed';
  type: 'pdf' | 'docx';
  activeSteps: string[];
}