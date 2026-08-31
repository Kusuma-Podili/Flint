import React, { useEffect, useRef } from 'react';

interface LiveTerminalProps {
  logs: string[];
}

export function LiveTerminal({ logs }: LiveTerminalProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="bg-[#0b0f19] border border-border rounded-xl p-4 font-mono text-xs text-gray-300 h-96 overflow-y-auto custom-scrollbar shadow-inner" ref={scrollRef}>
      <div className="flex items-center space-x-2 border-b border-gray-800 pb-2 mb-3">
        <div className="h-3 w-3 rounded-full bg-red-500/80"></div>
        <div className="h-3 w-3 rounded-full bg-yellow-500/80"></div>
        <div className="h-3 w-3 rounded-full bg-green-500/80"></div>
        <span className="text-gray-500 text-[10px] ml-2">live-stream-worker-01: stdout</span>
      </div>
      {logs.map((log, idx) => (
        <div key={idx} className="py-0.5 leading-relaxed hover:bg-gray-800/40 px-1 rounded flex">
          <span className="text-gray-600 select-none w-8 text-right mr-3">{idx + 1}</span>
          <span>{log}</span>
        </div>
      ))}
    </div>
  );
}
