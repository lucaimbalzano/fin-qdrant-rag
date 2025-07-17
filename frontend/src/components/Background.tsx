'use client';
import React from 'react';

function Background() {
  return (
    <div className="fixed inset-0 overflow-hidden">
      {/* Animated gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-teal-400 via-blue-300 to-purple-400 animate-gradient-xy"></div>
      
      {/* Floating orbs */}
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-teal-300/20 rounded-full blur-xl animate-float-slow"></div>
      <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-blue-300/20 rounded-full blur-xl animate-float-medium"></div>
      <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-purple-300/20 rounded-full blur-xl animate-float-fast"></div>
      
      {/* Additional decorative elements */}
      <div className="absolute top-1/2 left-1/2 w-32 h-32 bg-white/10 rounded-full blur-lg animate-pulse"></div>
      <div className="absolute top-1/3 right-1/3 w-24 h-24 bg-cyan-300/15 rounded-full blur-md animate-bounce"></div>
    </div>
  );
}

export default Background;