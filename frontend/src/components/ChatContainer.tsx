import React, { useState } from "react";
import ChatComponent from "@/components/ChatComponent";

export interface ChatMessage {
  id: string;
  content: string;
  sender: "user" | "assistant";
  timestamp: Date;
}

function generateId() {
  return Date.now().toString() + Math.random().toString(36).slice(2);
}

const ChatContainer: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isOpen, setIsOpen] = useState(true);

  async function handleSendMessage(userContent: string) {
    // 1. Add user message immediately
    const userMsg: ChatMessage = {
      id: generateId(),
      content: userContent,
      sender: "user",
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);

    try {
      // 2. Send to backend
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_message: userContent }),
      });
      if (!response.ok) throw new Error("Network error");
      const data = await response.json();

      // 3. Add assistant message
      const assistantMsg: ChatMessage = {
        id: data.metadata?.message_id?.toString() || generateId(),
        content: data.bot_response,
        sender: "assistant",
        timestamp: new Date(data.timestamp),
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      // 4. Error handling
      setMessages(prev => [
        ...prev,
        {
          id: generateId(),
          content: "Sorry, there was a problem contacting the assistant.",
          sender: "assistant",
          timestamp: new Date(),
        },
      ]);
    }
  }

  return (
    <ChatComponent
      isOpen={isOpen}
      messages={messages}
      onSendMessage={handleSendMessage}
    />
  );
};

export default ChatContainer; 