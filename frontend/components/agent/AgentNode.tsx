import { Handle, Position } from '@xyflow/react';
import { motion } from 'framer-motion';
import { Check, Loader2, AlertTriangle } from 'lucide-react';
import { twMerge } from 'tailwind-merge';

export function AgentNode({ data, isConnectable }: any) {
  const { label, icon, status, isAI, isSubNode, segment } = data;

  const statusStyles = {
    WAITING: "border-[#1E293B] bg-[#0B1220] text-slate-400",
    ACTIVE: "border-[#2B84EA] bg-[#2B84EA]/10 text-white shadow-sm",
    COMPLETED: "border-[#22C55E] bg-[#22C55E]/10 text-white",
    BLOCKED: "border-amber-500 bg-amber-500/10 text-white",
    FAILED: "border-red-500 bg-red-500/10 text-white",
  };

  const aiStyles = "border-[#8B5CF6] bg-[#8B5CF6]/10 text-white";
  const b2bActiveStyles = "border-[#F59E0B] bg-[#F59E0B]/10 text-white shadow-sm";
  const b2bCompletedStyles = "border-[#22C55E] bg-[#22C55E]/10 text-white";

  let appliedStyle = statusStyles[status as keyof typeof statusStyles] || statusStyles.WAITING;
  if (isAI && status !== 'WAITING') {
    appliedStyle = aiStyles;
  }
  if (segment === 'B2B' && status === 'ACTIVE') {
    appliedStyle = b2bActiveStyles;
  }
  if (segment === 'B2B' && status === 'COMPLETED') {
    appliedStyle = b2bCompletedStyles;
  }

  return (
    <div className={twMerge(
      "relative px-4 py-3 rounded-lg border flex items-center justify-between transition-all duration-300",
      isSubNode ? "min-w-[150px] scale-95" : "min-w-[180px]",
      appliedStyle
    )}>
      <Handle type="target" position={Position.Top} isConnectable={isConnectable} className="opacity-0" />

      <div className="flex items-center gap-3">
        <div className={isSubNode ? "text-base" : "text-xl"}>{icon}</div>
        <div>
          <div className={twMerge("font-medium tracking-wide", isSubNode ? "text-xs" : "text-sm")}>{label}</div>
          {segment && (
            <div className={twMerge(
              "text-[9px] tracking-widest uppercase mt-0.5",
              segment === 'B2B' ? "text-[#F59E0B]" : "text-[#2B84EA]"
            )}>
              {segment}{isSubNode ? ' · sub' : ''}
            </div>
          )}
        </div>
      </div>

      <div className="ml-4">
        {status === 'ACTIVE' && (
          <Loader2 className={twMerge(
            "w-4 h-4 animate-spin",
            segment === 'B2B' ? 'text-[#F59E0B]' : isAI ? 'text-[#8B5CF6]' : 'text-[#2B84EA]'
          )} />
        )}
        {status === 'COMPLETED' && <Check className="w-4 h-4 text-[#22C55E]" />}
        {status === 'BLOCKED' && <AlertTriangle className="w-4 h-4 text-amber-400" />}
        {status === 'WAITING' && <div className="w-2 h-2 rounded-full bg-slate-600" />}
      </div>

      {status === 'ACTIVE' && (
        <motion.div
          className={twMerge(
            "absolute inset-0 rounded-lg border",
            segment === 'B2B' ? 'border-[#F59E0B]' : isAI ? 'border-[#8B5CF6]' : 'border-[#2B84EA]'
          )}
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: [0, 0.5, 0], scale: 1.02 }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}

      <Handle type="source" position={Position.Bottom} isConnectable={isConnectable} className="opacity-0" />
    </div>
  );
}
