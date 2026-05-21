import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { SetupScreen } from "@/components/interview/SetupScreen";
import { InterviewScreen, type TranscriptItem } from "@/components/interview/InterviewScreen";
import { FeedbackScreen } from "@/components/interview/FeedbackScreen";
import type { FeedbackResponse } from "@/lib/api";

export const Route = createFileRoute("/")({
  component: Index,
});

type Screen = "setup" | "interview" | "feedback";

function Index() {
  const [screen, setScreen] = useState<Screen>("setup");
  const [sessionId, setSessionId] = useState("");
  const [initialTranscript, setInitialTranscript] = useState<TranscriptItem[]>([]);
  const [initialTurn, setInitialTurn] = useState(1);
  const [feedback, setFeedback] = useState<FeedbackResponse | null>(null);

  if (screen === "interview") {
    return (
      <InterviewScreen
        sessionId={sessionId}
        initialTranscript={initialTranscript}
        initialTurn={initialTurn}
        onDone={(fb) => {
          setFeedback(fb);
          setScreen("feedback");
        }}
      />
    );
  }

  if (screen === "feedback" && feedback) {
    return (
      <FeedbackScreen
        data={feedback}
        onRestart={() => {
          setSessionId("");
          setInitialTranscript([]);
          setInitialTurn(1);
          setFeedback(null);
          setScreen("setup");
        }}
      />
    );
  }

  return (
    <SetupScreen
      onStart={(data) => {
        setSessionId(data.session_id);
        setInitialTranscript([{ role: "interviewer", text: data.question }]);
        setInitialTurn(data.turn);
        setScreen("interview");
      }}
    />
  );
}
