import { useState, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Send, 
  Menu, 
  Plus, 
  ArrowLeft, 
  MessageCircle,
  Trash2,
  Settings,
  LogOut
} from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";
import axios from "axios";
import { ChatBubble } from "@/components/ChatBubble";
import { ShlokaCard } from "@/components/ShlokaCard";
import { TypingIndicator } from "@/components/TypingIndicator";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const GURU_AVATAR = "https://images.unsplash.com/photo-1662302392561-b1deecd3579d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA3MDR8MHwxfHNlYXJjaHwxfHxwZWFjZWZ1bCUyMGluZGlhbiUyMHNwaXJpdHVhbCUyMGd1cnUlMjBwb3J0cmFpdHxlbnwwfHx8fDE3NzEyNDIxNTR8MA&ixlib=rb-4.1.0&q=85&w=200";

export default function ChatPage() {
  const navigate = useNavigate();
  const { conversationId } = useParams();
  const [userId, setUserId] = useState(null);
  const [user, setUser] = useState(null);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(conversationId || null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    const storedUserId = localStorage.getItem("pocketGuruUserId");
    if (!storedUserId) {
      navigate("/onboarding");
      return;
    }
    setUserId(storedUserId);
    fetchUser(storedUserId);
    fetchConversations(storedUserId);
  }, [navigate]);

  useEffect(() => {
    if (conversationId && conversationId !== currentConversationId) {
      setCurrentConversationId(conversationId);
      fetchConversation(conversationId);
    }
  }, [conversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchUser = async (uid) => {
    try {
      const response = await axios.get(`${API}/users/${uid}`);
      setUser(response.data);
    } catch (error) {
      console.error("Error fetching user:", error);
    }
  };

  const fetchConversations = async (uid) => {
    try {
      const response = await axios.get(`${API}/conversations/${uid}`);
      setConversations(response.data);
    } catch (error) {
      console.error("Error fetching conversations:", error);
    }
  };

  const fetchConversation = async (convId) => {
    try {
      const response = await axios.get(`${API}/conversation/${convId}`);
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error("Error fetching conversation:", error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    const userMessage = message.trim();
    setMessage("");
    setIsLoading(true);

    // Optimistically add user message
    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: userMessage,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      const response = await axios.post(`${API}/chat`, {
        user_id: userId,
        message: userMessage,
        conversation_id: currentConversationId
      });

      // Update with actual messages
      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== tempUserMsg.id);
        return [...filtered, response.data.message, response.data.guru_response];
      });

      // Update conversation ID if new
      if (!currentConversationId) {
        setCurrentConversationId(response.data.conversation_id);
        navigate(`/chat/${response.data.conversation_id}`, { replace: true });
      }

      // Refresh conversations list
      fetchConversations(userId);
    } catch (error) {
      console.error("Error sending message:", error);
      toast.error("Failed to send message. Please try again.");
      // Remove optimistic message on error
      setMessages(prev => prev.filter(m => m.id !== tempUserMsg.id));
      setMessage(userMessage);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleNewConversation = () => {
    setCurrentConversationId(null);
    setMessages([]);
    setIsSidebarOpen(false);
    navigate("/chat", { replace: true });
  };

  const handleSelectConversation = (convId) => {
    setCurrentConversationId(convId);
    fetchConversation(convId);
    setIsSidebarOpen(false);
    navigate(`/chat/${convId}`, { replace: true });
  };

  const handleDeleteConversation = async (convId, e) => {
    e.stopPropagation();
    try {
      await axios.delete(`${API}/conversation/${convId}`);
      toast.success("Conversation deleted");
      fetchConversations(userId);
      if (convId === currentConversationId) {
        handleNewConversation();
      }
    } catch (error) {
      console.error("Error deleting conversation:", error);
      toast.error("Failed to delete conversation");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("pocketGuruUserId");
    navigate("/");
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return "Today";
    } else if (date.toDateString() === yesterday.toDateString()) {
      return "Yesterday";
    }
    return date.toLocaleDateString();
  };

  // Sidebar content
  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <Button
          onClick={handleNewConversation}
          className="w-full bg-[#128C7E] hover:bg-[#075E54] flex items-center gap-2"
          data-testid="new-conversation-btn"
        >
          <Plus className="w-4 h-4" />
          New Conversation
        </Button>
      </div>
      
      <ScrollArea className="flex-1">
        <div className="p-2">
          {conversations.length === 0 ? (
            <p className="text-center text-gray-500 py-8 text-sm">
              No conversations yet
            </p>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => handleSelectConversation(conv.id)}
                className={`conversation-item rounded-lg mb-1 flex items-center justify-between group ${
                  conv.id === currentConversationId ? "active" : ""
                }`}
                data-testid={`conversation-${conv.id}`}
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {conv.title}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatDate(conv.updated_at)}
                  </p>
                </div>
                <button
                  onClick={(e) => handleDeleteConversation(conv.id, e)}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition-opacity"
                  data-testid={`delete-conversation-${conv.id}`}
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                </button>
              </div>
            ))
          )}
        </div>
      </ScrollArea>

      <div className="p-4 border-t">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-[#128C7E] flex items-center justify-center text-white font-semibold">
            {user?.name?.charAt(0) || "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user?.name || "Seeker"}
            </p>
            <p className="text-xs text-gray-500 capitalize">
              {user?.alignment} Path
            </p>
          </div>
        </div>
        <Button
          variant="outline"
          onClick={handleLogout}
          className="w-full flex items-center gap-2"
          data-testid="logout-btn"
        >
          <LogOut className="w-4 h-4" />
          Logout
        </Button>
      </div>
    </div>
  );

  return (
    <div className="chat-layout" data-testid="chat-page">
      {/* Desktop Sidebar */}
      <div className="chat-sidebar hidden lg:flex">
        <div className="p-4 bg-[#075E54] text-white">
          <h2 className="font-heading text-xl font-semibold">Pocket Guru</h2>
        </div>
        <SidebarContent />
      </div>

      {/* Main Chat Area */}
      <div className="chat-container chat-main">
        {/* Header */}
        <div className="chat-header">
          {/* Mobile menu button */}
          <Sheet open={isSidebarOpen} onOpenChange={setIsSidebarOpen}>
            <SheetTrigger asChild>
              <button className="lg:hidden p-2 -ml-2" data-testid="mobile-menu-btn">
                <Menu className="w-5 h-5" />
              </button>
            </SheetTrigger>
            <SheetContent side="left" className="p-0 w-80">
              <SheetHeader className="p-4 bg-[#075E54] text-white">
                <SheetTitle className="text-white font-heading">Pocket Guru</SheetTitle>
              </SheetHeader>
              <SidebarContent />
            </SheetContent>
          </Sheet>

          {/* Guru info */}
          <img
            src={GURU_AVATAR}
            alt="Prana"
            className="guru-avatar"
          />
          <div className="flex-1">
            <h1 className="font-semibold text-lg">Prana</h1>
            <p className="text-xs text-white/70">Your Spiritual Guide</p>
          </div>

          {/* Settings dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="p-2" data-testid="settings-btn">
                <Settings className="w-5 h-5" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => navigate("/onboarding")}>
                Update Preferences
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="text-red-500">
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Messages Area */}
        <div className="chat-messages chat-bg-pattern chat-scroll">
          {messages.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
              <img
                src={GURU_AVATAR}
                alt="Prana"
                className="w-20 h-20 rounded-full mb-4 opacity-80"
              />
              <h2 className="font-heading text-2xl text-gray-700 mb-2">
                Namaste 🙏
              </h2>
              <p className="text-gray-500 max-w-sm">
                I am Prana, your spiritual guide. Share what's on your mind, 
                and let's explore the wisdom of the ages together.
              </p>
              <div className="mt-6 flex flex-wrap gap-2 justify-center">
                {["I feel stressed", "Guide me on my path", "What is dharma?"].map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => setMessage(prompt)}
                    className="px-4 py-2 bg-white rounded-full text-sm text-gray-700 border border-gray-200 hover:border-[#128C7E] hover:bg-[#F0FDF4] transition-colors"
                    data-testid={`quick-prompt-${prompt.replace(/\s+/g, "-").toLowerCase()}`}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, index) => (
                <div key={msg.id || index} className="message-enter">
                  {msg.role === "user" ? (
                    <ChatBubble
                      type="user"
                      content={msg.content}
                      timestamp={formatTime(msg.timestamp)}
                    />
                  ) : (
                    <div className="flex gap-2 items-end">
                      <img
                        src={GURU_AVATAR}
                        alt="Prana"
                        className="guru-avatar-small mb-5"
                      />
                      <div className="flex flex-col gap-1">
                        <ChatBubble
                          type="guru"
                          content={msg.content}
                          timestamp={formatTime(msg.timestamp)}
                        />
                        {msg.shloka && (
                          <ShlokaCard
                            sanskrit={msg.shloka.sanskrit}
                            translation={msg.shloka.translation}
                            source={msg.shloka.source}
                          />
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {isLoading && <TypingIndicator />}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <form onSubmit={handleSendMessage} className="chat-input-area">
          <input
            ref={inputRef}
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message..."
            className="chat-input"
            disabled={isLoading}
            data-testid="chat-input"
          />
          <button
            type="submit"
            disabled={!message.trim() || isLoading}
            className="send-button btn-press"
            data-testid="send-btn"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
}
