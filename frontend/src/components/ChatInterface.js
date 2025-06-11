import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const ChatInterface = ({ messages, inputValue, setInputValue, handleSendMessage }) => {
  return (
    <ChatContainer>
      <MessageList>
        {messages.map((message, index) => (
          <MessageItem
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            $sender={message.sender}
          >
            <MessageContent $sender={message.sender}>
              {message.text}
            </MessageContent>
          </MessageItem>
        ))}
      </MessageList>
      
      <InputForm onSubmit={handleSendMessage}>
        <InputField
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask about flights, prices, or travel recommendations..."
        />
        <SendButton type="submit">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </SendButton>
      </InputForm>
      
      <QuickSuggestions>
        <SuggestionButton onClick={() => setInputValue("What is the status of flight AA123?")}>
          Check flight status
        </SuggestionButton>
        <SuggestionButton onClick={() => setInputValue("What are the cheapest flights from JFK to LAX?")}>
          Find cheap flights
        </SuggestionButton>
        <SuggestionButton onClick={() => setInputValue("When is the best time to fly from SFO to ORD?")}>
          Best time to fly
        </SuggestionButton>
      </QuickSuggestions>
    </ChatContainer>
  );
};

const ChatContainer = styled.div`
  width: 100%;
  max-width: 800px;
  background: rgba(30, 30, 50, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const MessageList = styled.div`
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 400px;
  overflow-y: auto;
`;

const MessageItem = styled(motion.div)`
  display: flex;
  justify-content: ${props => props.$sender === 'user' ? 'flex-end' : 'flex-start'};
`;

const MessageContent = styled.div`
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 16px;
  background-color: ${props => props.$sender === 'user' ? 'rgba(79, 70, 229, 0.8)' : 'rgba(45, 45, 65, 0.8)'};
  color: white;
  font-size: 0.95rem;
  line-height: 1.5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
`;

const InputForm = styled.form`
  display: flex;
  padding: 16px;
  gap: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
`;

const InputField = styled.input`
  flex: 1;
  padding: 12px 16px;
  border-radius: 30px;
  border: none;
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.2s ease;
  
  &:focus {
    background-color: rgba(255, 255, 255, 0.15);
    box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.3);
  }
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }
`;

const SendButton = styled.button`
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background-color: #4f46e5;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: #4338ca;
    transform: scale(1.05);
  }
  
  &:active {
    transform: scale(0.95);
  }
`;

const QuickSuggestions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 0 16px 16px;
`;

const SuggestionButton = styled.button`
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background-color: rgba(255, 255, 255, 0.15);
    border-color: rgba(255, 255, 255, 0.3);
  }
`;

export default ChatInterface;
