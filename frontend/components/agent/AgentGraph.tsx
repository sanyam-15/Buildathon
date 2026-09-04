"use client";

import { useEffect } from 'react';
import { 
  ReactFlow, 
  Background, 
  Controls, 
  useNodesState, 
  useEdgesState, 
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { AgentNode } from './AgentNode';

const nodeTypes = {
  agent: AgentNode,
};

const initialNodes = [
  { id: 'sentinel', type: 'agent', position: { x: 380, y: 20 }, data: { label: 'Revenue Sentinel', icon: '⚡', status: 'WAITING' } },
  { id: 'classifier', type: 'agent', position: { x: 380, y: 110 }, data: { label: 'Leakage Classifier', icon: '🔍', status: 'WAITING' } },
  // B2C specialists
  { id: 'failed_payment', type: 'agent', position: { x: 40, y: 220 }, data: { label: 'Failed Payment', icon: '💳', status: 'WAITING', segment: 'B2C' } },
  { id: 'abandoned_cart', type: 'agent', position: { x: 220, y: 220 }, data: { label: 'Cart Specialist', icon: '🛒', status: 'WAITING', segment: 'B2C' } },
  { id: 'subscription', type: 'agent', position: { x: 400, y: 220 }, data: { label: 'Subscription', icon: '🔄', status: 'WAITING', segment: 'B2C' } },
  // B2B specialist + sub-nodes
  { id: 'overdue_receivable', type: 'agent', position: { x: 620, y: 220 }, data: { label: 'Overdue Receivable', icon: '📄', status: 'WAITING', segment: 'B2B', isAI: true } },
  { id: 'b2b_invoice_analyzer', type: 'agent', position: { x: 560, y: 310 }, data: { label: 'Invoice Analyzer', icon: '📊', status: 'WAITING', segment: 'B2B', isSubNode: true } },
  { id: 'b2b_history_analyst', type: 'agent', position: { x: 720, y: 310 }, data: { label: 'History Analyst', icon: '📈', status: 'WAITING', segment: 'B2B', isSubNode: true } },
  { id: 'b2b_followup_planner', type: 'agent', position: { x: 640, y: 400 }, data: { label: 'Follow-up Planner', icon: '🗓️', status: 'WAITING', segment: 'B2B', isSubNode: true } },
  // Shared pipeline
  { id: 'strategist', type: 'agent', position: { x: 380, y: 500 }, data: { label: 'Recovery Strategist', icon: '🧠', status: 'WAITING', isAI: true } },
  { id: 'policy', type: 'agent', position: { x: 380, y: 590 }, data: { label: 'Policy Engine', icon: '🛡️', status: 'WAITING', isAI: true } },
  { id: 'execution', type: 'agent', position: { x: 380, y: 680 }, data: { label: 'Execution Agent', icon: '⚡', status: 'WAITING' } },
  { id: 'monitor', type: 'agent', position: { x: 380, y: 770 }, data: { label: 'Monitor Agent', icon: '👁', status: 'WAITING' } },
];

const initialEdges = [
  { id: 'e-1', source: 'sentinel', target: 'classifier', animated: false },
  { id: 'e-2', source: 'classifier', target: 'failed_payment', animated: false },
  { id: 'e-3', source: 'classifier', target: 'abandoned_cart', animated: false },
  { id: 'e-4', source: 'classifier', target: 'subscription', animated: false },
  { id: 'e-b2b-main', source: 'classifier', target: 'overdue_receivable', animated: false },
  { id: 'e-5', source: 'failed_payment', target: 'strategist', animated: false },
  { id: 'e-6', source: 'abandoned_cart', target: 'strategist', animated: false },
  { id: 'e-7', source: 'subscription', target: 'strategist', animated: false },
  // B2B sub-node chain
  { id: 'e-b2b-1', source: 'overdue_receivable', target: 'b2b_invoice_analyzer', animated: false },
  { id: 'e-b2b-2', source: 'b2b_invoice_analyzer', target: 'b2b_history_analyst', animated: false },
  { id: 'e-b2b-3', source: 'b2b_history_analyst', target: 'b2b_followup_planner', animated: false },
  { id: 'e-b2b-4', source: 'b2b_followup_planner', target: 'strategist', animated: false },
  { id: 'e-8', source: 'strategist', target: 'policy', animated: false },
  { id: 'e-9', source: 'policy', target: 'execution', animated: false },
  { id: 'e-10', source: 'execution', target: 'monitor', animated: false },
];

const AGENT_TO_NODE: Record<string, string> = {
  revenue_sentinel: 'sentinel',
  leakage_classifier: 'classifier',
  failed_payment_specialist: 'failed_payment',
  abandoned_cart_specialist: 'abandoned_cart',
  subscription_specialist: 'subscription',
  overdue_receivable_specialist: 'overdue_receivable',
  b2b_invoice_analyzer: 'b2b_invoice_analyzer',
  b2b_history_analyst: 'b2b_history_analyst',
  b2b_followup_planner: 'b2b_followup_planner',
  recovery_strategist: 'strategist',
  policy_engine: 'policy',
  execution_agent: 'execution',
  monitor_agent: 'monitor',
};

const defaultEdgeOptions = {
  type: 'smoothstep',
  markerEnd: { type: MarkerType.ArrowClosed, color: '#1E293B' },
  style: { stroke: '#1E293B', strokeWidth: 2 },
};

export function AgentGraph({ events = [] }: { events: any[] }) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  useEffect(() => {
    if (events.length === 0) {
      setNodes(initialNodes.map(n => ({ ...n, data: { ...n.data, status: 'WAITING' } })));
      setEdges(initialEdges.map(e => ({
        ...e,
        animated: false,
        style: { stroke: '#1E293B', strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#1E293B' },
      })));
      return;
    }

    const agentStatus: Record<string, string> = {};

    events.forEach(ev => {
      const { agent, event_type } = ev;
      if (!agent) return;

      const nodeId = AGENT_TO_NODE[agent] || agent;

      if (event_type === 'agent_started' || event_type === 'execution_started') {
        agentStatus[nodeId] = 'ACTIVE';
      }

      if (event_type === 'agent_completed') {
        agentStatus[nodeId] = 'COMPLETED';
      }

      if (event_type === 'policy_blocked') agentStatus['policy'] = 'BLOCKED';
      if (event_type === 'followup_planned') agentStatus['b2b_followup_planner'] = 'COMPLETED';
    });

    const updatedNodes = initialNodes.map(n => {
      const status = agentStatus[n.id] || 'WAITING';
      return {
        ...n,
        data: { ...n.data, status },
      };
    });

    const updatedEdges = initialEdges.map(e => {
      const targetStatus = agentStatus[e.target];
      const isB2BEdge = e.id.startsWith('e-b2b');
      if (targetStatus === 'ACTIVE') {
        return {
          ...e,
          animated: true,
          style: { stroke: isB2BEdge ? '#F59E0B' : '#2B84EA', strokeWidth: 2 },
          markerEnd: { type: MarkerType.ArrowClosed, color: isB2BEdge ? '#F59E0B' : '#2B84EA' },
        };
      } else if (targetStatus === 'COMPLETED') {
        return {
          ...e,
          animated: false,
          style: { stroke: '#22C55E', strokeWidth: 2 },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#22C55E' },
        };
      }
      return {
        ...e,
        animated: false,
        style: { stroke: '#1E293B', strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#1E293B' },
      };
    });

    setNodes(updatedNodes);
    setEdges(updatedEdges);

  }, [events, setNodes, setEdges]);

  return (
    <div className="w-full h-[720px] glass-panel rounded-xl overflow-hidden relative">
      <div className="absolute top-4 left-4 z-10 flex items-center gap-3">
        <span className="font-medium tracking-widest text-xs text-muted-foreground uppercase">
          Live Agent Graph
        </span>
        <span className="text-[10px] px-2 py-0.5 rounded border border-[#2B84EA]/30 text-[#2B84EA] tracking-wider">B2C</span>
        <span className="text-[10px] px-2 py-0.5 rounded border border-[#F59E0B]/30 text-[#F59E0B] tracking-wider">B2B</span>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        defaultEdgeOptions={defaultEdgeOptions}
        fitView
        minZoom={0.4}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#1E293B" gap={20} size={1} />
        <Controls className="bg-[#0B1220] border-[#1E293B] fill-slate-400" />
      </ReactFlow>
    </div>
  );
}
