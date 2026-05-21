import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { api, getApiError, type StartResponse } from "@/lib/api";
import { Sparkles, Loader2, Check } from "lucide-react";

interface Props {
  onStart: (data: StartResponse) => void;
}

const FOCUS_OPTIONS = [
  { id: "technical", label: "Technical" },
  { id: "behavioral", label: "Behavioral" },
  { id: "hr", label: "HR" },
  { id: "system_design", label: "System Design" },
  { id: "dsa", label: "DSA" },
  { id: "group_discussion", label: "Group Discussion" },
  { id: "managerial", label: "Managerial" },
  { id: "case_study", label: "Case Study" },
];

export function SetupScreen({ onStart }: Props) {
  const [role, setRole] = useState("");
  const [background, setBackground] = useState("");
  const [selectedFocus, setSelectedFocus] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const toggleFocus = (id: string) => {
    setSelectedFocus((prev) =>
      prev.includes(id) ? prev.filter((f) => f !== id) : [...prev, id]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!role.trim()) {
      toast.error("Please enter the role you're applying for");
      return;
    }
    if (selectedFocus.length === 0) {
      toast.error("Please select at least one interview focus area");
      return;
    }

    const focusLabel = selectedFocus
      .map((id) => FOCUS_OPTIONS.find((o) => o.id === id)?.label ?? id)
      .join(", ");

    setLoading(true);
    try {
      const { data } = await api.post<StartResponse>("/start", {
        role: role.trim(),
        background: background.trim() || "Not specified",
        focus: focusLabel,
      });
      onStart(data);
    } catch (err) {
      toast.error(getApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-10 animate-in fade-in duration-500">
      <Card className="w-full max-w-xl border-border/60 shadow-2xl shadow-primary/5">
        <CardHeader className="text-center space-y-3">
          <div className="mx-auto h-12 w-12 rounded-2xl bg-primary/15 flex items-center justify-center">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>
          <CardTitle className="text-3xl font-bold tracking-tight">AI Mock Interview Coach</CardTitle>
          <CardDescription>Practice with a personalized AI interviewer and get detailed feedback.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">

            {/* Role */}
            <div className="space-y-2">
              <Label htmlFor="role">
                Role you're applying for <span className="text-destructive">*</span>
              </Label>
              <Input
                id="role"
                placeholder="e.g. AI Intern, Software Engineer, Data Analyst"
                value={role}
                onChange={(e) => setRole(e.target.value)}
              />
            </div>

            {/* Background — optional */}
            <div className="space-y-2">
              <Label htmlFor="background">
                Your background{" "}
                <span className="text-muted-foreground text-xs font-normal">(optional)</span>
              </Label>
              <Textarea
                id="background"
                placeholder="e.g. 2nd year B.Tech AIML student, built 3 ML projects"
                rows={2}
                value={background}
                onChange={(e) => setBackground(e.target.value)}
              />
            </div>

            {/* Focus area — chip multi-select */}
            <div className="space-y-2">
              <Label>
                Interview focus <span className="text-destructive">*</span>
                <span className="text-muted-foreground text-xs font-normal ml-1">(pick one or more)</span>
              </Label>
              <div className="flex flex-wrap gap-2">
                {FOCUS_OPTIONS.map((opt) => {
                  const active = selectedFocus.includes(opt.id);
                  return (
                    <button
                      key={opt.id}
                      type="button"
                      onClick={() => toggleFocus(opt.id)}
                      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border transition-all duration-150
                        ${active
                          ? "bg-primary text-primary-foreground border-primary shadow-sm"
                          : "bg-muted/40 text-muted-foreground border-border/60 hover:border-primary/50 hover:text-foreground"
                        }`}
                    >
                      {active && <Check className="h-3.5 w-3.5" />}
                      {opt.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <Button
              type="submit"
              size="lg"
              className="w-full text-base font-semibold"
              disabled={loading}
            >
              {loading
                ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" /> Starting…</>
                : "Start Interview"
              }
            </Button>

          </form>
        </CardContent>
      </Card>
    </div>
  );
}
