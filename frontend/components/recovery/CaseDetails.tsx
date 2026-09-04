"use client";

import { useEffect, useState } from "react";
import { getCaseDetails } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Loader2, FileText, CheckCircle2, XCircle, AlertCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export function CaseDetails({ caseId }: { caseId: string | null }) {
  const [caseData, setCaseData] = useState<any>(null);

  useEffect(() => {
    if (!caseId) {
      setCaseData(null);
      return;
    }

    const loadData = async () => {
      try {
        const data = await getCaseDetails(caseId);
        setCaseData(data);
      } catch (err) {
        console.error(err);
      }
    };
    
    loadData();
    // Poll for updates while case is active
    const interval = setInterval(loadData, 2000);
    return () => clearInterval(interval);
  }, [caseId]);

  if (!caseData) {
    return (
      <div className="glass-panel p-6 rounded-xl flex items-center justify-center h-full text-slate-500">
        Select a case or trigger an event
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'RECOVERED': return <CheckCircle2 className="w-5 h-5 text-[#22C55E]" />;
      case 'FAILED': return <XCircle className="w-5 h-5 text-[#EF4444]" />;
      case 'ESCALATED': return <AlertCircle className="w-5 h-5 text-[#F59E0B]" />;
      default: return <Loader2 className="w-5 h-5 text-[#2B84EA] animate-spin" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'RECOVERED': return 'bg-[#22C55E]/10 text-[#22C55E] border-[#22C55E]/20';
      case 'FAILED': return 'bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20';
      case 'ESCALATED': return 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20';
      default: return 'bg-[#2B84EA]/10 text-[#2B84EA] border-[#2B84EA]/20';
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="glass-panel p-6 rounded-xl flex flex-col h-full overflow-y-auto"
    >
      <div className="flex items-center gap-2 mb-6 text-[#94A3B8] border-b border-[#1E293B] pb-4">
        <FileText className="w-5 h-5" />
        <h3 className="text-sm font-medium tracking-widest uppercase">Case Details</h3>
      </div>

      <div className="space-y-6">
        <div>
          <div className="text-xs text-slate-500 uppercase tracking-widest mb-1">Event ID</div>
          <div className="font-mono text-sm text-slate-300">{caseData.event_id}</div>
        </div>

        <div>
          <div className="text-xs text-slate-500 uppercase tracking-widest mb-2">Segment</div>
          <Badge
            variant="outline"
            className={
              caseData.segment === "B2B" || caseData.category === "OVERDUE_RECEIVABLE"
                ? "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20"
                : "bg-[#2B84EA]/10 text-[#2B84EA] border-[#2B84EA]/20"
            }
          >
            {caseData.segment || (caseData.category === "OVERDUE_RECEIVABLE" ? "B2B" : "B2C")}
          </Badge>
        </div>

        <div>
          <div className="text-xs text-slate-500 uppercase tracking-widest mb-2">Category</div>
          {caseData.category ? (
            <Badge
              variant="outline"
              className={
                caseData.category === "OVERDUE_RECEIVABLE"
                  ? "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20"
                  : "bg-[#8B5CF6]/10 text-[#8B5CF6] border-[#8B5CF6]/20"
              }
            >
              {caseData.category.replace(/_/g, " ")}
            </Badge>
          ) : (
            <span className="text-sm text-slate-500">Analyzing...</span>
          )}
        </div>

        {caseData.investigation?.invoice && (
          <div>
            <div className="text-xs text-slate-500 uppercase tracking-widest mb-2">Invoice</div>
            <div className="text-sm text-slate-300 font-mono">
              {caseData.investigation.invoice.invoice_id}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              {caseData.investigation.invoice.company_name}
              {caseData.investigation.days_overdue != null && (
                <> · {caseData.investigation.days_overdue}d overdue</>
              )}
            </div>
          </div>
        )}

        {caseData.investigation?.followup_plan && (
          <div>
            <div className="text-xs text-slate-500 uppercase tracking-widest mb-2">Follow-up Plan</div>
            <div className="text-sm text-[#F59E0B]">
              {caseData.investigation.followup_plan.recommended_action}
            </div>
            <div className="text-xs text-slate-500 mt-1 leading-relaxed">
              {caseData.investigation.followup_plan.reasoning}
            </div>
          </div>
        )}

        <div>
          <div className="text-xs text-slate-500 uppercase tracking-widest mb-1">Amount at Risk</div>
          <div className="text-2xl font-light text-white">₹{caseData.amount_at_risk.toLocaleString()}</div>
        </div>

        <div>
          <div className="text-xs text-slate-500 uppercase tracking-widest mb-2">Status</div>
          <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm font-medium ${getStatusColor(caseData.status)}`}>
            {getStatusIcon(caseData.status)}
            {caseData.status}
          </div>
        </div>

        {caseData.execution_results && caseData.execution_results.length > 0 && (
          <div className="pt-4 border-t border-[#1E293B]">
            <div className="text-xs text-slate-500 uppercase tracking-widest mb-3">Actions Taken</div>
            <div className="space-y-2">
              {caseData.execution_results.map((er: any, idx: number) => (
                <div key={idx} className="text-sm text-slate-300 flex justify-between">
                  <span>{er.action.replace(/_/g, ' ')}</span>
                  {er.action === 'CREATE_PAYMENT_LINK' && er.result?.url && (
                    <a href={er.result.url} target="_blank" rel="noreferrer" className="text-[#2B84EA] hover:underline">Open Link</a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
