"use client";

import { useState } from "react";
import { RevenueMetrics } from "@/components/dashboard/RevenueMetrics";
import { AgentGraph } from "@/components/agent/AgentGraph";
import { LiveConsole } from "@/components/agent/LiveConsole";
import { DecisionPanel } from "@/components/agent/DecisionPanel";
import { CaseDetails } from "@/components/recovery/CaseDetails";
import { TriggerEventForm } from "@/components/recovery/TriggerEventForm";
import { RecoveryQueue } from "@/components/recovery/RecoveryQueue";
import { useRecoveryStream } from "@/hooks/useRecoveryStream";
import { Activity } from "lucide-react";

export default function Home() {
  const [activeCaseId, setActiveCaseId] = useState<string | null>(null);
  const { events, isActive } = useRecoveryStream(activeCaseId);

  // Extract strategy decision from events for the decision panel
  const decisionEvent = [...events].reverse().find(e => e.event_type === 'decision_made');
  const strategyData = decisionEvent?.metadata;

  return (
    <div className="min-h-screen bg-background text-slate-50 p-4 md:p-8 overflow-x-hidden selection:bg-cyan-500/30">
      
      {/* Header */}
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tighter bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
            Razorpay Relay
          </h1>
          <p className="text-muted-foreground mt-1 tracking-wide font-light">
            AI Revenue Recovery Command Center — B2C Payments & B2B Receivables
          </p>
        </div>
        
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#2B84EA]/10 border border-[#2B84EA]/20">
          <div className="w-2 h-2 rounded-full bg-[#2B84EA] animate-pulse" />
          <span className="text-xs font-medium text-[#2B84EA] tracking-widest uppercase">System Live</span>
        </div>
      </header>

      {/* Top Metrics */}
      <div className="mb-8">
        <RevenueMetrics />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">
        
        {/* Left Column - Trigger & Queue */}
        <div className="lg:col-span-3 space-y-6">
          <TriggerEventForm onCaseCreated={(id) => setActiveCaseId(id)} />
          <RecoveryQueue onSelectCase={(id) => setActiveCaseId(id)} />
        </div>

        {/* Middle Column - Graph & Decision */}
        <div className="lg:col-span-6 space-y-6">
          <div className="relative">
            {isActive && (
              <div className="absolute top-4 right-4 z-20 flex items-center gap-2 bg-[#0B1220]/90 px-3 py-1.5 rounded-full border border-[#1E293B] backdrop-blur-sm">
                <Activity className="w-4 h-4 text-[#22C55E]" />
                <span className="text-xs text-[#22C55E] font-medium tracking-wider">AGENT PROCESSING</span>
              </div>
            )}
            <AgentGraph events={events} />
          </div>
          <DecisionPanel strategyData={strategyData} />
        </div>

        {/* Right Column - Case Details */}
        <div className="lg:col-span-3 h-full">
          <CaseDetails caseId={activeCaseId} />
        </div>

      </div>

      {/* Bottom Console */}
      <div className="w-full mt-6">
        <LiveConsole events={events} />
      </div>

    </div>
  );
}
