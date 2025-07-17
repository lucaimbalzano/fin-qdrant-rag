import React from "react";
import { motion } from "framer-motion";
import { CardData } from "@/types";

interface CardAnimatedProps {
  card: CardData;
  index: number;
}

export function CardAnimated({ card, index }: CardAnimatedProps) {
  const IconComponent = card.icon;

  return (
    <motion.div
      className="bg-white/30 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/30 cursor-pointer"
      initial={{ scale: 1, rotate: 0, borderRadius: "16px" }}
      whileHover={{
        scale: 1.05,
        rotate: 5,
        borderRadius: "20px",
        transition: {
          duration: 0.3,
          ease: "easeInOut",
        }
      }}
      whileTap={{
        scale: 0.95,
        rotate: -2,
        transition: {
          duration: 0.1,
          ease: "easeInOut",
        }
      }}
      animate={{
        y: [0, -10, 0],
      }}
      transition={{
        duration: 2,
        ease: "easeInOut",
        repeat: Infinity,
        delay: index * 0.2,
      }}
    >
      <div className={`w-12 h-12 ${card.iconBgColor} rounded-lg flex items-center justify-center mb-4 mx-auto`}>
        <IconComponent className={`w-6 h-6 ${card.iconColor}`} />
      </div>
      <h3 className="text-xl font-semibold text-white mb-2 drop-shadow-sm">
        {card.title}
      </h3>
      <p className="text-white/90 drop-shadow-sm">
        {card.description}
      </p>
    </motion.div>
  );
}

// Helper function to render multiple cards
export function CardsGrid({ cards }: { cards: CardData[] }) {
  return (
    <div className="grid md:grid-cols-3 gap-8 mt-16">
      {cards.map((card, index) => (
        <CardAnimated key={card.id} card={card} index={index} />
      ))}
    </div>
  );
} 