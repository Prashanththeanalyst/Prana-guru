import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  ArrowLeft,
  Users,
  MessageCircle,
  BookOpen,
  Heart,
  HandHelping,
  Sparkles,
  RefreshCw,
  Eye,
  Lock,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";
import axios from "axios";
import { ChatBubble } from "@/components/ChatBubble";
import { ShlokaCard } from "@/components/ShlokaCard";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ALIGNMENT_ICONS = {
  jnana:     { icon: BookOpen,     color: "#6366F1", label: "Jnana"     },
  bhakti:    { icon: Heart,        color: "#EC4899", label: "Bhakti"    },
  karma:     { icon: HandHelping,  color: "#F59E0B", label: "Karma"     },
  universal: { icon: Sparkles,     color: "#128C7E", label: "Universal" },
};

// ---------- helpers ----------
function getStoredToken() {
  return localStorage.getItem("adminToken");
}
function storeToken(token) {
  localStorage.setItem("adminToken", token);
}
function clearToken() {
  localStorage.removeItem("adminToken");
}
function authHeaders() {
  const token = getStoredToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// ---------- component ----------
export default function AdminPage() {
  const navigate = useNavigate();

  // auth state
  const [isAuthenticated, setIsAuthenticated] = useState(!!getStoredToken());
  const [loginUsername, setLoginUsername]   = useState("");
  const [loginPassword, setLoginPassword]   = useState("");
  const [loginLoading,  setLoginLoading]    = useState(false);

  // data state
  const [stats,                  setStats]                  = useState(null);
  const [conversations,          setConversations]          = useState([]);
  const [filteredConversations,  setFilteredConversations]  = useState([]);
  const [alignmentFilter,        setAlignmentFilter]        = useState("all");
  const [isLoading,              setIsLoading]              = useState(false);
  const [selectedConversation,   setSelectedConversation]   = useState(null);
  const [isDialogOpen,           setIsDialogOpen]           = useState(false);

  useEffect(() => {
    if (isAuthenticated) fetchData();
  }, [isAuthenticated]);

  useEffect(() => {
    if (alignmentFilter === "all") {
      setFilteredConversations(conversations);
    } else {
      setFilteredConversations(
        conversations.filter((c) => c.user?.alignment === alignmentFilter)
      );
    }
  }, [alignmentFilter, conversations]);

  // ---- login ----
  const handleLogin = async (e) => {
    e.preventDefault();
    if (!loginUsername || !loginPassword) {
      toast.error("Please enter username and password");
      return;
    }
    setLoginLoading(true);
    try {
      const res = await axios.post(`${API}/auth/admin/login`, {
        username: loginUsername,
        password: loginPassword,
      });
      storeToken(res.data.access_token);
      setIsAuthenticated(true);
      toast.success("Welcome, Admin");
    } catch (err) {
      const detail = err.response?.data?.detail || "Invalid credentials";
      toast.error(detail);
    } finally {
      setLoginLoading(false);
    }
  };

  const handleLogout = () => {
    clearToken();
    setIsAuthenticated(false);
    setStats(null);
    setConversations([]);
    toast.success("Logged out");
  };

  // ---- data fetching ----
  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [statsRes, convsRes] = await Promise.all([
        axios.get(`${API}/admin/stats`,         { headers: authHeaders() }),
        axios.get(`${API}/admin/conversations`, { headers: authHeaders() }),
      ]);
      setStats(statsRes.data);
      setConversations(convsRes.data);
      setFilteredConversations(convsRes.data);
    } catch (err) {
      if (err.response?.status === 401 || err.response?.status === 403) {
        clearToken();
        setIsAuthenticated(false);
        toast.error("Session expired. Please log in again.");
      } else {
        toast.error("Failed to load admin data. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // ---- formatters ----
  const formatDate = (ts) => {
    const d = new Date(ts);
    return d.toLocaleDateString() + " " + d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };
  const formatTime = (ts) => new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  const getAlignmentBadge = (alignment) => {
    const cfg = ALIGNMENT_ICONS[alignment] || ALIGNMENT_ICONS.universal;
    const Icon = cfg.icon;
    return (
      <div
        className="flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium"
        style={{ backgroundColor: `${cfg.color}15`, color: cfg.color }}
      >
        <Icon className="w-3 h-3" />
        {cfg.label}
      </div>
    );
  };

  // ================================================================
  // LOGIN SCREEN
  // ================================================================
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#075E54] to-[#128C7E] flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-sm">
          <div className="flex flex-col items-center mb-6">
            <div className="w-14 h-14 rounded-full bg-[#128C7E]/10 flex items-center justify-center mb-3">
              <Lock className="w-7 h-7 text-[#128C7E]" />
            </div>
            <h1 className="font-heading text-2xl font-semibold text-[#075E54]">Admin Login</h1>
            <p className="text-sm text-gray-500 mt-1">Prana Guru Dashboard</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">Username</label>
              <Input
                type="text"
                value={loginUsername}
                onChange={(e) => setLoginUsername(e.target.value)}
                placeholder="admin"
                autoComplete="username"
                data-testid="admin-username"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">Password</label>
              <Input
                type="password"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete="current-password"
                data-testid="admin-password"
              />
            </div>
            <Button
              type="submit"
              disabled={loginLoading}
              className="w-full bg-[#128C7E] hover:bg-[#075E54]"
              data-testid="admin-login-btn"
            >
              {loginLoading ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Signing in...</>
              ) : (
                "Sign In"
              )}
            </Button>
          </form>

          <button
            onClick={() => navigate("/")}
            className="mt-4 w-full text-sm text-gray-400 hover:text-gray-600 text-center"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    );
  }

  // ================================================================
  // AUTHENTICATED DASHBOARD
  // ================================================================
  return (
    <div className="admin-container" data-testid="admin-page">
      {/* Header */}
      <div className="admin-header">
        <div className="max-w-7xl mx-auto flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate("/")}
            className="text-white hover:bg-white/10"
            data-testid="back-btn"
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <h1 className="font-heading text-2xl font-semibold">Admin Dashboard</h1>
            <p className="text-white/70 text-sm">Pocket Guru Conversation Logs</p>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={fetchData}
              className="bg-transparent border-white/30 text-white hover:bg-white/10"
              data-testid="refresh-btn"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleLogout}
              className="bg-transparent border-white/30 text-white hover:bg-white/10"
              data-testid="logout-btn"
            >
              Logout
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="admin-content">
        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-[#128C7E]/10 flex items-center justify-center">
                  <Users className="w-5 h-5 text-[#128C7E]" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_users}</p>
                  <p className="text-sm text-gray-500">Total Users</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-[#6366F1]/10 flex items-center justify-center">
                  <MessageCircle className="w-5 h-5 text-[#6366F1]" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_conversations}</p>
                  <p className="text-sm text-gray-500">Conversations</p>
                </div>
              </div>
            </div>
            {Object.entries(stats.alignment_breakdown || {}).map(([alignment, count]) => {
              const cfg = ALIGNMENT_ICONS[alignment] || ALIGNMENT_ICONS.universal;
              const Icon = cfg.icon;
              return (
                <div key={alignment} className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center"
                      style={{ backgroundColor: `${cfg.color}15` }}>
                      <Icon className="w-5 h-5" style={{ color: cfg.color }} />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-gray-900">{count}</p>
                      <p className="text-sm text-gray-500">{cfg.label}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Conversations Table */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="p-4 border-b flex items-center justify-between">
            <h2 className="font-semibold text-gray-900">Conversation Logs</h2>
            <Select value={alignmentFilter} onValueChange={setAlignmentFilter}>
              <SelectTrigger className="w-[180px]" data-testid="alignment-filter">
                <SelectValue placeholder="Filter by path" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Paths</SelectItem>
                <SelectItem value="jnana">Jnana</SelectItem>
                <SelectItem value="bhakti">Bhakti</SelectItem>
                <SelectItem value="karma">Karma</SelectItem>
                <SelectItem value="universal">Universal</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <ScrollArea className="h-[500px]">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Spiritual Path</TableHead>
                  <TableHead>Conversation</TableHead>
                  <TableHead>Messages</TableHead>
                  <TableHead>Last Active</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                      <Loader2 className="w-5 h-5 animate-spin mx-auto mb-2" />
                      Loading conversations…
                    </TableCell>
                  </TableRow>
                ) : filteredConversations.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-gray-500">
                      No conversations found
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredConversations.map((conv) => (
                    <TableRow key={conv.id} data-testid={`conv-row-${conv.id}`}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-[#128C7E] flex items-center justify-center text-white text-sm font-semibold">
                            {conv.user?.name?.charAt(0) || "U"}
                          </div>
                          <span className="font-medium">{conv.user?.name || "Anonymous"}</span>
                        </div>
                      </TableCell>
                      <TableCell>{getAlignmentBadge(conv.user?.alignment || "universal")}</TableCell>
                      <TableCell>
                        <p className="text-sm text-gray-700 truncate max-w-[200px]">{conv.title}</p>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-gray-600">{conv.messages?.length || 0}</span>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-gray-500">{formatDate(conv.updated_at)}</span>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => { setSelectedConversation(conv); setIsDialogOpen(true); }}
                          data-testid={`view-conv-${conv.id}`}
                        >
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </ScrollArea>
        </div>
      </div>

      {/* Conversation Detail Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle className="font-heading">
              Conversation with {selectedConversation?.user?.name || "Anonymous"}
            </DialogTitle>
          </DialogHeader>
          <ScrollArea className="flex-1 pr-4">
            <div className="space-y-4 py-4">
              {selectedConversation?.messages?.map((msg, index) => (
                <div key={msg.id || index}>
                  {msg.role === "user" ? (
                    <ChatBubble type="user" content={msg.content} timestamp={formatTime(msg.timestamp)} />
                  ) : (
                    <div className="flex flex-col gap-1">
                      <ChatBubble type="guru" content={msg.content} timestamp={formatTime(msg.timestamp)} />
                      {msg.shloka && (
                        <ShlokaCard
                          sanskrit={msg.shloka.sanskrit}
                          translation={msg.shloka.translation}
                          source={msg.shloka.source}
                        />
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </div>
  );
}
