import { useState, useEffect, useRef, useCallback } from "react";

interface Message {
  role: "ai" | "user";
  content: string;
}

export const useCoachSocket = (token: string) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [formAlert, setFormAlert] = useState<string | null>(null);
  const [score, setScore] = useState(0);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!token) return;

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const socket = new WebSocket(`${protocol}//localhost:8000/ws/coach?token=${token}`);
    socketRef.current = socket;

    socket.onopen = () => {
      setIsConnected(true);
      console.log("Coach WebSocket connected");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case "ai_response":
          setMessages(prev => [...prev, { role: "ai", content: data.content }]);
          break;
        case "form_alert":
          setFormAlert(data.content);
          setScore(data.score);
          setTimeout(() => setFormAlert(null), 3000);
          break;
        case "pong":
          console.log("Heartbeat received");
          break;
      }
    };

    socket.onclose = () => {
      setIsConnected(false);
      console.log("Coach WebSocket disconnected");
    };

    return () => {
      socket.close();
    };
  }, [token]);

  const sendMessage = useCallback((content: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      setMessages(prev => [...prev, { role: "user", content }]);
      socketRef.current.send(JSON.stringify({
        type: "user_message",
        content
      }));
    }
  }, []);

  const sendLandmarks = useCallback((landmarks: any, exercise: string = "squat") => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: "pose_landmarks",
        landmarks,
        exercise
      }));
    }
  }, []);

  return {
    messages,
    isConnected,
    formAlert,
    score,
    sendMessage,
    sendLandmarks
  };
};
