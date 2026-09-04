"use client";

import { useEffect, useState } from "react";
import { fetchCases } from "@/lib/api";
import { ScrollArea } from "@/components/ui/scroll-area";
import { CheckCircle2, Loader2, AlertCircle, XCircle } from "lucide-react";
import { motion } from "framer-motion";

export function RecoveryQueue({ onSelectCase }: { onSelectCase: (id: string) => void }) {
  const [cases, setCases] = useState<any[]>([]);

  useEffect(() => {
    const loadCases = async () => {
      try {
        const data = await fetchCases();
        setCases(data);
      } catch (err) {
        console.error(err);
      }
    };
    
    loadCases();
    const interval = setInterval(loadCases, 3000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'RECOVERED': return <CheckCircle2 className="w-4 h-4 text-[#22C55E]" />;
      case 'FAILED': return <XCircle className="w-4 h-4 text-[#EF4444]" />;
      case 'ESCALATED': return <AlertCircle className="w-4 h-4 text-[#F59E0B]" />;
      case 'CREATED': return <div className="w-2 h-2 rounded-full bg-slate-600 ml-1" />;
      default: return <Loader2 className="w-4 h-4 text-[#2B84EA] animate-spin" />;
    }
  };

  return (
    <div className="glass-panel p-6 rounded-xl flex flex-col h-[300px]">
      <h3 className="text-sm font-medium tracking-widest text-[#94A3B8] uppercase mb-4">Live Recovery Queue</h3>
      <ScrollArea className="flex-1 min-h-0 -mx-2 px-2">
        {cases.length === 0 ? (
          <div className="text-slate-500 text-sm italic">No cases yet.</div>
        ) : (
          <div className="space-y-2">
            {cases.map((c, i) => (
              <motion.button
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                key={c.id}
                onClick={() => onSelectCase(c.id)}
                className="w-full text-left p-3 rounded-lg hover:bg-white/[0.03] transition-colors flex items-center justify-between group border border-transparent hover:border-[#1E293B]"
              >
                <div className="flex items-center gap-3">
                  {getStatusIcon(c.status)}
                  <div>
                    <div className="text-sm font-medium text-slate-200 group-hover:text-white transition-colors">
                      {c.event_id}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <span
                        className={
                          c.segment === "B2B" || c.category === "OVERDUE_RECEIVABLE"
                            ? "text-[#F59E0B]"
                            : "text-[#2B84EA]"
                        }
                      >
                        {c.segment || (c.category === "OVERDUE_RECEIVABLE" ? "B2B" : "B2C")}
                      </span>
                      <span>·</span>
                      <span>{c.category?.replace(/_/g, " ") || "Unknown"}</span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-mono text-slate-300">₹{c.amount_at_risk.toLocaleString()}</div>
                  <div className={`text-xs ${c.status === 'RECOVERED' ? 'text-[#22C55E]' : 'text-slate-500'}`}>
                    {c.status}
                  </div>
                </div>
              </motion.button>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
