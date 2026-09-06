import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Header from './components/Header';
import AccountCard from './components/AccountCard';
import PositionsTable from './components/PositionsTable';
import SignalDisplay from './components/SignalDisplay';
import TradeLog from './components/TradeLog';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

export default function App() {
  const [account, setAccount] = useState(null);
  const [positions, setPositions] = useState([]);
  const [trades, setTrades] = useState([]);
  const [signal, setSignal] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  const fetchData = async () => {
    try {
      const [accRes, posRes, trdRes, sigRes] = await Promise.all([
        axios.get(`${API_URL}/api/account`),
        axios.get(`${API_URL}/api/account/positions`),
        axios.get(`${API_URL}/api/trades`),
        axios.get(`${API_URL}/api/signal/latest`)
      ]);
      setAccount(accRes.data);
      setPositions(posRes.data);
      setTrades(trdRes.data);
      setSignal(sigRes.data);
    } catch (e) {
      console.error('Error fetching data:', e);
    }
  };

  useEffect(() => {
    fetchData();

    // Setup WebSocket
    let ws;
    let reconnectTimeout;

    const connectWS = () => {
      ws = new WebSocket(WS_URL);

      ws.onopen = () => setIsConnected(true);

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'cycle_complete') {
            fetchData();
          }
        } catch (e) {
          console.error(e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        reconnectTimeout = setTimeout(connectWS, 5000);
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    connectWS();

    return () => {
      clearTimeout(reconnectTimeout);
      if (ws) ws.close();
    };
  }, []);

  return (
    <div className="min-h-screen flex flex-col font-sans">
      <Header isConnected={isConnected} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2">
            <AccountCard account={account} />
          </div>
          <div className="lg:col-span-1">
            <SignalDisplay signal={signal} />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <PositionsTable positions={positions} />
          </div>
          <div className="lg:col-span-1">
            <TradeLog trades={trades} />
          </div>
        </div>
      </main>
    </div>
  );
}

