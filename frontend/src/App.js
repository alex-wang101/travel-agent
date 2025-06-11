import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import StarryBackground from './components/StarryBackground';
import ChatInterface from './components/ChatInterface';

function App() {
  const [messages, setMessages] = useState([
    { 
      text: "Welcome to Smart Travel Assistant! How can I help you with your travel plans today?", 
      sender: "assistant" 
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  
  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    
    // Add user message
    setMessages(prev => [...prev, { text: inputValue, sender: "user" }]);
    
    // Simulate assistant response (in a real app, this would call your Python backend)
    setTimeout(() => {
      setMessages(prev => [
        ...prev, 
        { 
          text: "I'm processing your request. In a complete implementation, this would connect to your Python backend.", 
          sender: "assistant" 
        }
      ]);
    }, 1000);
    
    setInputValue('');
  };

  return (
    <AppContainer>
      <StarryBackground />
      
      <ContentContainer
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <Header>
          <Title>Smart Travel Assistant</Title>
          <Subtitle>Your AI-powered travel companion</Subtitle>
        </Header>
        
        <ChatInterface 
          messages={messages}
          inputValue={inputValue}
          setInputValue={setInputValue}
          handleSendMessage={handleSendMessage}
        />
      </ContentContainer>
    </AppContainer>
  );
}

const AppContainer = styled.div`
  position: relative;
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow: hidden;
`;

const ContentContainer = styled(motion.div)`
  position: relative;
  width: 100%;
  max-width: 1000px;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 10;
`;

const Header = styled.header`
  text-align: center;
  margin-bottom: 40px;
`;

const Title = styled.h1`
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #ffffff 0%, #88c8ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 0 20px rgba(136, 200, 255, 0.5);
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.7);
`;

export default App;
