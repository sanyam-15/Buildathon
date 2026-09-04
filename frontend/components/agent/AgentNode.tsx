import { Handle, Position } from '@xyflow/react';
import { motion } from 'framer-motion';
import { Check, Loader2, AlertTriangle, Play } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function AgentNode({ data, isConnectable }: any) {
  const { label, icon, status, isAI } = data;

  const statusStyles = {
    WAITING: "border-[#1E293B] bg-[#0B1220] text-slate-400",
    ACTIVE: "border-[#2B84EA] bg-[#2B84EA]/10 text-white shadow-sm",
    COMPLETED: "border-[#22C55E] bg-[#22C55E]/10 text-white",
    BLOCKED: "border-amber-500 bg-amber-500/10 text-white",
    FAILED: "border-red-500 bg-red-500/10 text-white",
  };

  const aiStyles = "border-[#8B5CF6] bg-[#8B5CF6]/10 text-white";
  const appliedStyle = (isAI && status !== 'WAITING') ? aiStyles : (statusStyles[status as keyof typeof statusStyles] || statusStyles.WAITING);

  return (
    <div className={twMerge(
      "px-4 py-3 rounded-lg border min-w-[180px] flex items-center justify-between transition-all duration-300",
      appliedStyle
    )}>
      <Handle type="target" position={Position.Top} isConnectable={isConnectable} className="opacity-0" />
      
      <div className="flex items-center gap-3">
        <div className="text-xl">{icon}</div>
        <div className="text-sm font-medium tracking-wide">{label}</div>
      </div>

      <div className="ml-4">
        {status === 'ACTIVE' && <Loader2 className={`w-4 h-4 animate-spin ${isAI ? 'text-[#8B5CF6]' : 'text-[#2B84EA]'}`} />}
        {status === 'COMPLETED' && <Check className="w-4 h-4 text-[#22C55E]" />}
        {status === 'BLOCKED' && <AlertTriangle className="w-4 h-4 text-amber-400" />}
        {status === 'WAITING' && <div className="w-2 h-2 rounded-full bg-slate-600" />}
      </div>

      {status === 'ACTIVE' && (
        <motion.div
          className={`absolute inset-0 rounded-lg border ${isAI ? 'border-[#8B5CF6]' : 'border-[#2B84EA]'}`}
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: [0, 0.5, 0], scale: 1.02 }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}

      <Handle type="source" position={Position.Bottom} isConnectable={isConnectable} className="opacity-0" />
    </div>
  );
}
