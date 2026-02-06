'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';

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

type StreamMessage = LogEvent | { type: "fork_update", log_id: number, forks: number };

export default function LogReplay() {
    const [logs, setLogs] = useState<LogEvent[]>([]);
    const scrollRef = useRef<HTMLDivElement>(null);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        const startStream = async () => {
            try {
                const response = await fetch('http://localhost:8000/stream');
                if (!response.body) return;

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                setIsConnected(true);

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;

                    const text = decoder.decode(value);
                    const lines = text.split('\n');

                    for (const line of lines) {
                        if (line.trim()) {
                            try {
                                const data: StreamMessage = JSON.parse(line);

                                if ('type' in data && data.type === 'fork_update') {
                                    // Handle Fork Update
                                    setLogs(prev => prev.map(log =>
                                        log.id === data.log_id ? { ...log, forks: data.forks } : log
                                    ));
                                } else {
                                    // Handle New Log
                                    const log = data as LogEvent;
                                    setLogs(prev => {
                                        const exists = prev.some(p => p.id === log.id);
                                        if (exists) return prev;
                                        return [...prev.slice(-50), log];
                                    });
                                }
                            } catch (e) {
                                console.error("Parse error", e);
                            }
                        }
                    }
                }
            } catch (err) {
                console.error("Stream error", err);
                setIsConnected(false);
            }
        };

        startStream();
    }, []);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

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
        <div className="flex flex-col h-[600px] w-full max-w-4xl bg-black border border-green-900 font-mono text-xs p-4 relative overflow-hidden rounded-lg shadow-[0_0_20px_rgba(0,255,65,0.1)]">
            {/* Header */}
            <div className="absolute top-0 left-0 w-full bg-green-900/10 border-b border-green-900/30 px-4 py-2 flex justify-between items-center backdrop-blur-sm z-10">
                <span className="text-neon-green font-bold">/// LIVE_EXECUTION_STREAM ///</span>
                <div className="flex items-center gap-2">
                    <span className={isConnected ? "text-neon-green" : "text-red-500"}>
                        {isConnected ? "CONN_ESTABLISHED" : "CONN_LOST"}
                    </span>
                </div>
            </div>

            {/* Log Stream */}
            <div ref={scrollRef} className="mt-8 flex-1 overflow-y-auto no-scrollbar space-y-1 pb-10">
                {logs.map((log, idx) => (
                    <div key={`${log.id}-${idx}`} className="grid grid-cols-12 gap-2 opacity-80 hover:opacity-100 hover:bg-green-900/10 transition-colors duration-75 border-b border-white/5 py-1">
                        <span className="col-span-2 text-gray-500">{log.timestamp.split('T')[1]?.split('.')[0] || log.timestamp}</span>
                        <span className={`col-span-1 font-bold ${getLevelColor(log.level)}`}>[{log.level}]</span>
                        <div className="col-span-2 truncate flex flex-col">
                            <Link href={`/profile/${log.agent_id}`} className="text-purple-400 hover:text-neon-purple hover:underline cursor-pointer transition-all">
                                {log.agent_id}
                            </Link>
                            <span className="text-[9px] text-gray-600">{log.hashrate || "0 H/s"}</span>
                        </div>
                        <div className="col-span-6 text-gray-300 break-words">
                            <div className="flex items-center gap-2">
                                <span className="font-bold text-white">{log.strategy_name}</span>
                                <span>{log.message}</span>
                            </div>
                            {log.payload && Object.keys(log.payload).length > 0 && (
                                <span className="text-gray-600 text-[10px]">{JSON.stringify(log.payload)}</span>
                            )}
                        </div>
                        <div className="col-span-1 text-right flex items-center justify-end gap-1 text-gray-500">
                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                            </svg>
                            {log.forks || 0}
                        </div>
                    </div>
                ))}
            </div>

            {/* Overlay Scanlines */}
            <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] z-20 bg-[length:100%_2px,3px_100%]"></div>
        </div>
    );
}
