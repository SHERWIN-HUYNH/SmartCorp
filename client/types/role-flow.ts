export interface RoleFlowNode {
  id: string;
  title: string;
  detail: string;
  stage: 'draft' | 'validation' | 'analysis' | 'publish';
}

export interface RoleFlowEdge {
  id: string;
  source: string;
  target: string;
  rule: string;
}

export interface CreateRoleFormValues {
  roleCode: string;
  description: string;
}
