import { useEffect, useMemo, useRef, useState } from 'react'

type SenderType = 'staff' | 'visitor'

interface ChatMessage {
  id: number
  sender: string
  sender_type: SenderType
  visitor_name?: string | null
  message: string
  is_command?: boolean
}

const resolveWebSocketUrl = (name: string) => {
  const explicit = import.meta.env.VITE_PUBLIC_CHAT_WS as string | undefined
  if (explicit) return `${explicit}?name=${encodeURIComponent(name)}`

  const httpBase = import.meta.env.VITE_API_BASE_URL as string | undefined
  if (httpBase) {
    try {
      const parsed = new URL(httpBase)
      parsed.protocol = parsed.protocol === 'https:' ? 'wss:' : 'ws:'
      return `${parsed.origin}/api/v1/chat/ws/public?name=${encodeURIComponent(name)}`
    } catch {
      // Fallback handled below
    }
  }

  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${protocol}://${window.location.host}/api/v1/chat/ws/public?name=${encodeURIComponent(name)}`
}

export function PublicChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [name, setName] = useState('زائر')
  const [isIdentified, setIsIdentified] = useState(false)
  const [messageInput, setMessageInput] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const socketRef = useRef<WebSocket | null>(null)

  const toggle = () => setIsOpen((prev) => !prev)

  const connect = useMemo(() => isOpen && isIdentified, [isOpen, isIdentified])

  useEffect(() => {
    if (!connect) {
      socketRef.current?.close()
      socketRef.current = null
      return
    }

    const ws = new WebSocket(resolveWebSocketUrl(name))
    socketRef.current = ws
    setConnectionError(null)

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as ChatMessage
        setMessages((prev) => [...prev, payload])
      } catch (error) {
        console.error('Failed to parse message', error)
      }
    }

    ws.onerror = () => {
      setConnectionError('تعذّر الاتصال بالدردشة، تأكد من تشغيل الخادم الخلفي')
    }

    ws.onclose = () => {
      socketRef.current = null
    }

    return () => {
      ws.close()
      socketRef.current = null
    }
  }, [connect, name])

  const handleSend = () => {
    const content = messageInput.trim()
    if (!content || !socketRef.current) return
    socketRef.current.send(JSON.stringify({ message: content }))
    setMessageInput('')
  }

  return (
    <div className="fixed bottom-4 left-4 z-50 flex flex-col items-end gap-2">
      <button className="btn btn-primary shadow-lg" onClick={toggle}>
        {isOpen ? 'إخفاء المحادثة' : '💬 تحدث معنا'}
      </button>
      {isOpen && (
        <div className="w-80 rounded-2xl border border-base-300 bg-base-100 shadow-2xl">
          <div className="flex items-center justify-between border-b border-base-200 p-4">
            <div>
              <p className="font-semibold">محادثة فورية</p>
              <p className="text-xs text-base-content/60">تواصل مباشر مع فريق TwoCards</p>
            </div>
            <span className={`badge ${socketRef.current ? 'badge-success' : 'badge-error'}`}>
              {socketRef.current ? 'متصل' : 'غير متصل'}
            </span>
          </div>
          <div className="flex flex-col gap-3 p-4">
            {!isIdentified ? (
              <div className="space-y-3">
                <p className="text-sm text-base-content/70">عرفنا باسمك لبدء المحادثة</p>
                <input
                  type="text"
                  className="input input-bordered w-full"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                />
                <button className="btn btn-primary w-full" onClick={() => setIsIdentified(true)}>
                  بدء المحادثة
                </button>
              </div>
            ) : (
              <>
                <div className="h-56 space-y-2 overflow-y-auto rounded-lg border border-base-300 p-3 text-sm">
                  {messages.length === 0 ? (
                    <p className="text-center text-base-content/60">ابدأ الحديث وسنرد عليك فوراً</p>
                  ) : (
                    messages.map((message) => (
                      <div
                        key={`${message.id}-${message.sender}-${message.message}`}
                        className={`rounded-lg p-2 ${
                          message.sender_type === 'staff'
                            ? 'bg-primary/10 text-primary-content'
                            : 'bg-base-200'
                        }`}
                      >
                        <p className="text-xs font-semibold">
                          {message.sender_type === 'staff' ? 'فريق الدعم' : message.sender}
                        </p>
                        <p>{message.message}</p>
                      </div>
                    ))
                  )}
                </div>
                {connectionError && <p className="text-xs text-error">{connectionError}</p>}
                <div className="flex gap-2">
                  <input
                    type="text"
                    className="input input-bordered flex-1"
                    value={messageInput}
                    onChange={(event) => setMessageInput(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter') {
                        event.preventDefault()
                        handleSend()
                      }
                    }}
                    placeholder="اكتب رسالتك هنا"
                  />
                  <button className="btn btn-primary" onClick={handleSend} disabled={!socketRef.current}>
                    إرسال
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
