import { useState, useEffect, useRef } from 'react';
import { API_URL } from '@/lib/api';

export interface AgentEvent {
  event_id: string;
  timestamp: string;
  case_id: string;
  event_type: string;
  agent?: string;
  message: string;
  metadata?: any;
}

export function useRecoveryStream(caseId: string | null) {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!caseId) {
      setEvents([]);
      return;
    }

    setEvents([]);
    setIsActive(true);
    setError(null);

    const es = new EventSource(`${API_URL}/recovery/${caseId}/stream`);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        if (!event.data) return;
        const data: AgentEvent = JSON.parse(event.data);
        if (data.event_type !== 'keepalive') {
          setEvents((prev) => [...prev, data]);
        }
        
        // Stop on completion states
        if (['case_completed', 'case_failed', 'case_escalated', 'revenue_recovered'].includes(data.event_type)) {
          setIsActive(false);
          es.close();
        }
      } catch (err) {
        // Silently ignore malformed SSE chunks (like partial keepalives)
      }
    };

    es.onerror = (err) => {
      // Silently handle SSE connection drops (normal when case ends or backend restarts)
      setIsActive(false);
      es.close();
    };

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [caseId]);

  return { events, isActive, error };
}
