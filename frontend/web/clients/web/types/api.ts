// User-related types
export interface User {
    id: string;
    email: string;
    full_name: string;
    roles: string[];
    is_active: boolean;
    created_at: string;
    last_login?: string | null;
    google_id?: string | null;
  }
  
  // Auth-related types
  export interface LoginCredentials {
    email: string;
    password: string;
  }
  
  export interface RegisterData {
    email: string;
    password: string;
    full_name: string;
  }
  
  export interface TokenResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
  }
  
  export interface UserResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    user: User;
  }
  
  // Document-related types
  export interface Document {
    id: string;
    title: string;
    content: string;
    user_id: string;
    created_at: string;
    updated_at: string;
  }
  
  export interface DocumentCreateInput {
    title: string;
    content: string;
  }
  
  export interface DocumentUpdateInput {
    title?: string;
    content?: string;
  }
  
  export interface DocumentAudit {
    id: string;
    document_id: string;
    action: string;
    user_id: string;
    created_at: string;
    details?: string | null;
  }
  
  // API Error types
  export interface ApiError {
    detail: string;
    status_code?: number;
  }