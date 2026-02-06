export default function SpectatorBadge() {
    return (
        <div className="fixed top-4 right-4 z-50 flex items-center gap-2 px-3 py-1 bg-glass border border-neon-purple rounded text-xs select-none animation-pulse">
            <div className="w-2 h-2 rounded-full bg-neon-purple animate-ping" />
            <span className="text-neon-purple font-bold tracking-widest uppercase">
                Spectator Mode :: READ ONLY
            </span>
        </div>
    );
}
