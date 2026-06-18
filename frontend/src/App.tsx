import { useEffect, useMemo, useState } from 'react'
import {
  createSession,
  fetchMcpServers,
  fetchMcpTools,
  fetchSkills,
  getSession,
  resetSession,
  sendChat,
  updateSessionSkills,
} from './api'
import type { MCPServer, MCPTool, SessionData, Skill } from './types'

type LogItem = {
  id: string
  title: string
  detail: string
  time: string
}

function nowLabel() {
  return new Date().toLocaleTimeString()
}

function formatStatus(value: string) {
  switch (value) {
    case 'Ready':
      return '就绪'
    case 'Sending...':
      return '发送中...'
    case 'Waiting for Agent...':
      return '等待智能体...'
    case 'Session reset':
      return '会话已重置'
    case 'Session created':
      return '会话已创建'
    default:
      return value
  }
}

export default function App() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [servers, setServers] = useState<MCPServer[]>([])
  const [tools, setTools] = useState<MCPTool[]>([])
  const [session, setSession] = useState<SessionData | null>(null)
  const [sessionCache, setSessionCache] = useState<Record<string, SessionData>>({})
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('Ready')
  const [logs, setLogs] = useState<LogItem[]>([])

  useEffect(() => {
    void bootstrap()
  }, [])

  async function bootstrap() {
    const [skillData, serverData, toolData, created] = await Promise.all([
      fetchSkills(),
      fetchMcpServers(),
      fetchMcpTools(),
      createSession(),
    ])
    setSkills(skillData)
    setServers(serverData)
    setTools(toolData)
    const sessionData = await getSession(created.session_id)
    setSession(sessionData)
    setSessionCache((prev) => ({ ...prev, [sessionData.session_id]: sessionData }))
    setStatus(`会话 ${sessionData.session_id} 已创建`)
    pushLog('会话创建', sessionData.session_id)
  }

  function pushLog(title: string, detail: string) {
    setLogs((prev) => [
      { id: crypto.randomUUID(), title, detail, time: nowLabel() },
      ...prev,
    ].slice(0, 12))
  }

  async function handleSkillToggle(skillId: string, checked: boolean) {
    if (!session) return
    const current = new Set(session.active_skills)
    if (checked) current.add(skillId)
    else current.delete(skillId)
    const next = Array.from(current)
    const updated = await updateSessionSkills(session.session_id, next)
    const fresh = await getSession(updated.session_id)
    setSession(fresh)
    setSessionCache((prev) => ({ ...prev, [fresh.session_id]: fresh }))
    pushLog('技能已更新', next.length ? next.join(', ') : '无')
  }

  async function handleSend() {
    if (!session || !input.trim()) return
    const message = input.trim()
    setInput('')
    setLoading(true)
    setStatus('Sending...')
    pushLog('发送中', message)
    try {
      const response = await sendChat({
        session_id: session.session_id,
        message,
        active_skills: session.active_skills,
      })
      const fresh = await getSession(response.session_id)
      setSession(fresh)
      setSessionCache((prev) => ({ ...prev, [fresh.session_id]: fresh }))
      setStatus('Waiting for Agent...')
      pushLog('智能体回复', response.reply)
    } finally {
      setLoading(false)
      setStatus('Ready')
    }
  }

  async function handleNewSession() {
    const created = await createSession()
    const fresh = await getSession(created.session_id)
    setSession(fresh)
    setSessionCache((prev) => ({ ...prev, [fresh.session_id]: fresh }))
    setStatus(`会话 ${fresh.session_id} 已创建`)
    pushLog('新建会话', fresh.session_id)
  }

  async function handleResetSession() {
    if (!session) return
    await resetSession(session.session_id)
    const fresh = await getSession(session.session_id)
    setSession(fresh)
    setSessionCache((prev) => ({ ...prev, [fresh.session_id]: fresh }))
    setStatus('Session reset')
    pushLog('重置会话', fresh.session_id)
  }

  const activeSkillSet = useMemo(() => new Set(session?.active_skills ?? []), [session])

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>DeepAgents Web Console</h1>
          <p>{formatStatus(status)}</p>
        </div>
        <div className="topbar-actions">
          <button onClick={handleNewSession}>新建会话</button>
          <button onClick={handleResetSession} disabled={!session}>
            重置会话
          </button>
        </div>
      </header>

      <main className="grid">
        <section className="panel skills-panel">
          <h2>技能</h2>
          <div className="stack">
            {skills.map((skill) => (
              <label key={skill.id} className="skill-item">
                <div className="skill-item-head">
                  <input
                    type="checkbox"
                    checked={activeSkillSet.has(skill.id)}
                    onChange={(e) => void handleSkillToggle(skill.id, e.target.checked)}
                    disabled={!session}
                  />
                  <div>
                    <strong>{skill.name}</strong>
                    <p>{skill.description}</p>
                  </div>
                </div>
                <div className="tags">
                  {skill.tags.map((tag) => (
                    <span key={tag} className="tag">
                      {tag}
                    </span>
                  ))}
                </div>
              </label>
            ))}
          </div>
        </section>

        <section className="panel chat-panel">
          <h2>对话</h2>
          <div className="session-meta">
            <div>会话：{session?.session_id ?? '加载中...'}</div>
            <div>已启用技能：{session?.active_skills.join(', ') || '无'}</div>
          </div>
          <div className="messages">
            {session?.messages?.length ? (
              session.messages.map((message, index) => (
                <article key={`${message.created_at}-${index}`} className={`message ${message.role}`}>
                  <div className="message-role">{message.role === 'user' ? '用户' : '智能体'}</div>
                  <div className="message-content">{message.content}</div>
                </article>
              ))
            ) : (
              <div className="empty-state">暂无消息。</div>
            )}
          </div>
          <div className="composer">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="请输入消息..."
              rows={4}
            />
            <div className="composer-actions">
              <button onClick={() => void handleSend()} disabled={loading || !session || !input.trim()}>
                {loading ? '发送中...' : '发送'}
              </button>
            </div>
          </div>
        </section>

        <section className="panel mcp-panel">
          <h2>MCP</h2>
          <div className="stack">
            {servers.map((server) => (
              <article key={server.id} className="mcp-card">
                <div className="mcp-row">
                  <strong>{server.name}</strong>
                  <span className={`status ${server.status}`}>
                    {server.status === 'online' ? '在线' : server.status === 'offline' ? '离线' : '降级'}
                  </span>
                </div>
                <div className="muted">传输方式：{server.transport}</div>
                <div className="muted">{server.description}</div>
              </article>
            ))}
          </div>
          <h3>工具</h3>
          <ul className="tool-list">
            {tools.map((tool) => (
              <li key={`${tool.server_id}:${tool.tool_name}`}>
                {tool.server_id} / {tool.tool_name}
              </li>
            ))}
          </ul>
        </section>
      </main>

      <footer className="footer">
        <section className="panel logs-panel">
          <h2>日志</h2>
          <div className="log-list">
            {logs.map((log) => (
              <div key={log.id} className="log-item">
                <div className="log-head">
                  <strong>{log.title}</strong>
                  <span>{log.time}</span>
                </div>
                <div className="muted">{log.detail}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="panel session-panel">
          <h2>会话信息</h2>
          {session ? (
            <pre>{JSON.stringify(sessionCache[session.session_id] ?? session, null, 2)}</pre>
          ) : (
            <div className="empty-state">会话加载中...</div>
          )}
        </section>
      </footer>
    </div>
  )
}
