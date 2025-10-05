const ORCHESTRATOR_URL = import.meta.env.VITE_ORCHESTRATOR_URL || 'http://localhost:8003';
const ASR_URL = import.meta.env.VITE_ASR_URL || 'http://localhost:8004';
const TTS_URL = import.meta.env.VITE_TTS_URL || 'http://localhost:8005';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface QueryResponse {
  response: string;
  tool_calls: Array<{
    tool: string;
    args: Record<string, unknown>;
  }>;
  tool_results: Array<{
    tool: string;
    result: unknown;
  }>;
}

export interface TranscriptionResponse {
  text: string;
  language: string;
  duration?: number;
}

export async function sendTextQuery(query: string, history: Message[] = []): Promise<QueryResponse> {
  const response = await fetch(`${ORCHESTRATOR_URL}/v1/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      conversation_history: history,
    }),
  });

  if (!response.ok) {
    throw new Error(`Orchestrator error: ${response.statusText}`);
  }

  return response.json();
}

export async function transcribeAudio(audioBlob: Blob): Promise<TranscriptionResponse> {
  const formData = new FormData();
  formData.append('file', audioBlob, 'audio.webm');

  const response = await fetch(`${ASR_URL}/v1/transcribe`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`ASR error: ${response.statusText}`);
  }

  return response.json();
}

export async function synthesizeSpeech(text: string): Promise<Blob> {
  const response = await fetch(`${TTS_URL}/v1/speak`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text,
      speed: 1.0,
    }),
  });

  if (!response.ok) {
    throw new Error(`TTS error: ${response.statusText}`);
  }

  return response.blob();
}
