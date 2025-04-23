import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Option {
  id: number;
  text: string;
}

export interface Poll {
  id: number;
  question: string;
  options: Option[];
}

export interface PollData {
  poll: Poll;
  results: Record<number, number>;
}

export const getPoll = async (): Promise<PollData> => {
  const response = await axios.get(`${API_BASE_URL}/api/poll`);
  return response.data;
};

export const submitVote = async (optionId: number, clientId: string): Promise<PollData> => {
  const response = await axios.post(`${API_BASE_URL}/api/poll/vote`, {
    option_id: optionId,
    client_id: clientId,
  });
  return response.data;
};

// WebSocket连接函数
export const createWebSocket = (onMessage: (data: any) => void): WebSocket => {
  const ws = new WebSocket(`ws://localhost:8000/ws/poll`);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };

  return ws;
}; 