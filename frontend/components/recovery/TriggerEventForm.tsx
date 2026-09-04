"use client";

import { useState } from "react";
import { triggerRecovery, triggerBatchRecovery } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, Rocket, Zap, Building2, ShoppingBag } from "lucide-react";

export function TriggerEventForm({ onCaseCreated }: { onCaseCreated: (id: string) => void }) {
  const [loading, setLoading] = useState(false);
  const [batchLoading, setBatchLoading] = useState(false);
  const [segment, setSegment] = useState<"B2C" | "B2B">("B2C");

  const [b2cForm, setB2cForm] = useState({
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

  const [b2bForm, setB2bForm] = useState({
    name: "Priya Menon",
    email: "accounts@acmelogistics.example.com",
    phone: "+919876543210",
    amount: 74999,
    company_name: "Acme Logistics Pvt Ltd",
    invoice_id: "INV-4821",
    po_number: "PO-99102",
    days_overdue: 32,
    previous_followups: 1,
    response_behavior: "acknowledged",
    payment_history_score: 0.72,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      let payload: any;

      if (segment === "B2B") {
        payload = {
          segment: "B2B",
          customer: {
            name: b2bForm.name,
            email: b2bForm.email,
            phone: b2bForm.phone,
          },
          amount: Number(b2bForm.amount),
          product_name: "B2B Invoice Settlement",
          signals: {
            invoice_overdue: true,
            days_overdue: Number(b2bForm.days_overdue),
            previous_followups: Number(b2bForm.previous_followups),
            response_behavior: b2bForm.response_behavior,
            payment_history_score: Number(b2bForm.payment_history_score),
          },
          invoice: {
            invoice_id: b2bForm.invoice_id,
            company_name: b2bForm.company_name,
            po_number: b2bForm.po_number,
            days_overdue: Number(b2bForm.days_overdue),
            invoice_value: Number(b2bForm.amount),
          },
        };
      } else {
        payload = {
          segment: "B2C",
          customer: {
            name: b2cForm.name,
            email: b2cForm.email,
            phone: b2cForm.phone,
          },
          amount: Number(b2cForm.amount),
          product_name: b2cForm.product,
          signals: {
            payment_attempted: b2cForm.payment_attempted === "true",
            payment_status: b2cForm.payment_status === "none" ? null : b2cForm.payment_status,
            checkout_started: b2cForm.checkout_started === "true",
            inactive_minutes: Number(b2cForm.inactive_minutes),
            cart_created: b2cForm.checkout_started === "true",
          },
          cart_items:
            b2cForm.checkout_started === "true" && b2cForm.payment_attempted === "false"
              ? [{ name: b2cForm.product, quantity: 1, price: Number(b2cForm.amount) }]
              : null,
        };
      }

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
      await triggerBatchRecovery(10, segment);
      alert(`${segment} batch recovery started. Check the Live Queue.`);
    } catch (err) {
      console.error(err);
    } finally {
      setBatchLoading(false);
    }
  };

  return (
    <div className="glass-panel p-6 rounded-xl flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium tracking-widest text-[#94A3B8] uppercase">
          Trigger Revenue Risk Event
        </h3>
        <Button
          variant="outline"
          size="sm"
          onClick={handleBatch}
          disabled={batchLoading}
          className="border-[#1E293B] text-[#2B84EA] hover:bg-[#2B84EA]/10 hover:border-[#2B84EA]/30"
        >
          {batchLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Zap className="w-4 h-4 mr-2" />}
          Batch {segment}
        </Button>
      </div>

      {/* Segment toggle */}
      <div className="grid grid-cols-2 gap-2 mb-5 p-1 rounded-lg bg-[#060B1A] border border-[#1E293B]">
        <button
          type="button"
          onClick={() => setSegment("B2C")}
          className={`flex items-center justify-center gap-2 py-2 rounded-md text-xs font-medium tracking-wider transition-colors ${
            segment === "B2C"
              ? "bg-[#2B84EA]/15 text-[#2B84EA] border border-[#2B84EA]/30"
              : "text-slate-500 hover:text-slate-300"
          }`}
        >
          <ShoppingBag className="w-3.5 h-3.5" />
          B2C Consumer
        </button>
        <button
          type="button"
          onClick={() => setSegment("B2B")}
          className={`flex items-center justify-center gap-2 py-2 rounded-md text-xs font-medium tracking-wider transition-colors ${
            segment === "B2B"
              ? "bg-[#F59E0B]/15 text-[#F59E0B] border border-[#F59E0B]/30"
              : "text-slate-500 hover:text-slate-300"
          }`}
        >
          <Building2 className="w-3.5 h-3.5" />
          B2B Receivables
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {segment === "B2C" ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Customer Name</Label>
                <Input
                  value={b2cForm.name}
                  onChange={(e) => setB2cForm({ ...b2cForm, name: e.target.value })}
                  className="bg-[#060B1A] border-[#1E293B] focus:border-[#2B84EA]"
                />
              </div>
              <div className="space-y-2">
                <Label>Email</Label>
                <Input
                  value={b2cForm.email}
                  onChange={(e) => setB2cForm({ ...b2cForm, email: e.target.value })}
                  className="bg-[#060B1A] border-[#1E293B] focus:border-[#2B84EA]"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Amount (₹)</Label>
                <Input
                  type="number"
                  value={b2cForm.amount}
                  onChange={(e) => setB2cForm({ ...b2cForm, amount: Number(e.target.value) })}
                  className="bg-[#060B1A] border-[#1E293B] focus:border-[#2B84EA]"
                />
              </div>
              <div className="space-y-2">
                <Label>Product</Label>
                <Input
                  value={b2cForm.product}
                  onChange={(e) => setB2cForm({ ...b2cForm, product: e.target.value })}
                  className="bg-[#060B1A] border-[#1E293B] focus:border-[#2B84EA]"
                />
              </div>
            </div>

            <div className="h-px w-full bg-[#1E293B] my-2" />
            <div className="text-xs text-slate-500 uppercase tracking-widest mb-2">Raw Event Signals</div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Payment Attempted</Label>
                <Select
                  value={b2cForm.payment_attempted}
                  onValueChange={(v) => setB2cForm({ ...b2cForm, payment_attempted: v })}
                >
                  <SelectTrigger className="bg-[#060B1A] border-[#1E293B]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="true">YES</SelectItem>
                    <SelectItem value="false">NO</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Payment Status</Label>
                <Select
                  value={b2cForm.payment_status}
                  onValueChange={(v) => setB2cForm({ ...b2cForm, payment_status: v })}
                >
                  <SelectTrigger className="bg-black/20 border-white/10">
                    <SelectValue />
                  </SelectTrigger>
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
                <Select
                  value={b2cForm.checkout_started}
                  onValueChange={(v) => setB2cForm({ ...b2cForm, checkout_started: v })}
                >
                  <SelectTrigger className="bg-black/20 border-white/10">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="true">YES</SelectItem>
                    <SelectItem value="false">NO</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Inactive Minutes</Label>
                <Input
                  type="number"
                  value={b2cForm.inactive_minutes}
                  onChange={(e) => setB2cForm({ ...b2cForm, inactive_minutes: Number(e.target.value) })}
                  className="bg-[#060B1A] border-[#1E293B] focus:border-[#2B84EA]"
                />
              </div>
            </div>
          </>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Contact Name</Label>
                <Input
                  value={b2bForm.name}
                  onChange={(e) => setB2bForm({ ...b2bForm, name: e.target.value })}
                  className="bg-[#060B1A] border-[#1E293B] focus:border-[#F59E0B]"
                />
              </div>
              <div className="space-y-2">
                <Label>Accounts Email</Label>
                <Input
                  value={b2bForm.email}
                  onChange={(e) => setB2bForm({ ...b2bForm, email: e.target.value })}
                  className="bg-[#060B1A] border-[#1E293B] focus:border-[#F59E0B]"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Company</Label>
                <Input
                  value={b2bForm.company_name}
                  onChange={(e) => setB2bForm({ ...b2bForm, company_name: e.target.value })}
                  className="bg-[#060B1A] border-[#1E293B] focus:border-[#F59E0B]"
                />
              </div>
              <div className="space-y-2">
                <Label>Invoice Value (₹)</Label>
                <Input
                  type="number"
                  value={b2bForm.amount}
                  onChange={(e) => setB2bForm({ ...b2bForm, amount: Number(e.target.value) })}
                  className="bg-[#060B1A] border-[#1E293B] focus:border-[#F59E0B]"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Invoice ID</Label>
                <Input
                  value={b2bForm.invoice_id}
                  onChange={(e) => setB2bForm({ ...b2bForm, invoice_id: e.target.value })}
                  className="bg-[#060B1A] border-[#1E293B] focus:border-[#F59E0B]"
                />
              </div>
              <div className="space-y-2">
                <Label>PO Number</Label>
                <Input
                  value={b2bForm.po_number}
                  onChange={(e) => setB2bForm({ ...b2bForm, po_number: e.target.value })}
                  className="bg-[#060B1A] border-[#1E293B] focus:border-[#F59E0B]"
                />
              </div>
            </div>

            <div className="h-px w-full bg-[#1E293B] my-2" />
            <div className="text-xs text-[#F59E0B]/80 uppercase tracking-widest mb-2">
              B2B Receivable Signals
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Days Overdue</Label>
                <Input
                  type="number"
                  value={b2bForm.days_overdue}
                  onChange={(e) => setB2bForm({ ...b2bForm, days_overdue: Number(e.target.value) })}
                  className="bg-[#060B1A] border-[#1E293B] focus:border-[#F59E0B]"
                />
              </div>
              <div className="space-y-2">
                <Label>Previous Follow-ups</Label>
                <Input
                  type="number"
                  value={b2bForm.previous_followups}
                  onChange={(e) => setB2bForm({ ...b2bForm, previous_followups: Number(e.target.value) })}
                  className="bg-[#060B1A] border-[#1E293B] focus:border-[#F59E0B]"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Response Behavior</Label>
                <Select
                  value={b2bForm.response_behavior}
                  onValueChange={(v) => setB2bForm({ ...b2bForm, response_behavior: v })}
                >
                  <SelectTrigger className="bg-[#060B1A] border-[#1E293B]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">NONE</SelectItem>
                    <SelectItem value="acknowledged">ACKNOWLEDGED</SelectItem>
                    <SelectItem value="promised_payment">PROMISED PAYMENT</SelectItem>
                    <SelectItem value="ignored">IGNORED</SelectItem>
                    <SelectItem value="disputed">DISPUTED</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Payment History Score (UI override — optional)</Label>
                <Input
                  type="number"
                  step="0.01"
                  min={0}
                  max={1}
                  value={b2bForm.payment_history_score}
                  onChange={(e) =>
                    setB2bForm({ ...b2bForm, payment_history_score: Number(e.target.value) })
                  }
                  className="bg-[#060B1A] border-[#1E293B] focus:border-[#F59E0B]"
                />
                <p className="text-[10px] text-slate-500 leading-relaxed">
                  Live score is computed from the buyer&apos;s closed-invoice AR ledger
                  (see History Analyst tool). This field is informational only.
                </p>
              </div>
            </div>
          </>
        )}

        <Button
          type="submit"
          disabled={loading}
          className={`w-full mt-4 text-white ${
            segment === "B2B"
              ? "bg-[#F59E0B] hover:bg-[#F59E0B]/90"
              : "bg-[#2B84EA] hover:bg-[#2B84EA]/90"
          }`}
        >
          {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Rocket className="w-4 h-4 mr-2" />}
          {segment === "B2B" ? "START B2B COLLECTIONS" : "START AUTONOMOUS RECOVERY"}
        </Button>
      </form>
    </div>
  );
}
