import React from 'react';
import { DollarSign, Wallet, TrendingUp, TrendingDown } from 'lucide-react';

export default function AccountCard({ account }) {
  if (!account) return <div className="h-40 bg-card rounded-2xl animate-pulse"></div>;

  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  });

  // Calculate profit/loss from starting $100k
  const startingBalance = 100000;
  const pnl = account.equity - startingBalance;
  const pnlPercent = (pnl / startingBalance) * 100;
  const isProfit = pnl >= 0;

  return (
    <div className="bg-card border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center gap-2 text-slate-400 mb-6">
        <Wallet className="w-5 h-5" />
        <h2 className="font-semibold">Portfolio Value</h2>
      </div>

      <div className="flex items-baseline gap-4 mb-2">
        <span className="text-4xl font-bold tracking-tight">
          {formatter.format(account.equity)}
        </span>
        <div className={`flex items-center gap-1 font-semibold ${isProfit ? 'text-bull' : 'text-bear'}`}>
          {isProfit ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
          {isProfit ? '+' : ''}{formatter.format(pnl)} ({pnlPercent.toFixed(2)}%)
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mt-8">
        <div className="bg-darker/50 p-4 rounded-xl border border-slate-800/50">
          <div className="text-slate-400 text-sm font-medium mb-1">Buying Power</div>
          <div className="text-xl font-semibold">{formatter.format(account.buying_power)}</div>
        </div>
        <div className="bg-darker/50 p-4 rounded-xl border border-slate-800/50">
          <div className="text-slate-400 text-sm font-medium mb-1">Cash Balance</div>
          <div className="text-xl font-semibold">{formatter.format(account.cash)}</div>
        </div>
      </div>
    </div>
  );
}

