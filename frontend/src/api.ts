import axios from 'axios'
import type { ChatResponse, MCPServer, MCPTool, SessionData, Skill } from './types'

const client = axios.create({
  baseURL: '/api',
})

export async function fetchSkills(): Promise<Skill[]> {
  const { data } = await client.get<Skill[]>('/skills')
  return data
}

export async function fetchMcpServers(): Promise<MCPServer[]> {
  const { data } = await client.get<MCPServer[]>('/mcp/servers')
  return data
}

export async function fetchMcpTools(): Promise<MCPTool[]> {
  const { data } = await client.get<MCPTool[]>('/mcp/tools')
  return data
}

export async function createSession(): Promise<{ session_id: string }> {
  const { data } = await client.post<{ session_id: string }>('/sessions')
  return data
}

export async function updateSessionSkills(sessionId: string, activeSkills: string[]): Promise<{ session_id: string; active_skills: string[] }> {
  const { data } = await client.post(`/sessions/${sessionId}/skills`, {
    active_skills: activeSkills,
  })
  return data
}

export async function resetSession(sessionId: string): Promise<{ status: string }> {
  const { data } = await client.post(`/sessions/${sessionId}/reset`)
  return data
}

export async function getSession(sessionId: string): Promise<SessionData> {
  const { data } = await client.get<SessionData>(`/sessions/${sessionId}`)
  return data
}

export async function sendChat(payload: {
  session_id: string
  message: string
  active_skills?: string[]
}): Promise<ChatResponse> {
  const { data } = await client.post<ChatResponse>('/chat', payload)
  return data
}

