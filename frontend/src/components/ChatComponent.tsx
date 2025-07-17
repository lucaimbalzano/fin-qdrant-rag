import React, { useRef, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Bot, User, Paperclip, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import { Message, ChatComponentProps } from "@/types";
import { apiService } from "@/services/api";
import { fileUtils } from "@/utils/fileUtils";

const RenderMessageContent = ({ content }: { content: string }) => {
  // If you want to allow HTML (for e.g. images), use dangerouslySetInnerHTML
  if (content.startsWith('<img')) {
    return <span dangerouslySetInnerHTML={{ __html: content }} />;
  }
  return <>{content}</>;
};

// Memoized ChatMessage component to prevent re-renders
const ChatMessage = React.memo(({ message, onCancelUpload }: { message: Message; onCancelUpload?: (messageId: string) => void }) => {
  const isUser = message.sender === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn(
        "flex w-full mb-4",
        isUser ? "justify-end" : "justify-start"
      )}
    >
              <div
          className={cn(
            "flex items-start gap-2 sm:gap-3 max-w-[90%] sm:max-w-[80%]",
            isUser ? "flex-row-reverse" : "flex-row"
          )}
        >
        <div
          className={cn(
            "flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center text-sm font-medium",
            isUser
              ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white"
              : "bg-gradient-to-r from-gray-100 to-gray-200 text-gray-700 border border-gray-200"
          )}
        >
          {isUser ? <User size={14} /> : <img src="/bot_icon.gif" alt="Bot" className="h-8 w-8 rounded-full object-cover" />}
        </div>

        <div
          className={cn(
            "rounded-2xl px-3 py-2 sm:px-4 sm:py-3 max-w-full shadow-sm flex flex-col items-start relative",
            isUser
              ? "bg-gradient-to-r from-blue-500 to-blue-600 text-white"
              : "bg-white border border-gray-200 text-gray-800"
          )}
        >
          {message.type === "file" ? (
            <div className="flex items-center gap-2 sm:gap-3 w-full">
              <Paperclip className="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs sm:text-sm font-medium truncate">
                  {message.file?.name}
                </p>
                <p className="text-xs opacity-60">
                  {(message.file?.size / 1024 / 1024).toFixed(2)} MB
                </p>
                {message.uploadStatus === "uploading" && (
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${message.uploadProgress || 0}%` }}
                      ></div>
                    </div>
                    <p className="text-xs mt-1 opacity-60">
                      Uploading... {message.uploadProgress || 0}%
                    </p>
                  </div>
                )}
                {message.uploadStatus === "completed" && (
                  <p className="text-xs mt-1 opacity-60 text-green-600">
                    Upload completed
                  </p>
                )}
                {message.uploadStatus === "failed" && (
                  <p className="text-xs mt-1 opacity-60 text-red-600">
                    Upload failed
                  </p>
                )}
              </div>
              {message.uploadStatus === "uploading" && onCancelUpload && (
                <button
                  onClick={() => onCancelUpload(message.id)}
                  className="flex-shrink-0 p-1 hover:bg-gray-100 rounded-full transition-colors"
                >
                  <X className="w-4 h-4 text-gray-500" />
                </button>
              )}
            </div>
          ) : (
            <>
              <p className="text-xs sm:text-sm text-left leading-relaxed whitespace-pre-wrap">
                <RenderMessageContent content={message.content} />
              </p>
              <span className={cn(
                "text-xs mt-1 opacity-60 text-left",
                isUser ? "text-blue-100" : "text-gray-500"
              )}>
                {message.timestamp.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </>
          )}
        </div>
      </div>
    </motion.div>
  );
});

ChatMessage.displayName = "ChatMessage";

const ChatComponent: React.FC<ChatComponentProps> = ({
  isOpen,
  messages,
  onSendMessage,
  className,
}) => {
  const [inputValue, setInputValue] = useState("");
  const [disclaimer, setDisclaimer] = useState("");
  const [localMessages, setLocalMessages] = useState<Message[]>(messages);
  const [loading, setLoading] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<Set<string>>(new Set());
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setLocalMessages(messages);
  }, [messages]);

  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      // Find the first scrollable child (with overflow-y-auto or scroll)
      const scrollable = scrollAreaRef.current.querySelector('[class*="overflow-y-auto"], [class*="overflow-y-scroll"]');
      if (scrollable) {
        (scrollable as HTMLElement).scrollTop = (scrollable as HTMLElement).scrollHeight;
      }
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [localMessages]);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.type !== "application/pdf") {
      setDisclaimer("Only PDF files are supported.");
      return;
    }

    setDisclaimer("");

    const sanitizedFileName = fileUtils.sanitizeFileName(file.name);

    // Create file message
    const fileMessage: Message = {
      id: Date.now().toString(),
      content: "",
      sender: "user",
      timestamp: new Date(),
      type: "file",
      file: {
        name: sanitizedFileName,
        size: file.size,
        type: file.type,
      },
      uploadProgress: 0,
      uploadStatus: "uploading",
    };

    // Add message to chat
    setLocalMessages((prev) => [...prev, fileMessage]);
    setUploadingFiles((prev) => new Set(prev).add(fileMessage.id));

                // Upload file with progress
      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("title", sanitizedFileName);

        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener("progress", (event) => {
          if (event.lengthComputable) {
            const progress = Math.round((event.loaded / event.total) * 100);
            setLocalMessages((prev) =>
              prev.map((msg) =>
                msg.id === fileMessage.id
                  ? { ...msg, uploadProgress: progress }
                  : msg
              )
            );
          }
        });

        xhr.addEventListener("load", () => {
          if (xhr.status === 200) {
            setLocalMessages((prev) =>
              prev.map((msg) =>
                msg.id === fileMessage.id
                  ? { ...msg, uploadStatus: "completed" as const }
                  : msg
              )
            );
          } else {
            setLocalMessages((prev) =>
              prev.map((msg) =>
                msg.id === fileMessage.id
                  ? { ...msg, uploadStatus: "failed" as const }
                  : msg
              )
            );
          }
          setUploadingFiles((prev) => {
            const newSet = new Set(prev);
            newSet.delete(fileMessage.id);
            return newSet;
          });
        });

        xhr.addEventListener("error", () => {
          setLocalMessages((prev) =>
            prev.map((msg) =>
              msg.id === fileMessage.id
                ? { ...msg, uploadStatus: "failed" as const }
                : msg
            )
          );
          setUploadingFiles((prev) => {
            const newSet = new Set(prev);
            newSet.delete(fileMessage.id);
            return newSet;
          });
        });

        xhr.open("POST", "http://localhost:8000/upload");
        xhr.send(formData);
      } catch (error) {
        setLocalMessages((prev) =>
          prev.map((msg) =>
            msg.id === fileMessage.id
              ? { ...msg, uploadStatus: "failed" as const }
              : msg
          )
        );
        setUploadingFiles((prev) => {
          const newSet = new Set(prev);
          newSet.delete(fileMessage.id);
          return newSet;
        });
      }

    // Clear the input
    e.target.value = "";
  };

  const handleCancelUpload = (messageId: string) => {
    // Remove the message from chat
    setLocalMessages((prev) => prev.filter((msg) => msg.id !== messageId));
    setUploadingFiles((prev) => {
      const newSet = new Set(prev);
      newSet.delete(messageId);
      return newSet;
    });
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) {
      setDisclaimer("Message cannot be empty.");
      return;
    }
    setDisclaimer("");

    // Add user message immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
      type: "text",
    };
    setLocalMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setLoading(true);

          // Call the /chat API and add the assistant's response
      try {
        const data = await apiService.sendChatMessage(userMessage.content);
        if (data && data.bot_response) {
          const assistantMessage: Message = {
            id: (Date.now() + 2).toString(),
            content: data.bot_response,
            sender: "assistant",
            timestamp: new Date(),
            type: "text",
          };
          setLocalMessages((prev) => [...prev, assistantMessage]);
        }
      } catch (error) {
        setDisclaimer("Failed to send message to chat API.");
      }
    setLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.4, ease: "easeInOut" }}
          className={cn("w-full max-w-4xl mx-auto sm:px-0", className)}
        >
          <Card className="bg-white/40 backdrop-blur-sm border border-white/30 shadow-xl rounded-2xl overflow-hidden">
            {/* Chat Header */}
            <div className="bg-gradient-to-r from-blue-500 to-blue-100 text-white p-4">
              <div className="flex items-center gap-3">
                <div className="pl-5">
                  <h3 className="font-semibold text-lg">AI Finance Assistant</h3>
                  <p className="text-sm opacity-90 animate-pulse">Online</p>
                </div>
              </div>
            </div>

            {/* Messages Area */}
            <div className="h-[400px] flex flex-col">
              <ScrollArea ref={scrollAreaRef} className="flex-1 p-2 sm:p-4 bg-white">
                <div className="space-y-2">
                  {localMessages.map((message) => (
                    <ChatMessage 
                      key={message.id} 
                      message={message} 
                      onCancelUpload={handleCancelUpload}
                    />
                  ))}
                  {loading && (
                    <div className="flex w-full mb-4 justify-start">
                      <div className="flex items-start gap-3 max-w-[80%] flex-row">
                        {/* Bot avatar */}
                        <div className="flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center bg-white ">
                          <img src="/bot_icon.gif" alt="Bot" className="h-8 w-8 rounded-full object-cover" />
                        </div>
                        {/* Bubble with loading GIF and typing... in a row */}
                        <div className="flex items-center gap-2 px-4 py-0 bg-white text-gray-400 text-sm font-medium opacity-80 animate-pulse rounded-2xl">
                          <img src="/loading_Paperplane.gif" alt="my gif" width={82} height={82} />
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>

              {/* Input Area */}
              <div className="p-2 sm:p-4 border-t border-white/20 bg-white/30">
                <form
                  onSubmit={e => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                >
                  {disclaimer && (
                    <div className="text-xs text-red-400 mb-2 text-left">{disclaimer}</div>
                  )}
                  <div className="flex gap-2 sm:gap-3 items-center">
                    {/* Upload Button */}
                    <label className="cursor-pointer flex items-center">
                      <input
                        type="file"
                        accept="application/pdf"
                        className="hidden"
                        onChange={handleFileChange}
                      />
                      <Paperclip className="w-4 h-4 sm:w-5 sm:h-5 text-gray-500 hover:text-blue-500" />
                    </label>
                    <Input
                      ref={inputRef}
                      value={inputValue}
                      onChange={e => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Type your message..."
                      className="flex-1 bg-white/80 backdrop-blur-sm border-white/30 text-gray-900 placeholder:text-gray-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 rounded-xl h-10 sm:h-12 text-xs sm:text-sm shadow-sm"
                    />
                    <Button
                      type="submit"
                      className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-xl h-10 sm:h-12 px-3 sm:px-6 shadow-lg transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                      size="sm"
                    >
                      <Send className="w-3 h-3 sm:w-4 sm:h-4" />
                    </Button>
                  </div>
                </form>
              </div>
            </div>
          </Card>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default ChatComponent;