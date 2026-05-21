import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Sparkles, Trophy, RotateCcw } from "lucide-react";
import type { FeedbackResponse } from "@/lib/api";

interface Props {
  data: FeedbackResponse;
  onRestart: () => void;
}

function scoreColor(score: number) {
  if (score >= 7) return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
  if (score >= 5) return "bg-amber-500/15 text-amber-400 border-amber-500/30";
  return "bg-rose-500/15 text-rose-400 border-rose-500/30";
}

export function FeedbackScreen({ data, onRestart }: Props) {
  return (
    <div className="min-h-screen animate-in fade-in duration-500">
      <header className="border-b border-border/60 backdrop-blur bg-background/70 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-primary/15 flex items-center justify-center">
            <Trophy className="h-4 w-4 text-primary" />
          </div>
          <h1 className="font-semibold tracking-tight">Your Interview Results</h1>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        <Card>
          <CardContent className="py-5 flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="text-xs uppercase tracking-wider text-muted-foreground">Total turns</div>
              <div className="text-2xl font-bold">{data.total_turns}</div>
            </div>
            <div className="text-right">
              <div className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Average score</div>
              <Badge className={`text-base px-3 py-1 border ${scoreColor(data.average_score)}`}>
                {data.average_score.toFixed(1)} / 10
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary" /> Coaching Feedback
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="markdown-body max-h-[55vh] overflow-y-auto pr-2">
              <ReactMarkdown>{data.feedback_markdown}</ReactMarkdown>
            </div>
          </CardContent>
        </Card>

        {data.rewritten_answers.length > 0 && (
          <section className="space-y-3">
            <h2 className="text-lg font-semibold tracking-tight">Your Weakest Answers — Rewritten</h2>
            <div className="space-y-4">
              {data.rewritten_answers.map((r, i) => (
                <RewrittenCard key={i} index={i} item={r} />
              ))}
            </div>
          </section>
        )}

        <div className="pt-2 pb-10 flex justify-center">
          <Button size="lg" onClick={onRestart} className="font-semibold">
            <RotateCcw className="h-4 w-4 mr-2" /> Start New Interview
          </Button>
        </div>
      </main>
    </div>
  );
}

function RewrittenCard({ index, item }: { index: number; item: { original: string; improved: string; what_changed: string[] } }) {
  const [tab, setTab] = useState<"improved" | "original">("improved");
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Answer #{index + 1}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Tabs value={tab} onValueChange={(v) => setTab(v as "improved" | "original")}>
          <TabsList>
            <TabsTrigger value="original">Original</TabsTrigger>
            <TabsTrigger value="improved">Improved</TabsTrigger>
          </TabsList>
          <TabsContent value="original" className="mt-3">
            <div className="rounded-lg bg-muted/50 p-3 text-sm whitespace-pre-wrap leading-relaxed">
              {item.original}
            </div>
          </TabsContent>
          <TabsContent value="improved" className="mt-3">
            <div className="rounded-lg bg-primary/5 border border-primary/20 p-3 text-sm whitespace-pre-wrap leading-relaxed">
              {item.improved}
            </div>
          </TabsContent>
        </Tabs>
        {item.what_changed?.length > 0 && (
          <div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground mb-2">What changed</div>
            <div className="flex flex-wrap gap-2">
              {item.what_changed.map((c, i) => (
                <Badge key={i} variant="secondary" className="font-normal">{c}</Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
