import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { BookOpen, Heart, HandHelping, Sparkles, ArrowLeft, ArrowRight, Loader2 } from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ALIGNMENTS = [
  {
    id: "jnana",
    name: "Jnana",
    subtitle: "Path of Knowledge",
    description: "Seek truth through wisdom, philosophy, and self-inquiry",
    icon: BookOpen,
    color: "#6366F1"
  },
  {
    id: "bhakti",
    name: "Bhakti",
    subtitle: "Path of Devotion",
    description: "Connect through love, surrender, and divine relationship",
    icon: Heart,
    color: "#EC4899"
  },
  {
    id: "karma",
    name: "Karma",
    subtitle: "Path of Action",
    description: "Find meaning through selfless service and righteous duty",
    icon: HandHelping,
    color: "#F59E0B"
  },
  {
    id: "universal",
    name: "Universal",
    subtitle: "All Paths",
    description: "Embrace wisdom from all spiritual traditions",
    icon: Sparkles,
    color: "#128C7E"
  }
];

const DEITIES = [
  { id: "krishna", name: "Lord Krishna", tradition: "Vaishnavism" },
  { id: "shiva", name: "Lord Shiva", tradition: "Shaivism" },
  { id: "devi", name: "Divine Mother (Devi)", tradition: "Shaktism" },
  { id: "rama", name: "Lord Rama", tradition: "Vaishnavism" },
  { id: "ganesha", name: "Lord Ganesha", tradition: "Hindu" },
  { id: "guru_nanak", name: "Guru Nanak", tradition: "Sikhism" },
  { id: "buddha", name: "Buddha", tradition: "Buddhism" },
  { id: "universal_divine", name: "Universal Divine", tradition: "Non-specific" }
];

const GOALS = [
  { id: "peace", name: "Peace of Mind", description: "Calm the mind and find inner stillness" },
  { id: "guidance", name: "Moral Guidance", description: "Navigate life's challenges with wisdom" },
  { id: "study", name: "Scriptural Study", description: "Deepen understanding of sacred texts" },
  { id: "healing", name: "Emotional Healing", description: "Find comfort during difficult times" },
  { id: "purpose", name: "Life Purpose", description: "Discover your dharma and calling" }
];

export default function OnboardingPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    alignment: "",
    preferred_deity: "",
    primary_goal: ""
  });

  const handleAlignmentSelect = (alignmentId) => {
    setFormData(prev => ({ ...prev, alignment: alignmentId }));
  };

  const handleDeitySelect = (deityId) => {
    setFormData(prev => ({ ...prev, preferred_deity: deityId }));
  };

  const handleGoalSelect = (goalId) => {
    setFormData(prev => ({ ...prev, primary_goal: goalId }));
  };

  const handleNext = () => {
    if (step === 1 && !formData.alignment) {
      toast.error("Please select your spiritual path");
      return;
    }
    if (step < 3) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleComplete = async () => {
    if (!formData.primary_goal) {
      toast.error("Please select your primary goal");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/users`, {
        alignment: formData.alignment,
        preferred_deity: formData.preferred_deity || null,
        primary_goal: formData.primary_goal,
        name: formData.name || null
      });
      
      localStorage.setItem("pocketGuruUserId", response.data.id);
      toast.success("Namaste! Welcome to your spiritual journey 🙏");
      navigate("/chat");
    } catch (error) {
      console.error("Error creating user:", error);
      toast.error("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="onboarding-container" data-testid="onboarding-page">
      {/* Progress indicator */}
      <div className="w-full max-w-md mb-8">
        <div className="flex justify-between items-center mb-2">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-colors ${
                s === step
                  ? "bg-[#128C7E] text-white"
                  : s < step
                  ? "bg-[#25D366] text-white"
                  : "bg-gray-200 text-gray-500"
              }`}
            >
              {s}
            </div>
          ))}
        </div>
        <div className="w-full bg-gray-200 h-1 rounded-full overflow-hidden">
          <div
            className="h-full bg-[#128C7E] transition-all duration-300"
            style={{ width: `${((step - 1) / 2) * 100}%` }}
          />
        </div>
      </div>

      {/* Step 1: Spiritual Path */}
      {step === 1 && (
        <div className="w-full max-w-lg fade-in" data-testid="step-1">
          <h2 className="font-heading text-3xl md:text-4xl font-semibold text-[#075E54] text-center mb-2">
            Choose Your Path
          </h2>
          <p className="text-gray-600 text-center mb-8 font-body">
            What is your primary spiritual inclination?
          </p>

          <div className="onboarding-card-grid">
            {ALIGNMENTS.map((alignment) => {
              const Icon = alignment.icon;
              const isSelected = formData.alignment === alignment.id;
              return (
                <button
                  key={alignment.id}
                  onClick={() => handleAlignmentSelect(alignment.id)}
                  className={`onboarding-card p-5 text-left rounded-xl border-2 ${
                    isSelected
                      ? "border-[#128C7E] bg-[#F0FDF4] ring-2 ring-[#128C7E]/20"
                      : "border-gray-100 bg-white hover:border-gray-200"
                  }`}
                  data-testid={`alignment-${alignment.id}`}
                >
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center mb-3"
                    style={{ backgroundColor: `${alignment.color}15` }}
                  >
                    <Icon className="w-5 h-5" style={{ color: alignment.color }} />
                  </div>
                  <h3 className="font-heading text-lg font-semibold text-gray-900">
                    {alignment.name}
                  </h3>
                  <p className="text-sm text-[#128C7E] font-medium mb-1">
                    {alignment.subtitle}
                  </p>
                  <p className="text-sm text-gray-500">{alignment.description}</p>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Step 2: Deity/Figure (Optional) */}
      {step === 2 && (
        <div className="w-full max-w-lg fade-in" data-testid="step-2">
          <h2 className="font-heading text-3xl md:text-4xl font-semibold text-[#075E54] text-center mb-2">
            Divine Connection
          </h2>
          <p className="text-gray-600 text-center mb-2 font-body">
            Which deities or figures do you resonate with most?
          </p>
          <p className="text-gray-400 text-sm text-center mb-8 font-body">
            (Optional - helps personalize your guidance)
          </p>

          {/* Optional name input */}
          <div className="mb-6">
            <Input
              placeholder="Your name (optional)"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="max-w-xs mx-auto"
              data-testid="name-input"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            {DEITIES.map((deity) => {
              const isSelected = formData.preferred_deity === deity.id;
              return (
                <button
                  key={deity.id}
                  onClick={() => handleDeitySelect(deity.id)}
                  className={`p-4 text-left rounded-xl border-2 transition-all ${
                    isSelected
                      ? "border-[#128C7E] bg-[#F0FDF4]"
                      : "border-gray-100 bg-white hover:border-gray-200"
                  }`}
                  data-testid={`deity-${deity.id}`}
                >
                  <h3 className="font-semibold text-gray-900 text-sm">{deity.name}</h3>
                  <p className="text-xs text-gray-500">{deity.tradition}</p>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Step 3: Primary Goal */}
      {step === 3 && (
        <div className="w-full max-w-lg fade-in" data-testid="step-3">
          <h2 className="font-heading text-3xl md:text-4xl font-semibold text-[#075E54] text-center mb-2">
            Your Intention
          </h2>
          <p className="text-gray-600 text-center mb-8 font-body">
            What brings you to seek spiritual guidance?
          </p>

          <div className="space-y-3">
            {GOALS.map((goal) => {
              const isSelected = formData.primary_goal === goal.id;
              return (
                <button
                  key={goal.id}
                  onClick={() => handleGoalSelect(goal.id)}
                  className={`w-full p-4 text-left rounded-xl border-2 transition-all ${
                    isSelected
                      ? "border-[#128C7E] bg-[#F0FDF4]"
                      : "border-gray-100 bg-white hover:border-gray-200"
                  }`}
                  data-testid={`goal-${goal.id}`}
                >
                  <h3 className="font-semibold text-gray-900">{goal.name}</h3>
                  <p className="text-sm text-gray-500">{goal.description}</p>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Navigation buttons */}
      <div className="flex gap-4 mt-8 w-full max-w-md justify-between">
        {step > 1 ? (
          <Button
            variant="outline"
            onClick={handleBack}
            className="flex items-center gap-2"
            data-testid="back-btn"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>
        ) : (
          <Button
            variant="ghost"
            onClick={() => navigate("/")}
            className="text-gray-500"
            data-testid="cancel-btn"
          >
            Cancel
          </Button>
        )}

        {step < 3 ? (
          <Button
            onClick={handleNext}
            className="bg-[#128C7E] hover:bg-[#075E54] flex items-center gap-2"
            data-testid="next-btn"
          >
            Next
            <ArrowRight className="w-4 h-4" />
          </Button>
        ) : (
          <Button
            onClick={handleComplete}
            disabled={loading}
            className="bg-[#128C7E] hover:bg-[#075E54] flex items-center gap-2"
            data-testid="complete-btn"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Setting up...
              </>
            ) : (
              <>
                Begin Journey
                <Sparkles className="w-4 h-4" />
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  );
}
