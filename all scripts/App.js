// src/App.js

import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';

// The URL of your Python Flask backend API
//const API_URL = 'http://localhost:5055/api';
//const API_URL = 'https://h4dassistant.com/api';
const API_URL = '/api';

// A component for the live thinking bubble
const ThinkingBubble = ({ steps }) => (
  <div className="thinking-bubble">
    <strong>🤔 Thinking...</strong>
    <ul>
      {steps.map((step, index) => (
        <li key={index}>{step}</li>
      ))}
    </ul>
  </div>
);

// A component to render the assistant's message, handling markdown
const AssistantMessage = ({ content }) => {
  if (content && typeof content === 'object' && content.format === 'markdown') {
    return <ReactMarkdown>{content.text}</ReactMarkdown>;
  }
  const text = (typeof content === 'object' && content.text) ? content.text : String(content);
  return <p>{text}</p>;
};

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [thinkingSteps, setThinkingSteps] = useState([]);
  const [threadId, setThreadId] = useState(null);
  const chatWindowRef = useRef(null);

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [messages, thinkingSteps]);

  const handleSend = async () => {
    if (input.trim() === '') return;
    const userInput = input;
    setMessages(prev => [...prev, { role: 'user', content: userInput }]);
    setInput('');
    setIsThinking(true);
    setThinkingSteps([]);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userInput, thread_id: threadId }),
      });

      if (!response.body) return;
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';

        for (const part of parts) {
            if (part.startsWith('data:')) {
                const jsonData = part.substring(5).trim();
                if (jsonData) {
                    try {
                        const data = JSON.parse(jsonData);
                        if (data.type === 'thinking') {
                            setThinkingSteps(prev => [...prev, data.content]);
                        } else if (data.type === 'thread_created') {
                            setThreadId(data.thread_id);
                        } else if (data.type === 'final') {
                            setMessages(prev => [...prev, { role: 'assistant', content: data.content }]);
                        } else if (data.type === 'error') {
                            setMessages(prev => [...prev, { role: 'assistant', content: `[ERROR]: ${data.content}` }]);
                        }
                    } catch (e) {
                        console.error("Error parsing JSON from stream:", jsonData, e);
                    }
                }
            }
        }
      }
    } catch (error) {
      console.error("Streaming failed:", error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'A connection error occurred. Is the backend server running?'}]);
    } finally {
      setIsThinking(false);
    }
  };

  const startNewChat = () => {
      setMessages([]);
      setThinkingSteps([]);
      setThreadId(null);
      setInput('');
      setIsThinking(false);
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !isThinking) handleSend();
  };

  return (
    <div className="App">
      <header>
        <h1>Hacking for Defense Assistant</h1>
        <button className="new-chat-btn" onClick={startNewChat}>New Chat</button>
      </header>
      <div className="chat-window" ref={chatWindowRef}>
        <div className="chat-content">
            {messages.map((msg, index) => (
            <div key={index} className={`message-container ${msg.role}-container`}>
                <div className={`message ${msg.role}`}>
                {msg.role === 'assistant' 
                    ? <AssistantMessage content={msg.content} /> 
                    : <p>{msg.content}</p>
                }
                </div>
            </div>
            ))}
            {isThinking && <ThinkingBubble steps={thinkingSteps} />}
        </div>
      </div>
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about the book..."
          disabled={isThinking}
        />
        <button onClick={handleSend} disabled={isThinking}>
          {isThinking ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

export default App;
