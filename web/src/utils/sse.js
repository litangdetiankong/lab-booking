export async function streamChat(messages, onEvent) {
  const resp = await fetch('/api/ai/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json',
               Authorization: `Bearer ${localStorage.getItem('token')}` },
    body: JSON.stringify({ messages }),
  })
  if (!resp.ok || !resp.body) throw new Error(`SSE 连接失败: ${resp.status}`)

  const reader = resp.body.getReader()
  const decoder = new TextDecoder()
  let buf = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buf += decoder.decode(value, { stream: true })

    const frames = buf.split('\n\n')
    buf = frames.pop()
    for (const frame of frames) {
      const line = frame.trim()
      if (!line.startsWith('data:')) continue
      onEvent(JSON.parse(line.slice(5).trim()))
    }
  }
}