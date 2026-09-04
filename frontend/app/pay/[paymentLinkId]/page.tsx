"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Loader2, CheckCircle2, ShieldCheck, Lock, Download, CreditCard } from "lucide-react";
import { motion } from "framer-motion";
import { API_URL } from "@/lib/api";

export default function MockCheckoutPage() {
  const params = useParams();
  const paymentLinkId = params.paymentLinkId as string;
  
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  // In a real app, we'd fetch the payment link details.
  // For the MVP mock, we'll assume it's for the generic amount.
  
  const handlePay = async () => {
    setLoading(true);
    try {
      // Trigger the mock webhook
      const res = await fetch(`${API_URL}/webhooks/payment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payment_link_id: paymentLinkId, status: "paid" })
      });
      
      if (!res.ok) throw new Error("Webhook failed");
      
      setSuccess(true);
    } catch (err) {
      console.error(err);
      alert("Payment failed");
    } finally {
      setLoading(false);
    }
  };

  const txnId = `txn_${paymentLinkId.split('_').slice(-1)[0] || paymentLinkId.slice(-8)}`;
  const now = new Date();
  const formattedDate = now.toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' });
  const formattedTime = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });

  if (success) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-4">
        <motion.div 
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="bg-white p-8 md:p-10 rounded-2xl flex flex-col items-center text-center max-w-md w-full shadow-[0_4px_24px_-4px_rgba(0,0,0,0.08)]"
        >
          {/* Branding */}
          <div className="flex items-center gap-2 mb-8">
            <div className="w-8 h-8 rounded-lg bg-[#2B84EA] flex items-center justify-center">
              <CreditCard className="w-4 h-4 text-white" />
            </div>
            <span className="text-lg font-semibold text-[#0F172A] tracking-tight">Razorpay Relay</span>
          </div>

          {/* Success Icon */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", delay: 0.2 }}
            className="w-20 h-20 rounded-full bg-[#22C55E]/10 flex items-center justify-center mb-6"
          >
            <CheckCircle2 className="w-12 h-12 text-[#22C55E]" />
          </motion.div>

          <h1 className="text-2xl font-bold text-[#0F172A] mb-1">Payment Successful</h1>
          <p className="text-[#94A3B8] text-sm mb-6">Your transaction has been completed</p>

          {/* Amount */}
          <div className="text-4xl font-bold text-[#0F172A] mb-8">₹4,999</div>

          {/* Transaction Details */}
          <div className="w-full border-t border-[#E2E8F0] pt-6 space-y-4 text-sm">
            <div className="flex justify-between">
              <span className="text-[#94A3B8]">Transaction ID</span>
              <span className="text-[#0F172A] font-mono font-medium">{txnId}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#94A3B8]">Payment Method</span>
              <span className="text-[#0F172A] font-medium">UPI</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#94A3B8]">Merchant</span>
              <span className="text-[#0F172A] font-medium">Premium Plan</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#94A3B8]">Date</span>
              <span className="text-[#0F172A] font-medium">{formattedDate}, {formattedTime}</span>
            </div>
          </div>

          {/* Download Receipt */}
          <Button 
            variant="outline" 
            className="w-full mt-8 h-11 border-[#E2E8F0] text-[#0F172A] hover:bg-[#F1F5F9] font-medium"
          >
            <Download className="w-4 h-4 mr-2" />
            Download Receipt
          </Button>

          {/* Security Badge */}
          <div className="mt-6 flex items-center gap-1.5 text-[#94A3B8] text-xs">
            <Lock className="w-3.5 h-3.5" />
            <span>Secured by Razorpay Relay Payment Gateway</span>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col items-center justify-center p-4">
      
      {/* Branding */}
      <div className="mb-8 flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg bg-[#2B84EA] flex items-center justify-center">
          <CreditCard className="w-4 h-4 text-white" />
        </div>
        <span className="text-lg font-semibold text-[#0F172A] tracking-tight">Razorpay Relay</span>
      </div>

      <motion.div 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-white p-8 rounded-2xl w-full max-w-md shadow-[0_4px_24px_-4px_rgba(0,0,0,0.08)]"
      >
        {/* Secure Checkout Header */}
        <div className="flex items-center gap-2 mb-6 text-[#94A3B8]">
          <Lock className="w-4 h-4 text-[#22C55E]" />
          <span className="text-xs tracking-widest uppercase font-medium">Secure Checkout</span>
        </div>

        <div className="flex justify-between items-start mb-8 pb-6 border-b border-[#E2E8F0]">
          <div>
            <h2 className="text-lg font-semibold text-[#0F172A]">Pending Recovery</h2>
            <p className="text-sm text-[#94A3B8]">Ref: {paymentLinkId.split('_')[2] || paymentLinkId}</p>
          </div>
        </div>

        <div className="space-y-4 mb-8">
          <div className="flex justify-between text-[#64748B]">
            <span>Subtotal</span>
            <span className="text-[#0F172A]">₹4,999.00</span>
          </div>
          <div className="flex justify-between text-[#64748B]">
            <span>Tax</span>
            <span className="text-[#0F172A]">₹0.00</span>
          </div>
          <div className="flex justify-between text-[#0F172A] font-semibold text-lg pt-4 border-t border-[#E2E8F0]">
            <span>Total</span>
            <span>₹4,999.00</span>
          </div>
        </div>

        <Button 
          onClick={handlePay} 
          disabled={loading}
          className="w-full h-12 text-base bg-[#2B84EA] hover:bg-[#2B84EA]/90 text-white font-medium rounded-lg"
        >
          {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Pay Now"}
        </Button>
        
        <p className="text-center text-xs text-[#94A3B8] mt-4">
          This is a mock checkout page for demonstration purposes.
        </p>
      </motion.div>

      {/* Security Footer */}
      <div className="mt-6 flex items-center gap-1.5 text-[#94A3B8] text-xs">
        <ShieldCheck className="w-3.5 h-3.5" />
        <span>Secured by Razorpay Relay Payment Gateway</span>
      </div>
    </div>
  );
}
