"use client";

import { useEffect, useRef, useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Terminal, Shield, Zap, Search, Brain, Eye, CreditCard, MessageCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export function LiveConsole({ events = [] }: { events: any[] }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [filter, setFilter] = useState("ALL");

  useEffect(() => {
    // Auto-scroll to bottom
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  const getIconForAgent = (agent: string, type: string) => {
    if (type.includes('policy')) return <Shield className="w-3.5 h-3.5 text-[#F59E0B]" />;
    if (type.includes('tool') || agent === 'execution_agent') return <Zap className="w-3.5 h-3.5 text-[#2B84EA]" />;
    if (type.includes('payment') || agent?.includes('payment')) return <CreditCard className="w-3.5 h-3.5 text-[#22C55E]" />;
    if (agent?.includes('strategist')) return <Brain className="w-3.5 h-3.5 text-[#8B5CF6]" />;
    if (agent === 'monitor_agent') return <Eye className="w-3.5 h-3.5 text-[#2B84EA]" />;
    if (agent?.includes('classifier') || agent?.includes('specialist')) return <Search className="w-3.5 h-3.5 text-[#F59E0B]" />;
    return <Terminal className="w-3.5 h-3.5 text-[#94A3B8]" />;
  };

  const getColorForType = (type: string) => {
    if (type === 'policy_blocked' || type === 'case_failed') return 'text-[#EF4444]';
    if (type === 'policy_approved' || type === 'payment_verified' || type === 'revenue_recovered') return 'text-[#22C55E]';
    if (type === 'decision_made') return 'text-[#8B5CF6]';
    if (type === 'tool_started' || type === 'tool_completed') return 'text-[#2B84EA]';
    if (type === 'agent_started') return 'text-[#2B84EA]';
    return 'text-[#94A3B8]';
  };

  const formatTime = (isoString: string) => {
    const d = new Date(isoString);
    return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`;
  };

  const filteredEvents = events.filter(ev => {
    if (filter === 'ALL') return true;
    if (filter === 'AGENTS') return ev.event_type === 'agent_started' || ev.event_type === 'agent_completed';
    if (filter === 'TOOLS') return ev.event_type === 'tool_started' || ev.event_type === 'tool_completed' || ev.event_type === 'execution_started';
    if (filter === 'DECISIONS') return ev.event_type === 'decision_made' || ev.event_type === 'policy_approved' || ev.event_type === 'policy_blocked';
    return true;
  });

  return (
    <div className="glass-panel rounded-xl flex flex-col h-[400px]">
      <div className="flex items-center justify-between px-5 py-3 border-b border-[#1E293B]">
        <div className="flex items-center gap-2 text-xs font-medium tracking-widest text-[#94A3B8] uppercase">
          <Terminal className="w-4 h-4" />
          Live Orchestration Log
        </div>
        <div className="flex gap-1">
          {["ALL", "AGENTS", "TOOLS", "DECISIONS"].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`text-[10px] px-2.5 py-1 rounded-md tracking-wider transition-colors ${
                filter === f
                  ? 'bg-[#2B84EA]/10 text-[#2B84EA] font-medium'
                  : 'text-[#94A3B8] hover:text-[#F8FAFC] hover:bg-white/5'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>
      <ScrollArea className="flex-1 min-h-0 p-5 font-mono text-sm" ref={scrollRef}>
        <AnimatePresence initial={false}>
          {filteredEvents.length === 0 && (
            <div className="text-[#94A3B8] italic text-xs">Waiting for events...</div>
          )}
          {filteredEvents.map((ev, i) => (
            <motion.div
              key={ev.event_id || i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="mb-3 grid grid-cols-[72px_1fr] gap-4 group py-1.5 px-2 rounded-md hover:bg-white/[0.02] transition-colors"
            >
              <div className="text-[#94A3B8] text-[11px] font-mono mt-0.5 group-hover:text-slate-300 transition-colors tabular-nums">
                {formatTime(ev.timestamp)}
              </div>
              <div>
                <div className="flex items-center gap-2 mb-0.5">
                  {getIconForAgent(ev.agent, ev.event_type)}
                  <span className={`text-[11px] font-semibold tracking-wider uppercase ${getColorForType(ev.event_type)}`}>
                    {ev.event_type.replace(/_/g, ' ')}
                  </span>
                  <span className="text-[11px] text-slate-600 uppercase tracking-wider">
                    {ev.agent?.replace(/_/g, ' ')}
                  </span>
                </div>
                <div className="text-[#94A3B8] text-[13px] leading-relaxed">
                  {ev.message}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </ScrollArea>
    </div>
  );
}
