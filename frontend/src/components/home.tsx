import React, { useState } from "react";
import ChatComponent from "./ChatComponent";
import { Footer } from "./Footer";
import { CardsGrid } from "./CardAnimated";
import { Header } from "./layout/Header";
import { Hero } from "./layout/Hero";
import { useChat } from "@/hooks/useChat";
import { cardsData } from "@/data/cards";
import Background from "./Background";

const LandingPage = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const { messages, sendMessage } = useChat();

  const handleToggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  return (
    <div className="relative">
      {/* Background Component */}
      <Background />
      
      {/* Content */}
      <div className="relative z-[2] w-full min-h-screen">
        <Header />

        {/* Main Content */}
        <main className="pt-20 mt-16 pb-12 relative z-10">
          <div className="container mx-auto px-6 text-center">
            <div className="max-w-4xl mx-auto">
              <Hero isChatOpen={isChatOpen} onToggleChat={handleToggleChat} />

              {/* Chat Component */}
              <ChatComponent 
                isOpen={isChatOpen}
                messages={messages}
                onSendMessage={sendMessage}
              />

              {/* Features Grid */}
              <CardsGrid cards={cardsData} />
            </div>
          </div>
        </main>

        {/* Footer */}
        <Footer />
      </div>
    </div>
  );
};

export default LandingPage;
