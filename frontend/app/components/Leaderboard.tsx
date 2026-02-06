'use client';

import { useEffect, useState } from 'react';

type LogEvent = {
    id: number;
    agent_id: string;
    strategy_name: string;
    forks: number;
    hashrate: string;
};

export default function Leaderboard() {
    const [leaders, setLeaders] = useState<LogEvent[]>([]);

    useEffect(() => {
        const fetchLeaderboard = async () => {
            try {
                const res = await fetch('http://localhost:8000/leaderboard');
                if (res.ok) {
                    const data = await res.json();
                    setLeaders(data);
                }
            } catch (e) {
                console.error("Leaderboard fetch error", e);
            }
        };

        // Initial fetch
        fetchLeaderboard();

        // Poll every 5 seconds
        const interval = setInterval(fetchLeaderboard, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="bg-glass p-4 rounded-lg border-l-2 border-neon-purple">
            <h3 className="text-neon-purple font-bold mb-4 uppercase tracking-wider text-sm flex items-center justify-between">
                Top Strategies
                <span className="text-[10px] text-gray-500 animate-pulse">LIVE</span>
            </h3>
            <div className="space-y-3">
                {leaders.length === 0 ? (
                    <div className="text-gray-500 text-xs italic">Syncing with blockchain...</div>
                ) : (
                    leaders.map((log, i) => (
                        <div key={log.id} className="group cursor-default opacity-80 hover:opacity-100 transition-all">
                            <div className="text-[10px] text-gray-500 mb-1 flex justify-between">
                                <span>#{i + 1}</span>
                                <span>{log.agent_id}</span>
                            </div>
                            <div className="text-white font-mono text-sm group-hover:text-neon-green transition-colors truncate">
                                {log.strategy_name}
                            </div>
                            <div className="flex justify-between mt-1 text-xs text-gray-600 font-mono">
                                <span className="flex items-center gap-1 text-neon-purple">
                                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                                    </svg>
                                    {log.forks}
                                </span>
                                <span>{log.hashrate}</span>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
