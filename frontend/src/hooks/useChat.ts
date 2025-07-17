import { useState } from "react";
import { Message } from "@/types";

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! I'm your AI assistant. How can I help you today?",
      sender: "assistant",
      timestamp: new Date(),
    },
  ]);

  const sendMessage = async (message: string) => {
    // Add user message immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      content: message,
      sender: "user",
      timestamp: new Date(),
      type: "text",
    };
    setMessages((prev) => [...prev, userMessage]);

    // Call the /chat API and add the assistant's response
    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "accept": "application/json",
        },
        body: JSON.stringify({ user_message: userMessage.content }),
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data && data.bot_response) {
          const assistantMessage: Message = {
            id: (Date.now() + 2).toString(),
            content: data.bot_response,
            sender: "assistant",
            timestamp: new Date(),
            type: "text",
          };
          setMessages((prev) => [...prev, assistantMessage]);
        }
      } else {
        console.error("Failed to get response from chat API.");
      }
    } catch (error) {
      console.error("Failed to send message to chat API:", error);
    }
  };

  return {
    messages,
    sendMessage,
  };
}; 