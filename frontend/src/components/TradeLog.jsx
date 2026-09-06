import React from 'react';
import { History } from 'lucide-react';

export default function TradeLog({ trades }) {
  if (!trades || trades.length === 0) {
    return (
      <div className="bg-card border border-slate-800 rounded-2xl p-6 h-full flex flex-col">
        <div className="flex items-center gap-2 text-slate-400 mb-6">
          <History className="w-5 h-5" />
          <h2 className="font-semibold">Recent Activity</h2>
        </div>
        <div className="flex-1 flex items-center justify-center text-slate-500">
          No recent activity
        </div>
      </div>
    );
  }

  return (
    <div className="bg-card border border-slate-800 rounded-2xl p-6 shadow-xl h-full flex flex-col max-h-96">
      <div className="flex items-center gap-2 text-slate-400 mb-6 shrink-0">
        <History className="w-5 h-5" />
        <h2 className="font-semibold">Recent Activity</h2>
      </div>

      <div className="overflow-y-auto pr-2 space-y-3 flex-1 custom-scrollbar">
        {trades.slice().reverse().map((t, i) => (
          <div key={i} className="p-3 bg-darker/50 rounded-lg border border-slate-800/50 text-sm">
            {t.message ? (
              <span className="text-slate-300">{t.message}</span>
            ) : (
              <div className="flex justify-between items-center">
                <span className="font-medium text-slate-200">
                  {t.qty}x {t.symbol} <span className="text-slate-500 mx-1">•</span> <span className="text-accent">{t.status}</span>
                </span>
                <span className="text-xs text-slate-500">
                  {new Date(t.timestamp).toLocaleTimeString()}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

