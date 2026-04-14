import { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TextInput,
  ActivityIndicator,
  Alert,
} from "react-native";
import { useRouter } from "expo-router";
import AsyncStorage from "@react-native-async-storage/async-storage";
import axios from "axios";
import { API } from "../constants/api";

const ALIGNMENTS = [
  { id: "jnana",     name: "Jnana",     subtitle: "Path of Knowledge",  description: "Seek truth through wisdom and self-inquiry",       emoji: "📖" },
  { id: "bhakti",    name: "Bhakti",    subtitle: "Path of Devotion",   description: "Connect through love, surrender, and devotion",    emoji: "❤️" },
  { id: "karma",     name: "Karma",     subtitle: "Path of Action",     description: "Find meaning through service and righteous duty",  emoji: "🤝" },
  { id: "universal", name: "Universal", subtitle: "All Paths",          description: "Embrace wisdom from all spiritual traditions",     emoji: "✨" },
];

const DEITIES = [
  { id: "krishna",          name: "Lord Krishna",          tradition: "Vaishnavism"   },
  { id: "shiva",            name: "Lord Shiva",            tradition: "Shaivism"      },
  { id: "devi",             name: "Divine Mother (Devi)",  tradition: "Shaktism"      },
  { id: "rama",             name: "Lord Rama",             tradition: "Vaishnavism"   },
  { id: "ganesha",          name: "Lord Ganesha",          tradition: "Hindu"         },
  { id: "guru_nanak",       name: "Guru Nanak",            tradition: "Sikhism"       },
  { id: "buddha",           name: "Buddha",                tradition: "Buddhism"      },
  { id: "universal_divine", name: "Universal Divine",      tradition: "Non-specific"  },
];

const GOALS = [
  { id: "peace",    name: "Peace of Mind",    description: "Calm the mind and find inner stillness"       },
  { id: "guidance", name: "Moral Guidance",   description: "Navigate life's challenges with wisdom"        },
  { id: "study",    name: "Scriptural Study", description: "Deepen understanding of sacred texts"          },
  { id: "healing",  name: "Emotional Healing",description: "Find comfort during difficult times"           },
  { id: "purpose",  name: "Life Purpose",     description: "Discover your dharma and calling"              },
];

export default function OnboardingScreen() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    alignment: "",
    preferred_deity: "",
    primary_goal: "",
  });

  const handleNext = () => {
    if (step === 1 && !formData.alignment) {
      Alert.alert("Please select your spiritual path");
      return;
    }
    setStep((s) => Math.min(s + 1, 3));
  };

  const handleComplete = async () => {
    if (!formData.primary_goal) {
      Alert.alert("Please select your primary goal");
      return;
    }
    setLoading(true);
    try {
      const response = await axios.post(`${API}/users`, {
        alignment: formData.alignment,
        preferred_deity: formData.preferred_deity || null,
        primary_goal: formData.primary_goal,
        name: formData.name || null,
      });
      await AsyncStorage.setItem("pocketGuruUserId", response.data.id);
      router.replace("/chat");
    } catch (error) {
      if (error.response?.status === 429) {
        Alert.alert("Too many requests", "Please wait a moment and try again.");
      } else if (!error.response) {
        Alert.alert("Connection error", "Please check your internet connection.");
      } else {
        Alert.alert("Error", "Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  // ---- Progress bar ----
  const ProgressBar = () => (
    <View style={styles.progressContainer}>
      <View style={styles.progressTrack}>
        <View style={[styles.progressFill, { width: `${((step - 1) / 2) * 100}%` }]} />
      </View>
      <View style={styles.stepsRow}>
        {[1, 2, 3].map((s) => (
          <View
            key={s}
            style={[
              styles.stepDot,
              s === step   ? styles.stepDotActive   : {},
              s < step     ? styles.stepDotDone    : {},
            ]}
          >
            <Text style={styles.stepDotText}>{s}</Text>
          </View>
        ))}
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        <ProgressBar />

        {/* ---- STEP 1: Spiritual Path ---- */}
        {step === 1 && (
          <View style={styles.stepContainer}>
            <Text style={styles.stepTitle}>Choose Your Path</Text>
            <Text style={styles.stepSubtitle}>What is your primary spiritual inclination?</Text>
            {ALIGNMENTS.map((a) => (
              <TouchableOpacity
                key={a.id}
                style={[styles.card, formData.alignment === a.id && styles.cardSelected]}
                onPress={() => setFormData((p) => ({ ...p, alignment: a.id }))}
                activeOpacity={0.75}
              >
                <Text style={styles.cardEmoji}>{a.emoji}</Text>
                <View style={styles.cardText}>
                  <Text style={styles.cardTitle}>{a.name}</Text>
                  <Text style={styles.cardSubtitle}>{a.subtitle}</Text>
                  <Text style={styles.cardDesc}>{a.description}</Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {/* ---- STEP 2: Deity + Name ---- */}
        {step === 2 && (
          <View style={styles.stepContainer}>
            <Text style={styles.stepTitle}>Divine Connection</Text>
            <Text style={styles.stepSubtitle}>Which figure do you resonate with? (optional)</Text>

            <TextInput
              style={styles.textInput}
              placeholder="Your name (optional)"
              placeholderTextColor="#aaa"
              value={formData.name}
              onChangeText={(v) => setFormData((p) => ({ ...p, name: v }))}
            />

            <View style={styles.deityGrid}>
              {DEITIES.map((d) => (
                <TouchableOpacity
                  key={d.id}
                  style={[styles.deityCard, formData.preferred_deity === d.id && styles.cardSelected]}
                  onPress={() => setFormData((p) => ({ ...p, preferred_deity: d.id }))}
                  activeOpacity={0.75}
                >
                  <Text style={styles.deityName}>{d.name}</Text>
                  <Text style={styles.deityTradition}>{d.tradition}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}

        {/* ---- STEP 3: Primary Goal ---- */}
        {step === 3 && (
          <View style={styles.stepContainer}>
            <Text style={styles.stepTitle}>Your Intention</Text>
            <Text style={styles.stepSubtitle}>What brings you to seek spiritual guidance?</Text>
            {GOALS.map((g) => (
              <TouchableOpacity
                key={g.id}
                style={[styles.card, formData.primary_goal === g.id && styles.cardSelected]}
                onPress={() => setFormData((p) => ({ ...p, primary_goal: g.id }))}
                activeOpacity={0.75}
              >
                <View style={styles.cardText}>
                  <Text style={styles.cardTitle}>{g.name}</Text>
                  <Text style={styles.cardDesc}>{g.description}</Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {/* ---- Navigation buttons ---- */}
        <View style={styles.navRow}>
          {step > 1 ? (
            <TouchableOpacity style={styles.backBtn} onPress={() => setStep((s) => s - 1)}>
              <Text style={styles.backBtnText}>← Back</Text>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
              <Text style={styles.backBtnText}>Cancel</Text>
            </TouchableOpacity>
          )}

          {step < 3 ? (
            <TouchableOpacity style={styles.nextBtn} onPress={handleNext}>
              <Text style={styles.nextBtnText}>Next →</Text>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity
              style={[styles.nextBtn, loading && styles.btnDisabled]}
              onPress={handleComplete}
              disabled={loading}
            >
              {loading
                ? <ActivityIndicator color="#fff" />
                : <Text style={styles.nextBtnText}>Begin Journey ✨</Text>
              }
            </TouchableOpacity>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container:      { flex: 1, backgroundColor: "#F7FDF9" },
  scrollContent:  { padding: 20, paddingBottom: 40 },

  progressContainer: { marginBottom: 24 },
  progressTrack:  { height: 4, backgroundColor: "#E5E7EB", borderRadius: 2, marginBottom: 12 },
  progressFill:   { height: 4, backgroundColor: "#128C7E", borderRadius: 2 },
  stepsRow:       { flexDirection: "row", justifyContent: "space-between" },
  stepDot:        {
    width: 32, height: 32, borderRadius: 16,
    backgroundColor: "#E5E7EB",
    alignItems: "center", justifyContent: "center",
  },
  stepDotActive:  { backgroundColor: "#128C7E" },
  stepDotDone:    { backgroundColor: "#25D366" },
  stepDotText:    { fontSize: 13, fontWeight: "600", color: "#fff" },

  stepContainer:  { marginBottom: 8 },
  stepTitle:      { fontSize: 26, fontWeight: "700", color: "#075E54", marginBottom: 6 },
  stepSubtitle:   { fontSize: 14, color: "#6B7280", marginBottom: 20 },

  card: {
    flexDirection: "row",
    backgroundColor: "#fff",
    borderRadius: 14,
    padding: 16,
    marginBottom: 10,
    borderWidth: 2,
    borderColor: "#E5E7EB",
    alignItems: "flex-start",
  },
  cardSelected:   { borderColor: "#128C7E", backgroundColor: "#F0FDF4" },
  cardEmoji:      { fontSize: 28, marginRight: 14, marginTop: 2 },
  cardText:       { flex: 1 },
  cardTitle:      { fontSize: 16, fontWeight: "700", color: "#111827", marginBottom: 2 },
  cardSubtitle:   { fontSize: 13, color: "#128C7E", fontWeight: "600", marginBottom: 3 },
  cardDesc:       { fontSize: 13, color: "#6B7280", lineHeight: 18 },

  textInput: {
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#D1D5DB",
    borderRadius: 10,
    padding: 12,
    fontSize: 15,
    color: "#111827",
    marginBottom: 16,
  },

  deityGrid: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  deityCard: {
    width: "47%",
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 12,
    borderWidth: 2,
    borderColor: "#E5E7EB",
    marginBottom: 4,
  },
  deityName:      { fontSize: 14, fontWeight: "600", color: "#111827", marginBottom: 3 },
  deityTradition: { fontSize: 12, color: "#9CA3AF" },

  navRow:         { flexDirection: "row", justifyContent: "space-between", marginTop: 20 },
  backBtn: {
    paddingVertical: 13,
    paddingHorizontal: 20,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#D1D5DB",
  },
  backBtnText:    { fontSize: 15, color: "#6B7280", fontWeight: "600" },
  nextBtn: {
    flex: 1,
    marginLeft: 12,
    backgroundColor: "#128C7E",
    paddingVertical: 13,
    borderRadius: 10,
    alignItems: "center",
  },
  btnDisabled:    { backgroundColor: "#9CA3AF" },
  nextBtnText:    { fontSize: 15, color: "#fff", fontWeight: "700" },
});
