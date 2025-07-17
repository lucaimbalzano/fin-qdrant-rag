'use client';
import React, { useState } from 'react';
import { Github, Star } from 'lucide-react';
import { Colors, Liquid } from '@/components/LiquidGradient';

type ColorKey =
  | 'color1'
  | 'color2'
  | 'color3'
  | 'color4'
  | 'color5'
  | 'color6'
  | 'color7'
  | 'color8'
  | 'color9'
  | 'color10'
  | 'color11'
  | 'color12'
  | 'color13'
  | 'color14'
  | 'color15'
  | 'color16'
  | 'color17';

const COLORS: Colors = {
  color1: '#FFFFFF',
  color2: '#60A5FA', // Light blue
  color3: '#93C5FD', // Lighter blue
  color4: '#F0F9FF', // Very light blue
  color5: '#E0F2FE', // Light cyan
  color6: '#7DD3FC', // Sky blue
  color7: '#38BDF8', // Cyan
  color8: '#0EA5E9', // Blue
  color9: '#0284C7', // Darker blue
  color10: '#0369A1', // Dark blue
  color11: '#075985', // Darker blue
  color12: '#BAE6FD', // Very light blue
  color13: '#0C4A6E', // Dark blue
  color14: '#B3E5FC', // Light blue
  color15: '#81D4FA', // Light blue
  color16: '#4FC3F7', // Light blue
  color17: '#29B6F6', // Light blue
};
const GitHubButton: React.FC = () => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className='flex justify-center'>
      <a
        href='https://github.com/lucaimbalzano/fin-qdrant-rag'
        target='_blank'
        className='relative inline-block  sm:w-36 w-14 h-[2.7em] mx-auto group dark:bg-white bg-white dark:border-white border-white border-2 rounded-lg'
      >
        <div className='absolute w-[112.81%] h-[128.57%] top-[8.57%] left-1/2 -translate-x-1/2 filter blur-[8px] opacity-30'>
          <span className='absolute inset-0 rounded-lg bg-[#d9d9d9] filter blur-[3px]'></span>
          <div className='relative w-full h-full overflow-hidden rounded-lg'>
            <Liquid isHovered={isHovered} colors={COLORS} />
          </div>
        </div>
        <div className='absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-[40%] w-[92.23%] h-[112.85%] rounded-lg bg-[#010128] filter blur-[3px] opacity-50'></div>
        <div className='relative w-full h-full overflow-hidden rounded-lg'>
          <span className='absolute inset-0 rounded-lg bg-[#d9d9d9]'></span>
          <span className='absolute inset-0 rounded-lg bg-white'></span>
          <Liquid isHovered={isHovered} colors={COLORS} />
          {[1, 2, 3, 4, 5].map((i) => (
            <span
              key={i}
              className={`absolute inset-0 rounded-lg border-solid border-[3px] border-gradient-to-b from-transparent to-white mix-blend-overlay filter ${
                i <= 2 ? 'blur-[3px]' : i === 3 ? 'blur-[5px]' : 'blur-[4px]'
              }`}
            ></span>
          ))}
          <span className='absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-[40%] w-[70.8%] h-[42.85%] rounded-lg filter blur-[15px] bg-[#006]'></span>
        </div>
        <button
          className='absolute inset-0 rounded-lg bg-transparent cursor-pointer'
          aria-label='Get Started'
          type='button'
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <span className=' flex  items-center justify-between px-4 gap-2   rounded-lg group-hover:text-gray-400 text-white text-xl font-semibold tracking-wide whitespace-nowrap'>
            <Star className='group-hover:fill-gray-400 fill-white w-6 h-6 flex-shrink-0 sm:inline-block hidden' />
            <Github className='sm:hidden inline-block group-hover:fill-gray-400 fill-white w-6 h-6 flex-shrink-0' />
            <span className='sm:inline-block hidden'>Github</span>
          </span>
        </button>
      </a>
    </div>
  );
};

export default GitHubButton;
