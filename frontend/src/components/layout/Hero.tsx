import React from "react";
import { Button } from "@/components/ui/button";
import { MessageCircle, X } from "lucide-react";

interface HeroProps {
  isChatOpen: boolean;
  onToggleChat: () => void;
}

export function Hero({ isChatOpen, onToggleChat }: HeroProps) {
  return (
    <div className="text-center">
      <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight drop-shadow-lg">
        Your AI-Powered
        <span className="bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent block">
          Finance Assistant
        </span>
      </h1>

      <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto leading-relaxed drop-shadow-md">
        Get personalized financial advice, and make
        smarter money decisions with our intelligent chatbot.
      </p>

      <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
        <button
          type="button"
          onClick={onToggleChat}
          className="py-4 px-6 text-sm bg-white/20 backdrop-blur-sm text-white rounded-full cursor-pointer font-semibold text-center shadow-lg border border-white/30 transition-all duration-500 hover:bg-white/30 hover:scale-105 flex items-center gap-2"
        >
          {isChatOpen ? (
            <>
              <X className="w-4 h-4" />
              Close Chat
            </>
          ) : (
            <>
              <MessageCircle className="w-4 h-4" />
              Start Chatting Now
            </>
          )}
        </button>
      </div>
    </div>
  );
} 