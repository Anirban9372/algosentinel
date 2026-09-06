import React from 'react';
import { Layers } from 'lucide-react';

export default function PositionsTable({ positions }) {
  if (!positions || positions.length === 0) {
    return (
      <div className="bg-card border border-slate-800 rounded-2xl p-6 h-full flex flex-col">
        <div className="flex items-center gap-2 text-slate-400 mb-6">
          <Layers className="w-5 h-5" />
          <h2 className="font-semibold">Active Positions</h2>
        </div>
        <div className="flex-1 flex items-center justify-center text-slate-500">
          No open positions
        </div>
      </div>
    );
  }

  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  });

  return (
    <div className="bg-card border border-slate-800 rounded-2xl p-6 shadow-xl h-full flex flex-col">
      <div className="flex items-center gap-2 text-slate-400 mb-6">
        <Layers className="w-5 h-5" />
        <h2 className="font-semibold">Active Positions</h2>
      </div>

      <div className="overflow-x-auto flex-1">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-700 text-slate-400 text-sm">
              <th className="pb-3 font-medium">Symbol</th>
              <th className="pb-3 font-medium text-right">Qty</th>
              <th className="pb-3 font-medium text-right">Avg Price</th>
              <th className="pb-3 font-medium text-right">Market Value</th>
              <th className="pb-3 font-medium text-right">Unrealized P&L</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {positions.map((p) => {
              const isProfit = p.unrealized_pl >= 0;
              return (
                <tr key={p.symbol} className="border-b border-slate-800/50 hover:bg-slate-800/20 transition-colors">
                  <td className="py-4 font-semibold">{p.symbol}</td>
                  <td className="py-4 text-right">{p.qty}</td>
                  <td className="py-4 text-right">{formatter.format(p.avg_fill_price)}</td>
                  <td className="py-4 text-right">{formatter.format(p.market_value)}</td>
                  <td className={`py-4 text-right font-medium ${isProfit ? 'text-bull' : 'text-bear'}`}>
                    {isProfit ? '+' : ''}{formatter.format(p.unrealized_pl)} ({(p.unrealized_plpc * 100).toFixed(2)}%)
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

