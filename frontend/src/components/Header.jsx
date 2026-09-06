import React from 'react';
import { Activity } from 'lucide-react';

export default function Header({ isConnected }) {
  return (
    <header className="border-b border-slate-800 bg-darker/50 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-accent/10 rounded-lg">
            <Activity className="w-6 h-6 text-accent" />
          </div>
          <h1 className="text-xl font-bold tracking-tight">AlgoSentinel</h1>
        </div>

        <div className="flex items-center gap-2">
          <div className={`w-2.5 h-2.5 rounded-full ${isConnected ? 'bg-bull' : 'bg-bear animate-pulse'}`} />
          <span className="text-sm font-medium text-slate-400">
            {isConnected ? 'System Live' : 'Disconnected'}
          </span>
        </div>
      </div>
    </header>
  );
}

