import React, { useEffect, useRef, useState } from 'react';
import { v4 as uuidv4 } from 'uuid';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface Status {
  type: 'status' | 'message' | 'error';
  content: string;
  role?: 'user' | 'assistant';
}

const Conversation: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [status, setStatus] = useState<string>('');
  const [input, setInput] = useState('');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const conversationId = useRef(uuidv4());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const websocket = new WebSocket(`ws://localhost:8000/ws/${conversationId.current}`);

    websocket.onopen = () => {
      console.log('Connected to WebSocket');
    };

    websocket.onmessage = (event) => {
      const data: Status = JSON.parse(event.data);
      
      if (data.type === 'message' && data.role && data.content) {
        const newMessage: Message = {
          role: data.role,
          content: data.content
        };
        setMessages(prev => [...prev, newMessage]);
      } else if (data.type === 'status') {
        setStatus(data.content);
      } else if (data.type === 'error') {
        setStatus(`Error: ${data.content}`);
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setStatus('Connection error');
    };

    websocket.onclose = () => {
      console.log('WebSocket connection closed');
      setStatus('Connection closed');
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !ws) return;

    const message = { content: input };
    ws.send(JSON.stringify(message));
    setInput('');
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white p-4">
      <div className="flex-1 overflow-y-auto mb-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`mb-4 ${
              message.role === 'user' ? 'text-right' : 'text-left'
            }`}
          >
            <div
              className={`inline-block p-3 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-white'
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
        {status && (
          <div className="text-center text-gray-400 italic">
            {status}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 p-2 rounded bg-gray-800 text-white border border-gray-700 focus:outline-none focus:border-blue-500"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none"
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default Conversation; 