export type Skill = {
  id: string
  name: string
  description: string
  tags: string[]
}

export type MCPServer = {
  id: string
  name: string
  transport: string
  status: 'online' | 'offline' | 'degraded'
  enabled: boolean
  description?: string
}

export type MCPTool = {
  server_id: string
  tool_name: string
}

export type SessionMessage = {
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export type SessionData = {
  session_id: string
  messages: SessionMessage[]
  created_at: string
  updated_at: string
  meta: Record<string, unknown>
  active_skills: string[]
}

export type ChatResponse = {
  session_id: string
  reply: string
  active_skills: string[]
}

