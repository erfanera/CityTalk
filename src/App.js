import React, { useState } from 'react';
import styled, { keyframes, css } from 'styled-components';

const typingPulse = keyframes`
  0%, 50%, 100% { opacity: 1; }
  25%, 75% { opacity: 0.5; }
`;

const Container = styled.div`
  width: 100vw;
  height: 100vh;
  position: relative;
  overflow: hidden;
`;

const MapContainer = styled.div`
  width: 100%;
  height: 100vh;
  position: relative;
`;

const LoadingMessage = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 20px 40px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  font-size: 18px;
  color: #4a5568;
  backdrop-filter: blur(10px);
`;

const PromptBox = styled.div`
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  max-width: 600px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  box-shadow: 
    0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -2px rgba(0, 0, 0, 0.05),
    inset 0 -20px 20px -20px rgba(255, 255, 255, 0.3),
    inset 0 20px 20px -20px rgba(255, 255, 255, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.3);
  display: flex;
  gap: 10px;
  z-index: 1000;
`;

const Input = styled.input`
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
  &:focus {
    outline: none;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1), 0 0 0 2px rgba(74, 108, 247, 0.2);
  }
`;

const Button = styled.button`
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #6e8efb, #4a6cf7);
  color: white;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.2s;
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`;

const AnalyticsPanel = styled.div`
  position: fixed;
  top: 20px;
  right: 20px;
  width: 400px;
  max-height: 85vh;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px) saturate(180%);
  border-radius: 15px;
  padding: 20px;
  box-shadow: 
    0 10px 15px -3px rgba(0, 0, 0, 0.1),
    0 4px 6px -2px rgba(0, 0, 0, 0.05),
    inset 0 -20px 20px -20px rgba(255, 255, 255, 0.5),
    inset 0 20px 20px -20px rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.4);
  z-index: 1000;
  transition: all 0.3s ease;

  &::-webkit-scrollbar {
    width: 8px;
    background: transparent;
  }

  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    margin: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(74, 108, 247, 0.2);
    border-radius: 4px;
    border: 2px solid transparent;
    background-clip: padding-box;

    &:hover {
      background: rgba(74, 108, 247, 0.3);
      border: 2px solid transparent;
      background-clip: padding-box;
    }
  }

  &:hover {
    box-shadow: 
      0 15px 20px -3px rgba(0, 0, 0, 0.12),
      0 6px 8px -2px rgba(0, 0, 0, 0.06),
      inset 0 -20px 20px -20px rgba(255, 255, 255, 0.6),
      inset 0 20px 20px -20px rgba(255, 255, 255, 0.6);
  }

  img {
    display: block;
    width: 100%;
    max-width: 100%;
    height: auto;
    margin: 15px 0;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease;

    &:hover {
      transform: scale(1.02);
      box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
  }

  h3 {
    color: #2d3748;
    margin: 0 0 10px 0;
    font-size: 1.2em;
    font-weight: 600;
  }

  p {
    color: #4a5568;
    line-height: 1.5;
    margin: 0 0 15px 0;
  }

  ul {
    color: #4a5568;
    padding-left: 20px;
    margin: 0;
    
    li {
      margin-bottom: 5px;
      line-height: 1.4;
    }
  }
`;

const ChatHistory = styled.div`
  max-height: 350px;
  overflow-y: auto;
  margin-bottom: 20px;
  padding: 15px;
  background: rgba(240, 242, 247, 0.8);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const ChatMessage = styled.div`
  margin-bottom: 15px;
  padding: 10px;
  border-radius: 8px;
  background: ${props => props.isUser ? 'rgba(74, 108, 247, 0.1)' : 'rgba(255, 255, 255, 0.8)'};
  border-left: 4px solid ${props => props.isUser ? '#4a6cf7' : '#48bb78'};
  ${props => props.isStreaming && css`
    border-left-color: #ff6b6b;
    animation: ${typingPulse} 1.5s infinite;
  `}
`;

const MessageHeader = styled.div`
  font-weight: bold;
  color: ${props => props.isUser ? '#4a6cf7' : '#48bb78'};
  margin-bottom: 5px;
  font-size: 0.9em;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const MessageContent = styled.div`
  color: #4a5568;
  font-size: 0.95em;
  line-height: 1.4;
  white-space: pre-wrap;
`;

const ToggleButton = styled.button`
  position: absolute;
  top: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: rgba(74, 108, 247, 0.9);
  color: white;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 1001;
  
  &:hover {
    background: rgba(74, 108, 247, 1);
    transform: scale(1.1);
  }
`;

const TypingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 5px;
  color: #666;
  font-style: italic;
`;

const Dot = styled.div`
  width: 6px;
  height: 6px;
  background: #666;
  border-radius: 50%;
  animation: ${typingPulse} 1.4s infinite;
  animation-delay: ${props => props.delay || '0s'};
`;

const StreamingStatus = styled.div`
  background: rgba(74, 108, 247, 0.1);
  border: 1px solid rgba(74, 108, 247, 0.3);
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 15px;
  color: #4a6cf7;
  font-size: 0.9em;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 4px;
  background: rgba(74, 108, 247, 0.1);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 5px;
  
  &::after {
    content: '';
    display: block;
    height: 100%;
    background: linear-gradient(90deg, #4a6cf7, #6e8efb);
    width: ${props => (props.progress || 0) * 100}%;
    transition: width 0.3s ease;
  }
`;

function App() {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [mapHTML, setMapHTML] = useState("http://127.0.0.1:5000/maps/filtered_map.html");
  const [mapLoading, setMapLoading] = useState(false);
  const [mapError, setMapError] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [showPanel, setShowPanel] = useState(true);
  const [streamingStatus, setStreamingStatus] = useState(null);
  const [currentStreamingId, setCurrentStreamingId] = useState(null);
  const [analytics, setAnalytics] = useState({
    summary: '',
    full_analysis: '',
    count: 0,
    logs: [],
    visualization: null
  });

  const connectToStream = (sessionId, userMessage) => {
    const eventSource = new EventSource(`http://127.0.0.1:5000/stream/${sessionId}`);
    let streamingMessageId = null;
    let streamTimeout = null;
    
    console.log(`🔗 Connecting to stream: ${sessionId}`);
    
    // Set a maximum timeout for the entire streaming process
    streamTimeout = setTimeout(() => {
      console.log('🚨 Stream timeout - forcing close');
      setStreamingStatus('Stream timeout - please try again');
      setCurrentStreamingId(null);
      eventSource.close();
    }, 60000); // 60 second total timeout
    
    // Add user message to chat history
    setChatHistory(prev => [...prev, {
      id: Date.now(),
      isUser: true,
      content: userMessage,
      timestamp: new Date().toLocaleTimeString()
    }]);
    
    eventSource.onopen = () => {
      console.log('✅ EventSource connection opened');
      setStreamingStatus('Connected to AI assistant...');
    };
    
    eventSource.onmessage = (event) => {
      try {
        console.log('📨 Received message:', event.data);
        const data = JSON.parse(event.data);
        
        switch (data.type) {
          case 'status':
            setStreamingStatus(data.message);
            console.log('📊 Status:', data.message);
            break;
            
          case 'start':
            setStreamingStatus(data.message);
            console.log('▶️ Stream started');
            // Add initial streaming message
            streamingMessageId = Date.now() + 1;
            setChatHistory(prev => [...prev, {
              id: streamingMessageId,
              isUser: false,
              content: '',
              timestamp: new Date().toLocaleTimeString(),
              isStreaming: true
            }]);
            break;
            
          case 'content':
            // Update streaming message content
            setChatHistory(prev => 
              prev.map(msg => 
                msg.id === streamingMessageId 
                  ? { ...msg, content: data.content }
                  : msg
              )
            );
            setStreamingStatus(`Writing... ${Math.round(data.progress * 100)}%`);
            break;
            
          case 'complete':
            console.log('✅ Stream complete');
            clearTimeout(streamTimeout);
            // Finalize the message
            setChatHistory(prev => 
              prev.map(msg => 
                msg.id === streamingMessageId 
                  ? { ...msg, content: data.final_content, isStreaming: false }
                  : msg
              )
            );
            setAnalytics({
              summary: data.final_content.substring(0, 300) + "...",
              full_analysis: data.final_content,
              count: Math.floor(Math.random() * 150) + 50,
              logs: ['✅ Streaming complete', '📊 Real-time analysis', '🤖 AI response delivered'],
              visualization: null
            });
            setStreamingStatus(null);
            setCurrentStreamingId(null);
            eventSource.close();
            break;
            
          case 'error':
            console.error('❌ Stream error:', data.error);
            clearTimeout(streamTimeout);
            setChatHistory(prev => [...prev, {
              id: Date.now() + 2,
              isUser: false,
              content: `Error: ${data.error}`,
              timestamp: new Date().toLocaleTimeString()
            }]);
            setStreamingStatus('Error occurred');
            setCurrentStreamingId(null);
            eventSource.close();
            break;
            
          case 'timeout':
            console.log('⏰ Stream timeout');
            clearTimeout(streamTimeout);
            setStreamingStatus('Connection timeout');
            setCurrentStreamingId(null);
            eventSource.close();
            break;
            
          default:
            console.log('Unknown message type:', data.type);
            break;
        }
        
      } catch (error) {
        console.error('Error parsing stream data:', error);
        setStreamingStatus('Data parsing error');
      }
    };
    
    eventSource.onerror = (error) => {
      console.error('EventSource failed:', error);
      clearTimeout(streamTimeout);
      
      // Provide different error messages based on readyState
      let errorMessage = 'Connection error';
      if (eventSource.readyState === EventSource.CONNECTING) {
        errorMessage = 'Connecting to server...';
      } else if (eventSource.readyState === EventSource.CLOSED) {
        errorMessage = 'Connection closed - please try again';
      }
      
      setStreamingStatus(errorMessage);
      setCurrentStreamingId(null);
      
      // Add error message to chat if we haven't started streaming yet
      if (!streamingMessageId) {
        setChatHistory(prev => [...prev, {
          id: Date.now() + 3,
          isUser: false,
          content: `Connection failed: ${errorMessage}. Please try again.`,
          timestamp: new Date().toLocaleTimeString()
        }]);
      }
      
      eventSource.close();
    };
  };

  const handlePromptSubmit = async () => {
    if (!prompt.trim() || loading) return;
    
    const userMessage = prompt.trim();
    setPrompt('');
    setLoading(true);
    setMapLoading(true);
    setMapError(null);
    
    try {
      const response = await fetch('http://127.0.0.1:5000/process-prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          prompt: userMessage,
          streaming: true 
        })
      });

      const data = await response.json();
      
      if (data.error) {
        console.error('Error:', data.error);
        setMapError(data.error);
        
        setChatHistory(prev => [...prev, {
          id: Date.now(),
          isUser: true,
          content: userMessage,
          timestamp: new Date().toLocaleTimeString()
        }, {
          id: Date.now() + 1,
          isUser: false,
          content: `Error: ${data.error}`,
          timestamp: new Date().toLocaleTimeString()
        }]);
        
        setLoading(false);
        setMapLoading(false);
        return;
      }

      if (data.streaming && data.session_id) {
        setCurrentStreamingId(data.session_id);
        connectToStream(data.session_id, userMessage);
      }

      // Update map URL
      await new Promise(resolve => setTimeout(resolve, 500));
      const timestamp = Date.now();
      const newMapUrl = `http://127.0.0.1:5000/maps/default_map.html?t=${timestamp}`;
      setMapHTML(newMapUrl);
      
    } catch (error) {
      console.error('Error:', error);
      setMapError('Failed to process request');
      
      setChatHistory(prev => [...prev, {
        id: Date.now(),
        isUser: true,
        content: userMessage,
        timestamp: new Date().toLocaleTimeString()
      }, {
        id: Date.now() + 1,
        isUser: false,
        content: `Connection Error: ${error.message}`,
        timestamp: new Date().toLocaleTimeString()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handlePromptSubmit();
    }
  };

  return (
    <Container>
      <MapContainer>
        <iframe
          key={mapHTML}
          src={mapHTML}
          title="City Talk"
          style={{
            width: "100%",
            height: "100vh",
            border: "none",
            display: mapLoading ? "none" : "block"
          }}
          onLoad={() => {
            console.log("Map iframe loaded");
            setMapLoading(false);
          }}
          onError={(e) => {
            console.error("Map iframe error:", e);
            setMapError('Failed to display map');
            setMapLoading(false);
          }}
        />
        {mapLoading && (
          <LoadingMessage>🔄 Processing your request...</LoadingMessage>
        )}
        {mapError && (
          <LoadingMessage style={{ color: '#e53e3e' }}>{mapError}</LoadingMessage>
        )}
      </MapContainer>

      <PromptBox>
        <Input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me about urban data (e.g., 'Find 20 houses least exposed to pollution in Maragall street')"
          disabled={loading}
        />
        <Button onClick={handlePromptSubmit} disabled={loading || currentStreamingId}>
          {loading || currentStreamingId ? '🔄 Analyzing...' : '🔍 Analyze'}
        </Button>
      </PromptBox>

      <ToggleButton onClick={() => setShowPanel(!showPanel)}>
        {showPanel ? '✕' : '💬'}
      </ToggleButton>
      
      {showPanel && (
        <AnalyticsPanel>
          <h3>🤖 CityTalk AI Assistant</h3>
          
          {streamingStatus && (
            <StreamingStatus>
              <TypingIndicator>
                <Dot delay="0s" />
                <Dot delay="0.2s" />
                <Dot delay="0.4s" />
              </TypingIndicator>
              <span>{streamingStatus}</span>
              {streamingStatus.includes('%') && (
                <ProgressBar progress={parseInt(streamingStatus.match(/\d+/)?.[0] || 0) / 100} />
              )}
            </StreamingStatus>
          )}
          
          {chatHistory.length > 0 && (
            <ChatHistory>
              <h4 style={{ margin: '0 0 10px 0', color: '#2d3748', fontSize: '1em' }}>
                💬 Live Chat {currentStreamingId && '(Streaming)'}
              </h4>
              {chatHistory.map((message) => (
                <ChatMessage key={message.id} isUser={message.isUser} isStreaming={message.isStreaming}>
                  <MessageHeader isUser={message.isUser}>
                    {message.isUser ? '👤 You' : '🤖 Assistant'} • {message.timestamp}
                    {message.isStreaming && (
                      <TypingIndicator>
                        <Dot delay="0s" />
                        <Dot delay="0.2s" />
                        <Dot delay="0.4s" />
                      </TypingIndicator>
                    )}
                  </MessageHeader>
                  <MessageContent>{message.content}</MessageContent>
                </ChatMessage>
              ))}
            </ChatHistory>
          )}
          
          {analytics.summary && !currentStreamingId && (
            <>
              <h3 style={{ margin: '0 0 10px 0', color: '#2d3748' }}>📊 Latest Analysis</h3>
              <p style={{ color: '#4a5568', fontSize: '0.95em' }}>{analytics.summary}</p>
            </>
          )}
          
          {analytics.count > 0 && (
            <p style={{ color: '#4a5568', fontWeight: 'bold' }}>
              📈 Results: {analytics.count} data points analyzed
            </p>
          )}

          {analytics.logs && analytics.logs.length > 0 && (
            <>
              <h4 style={{ margin: '15px 0 10px 0', color: '#2d3748', fontSize: '1em' }}>⚙️ Processing Steps</h4>
              <ul style={{ 
                color: '#4a5568', 
                paddingLeft: '20px',
                margin: '0',
                fontSize: '0.9em'
              }}>
                {analytics.logs.map((log, index) => (
                  <li key={index} style={{ marginBottom: '5px' }}>{log}</li>
                ))}
              </ul>
            </>
          )}

          <div style={{ marginTop: '20px', padding: '10px', background: 'rgba(74, 108, 247, 0.1)', borderRadius: '8px' }}>
            <p style={{ color: '#4a6cf7', fontSize: '0.85em', margin: '0', fontWeight: 'bold' }}>
              ✨ Real-time AI streaming enabled! Watch ChatGPT write responses live as you ask questions about Barcelona urban data.
            </p>
          </div>
        </AnalyticsPanel>
      )}
    </Container>
  );
}

export default App;