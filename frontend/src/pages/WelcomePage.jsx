import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-react";

export default function WelcomePage() {
  const navigate = useNavigate();
  const userId = localStorage.getItem("pocketGuruUserId");

  const handleGetStarted = () => {
    if (userId) {
      navigate("/chat");
    } else {
      navigate("/onboarding");
    }
  };

  return (
    <div className="welcome-container" data-testid="welcome-page">
      {/* Lotus Icon */}
      <div className="mb-8 slide-up" style={{ animationDelay: "0.1s" }}>
        <div className="w-24 h-24 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center lotus-glow">
          <svg
            viewBox="0 0 100 100"
            className="w-16 h-16"
            fill="currentColor"
          >
            <path d="M50 20 C50 20, 30 35, 30 55 C30 75, 50 85, 50 85 C50 85, 70 75, 70 55 C70 35, 50 20, 50 20" opacity="0.9" />
            <path d="M50 25 C40 30, 20 45, 20 60 C20 70, 35 80, 50 85" fill="none" stroke="currentColor" strokeWidth="2" opacity="0.6" />
            <path d="M50 25 C60 30, 80 45, 80 60 C80 70, 65 80, 50 85" fill="none" stroke="currentColor" strokeWidth="2" opacity="0.6" />
            <ellipse cx="50" cy="70" rx="8" ry="4" opacity="0.4" />
          </svg>
        </div>
      </div>

      {/* Title */}
      <h1 
        className="font-heading text-5xl md:text-6xl font-semibold mb-4 slide-up"
        style={{ animationDelay: "0.2s" }}
        data-testid="welcome-title"
      >
        Pocket Guru
      </h1>

      {/* Subtitle */}
      <p 
        className="text-lg md:text-xl text-white/90 mb-2 slide-up font-body"
        style={{ animationDelay: "0.3s" }}
      >
        Your Spiritual Companion
      </p>

      {/* Description */}
      <p 
        className="text-base text-white/70 max-w-md mb-12 slide-up font-body leading-relaxed"
        style={{ animationDelay: "0.4s" }}
      >
        Find peace, wisdom, and guidance through the timeless teachings 
        of Vedic literature and spiritual masters.
      </p>

      {/* CTA Button */}
      <Button
        onClick={handleGetStarted}
        size="lg"
        className="bg-white text-[#075E54] hover:bg-white/90 font-semibold px-8 py-6 text-lg rounded-full slide-up btn-press"
        style={{ animationDelay: "0.5s" }}
        data-testid="get-started-btn"
      >
        <Sparkles className="w-5 h-5 mr-2" />
        {userId ? "Continue Your Journey" : "Begin Your Journey"}
      </Button>

      {/* Guru name */}
      <p 
        className="mt-8 text-sm text-white/60 slide-up font-body"
        style={{ animationDelay: "0.6s" }}
      >
        Meet Prana — Your AI Spiritual Guide
      </p>

      {/* Admin link */}
      <button
        onClick={() => navigate("/admin")}
        className="mt-12 text-xs text-white/40 hover:text-white/60 transition-colors"
        data-testid="admin-link"
      >
        Admin Dashboard
      </button>
    </div>
  );
}
