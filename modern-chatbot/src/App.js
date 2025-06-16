// src/App.js

import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';

const API_URL = '/api';

// --- Instructions Page Component (Unchanged) ---
const InstructionsPage = ({ navigateToChat }) => (
  <div className="instructions-container">
    <div className="instructions-box">
      <h2>Welcome to the Hacking for Defense Assistant</h2>
      <p>
        Here you can interact with the entire knowledgebase contained in the Hacking for Defense book, including its flow charts, images, and all text.
      </p>
      <h3>Intended Use</h3>
      <ol>
        <li>
          <strong>Learning Tool:</strong> To have an alternate method of interacting with the text to help learn the H4D methodology.
        </li>
        <li>
          <strong>Prompt Engineering:</strong> To build complex, project-specific prompts for Google Workspace Gemini 2.5 Pro interactions with your actual project data.
        </li>
      </ol>
      <div className="warning-box">
        <p><strong>⚠️ Important Security Notice</strong></p>
        <p>
          Do not put actual project data in this chat. This chat uses OpenAI GPT-4.1 API calls for interaction. <strong>Anything you put in this chat is sent to OpenAI.</strong>
        </p>
        <p>
          This is a prompt builder and learning tool only. Copy your developed prompts and all project data into the AFRL-approved Gemini instance to produce H4D-aligned project outputs. Orient your questions here to develop comprehensive prompts.
        </p>
      </div>
      <button onClick={navigateToChat}>Go to Chat</button>
    </div>
  </div>
);


// --- Login Screen Component (Unchanged) ---
const LoginScreen = ({ onLoginSuccess }) => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  const handleLogin = async () => {
    if (password.trim() === '') {
        setError('Password cannot be empty.');
        return;
    }
    setIsLoggingIn(true);
    setError('');
    
    try {
      const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        onLoginSuccess();
      } else {
        setError(data.message || 'Invalid password.');
      }
    } catch (err) {
      console.error("Login failed:", err);
      setError('A connection error occurred. Could not verify password.');
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !isLoggingIn) {
      handleLogin();
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>H4D Assistant Access</h2>
        <p>Please enter the password to continue.</p>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter password..."
          disabled={isLoggingIn}
          autoFocus
        />
        <button onClick={handleLogin} disabled={isLoggingIn}>
          {isLoggingIn ? 'Verifying...' : 'Login'}
        </button>
        {error && <p className="login-error">{error}</p>}
      </div>
    </div>
  );
};


// The rest of the components are unchanged
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

const AssistantMessage = ({ content }) => {
  if (content && typeof content === 'object' && content.format === 'markdown') {
    return <ReactMarkdown>{content.text}</ReactMarkdown>;
  }
  const text = (typeof content === 'object' && content.text) ? content.text : String(content);
  return <p>{text}</p>;
};


// --- Chat Page Component (Unchanged) ---
const ChatPage = ({ navigateToInstructions }) => {
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
        <div className="header-buttons">
          <button className="nav-btn" onClick={navigateToInstructions}>Instructions</button>
          <button className="new-chat-btn" onClick={startNewChat}>New Chat</button>
        </div>
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
};


function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  // --- UPDATED: Page navigation state now has three possible values ---
  const [currentPage, setCurrentPage] = useState('instructions');

  useEffect(() => {
    const sessionAuth = sessionStorage.getItem('h4d-authenticated');
    if (sessionAuth === 'true') {
        setIsAuthenticated(true);
    }
  }, []);

  // --- UPDATED: This function is called on successful login ---
  const handleLoginSuccess = () => {
      sessionStorage.setItem('h4d-authenticated', 'true');
      setIsAuthenticated(true);
      setCurrentPage('chat'); // Go to chat after successful login
  };

  // --- UPDATED: This function handles navigation from the instructions page ---
  const handleNavigateFromInstructions = () => {
      if (isAuthenticated) {
          setCurrentPage('chat');
      } else {
          setCurrentPage('login');
      }
  };

  // --- UPDATED: Main render logic to handle the three different pages ---
  const renderPage = () => {
    switch (currentPage) {
        case 'login':
            return <LoginScreen onLoginSuccess={handleLoginSuccess} />;
        case 'chat':
            return <ChatPage navigateToInstructions={() => setCurrentPage('instructions')} />;
        case 'instructions':
        default:
            return <InstructionsPage navigateToChat={handleNavigateFromInstructions} />;
    }
  };

  return <>{renderPage()}</>;
}

export default App;
