import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Mic, MicOff, Send, Loader2, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { api, getApiError, type AnswerResponse, type FeedbackResponse } from "@/lib/api";

export interface TranscriptItem {
  role: "interviewer" | "candidate";
  text: string;
}

interface Props {
  sessionId: string;
  initialTranscript: TranscriptItem[];
  initialTurn: number;
  onDone: (feedback: FeedbackResponse) => void;
}

// Minimal types for Web Speech API
interface SpeechRecognitionLike {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  onresult: ((e: any) => void) | null;
  onerror: ((e: any) => void) | null;
  onend: (() => void) | null;
}

export function InterviewScreen({ sessionId, initialTranscript, initialTurn, onDone }: Props) {
  const [transcript, setTranscript] = useState<TranscriptItem[]>(initialTranscript);
  const [currentTurn, setCurrentTurn] = useState(initialTurn);
  const [answer, setAnswer] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [finalizing, setFinalizing] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);
  const taRef = useRef<HTMLTextAreaElement>(null);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const baseTextRef = useRef("");

  const SpeechRecognitionCtor =
    typeof window !== "undefined"
      ? (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      : null;
  const speechSupported = !!SpeechRecognitionCtor;

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [transcript, isLoading]);

  useEffect(() => {
    if (taRef.current) {
      taRef.current.style.height = "auto";
      taRef.current.style.height = Math.min(taRef.current.scrollHeight, 200) + "px";
    }
  }, [answer]);

  const stopRecording = () => {
    recognitionRef.current?.stop();
  };

  const startRecording = () => {
    if (!SpeechRecognitionCtor) return;
    const rec: SpeechRecognitionLike = new SpeechRecognitionCtor();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = "en-US";
    baseTextRef.current = answer ? answer.trim() + " " : "";

    rec.onresult = (e: any) => {
      let interim = "";
      let finalChunk = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const t = e.results[i][0].transcript;
        if (e.results[i].isFinal) finalChunk += t + " ";
        else interim += t;
      }
      if (finalChunk) baseTextRef.current += finalChunk;
      setAnswer((baseTextRef.current + interim).replace(/\s+/g, " ").trimStart());
    };
    rec.onerror = (e: any) => {
      if (e?.error && e.error !== "aborted" && e.error !== "no-speech") {
        toast.error(`Mic error: ${e.error}`);
      }
    };
    rec.onend = () => {
      setIsRecording(false);
      recognitionRef.current = null;
    };

    recognitionRef.current = rec;
    try {
      rec.start();
      setIsRecording(true);
    } catch {
      setIsRecording(false);
    }
  };

  const toggleMic = () => {
    if (!speechSupported) return;
    if (isRecording) stopRecording();
    else startRecording();
  };

  const handleSend = async () => {
    const text = answer.trim();
    if (!text) {
      toast.error("Please type or speak your answer");
      return;
    }
    if (isRecording) stopRecording();

    setTranscript((t) => [...t, { role: "candidate", text }]);
    setAnswer("");
    setIsLoading(true);
    try {
      const { data } = await api.post<AnswerResponse>("/answer", {
        session_id: sessionId,
        answer: text,
      });
      if (data.done) {
        setFinalizing(true);
        const { data: fb } = await api.get<FeedbackResponse>("/feedback", {
          params: { session_id: sessionId },
        });
        onDone(fb);
        return;
      }
      setTranscript((t) => [...t, { role: "interviewer", text: data.question }]);
      setCurrentTurn(data.turn);
    } catch (err) {
      toast.error(getApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const totalTurns = 6;

  return (
    <div className="min-h-screen flex flex-col animate-in fade-in duration-300">
      <header className="border-b border-border/60 backdrop-blur bg-background/70 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary/15 flex items-center justify-center">
              <Sparkles className="h-4 w-4 text-primary" />
            </div>
            <h1 className="font-semibold tracking-tight">AI Mock Interview Coach</h1>
          </div>
          <Badge variant="secondary" className="font-mono">
            Turn {currentTurn} / {totalTurns}
          </Badge>
        </div>
      </header>

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-6 flex flex-col gap-4 min-h-0">
        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto rounded-xl border border-border/60 bg-card/40 p-4 space-y-4 min-h-[50vh]"
        >
          {transcript.map((m, i) => (
            <div
              key={i}
              className={`flex ${m.role === "candidate" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                  m.role === "candidate"
                    ? "bg-primary text-primary-foreground rounded-br-sm"
                    : "bg-muted text-foreground rounded-bl-sm"
                }`}
              >
                {m.text}
              </div>
            </div>
          ))}
          {(isLoading || finalizing) && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-2xl rounded-bl-sm px-4 py-3 text-sm flex items-center gap-2 text-muted-foreground">
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                {finalizing ? "Preparing your feedback…" : "Thinking…"}
              </div>
            </div>
          )}
        </div>

        <div className="rounded-xl border border-border/60 bg-card/60 p-3">
          <div className="flex flex-col sm:flex-row gap-2 items-stretch sm:items-end">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    type="button"
                    size="icon"
                    variant={isRecording ? "destructive" : "secondary"}
                    onClick={toggleMic}
                    disabled={!speechSupported || isLoading || finalizing}
                    className={`h-11 w-11 rounded-full shrink-0 ${isRecording ? "mic-recording" : ""}`}
                    aria-label={isRecording ? "Stop recording" : "Start recording"}
                  >
                    {isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
                  </Button>
                </TooltipTrigger>
                {!speechSupported && (
                  <TooltipContent>Mic not supported in this browser</TooltipContent>
                )}
              </Tooltip>
            </TooltipProvider>

            <Textarea
              ref={taRef}
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder={isRecording ? "Listening…" : "Type your answer or use the mic…"}
              rows={2}
              className="flex-1 resize-none min-h-[44px] max-h-[200px]"
              disabled={isLoading || finalizing}
            />

            <Button
              type="button"
              onClick={handleSend}
              disabled={isLoading || finalizing}
              className="h-11 px-5 font-semibold shrink-0"
            >
              {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : (
                <><Send className="h-4 w-4 mr-2" /> Send</>
              )}
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}
