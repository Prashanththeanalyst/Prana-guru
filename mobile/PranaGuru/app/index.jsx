import { useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Animated,
} from "react-native";
import { useRouter } from "expo-router";
import AsyncStorage from "@react-native-async-storage/async-storage";

export default function WelcomeScreen() {
  const router = useRouter();
  const fadeAnim  = new Animated.Value(0);
  const slideAnim = new Animated.Value(30);

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim,  { toValue: 1, duration: 800, useNativeDriver: true }),
      Animated.timing(slideAnim, { toValue: 0, duration: 800, useNativeDriver: true }),
    ]).start();
  }, []);

  const handleGetStarted = async () => {
    try {
      const userId = await AsyncStorage.getItem("pocketGuruUserId");
      if (userId) {
        router.replace("/chat");
      } else {
        router.push("/onboarding");
      }
    } catch {
      router.push("/onboarding");
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Lotus symbol */}
      <Animated.View
        style={[styles.logoContainer, { opacity: fadeAnim, transform: [{ translateY: slideAnim }] }]}
      >
        <View style={styles.logoCircle}>
          <Text style={styles.logoEmoji}>🪷</Text>
        </View>
      </Animated.View>

      {/* Title */}
      <Animated.Text
        style={[styles.title, { opacity: fadeAnim, transform: [{ translateY: slideAnim }] }]}
      >
        Pocket Guru
      </Animated.Text>

      {/* Subtitle */}
      <Animated.Text
        style={[styles.subtitle, { opacity: fadeAnim, transform: [{ translateY: slideAnim }] }]}
      >
        Your Spiritual Companion
      </Animated.Text>

      {/* Description */}
      <Animated.Text
        style={[styles.description, { opacity: fadeAnim, transform: [{ translateY: slideAnim }] }]}
      >
        Find peace, wisdom, and guidance through the timeless teachings of
        Vedic literature and spiritual masters.
      </Animated.Text>

      {/* CTA */}
      <Animated.View style={{ opacity: fadeAnim, transform: [{ translateY: slideAnim }] }}>
        <TouchableOpacity style={styles.button} onPress={handleGetStarted} activeOpacity={0.85}>
          <Text style={styles.buttonText}>✨  Begin Your Journey</Text>
        </TouchableOpacity>
      </Animated.View>

      <Text style={styles.guruLabel}>Meet Prana — Your AI Spiritual Guide</Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#075E54",
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
  },
  logoContainer: { marginBottom: 24 },
  logoCircle: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: "rgba(255,255,255,0.12)",
    alignItems: "center",
    justifyContent: "center",
  },
  logoEmoji:   { fontSize: 48 },
  title:       { fontSize: 40, fontWeight: "700", color: "#fff", marginBottom: 8, letterSpacing: 0.5 },
  subtitle:    { fontSize: 18, color: "rgba(255,255,255,0.9)", marginBottom: 12 },
  description: {
    fontSize: 15,
    color: "rgba(255,255,255,0.7)",
    textAlign: "center",
    lineHeight: 22,
    marginBottom: 40,
    maxWidth: 300,
  },
  button: {
    backgroundColor: "#fff",
    paddingHorizontal: 36,
    paddingVertical: 16,
    borderRadius: 50,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
  buttonText: { color: "#075E54", fontSize: 17, fontWeight: "700" },
  guruLabel:  { marginTop: 32, fontSize: 13, color: "rgba(255,255,255,0.5)" },
});
