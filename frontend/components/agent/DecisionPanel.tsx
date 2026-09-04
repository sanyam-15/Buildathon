"use client";

import { motion } from "framer-motion";
import { BrainCircuit, Target, HelpCircle, ArrowRight } from "lucide-react";

export function DecisionPanel({ strategyData }: { strategyData: any }) {
  if (!strategyData) {
    return (
      <div className="glass-panel p-6 rounded-xl flex flex-col items-center justify-center text-center min-h-[300px]">
        <BrainCircuit className="w-12 h-12 text-slate-700 mb-4 animate-pulse" />
        <h3 className="text-lg font-medium text-slate-300">Awaiting Strategy</h3>
        <p className="text-sm text-slate-500 max-w-[250px] mt-2">
          The Strategy Agent is analyzing the case to determine the optimal recovery path.
        </p>
      </div>
    );
  }

  const alts = strategyData.alternatives_considered || [];
  // Sort by probability descending
  const sortedAlts = [...alts].sort((a, b) => b.recovery_probability - a.recovery_probability);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel p-6 rounded-xl flex flex-col"
    >
      <div className="flex items-center gap-2 mb-6">
        <BrainCircuit className="w-5 h-5 text-[#8B5CF6]" />
        <h3 className="text-sm font-medium tracking-widest text-muted-foreground uppercase">AI Recovery Decision</h3>
      </div>

      <div className="mb-6">
        <div className="text-xs text-slate-500 uppercase tracking-widest mb-2">Selected Strategy</div>
        <div className="flex items-center gap-3">
          <div className="px-3 py-1.5 rounded-md bg-[#8B5CF6]/10 text-[#8B5CF6] border border-[#8B5CF6]/20 font-medium text-sm">
            {strategyData.primary_action.replace(/_/g, ' ')}
          </div>
          {strategyData.communication_channel !== "NONE" && (
            <>
              <ArrowRight className="w-4 h-4 text-slate-600" />
              <div className="px-3 py-1.5 rounded-md bg-[#2B84EA]/10 text-[#2B84EA] border border-[#2B84EA]/20 font-medium text-sm">
                VIA {strategyData.communication_channel}
              </div>
            </>
          )}
        </div>
      </div>

      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <div className="text-xs text-slate-500 uppercase tracking-widest">Expected Recovery</div>
          <div className="text-sm font-bold text-emerald-400">
            {(strategyData.expected_recovery_probability * 100).toFixed(0)}%
          </div>
        </div>
        <div className="h-2 w-full bg-[#1E293B] rounded-full overflow-hidden">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${strategyData.expected_recovery_probability * 100}%` }}
            transition={{ duration: 1, delay: 0.2 }}
            className="h-full bg-emerald-500"
          />
        </div>
      </div>

      <div className="mb-6">
        <div className="flex items-center gap-2 text-xs text-slate-500 uppercase tracking-widest mb-2">
          <HelpCircle className="w-4 h-4" /> Why this strategy?
        </div>
        <p className="text-sm text-slate-300 leading-relaxed border-l-2 border-[#8B5CF6]/50 pl-4 py-1">
          {strategyData.reason}
        </p>
      </div>

      <div>
        <div className="text-xs text-slate-500 uppercase tracking-widest mb-4">Alternatives Considered</div>
        <div className="flex flex-col gap-4">
          {sortedAlts.map((alt: any, i: number) => (
            <div key={i} className="flex flex-col gap-1.5">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-300 font-medium">{alt.action.replace(/_/g, ' ')}</span>
                <span className="text-slate-400 font-mono">{(alt.recovery_probability * 100).toFixed(0)}%</span>
              </div>
              <div className="h-1.5 w-full bg-[#1E293B] rounded-full overflow-hidden">
                <div 
                  className={`h-full ${alt.action === strategyData.primary_action ? 'bg-[#8B5CF6]' : 'bg-slate-600'}`}
                  style={{ width: `${alt.recovery_probability * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

    </motion.div>
  );
}
