import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { FileIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp?: string;
  fileUpload?: {
    name: string;
    type: string;
  };
}

const ChatMessage = ({
  message = "",
  isUser = false,
  timestamp = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  }),
  fileUpload,
}: ChatMessageProps) => {
  return (
    <div
      className={cn(
        "flex w-full mb-4",
        isUser ? "justify-end" : "justify-start",
      )}
    >
      {!isUser && (
        <div className="mr-2 flex-shrink-0">
          <Avatar>
            <AvatarImage
              src="https://api.dicebear.com/7.x/avataaars/svg?seed=tempo"
              alt="Tempo Assistant"
            />
            <AvatarFallback>TA</AvatarFallback>
          </Avatar>
        </div>
      )}

      <Card
        className={cn(
          "max-w-[80%] shadow-sm",
          isUser ? "bg-primary text-primary-foreground" : "bg-card",
          isUser ? "rounded-tr-none" : "rounded-tl-none",
        )}
      >
        <CardContent className="p-3">
          {fileUpload ? (
            <div className="flex items-center gap-2">
              <div className="bg-muted rounded-md p-2">
                <FileIcon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-medium">{fileUpload.name}</p>
                <p className="text-xs text-muted-foreground">
                  {fileUpload.type}
                </p>
              </div>
            </div>
          ) : (
            <p className="text-sm">{message}</p>
          )}
          <div
            className={cn(
              "text-xs mt-1",
              isUser ? "text-primary-foreground/70" : "text-muted-foreground",
            )}
          >
            {timestamp}
          </div>
        </CardContent>
      </Card>

      {isUser && (
        <div className="ml-2 flex-shrink-0">
          <Avatar>
            <AvatarImage
              src="https://api.dicebear.com/7.x/avataaars/svg?seed=user"
              alt="User"
            />
            <AvatarFallback>U</AvatarFallback>
          </Avatar>
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
