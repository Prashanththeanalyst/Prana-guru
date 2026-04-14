import { useState, useEffect, useRef } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
  Modal,
} from "react-native";
import { useRouter } from "expo-router";
import AsyncStorage from "@react-native-async-storage/async-storage";
import axios from "axios";
import { API } from "../../constants/api";

export default function ChatScreen() {
  const router = useRouter();
  const flatListRef = useRef(null);

  const [userId,             setUserId]            = useState(null);
  const [user,               setUser]              = useState(null);
  const [messages,           setMessages]          = useState([]);
  const [conversations,      setConversations]     = useState([]);
  const [currentConvId,      setCurrentConvId]     = useState(null);
  const [inputText,          setInputText]         = useState("");
  const [isLoading,          setIsLoading]         = useState(false);
  const [isSidebarVisible,   setSidebarVisible]    = useState(false);

  // ---- init ----
  useEffect(() => {
    (async () => {
      try {
        const uid = await AsyncStorage.getItem("pocketGuruUserId");
        if (!uid) { router.replace("/onboarding"); return; }
        setUserId(uid);
        fetchUser(uid);
        fetchConversations(uid);
      } catch {
        router.replace("/onboarding");
      }
    })();
  }, []);

  // ---- data helpers ----
  const fetchUser = async (uid) => {
    try {
      const res = await axios.get(`${API}/users/${uid}`);
      setUser(res.data);
    } catch (err) {
      if (err.response?.status === 404) {
        await AsyncStorage.removeItem("pocketGuruUserId");
        router.replace("/onboarding");
      }
    }
  };

  const fetchConversations = async (uid) => {
    try {
      const res = await axios.get(`${API}/conversations/${uid}`);
      setConversations(res.data);
    } catch {
      // non-fatal — sidebar stays empty
    }
  };

  const fetchConversation = async (convId) => {
    try {
      const res = await axios.get(`${API}/conversation/${convId}`);
      setMessages(res.data.messages || []);
      setCurrentConvId(convId);
    } catch (err) {
      Alert.alert("Error", "Could not load conversation.");
    }
  };

  // ---- send message ----
  const handleSend = async () => {
    const text = inputText.trim();
    if (!text || isLoading) return;

    const tempMsg = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };

    setInputText("");
    setIsLoading(true);
    setMessages((prev) => [...prev, tempMsg]);

    try {
      const res = await axios.post(`${API}/chat`, {
        user_id: userId,
        message: text,
        conversation_id: currentConvId,
      });

      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== tempMsg.id);
        return [...filtered, res.data.message, res.data.guru_response];
      });

      if (!currentConvId) {
        setCurrentConvId(res.data.conversation_id);
        fetchConversations(userId);
      }
    } catch (err) {
      setMessages((prev) => prev.filter((m) => m.id !== tempMsg.id));
      setInputText(text);
      if (err.response?.status === 429) {
        Alert.alert("Rate limit", "You're sending messages too fast. Please wait a moment.");
      } else if (!err.response) {
        Alert.alert("Connection error", "Please check your internet connection.");
      } else {
        Alert.alert("Error", "Failed to send message. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // ---- new conversation ----
  const handleNewConversation = () => {
    setCurrentConvId(null);
    setMessages([]);
    setSidebarVisible(false);
  };

  // ---- delete conversation ----
  const handleDeleteConversation = (convId) => {
    Alert.alert(
      "Delete Conversation",
      "Are you sure you want to delete this conversation?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Delete",
          style: "destructive",
          onPress: async () => {
            try {
              await axios.delete(`${API}/conversation/${convId}`);
              fetchConversations(userId);
              if (convId === currentConvId) handleNewConversation();
            } catch {
              Alert.alert("Error", "Could not delete conversation.");
            }
          },
        },
      ]
    );
  };

  // ---- logout ----
  const handleLogout = async () => {
    await AsyncStorage.removeItem("pocketGuruUserId");
    router.replace("/");
  };

  // ---- formatters ----
  const formatTime = (ts) =>
    new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  const formatDate = (ts) => {
    const d = new Date(ts);
    const today = new Date();
    if (d.toDateString() === today.toDateString()) return "Today";
    const yest = new Date(today);
    yest.setDate(yest.getDate() - 1);
    if (d.toDateString() === yest.toDateString()) return "Yesterday";
    return d.toLocaleDateString();
  };

  // ---- render message ----
  const renderMessage = ({ item }) => {
    const isUser = item.role === "user";
    return (
      <View style={[styles.msgRow, isUser ? styles.msgRowUser : styles.msgRowGuru]}>
        {!isUser && (
          <View style={styles.guruAvatar}>
            <Text style={styles.guruAvatarText}>🪷</Text>
          </View>
        )}
        <View style={{ maxWidth: "75%" }}>
          <View style={[styles.bubble, isUser ? styles.bubbleUser : styles.bubbleGuru]}>
            <Text style={[styles.bubbleText, isUser ? styles.bubbleTextUser : styles.bubbleTextGuru]}>
              {item.content}
            </Text>
            <Text style={[styles.timestamp, isUser ? styles.timestampUser : styles.timestampGuru]}>
              {formatTime(item.timestamp)}
            </Text>
          </View>
          {/* Shloka card */}
          {item.shloka && (
            <View style={styles.shlokaCard}>
              <Text style={styles.shlokaSource}>{item.shloka.source}</Text>
              <Text style={styles.shlokaSanskrit}>{item.shloka.sanskrit}</Text>
              <Text style={styles.shlokaTranslation}>{item.shloka.translation}</Text>
            </View>
          )}
        </View>
      </View>
    );
  };

  // ---- sidebar modal ----
  const SidebarModal = () => (
    <Modal
      visible={isSidebarVisible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={() => setSidebarVisible(false)}
    >
      <SafeAreaView style={styles.sidebar}>
        <View style={styles.sidebarHeader}>
          <Text style={styles.sidebarTitle}>Pocket Guru</Text>
          <TouchableOpacity onPress={() => setSidebarVisible(false)}>
            <Text style={styles.sidebarClose}>✕</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity style={styles.newConvBtn} onPress={handleNewConversation}>
          <Text style={styles.newConvBtnText}>+ New Conversation</Text>
        </TouchableOpacity>

        <FlatList
          data={conversations}
          keyExtractor={(c) => c.id}
          style={{ flex: 1 }}
          ListEmptyComponent={
            <Text style={styles.emptyText}>No conversations yet</Text>
          }
          renderItem={({ item }) => (
            <View style={[styles.convItem, item.id === currentConvId && styles.convItemActive]}>
              <TouchableOpacity
                style={{ flex: 1 }}
                onPress={() => { fetchConversation(item.id); setSidebarVisible(false); }}
              >
                <Text style={styles.convTitle} numberOfLines={1}>{item.title}</Text>
                <Text style={styles.convDate}>{formatDate(item.updated_at)}</Text>
              </TouchableOpacity>
              <TouchableOpacity
                onPress={() => handleDeleteConversation(item.id)}
                style={styles.deleteBtn}
              >
                <Text style={styles.deleteBtnText}>🗑</Text>
              </TouchableOpacity>
            </View>
          )}
        />

        <View style={styles.sidebarFooter}>
          <View style={styles.userInfo}>
            <View style={styles.userAvatar}>
              <Text style={styles.userAvatarText}>{user?.name?.charAt(0) || "U"}</Text>
            </View>
            <View>
              <Text style={styles.userName}>{user?.name || "Seeker"}</Text>
              <Text style={styles.userAlignment}>{user?.alignment} Path</Text>
            </View>
          </View>
          <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
            <Text style={styles.logoutBtnText}>Logout</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </Modal>
  );

  // ---- typing indicator ----
  const TypingIndicator = () => (
    <View style={[styles.msgRow, styles.msgRowGuru]}>
      <View style={styles.guruAvatar}>
        <Text style={styles.guruAvatarText}>🪷</Text>
      </View>
      <View style={[styles.bubble, styles.bubbleGuru, styles.typingBubble]}>
        <Text style={styles.typingDots}>• • •</Text>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => setSidebarVisible(true)} style={styles.menuBtn}>
          <Text style={styles.menuBtnText}>☰</Text>
        </TouchableOpacity>
        <View style={styles.guruAvatar}>
          <Text style={styles.guruAvatarText}>🪷</Text>
        </View>
        <View style={{ flex: 1 }}>
          <Text style={styles.headerTitle}>Prana</Text>
          <Text style={styles.headerSubtitle}>Your Spiritual Guide</Text>
        </View>
      </View>

      {/* Messages */}
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        keyboardVerticalOffset={0}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={(item, i) => item.id || String(i)}
          renderItem={renderMessage}
          contentContainerStyle={styles.messageList}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
          ListEmptyComponent={
            <View style={styles.emptyChat}>
              <Text style={styles.emptyChatEmoji}>🙏</Text>
              <Text style={styles.emptyChatTitle}>Namaste</Text>
              <Text style={styles.emptyChatText}>
                I am Prana, your spiritual guide. Share what's on your mind,
                and let's explore the wisdom of the ages together.
              </Text>
              {["I feel stressed", "Guide me on my path", "What is dharma?"].map((prompt) => (
                <TouchableOpacity
                  key={prompt}
                  style={styles.quickPrompt}
                  onPress={() => setInputText(prompt)}
                >
                  <Text style={styles.quickPromptText}>{prompt}</Text>
                </TouchableOpacity>
              ))}
            </View>
          }
          ListFooterComponent={isLoading ? <TypingIndicator /> : null}
        />

        {/* Input */}
        <View style={styles.inputRow}>
          <TextInput
            style={styles.textInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Type your message…"
            placeholderTextColor="#9CA3AF"
            multiline
            maxLength={1000}
            editable={!isLoading}
            onSubmitEditing={handleSend}
          />
          <TouchableOpacity
            style={[styles.sendBtn, (!inputText.trim() || isLoading) && styles.sendBtnDisabled]}
            onPress={handleSend}
            disabled={!inputText.trim() || isLoading}
          >
            {isLoading
              ? <ActivityIndicator color="#fff" size="small" />
              : <Text style={styles.sendBtnText}>➤</Text>
            }
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>

      <SidebarModal />
    </SafeAreaView>
  );
}

const TEAL = "#128C7E";
const DARK_TEAL = "#075E54";

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#ECE5DD" },

  // Header
  header: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: DARK_TEAL,
    paddingHorizontal: 12,
    paddingVertical: 10,
    gap: 10,
  },
  menuBtn:     { padding: 4 },
  menuBtnText: { fontSize: 22, color: "#fff" },
  headerTitle: { fontSize: 17, fontWeight: "700", color: "#fff" },
  headerSubtitle: { fontSize: 12, color: "rgba(255,255,255,0.7)" },

  // Messages
  messageList: { padding: 12, paddingBottom: 4 },
  msgRow: { flexDirection: "row", marginBottom: 6, alignItems: "flex-end" },
  msgRowUser: { justifyContent: "flex-end" },
  msgRowGuru: { justifyContent: "flex-start" },

  guruAvatar: {
    width: 32, height: 32, borderRadius: 16,
    backgroundColor: "#fff",
    alignItems: "center", justifyContent: "center",
    marginRight: 6, marginBottom: 20,
  },
  guruAvatarText: { fontSize: 18 },

  bubble: { borderRadius: 16, padding: 10, maxWidth: "100%" },
  bubbleUser: { backgroundColor: "#DCF8C6", borderBottomRightRadius: 4 },
  bubbleGuru: { backgroundColor: "#fff", borderBottomLeftRadius: 4 },
  bubbleText: { fontSize: 15, lineHeight: 20 },
  bubbleTextUser: { color: "#111827" },
  bubbleTextGuru: { color: "#111827" },
  timestamp: { fontSize: 11, marginTop: 4, textAlign: "right" },
  timestampUser: { color: "#6B7280" },
  timestampGuru: { color: "#9CA3AF" },

  // Shloka card
  shlokaCard: {
    backgroundColor: "#FFF8E7",
    borderLeftWidth: 3,
    borderLeftColor: "#F59E0B",
    borderRadius: 8,
    padding: 10,
    marginTop: 4,
  },
  shlokaSource:      { fontSize: 11, color: "#92400E", fontWeight: "600", marginBottom: 4 },
  shlokaSanskrit:    { fontSize: 13, color: "#78350F", fontStyle: "italic", marginBottom: 4, lineHeight: 18 },
  shlokaTranslation: { fontSize: 13, color: "#92400E", lineHeight: 18 },

  // Typing indicator
  typingBubble: { paddingHorizontal: 14, paddingVertical: 10 },
  typingDots:   { fontSize: 18, color: "#9CA3AF", letterSpacing: 3 },

  // Empty chat
  emptyChat:       { alignItems: "center", padding: 32, marginTop: 60 },
  emptyChatEmoji:  { fontSize: 48, marginBottom: 12 },
  emptyChatTitle:  { fontSize: 24, fontWeight: "700", color: "#374151", marginBottom: 8 },
  emptyChatText:   { fontSize: 14, color: "#6B7280", textAlign: "center", lineHeight: 20, marginBottom: 20 },
  quickPrompt: {
    backgroundColor: "#fff",
    borderRadius: 20,
    paddingVertical: 8,
    paddingHorizontal: 16,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#D1D5DB",
  },
  quickPromptText: { fontSize: 14, color: "#374151" },

  // Input row
  inputRow: {
    flexDirection: "row",
    alignItems: "flex-end",
    backgroundColor: "#F0F0F0",
    padding: 8,
    gap: 8,
  },
  textInput: {
    flex: 1,
    backgroundColor: "#fff",
    borderRadius: 22,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 15,
    maxHeight: 120,
    color: "#111827",
  },
  sendBtn: {
    width: 44, height: 44, borderRadius: 22,
    backgroundColor: TEAL,
    alignItems: "center", justifyContent: "center",
  },
  sendBtnDisabled: { backgroundColor: "#9CA3AF" },
  sendBtnText: { color: "#fff", fontSize: 18 },

  // Sidebar
  sidebar: { flex: 1, backgroundColor: "#fff" },
  sidebarHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: DARK_TEAL,
    padding: 16,
  },
  sidebarTitle: { fontSize: 20, fontWeight: "700", color: "#fff" },
  sidebarClose: { fontSize: 18, color: "#fff" },
  newConvBtn: {
    margin: 12,
    backgroundColor: TEAL,
    borderRadius: 10,
    padding: 12,
    alignItems: "center",
  },
  newConvBtnText: { color: "#fff", fontWeight: "700", fontSize: 15 },
  emptyText: { textAlign: "center", color: "#9CA3AF", marginTop: 32 },
  convItem: {
    flexDirection: "row",
    alignItems: "center",
    padding: 14,
    borderBottomWidth: 1,
    borderBottomColor: "#F3F4F6",
  },
  convItemActive: { backgroundColor: "#F0FDF4" },
  convTitle:      { fontSize: 14, fontWeight: "600", color: "#111827" },
  convDate:       { fontSize: 12, color: "#9CA3AF", marginTop: 2 },
  deleteBtn:      { padding: 8 },
  deleteBtnText:  { fontSize: 18 },
  sidebarFooter: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: "#F3F4F6",
  },
  userInfo:    { flexDirection: "row", alignItems: "center", gap: 12, marginBottom: 12 },
  userAvatar: {
    width: 40, height: 40, borderRadius: 20,
    backgroundColor: TEAL,
    alignItems: "center", justifyContent: "center",
  },
  userAvatarText: { color: "#fff", fontWeight: "700", fontSize: 16 },
  userName:       { fontSize: 14, fontWeight: "600", color: "#111827" },
  userAlignment:  { fontSize: 12, color: "#6B7280", textTransform: "capitalize" },
  logoutBtn: {
    borderWidth: 1, borderColor: "#D1D5DB",
    borderRadius: 8, padding: 10, alignItems: "center",
  },
  logoutBtnText: { color: "#374151", fontWeight: "600" },
});
