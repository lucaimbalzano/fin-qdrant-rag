import { MessageCircle, Paperclip } from "lucide-react";
import { CardData } from "@/types";

export const cardsData: CardData[] = [
  {
    id: "1",
    icon: MessageCircle,
    title: "AI-Powered Advice",
    description: "Get personalized financial recommendations based on your unique situation.",
    iconBgColor: "bg-blue-100",
    iconColor: "text-blue-500",
  },
  {
    id: "2",
    icon: MessageCircle,
    title: "24/7 Support",
    description: "Chat with our finance assistant anytime, anywhere for instant help.",
    iconBgColor: "bg-green-100",
    iconColor: "text-green-500",
  },
  {
    id: "3",
    icon: Paperclip,
    title: "Document Analysis",
    description: "Upload financial documents for instant analysis and insights.",
    iconBgColor: "bg-purple-100",
    iconColor: "text-purple-500",
  },
]; 