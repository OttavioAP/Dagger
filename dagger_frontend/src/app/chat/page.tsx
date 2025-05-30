'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/auth_context';
import ReactMarkdown from 'react-markdown';

interface Message {
  role: 'user' | 'bot';
  content: string;
}

export default function ChatPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const user_id = user?.id;

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || !user_id) return;
    const userMessage: Message = { role: 'user', content: input };
    setMessages((msgs) => [...msgs, userMessage]);
    setInput('');
    setLoading(true);
    try {
      const params = new URLSearchParams({ query: input, user_id });
      const res = await fetch(`/api/agentic?${params.toString()}`);
      const responseData = await res.json();
      let botReply = '';
      if (responseData.data) {
        if (typeof responseData.data === 'string') botReply = responseData.data;
        else if (responseData.data.data) botReply = responseData.data.data;
        else if (responseData.data.response) botReply = responseData.data.response;
        else if (typeof responseData.data === 'object' && responseData.data.response) botReply = responseData.data.response;
        else botReply = JSON.stringify(responseData.data);
      } else if (responseData.response) {
        botReply = responseData.response;
      } else if (typeof responseData === 'string') {
        botReply = responseData;
      } else {
        botReply = JSON.stringify(responseData);
      }
      setMessages((msgs) => [...msgs, { role: 'bot', content: botReply }]);
    } catch (err) {
      setMessages((msgs) => [...msgs, { role: 'bot', content: 'Sorry, there was an error.' }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div className="flex flex-col h-full max-h-screen w-full items-center px-4">
      <div className="w-full max-w-xl flex flex-col h-full relative">
        <h1 className="text-white text-xl font-semibold mb-4 text-center pt-6">What can I help with?</h1>

        <div className="flex-1 overflow-y-auto bg-[#232324] rounded-lg p-4 shadow-lg border border-[#35373B] mb-2">
          {messages.map((msg, idx) => (
            <div key={idx} className={`mb-3 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`px-3 py-2 rounded-lg text-sm max-w-[80%] break-words ${msg.role === 'user' ? 'bg-[#232324] text-white border border-[#35373B]' : 'bg-[#232324] text-gray-200 border border-[#35373B]'}`}>
                <ReactMarkdown>{typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}</ReactMarkdown>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="sticky bottom-0 bg-[#181A1B] pt-2 pb-4">
          <form
            className="flex items-center bg-[#232324] rounded-2xl shadow-lg px-4 py-2 border border-[#35373B]"
            onSubmit={e => { e.preventDefault(); sendMessage(); }}
          >
            <input
              ref={inputRef}
              className="flex-1 bg-transparent text-white placeholder-gray-400 outline-none border-none py-2 px-0 text-base"
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={user ? "Ask anything" : "Please log in to chat"}
              disabled={loading || !user}
              autoFocus
            />
            <button
              type="submit"
              className="ml-2 bg-[#232324] hover:bg-[#35373B] text-white rounded-full p-2 transition disabled:opacity-50"
              disabled={loading || !input.trim() || !user}
              aria-label="Send"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 19.5l15-7.5-15-7.5v6l10 1.5-10 1.5v6z" />
              </svg>
            </button>
          </form>
          {!user && (
            <div className="text-center text-red-400 mt-2">Please log in to use the chat.</div>
          )}
        </div>
      </div>
    </div>
  );
}
