import React from 'react';
import { Target, AlertCircle } from 'lucide-react';

export default function SignalDisplay({ signal }) {
  if (!signal) {
    return (
      <div className="bg-card border border-slate-800 rounded-2xl p-6 h-full">
        <div className="animate-pulse h-full bg-slate-800/50 rounded-xl" />
      </div>
    );
  }

  const isBull = signal.signal === 'BULLISH';
  const isBear = signal.signal === 'BEARISH';
  const color = isBull ? 'text-bull' : isBear ? 'text-bear' : 'text-slate-400';
  const bg = isBull ? 'bg-bull/10 border-bull/20' : isBear ? 'bg-bear/10 border-bear/20' : 'bg-slate-800/50 border-slate-700';

  return (
    <div className="bg-card border border-slate-800 rounded-2xl p-6 shadow-xl h-full flex flex-col">
      <div className="flex items-center gap-2 text-slate-400 mb-6">
        <Target className="w-5 h-5" />
        <h2 className="font-semibold">Latest AI Signal</h2>
      </div>

      <div className={`p-6 rounded-xl border ${bg} flex-1 flex flex-col justify-center items-center text-center`}>
        <div className={`text-4xl font-extrabold tracking-tight mb-2 ${color}`}>
          {signal.signal}
        </div>
        <div className="text-slate-300 font-medium mb-4">
          Confidence: {(signal.confidence * 100).toFixed(0)}%
        </div>
        <div className="text-sm text-slate-400 italic max-w-sm mx-auto flex items-start gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <p className="text-left">{signal.reason}</p>
        </div>
      </div>
    </div>
  );
}

