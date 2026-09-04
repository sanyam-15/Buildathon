"use client";

import { motion } from "framer-motion";
import { TrendingUp, TrendingDown, AlertCircle, CheckCircle2 } from "lucide-react";
import { useEffect, useState } from "react";
import { fetchStats } from "@/lib/api";

export function RevenueMetrics() {
  const [stats, setStats] = useState({
    total_at_risk: 0,
    total_recovered: 0,
    recovery_rate: 0,
    active_cases: 0,
  });

  useEffect(() => {
    // Polling for MVP dashboard simplicity
    const loadStats = async () => {
      try {
        const data = await fetchStats();
        setStats(data);
      } catch (err) {
        console.error(err);
      }
    };
    
    loadStats();
    const interval = setInterval(loadStats, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <MetricCard 
        title="Revenue At Risk" 
        value={stats.total_at_risk} 
        icon={<AlertCircle className="w-4 h-4 text-[#F59E0B]" />} 
        prefix="₹"
        accentColor="#F59E0B"
      />
      <MetricCard 
        title="Revenue Recovered" 
        value={stats.total_recovered} 
        icon={<CheckCircle2 className="w-4 h-4 text-[#22C55E]" />} 
        prefix="₹"
        accentColor="#22C55E"
      />
      <MetricCard 
        title="Recovery Rate" 
        value={stats.recovery_rate} 
        icon={<TrendingUp className="w-4 h-4 text-[#2B84EA]" />} 
        suffix="%"
        accentColor="#2B84EA"
      />
      <MetricCard 
        title="Active Recoveries" 
        value={stats.active_cases} 
        icon={<TrendingDown className="w-4 h-4 text-[#8B5CF6]" />} 
        accentColor="#8B5CF6"
      />
    </div>
  );
}

function MetricCard({ title, value, icon, prefix = "", suffix = "", accentColor }: any) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel p-6 rounded-xl flex flex-col gap-2 relative overflow-hidden"
    >
      <div className="flex items-center justify-between text-[#94A3B8]">
        <span className="text-xs font-medium tracking-widest uppercase">{title}</span>
        {icon}
      </div>
      <div className="flex items-baseline gap-1">
        {prefix && <span className="text-2xl font-light text-[#94A3B8]">{prefix}</span>}
        <motion.span 
          key={value}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-4xl font-semibold tracking-tight text-[#F8FAFC]"
        >
          {value.toLocaleString()}
        </motion.span>
        {suffix && <span className="text-2xl font-light text-[#94A3B8]">{suffix}</span>}
      </div>
    </motion.div>
  );
}
