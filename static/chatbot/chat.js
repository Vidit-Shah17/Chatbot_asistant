document.addEventListener('DOMContentLoaded', function() {
  const chatBox = document.getElementById('chat');
  const form = document.getElementById('chat-form');
  const input = document.getElementById('message');

  function appendMessage(text, cls='bot') {
    const div = document.createElement('div');
    div.className = cls + ' message';
    div.innerText = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function setTyping(on=true) {
    let el = document.getElementById('typing');
    if (on) {
      if (!el) {
        el = document.createElement('div');
        el.id = 'typing';
        el.className = 'bot message typing';
        el.innerText = 'HelpMate is typing...';
        chatBox.appendChild(el);
        chatBox.scrollTop = chatBox.scrollHeight;
      }
    } else {
      if (el) el.remove();
    }
  }

  async function sendMessage(event) {
    event.preventDefault();
    const text = input.value.trim();
    if (!text) return false;
    appendMessage(text, 'user');
    input.value = '';
    setTyping(true);

    try {
      const res = await fetch('/api/chat/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: text})
      });

      const contentType = res.headers.get('content-type') || '';
      if (!res.ok) {
        if (contentType.includes('application/json')) {
          const j = await res.json();
          appendMessage('Error: ' + (j.error || JSON.stringify(j)), 'bot');
        } else {
          const txt = await res.text();
          appendMessage('Server error: ' + txt.slice(0, 300), 'bot');
        }
        setTyping(false);
        return false;
      }

      if (contentType.includes('application/json')) {
        const data = await res.json();
        const resp = data.response;
        if (typeof resp === 'object') {
         
          let s = '';
          for (const k in resp) {
            s += `${k}: ${resp[k]}\n`;
          }
          appendMessage(s.trim(), 'bot');
        } else {
          appendMessage(resp || 'No response', 'bot');
        }
      } else {
        const txt = await res.text();
        appendMessage(txt, 'bot');
      }
    } catch (err) {
      console.error('Fetch error:', err);
      appendMessage('Network or parsing error: ' + (err.message || err), 'bot');
    } finally {
      setTyping(false);
    }
    return false;
  }

  form.addEventListener('submit', sendMessage);
});
