import React from "react";
import { TrendingUp } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-white/30 backdrop-blur-sm border-t border-white/20 py-12 relative z-10">
      <div className="container mx-auto px-6">
        <div className="grid md:grid-cols-4 gap-8">
          
          {/* Brand Section */}
          <div className="md:col-span-1">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-gray-800">fqr_proj</span>
            </div>
            <p className="text-gray-600 text-sm mb-4">
              Your AI-powered finance assistant for smarter money decisions.
            </p>
          </div>

        </div>

        <div className="border-t border-white/20 mt-8 pt-8 text-center">
          <p className="text-gray-600 text-sm">
            © 2025 Fqr_proj Finance Assistant. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
} 