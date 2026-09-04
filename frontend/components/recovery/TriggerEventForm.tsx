"use client";

import { useState } from "react";
import { triggerRecovery, triggerBatchRecovery } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, Rocket, Zap } from "lucide-react";

export function TriggerEventForm({ onCaseCreated }: { onCaseCreated: (id: string) => void }) {
  const [loading, setLoading] = useState(false);
  const [batchLoading, setBatchLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    name: "Test Customer",
    email: "throwayayemails@gmail.com",
    phone: "+9870667515",
    amount: 4999,
    product: "Premium Plan",
    payment_attempted: "false",
    payment_status: "none",
    checkout_started: "true",
    inactive_minutes: 120,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const payload = {
        customer: {
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
        },
        amount: Number(formData.amount),
        product_name: formData.product,
        signals: {
          payment_attempted: formData.payment_attempted === "true",
          payment_status: formData.payment_status === "none" ? null : formData.payment_status,
          checkout_started: formData.checkout_started === "true",
          inactive_minutes: Number(formData.inactive_minutes),
          cart_created: formData.checkout_started === "true",
        },
        // If it's a cart event, add a dummy cart item
        cart_items: formData.checkout_started === "true" && formData.payment_attempted === "false" 
          ? [{ name: formData.product, quantity: 1, price: Number(formData.amount) }]
          : null
      };
      
      const res = await triggerRecovery(payload);
      onCaseCreated(res.case_id);
    } catch (err) {
      console.error(err);
      alert("Failed to trigger event");
    } finally {
      setLoading(false);
    }
  };

  const handleBatch = async () => {
    setBatchLoading(true);
    try {
      await triggerBatchRecovery(10);
      alert("Batch recovery started. Check the Live Queue.");
    } catch (err) {
      console.error(err);
    } finally {
      setBatchLoading(false);
    }
  };

  return (
    <div className="glass-panel p-6 rounded-xl flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-sm font-medium tracking-widest text-[#94A3B8] uppercase">Trigger Revenue Risk Event</h3>
        <Button variant="outline" size="sm" onClick={handleBatch} disabled={batchLoading} className="border-[#1E293B] text-[#2B84EA] hover:bg-[#2B84EA]/10 hover:border-[#2B84EA]/30">
          {batchLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Zap className="w-4 h-4 mr-2" />}
          Run Auto Batch
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Customer Name</Label>
            <Input value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="bg-[#060B1A] border-[#1E293B] focus:border-[#2B84EA]" />
          </div>
          <div className="space-y-2">
            <Label>Email</Label>
            <Input value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="bg-[#060B1A] border-[#1E293B] focus:border-[#2B84EA]" />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Amount (₹)</Label>
            <Input type="number" value={formData.amount} onChange={e => setFormData({...formData, amount: Number(e.target.value)})} className="bg-[#060B1A] border-[#1E293B] focus:border-[#2B84EA]" />
          </div>
          <div className="space-y-2">
            <Label>Product</Label>
            <Input value={formData.product} onChange={e => setFormData({...formData, product: e.target.value})} className="bg-[#060B1A] border-[#1E293B] focus:border-[#2B84EA]" />
          </div>
        </div>

        <div className="h-px w-full bg-[#1E293B] my-2" />
        <div className="text-xs text-slate-500 uppercase tracking-widest mb-2">Raw Event Signals</div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Payment Attempted</Label>
            <Select value={formData.payment_attempted} onValueChange={v => setFormData({...formData, payment_attempted: v})}>
              <SelectTrigger className="bg-[#060B1A] border-[#1E293B]"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="true">YES</SelectItem>
                <SelectItem value="false">NO</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Payment Status</Label>
            <Select value={formData.payment_status} onValueChange={v => setFormData({...formData, payment_status: v})}>
              <SelectTrigger className="bg-black/20 border-white/10"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="none">NONE</SelectItem>
                <SelectItem value="failed">FAILED</SelectItem>
                <SelectItem value="success">SUCCESS</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Checkout Started</Label>
            <Select value={formData.checkout_started} onValueChange={v => setFormData({...formData, checkout_started: v})}>
              <SelectTrigger className="bg-black/20 border-white/10"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="true">YES</SelectItem>
                <SelectItem value="false">NO</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Inactive Minutes</Label>
            <Input type="number" value={formData.inactive_minutes} onChange={e => setFormData({...formData, inactive_minutes: Number(e.target.value)})} className="bg-[#060B1A] border-[#1E293B] focus:border-[#2B84EA]" />
          </div>
        </div>

        <Button type="submit" disabled={loading} className="w-full mt-4 bg-[#2B84EA] hover:bg-[#2B84EA]/90 text-white">
          {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Rocket className="w-4 h-4 mr-2" />}
          START AUTONOMOUS RECOVERY
        </Button>
      </form>
    </div>
  );
}
