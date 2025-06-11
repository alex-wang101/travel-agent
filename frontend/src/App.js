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
  
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    
    // Add user message
    const userMessage = inputValue;
    setMessages(prev => [...prev, { text: userMessage, sender: "user" }]);
    setInputValue('');
    
    try {
      // Show loading indicator
      setMessages(prev => [...prev, { text: "Thinking...", sender: "assistant", isLoading: true }]);
      
      // Call the backend API
      const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: userMessage })
      });
      
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      
      const data = await response.json();
      
      // Remove loading message and add the real response
      setMessages(prev => {
        const filtered = prev.filter(msg => !msg.isLoading);
        return [...filtered, { text: data.response, sender: "assistant" }];
      });
      
    } catch (error) {
      console.error('Error:', error);
      
      // Remove loading message and add error message
      setMessages(prev => {
        const filtered = prev.filter(msg => !msg.isLoading);
        return [...filtered, { 
          text: "Sorry, there was an error processing your request. Please try again.", 
          sender: "assistant" 
        }];
      });
    }
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
