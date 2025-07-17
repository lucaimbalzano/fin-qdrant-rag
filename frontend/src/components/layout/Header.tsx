import React from "react";
import { TrendingUp } from "lucide-react";
import GitHubButton from "@/components/GithubButton";

export function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-40 bg-white/20 backdrop-blur-md border-b border-white/30">
      <div className="container mx-auto px-6 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-r from-white to-gray-200 rounded-lg flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-gray-800" />
          </div>
        </div>
        
        {/* GitHub Button */}
        <div className="flex items-center">
          <GitHubButton />
        </div>
      </div>
    </header>
  );
} 