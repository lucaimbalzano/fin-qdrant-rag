import { LucideIcon } from "lucide-react";

// Chat related types
export interface Message {
  id: string;
  content: string;
  sender: "user" | "assistant";
  timestamp: Date;
  type?: "text" | "file";
  file?: {
    name: string;
    size: number;
    type: string;
  };
  uploadProgress?: number;
  uploadStatus?: "uploading" | "completed" | "failed" | "cancelled";
}

export interface ChatComponentProps {
  isOpen: boolean;
  messages: Message[];
  onSendMessage: (message: string) => void;
  className?: string;
}

// Card related types
export interface CardData {
  id: string;
  icon: LucideIcon;
  title: string;
  description: string;
  iconBgColor: string;
  iconColor: string;
}

// Home page types
export interface HomePageProps {
  // Add any props if needed in the future
}

// Background types
export interface BackgroundProps {
  // Add any props if needed in the future
} 