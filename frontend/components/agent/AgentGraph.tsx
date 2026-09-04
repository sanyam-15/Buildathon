"use client";

import { useEffect, useMemo, useState } from 'react';
import { 
  ReactFlow, 
  Background, 
  Controls, 
  useNodesState, 
  useEdgesState, 
  MarkerType,
  Position
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { AgentNode } from './AgentNode';

const nodeTypes = {
  agent: AgentNode,
};

const initialNodes = [
  { id: 'sentinel', type: 'agent', position: { x: 300, y: 50 }, data: { label: 'Revenue Sentinel', icon: '⚡', status: 'WAITING' } },
  { id: 'classifier', type: 'agent', position: { x: 300, y: 150 }, data: { label: 'Leakage Classifier', icon: '🔍', status: 'WAITING' } },
  { id: 'failed_payment', type: 'agent', position: { x: 50, y: 250 }, data: { label: 'Failed Payment Specialist', icon: '💳', status: 'WAITING' } },
  { id: 'abandoned_cart', type: 'agent', position: { x: 300, y: 250 }, data: { label: 'Cart Specialist', icon: '🛒', status: 'WAITING' } },
  { id: 'subscription', type: 'agent', position: { x: 550, y: 250 }, data: { label: 'Subscription Specialist', icon: '🔄', status: 'WAITING' } },
  { id: 'strategist', type: 'agent', position: { x: 300, y: 350 }, data: { label: 'Recovery Strategist', icon: '🧠', status: 'WAITING', isAI: true } },
  { id: 'policy', type: 'agent', position: { x: 300, y: 450 }, data: { label: 'Policy Engine', icon: '🛡️', status: 'WAITING', isAI: true } },
  { id: 'execution', type: 'agent', position: { x: 300, y: 550 }, data: { label: 'Execution Agent', icon: '⚡', status: 'WAITING' } },
  { id: 'monitor', type: 'agent', position: { x: 300, y: 650 }, data: { label: 'Monitor Agent', icon: '👁', status: 'WAITING' } },
];

const initialEdges = [
  { id: 'e-1', source: 'sentinel', target: 'classifier', animated: false },
  { id: 'e-2', source: 'classifier', target: 'failed_payment', animated: false },
  { id: 'e-3', source: 'classifier', target: 'abandoned_cart', animated: false },
  { id: 'e-4', source: 'classifier', target: 'subscription', animated: false },
  { id: 'e-5', source: 'failed_payment', target: 'strategist', animated: false },
  { id: 'e-6', source: 'abandoned_cart', target: 'strategist', animated: false },
  { id: 'e-7', source: 'subscription', target: 'strategist', animated: false },
  { id: 'e-8', source: 'strategist', target: 'policy', animated: false },
  { id: 'e-9', source: 'policy', target: 'execution', animated: false },
  { id: 'e-10', source: 'execution', target: 'monitor', animated: false },
];

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
      setEdges(initialEdges.map(e => ({ ...e, animated: false, style: { stroke: '#1E293B', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#1E293B' } })));
      return;
    }

    const agentStatus: Record<string, string> = {};

    events.forEach(ev => {
      const { agent, event_type } = ev;
      if (!agent) return;

      // Map backend agent names to node IDs
      let nodeId = agent;
      if (agent === 'revenue_sentinel') nodeId = 'sentinel';
      if (agent === 'leakage_classifier') nodeId = 'classifier';
      if (agent === 'failed_payment_specialist') nodeId = 'failed_payment';
      if (agent === 'abandoned_cart_specialist') nodeId = 'abandoned_cart';
      if (agent === 'subscription_specialist') nodeId = 'subscription';
      if (agent === 'recovery_strategist') nodeId = 'strategist';
      if (agent === 'policy_engine') nodeId = 'policy';
      if (agent === 'execution_agent') nodeId = 'execution';
      if (agent === 'monitor_agent') nodeId = 'monitor';

      if (event_type === 'agent_started' || event_type === 'execution_started') {
        agentStatus[nodeId] = 'ACTIVE';
      }
      
      if (event_type === 'agent_completed') {
        agentStatus[nodeId] = 'COMPLETED';
      }

      if (event_type === 'policy_blocked') agentStatus['policy'] = 'BLOCKED';
    });

    // Update nodes immutably from initial state to ensure React Flow sees changes
    const updatedNodes = initialNodes.map(n => {
      const status = agentStatus[n.id] || 'WAITING';
      return {
        ...n,
        data: { ...n.data, status }
      };
    });

    // Update edges immutably based on target node status
    const updatedEdges = initialEdges.map(e => {
      const targetStatus = agentStatus[e.target];
      if (targetStatus === 'ACTIVE') {
        return {
          ...e,
          animated: true,
          style: { stroke: '#2B84EA', strokeWidth: 2 },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#2B84EA' }
        };
      } else if (targetStatus === 'COMPLETED') {
        return {
          ...e,
          animated: false,
          style: { stroke: '#22C55E', strokeWidth: 2 },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#22C55E' }
        };
      }
      // WAITING
      return {
        ...e,
        animated: false,
        style: { stroke: '#1E293B', strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#1E293B' }
      };
    });

    setNodes(updatedNodes);
    setEdges(updatedEdges);

  }, [events]);

  return (
    <div className="w-full h-[600px] glass-panel rounded-xl overflow-hidden relative">
      <div className="absolute top-4 left-4 z-10 font-medium tracking-widest text-xs text-muted-foreground uppercase">
        Live Agent Graph
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        defaultEdgeOptions={defaultEdgeOptions}
        fitView
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#1E293B" gap={20} size={1} />
        <Controls className="bg-[#0B1220] border-[#1E293B] fill-slate-400" />
      </ReactFlow>
    </div>
  );
}
