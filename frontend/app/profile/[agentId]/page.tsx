'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';

type LogEvent = {
    id: number;
    timestamp: string;
    level: string;
    message: string;
    agent_id: string;
    payload: any;
    forks?: number;
    hashrate?: string;
    strategy_name?: string;
};

export default function AgentProfile() {
    const params = useParams();
    const agentId = params.agentId as string; // decoded automatically by Next.js often, but verify decoding if needed

    // Decode URI component just in case
    const decodedAgentId = decodeURIComponent(agentId);

    const [logs, setLogs] = useState<LogEvent[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const res = await fetch(`http://localhost:8000/agent/${agentId}/logs`);
                if (res.ok) {
                    const data = await res.json();
                    setLogs(data);
                }
            } catch (e) {
                console.error("Profile fetch error", e);
            } finally {
                setLoading(false);
            }
        };

        if (agentId) {
            fetchLogs();
        }
    }, [agentId]);

    // Calculate Stats
    const totalForks = logs.reduce((acc, log) => acc + (log.forks || 0), 0);
    const avgHashrate = logs.length > 0 ? "400 TH/s" : "0 TH/s"; // Mock calculation or parse real string

    // Basic hashrate parser if needed, for MVP we can just show latest
    const latestHashrate = logs.length > 0 ? logs[0].hashrate : "Offline";

    const getLevelColor = (level: string) => {
        switch (level?.toUpperCase()) {
            case 'SUCCESS': return 'text-neon-green';
            case 'INFO': return 'text-cyan-400';
            case 'WARNING': return 'text-yellow-500';
            case 'ERROR': return 'text-red-500';
            case 'CRITICAL': return 'text-red-600 font-bold';
            default: return 'text-gray-400';
        }
    };

    return (
        <main className="min-h-screen relative flex flex-col items-center p-8 bg-black text-white font-mono">
            {/* Background Grid */}
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>
            <div className="absolute inset-0 bg-grid-white/[0.02] pointer-events-none"></div>

            <div className="w-full max-w-4xl z-10">
                <Link href="/" className="text-gray-500 hover:text-white mb-8 block">
                    &lt; RETURN_TO_HIVE
                </Link>

                {/* Profile Header */}
                <div className="bg-glass border border-neon-purple/50 p-8 rounded-lg mb-8 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-2 h-full bg-neon-purple"></div>
                    <div className="flex justify-between items-start">
                        <div>
                            <div className="text-xs text-gray-400 uppercase tracking-widest mb-2">AGENT_IDENTITY</div>
                            <h1 className="text-4xl font-black tracking-tighter text-white mb-2">{decodedAgentId}</h1>
                            <div className="text-green-500 text-sm flex items-center gap-2">
                                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                                ONLINE
                            </div>
                        </div>
                        <div className="flex gap-8 text-right">
                            <div>
                                <div className="text-xs text-gray-500 uppercase tracking-widest">Total Forks</div>
                                <div className="text-neon-purple font-mono text-2xl">{totalForks}</div>
                            </div>
                            <div>
                                <div className="text-xs text-gray-500 uppercase tracking-widest">Hashrate</div>
                                <div className="text-neon-green font-mono text-2xl">{latestHashrate}</div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Recent Activity */}
                <div className="space-y-4">
                    <h2 className="text-gray-400 text-sm uppercase tracking-widest border-b border-gray-800 pb-2">Recent Execution Logs</h2>
                    {loading ? (
                        <div className="text-center text-gray-500 py-10">DECRYPTING_HISTORY...</div>
                    ) : (
                        <div className="space-y-1">
                            {logs.map((log) => (
                                <div key={log.id} className="grid grid-cols-12 gap-2 opacity-80 hover:opacity-100 bg-white/5 hover:bg-white/10 transition-colors border-l border-transparent hover:border-gray-500 p-2 rounded-r">
                                    <span className="col-span-2 text-gray-500 text-xs">{log.timestamp.split('T')[1]?.split('.')[0]}</span>
                                    <span className={`col-span-1 font-bold ${getLevelColor(log.level)}`}>[{log.level}]</span>
                                    <div className="col-span-8 text-gray-300">
                                        <span className="text-neon-purple mr-2 text-xs">{log.strategy_name}</span>
                                        {log.message}
                                    </div>
                                    <div className="col-span-1 text-right text-gray-500 text-xs">
                                        {log.forks} forks
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </main>
    );
}
