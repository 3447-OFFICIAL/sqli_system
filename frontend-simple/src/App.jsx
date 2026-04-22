import React, { useState, useEffect, useRef } from 'react';
import { Shield, Activity, Database, AlertCircle, CheckCircle, Search, LogOut, Terminal as TerminalIcon, Cpu, Zap } from 'lucide-react';
import { login, predict, getLogs, WS_URL } from './api';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';

// --- COMPONENTS ---

const Gauge = ({ value, color }) => {
  const data = [
    { name: 'Value', value: value },
    { name: 'Remaining', value: 100 - value },
  ];
  return (
    <div className="relative w-full h-[200px]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="100%"
            startAngle={180}
            endAngle={0}
            innerRadius={60}
            outerRadius={80}
            paddingAngle={0}
            dataKey="value"
          >
            <Cell fill={color} />
            <Cell fill="rgba(255,255,255,0.05)" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-center">
        <span className="text-4xl font-black text-white">{value.toFixed(1)}</span>
        <p className="text-[10px] text-cyber-dim uppercase tracking-widest font-mono">Threat Probability</p>
      </div>
    </div>
  );
};

const RadarPanel = ({ data }) => {
  const radarData = [
    { subject: 'Semantic', A: data?.semantic || 0, fullMark: 100 },
    { subject: 'Time-Based', A: data?.time || 0, fullMark: 100 },
    { subject: 'Union', A: data?.union || 0, fullMark: 100 },
    { subject: 'Boolean', A: data?.boolean || 0, fullMark: 100 },
    { subject: 'Tautology', A: data?.tautology || 0, fullMark: 100 },
    { subject: 'Obfuscation', A: data?.obf || 0, fullMark: 100 },
  ];

  return (
    <div className="h-[250px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
          <PolarGrid stroke="rgba(100,255,218,0.1)" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: '#8892b0', fontSize: 10 }} />
          <Radar
            name="Threat"
            dataKey="A"
            stroke="#64ffda"
            fill="#64ffda"
            fillOpacity={0.3}
            animationDuration={800}
            isAnimationActive={true}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

const Terminal = ({ logs }) => {
  const scrollRef = useRef(null);
  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [logs]);

  return (
    <div className="bg-black/80 border border-cyber-accent/20 rounded-lg p-3 font-mono text-[11px] h-[150px] overflow-y-auto" ref={scrollRef}>
      <div className="text-cyber-accent/60 mb-2 border-b border-white/5 pb-1 flex items-center gap-2">
         <TerminalIcon size={12} /> soc-admin@aegis-sentinel:~# tail -f /var/log/waf/intercept.log
      </div>
      {logs.map((log, i) => (
        <div key={i} className={`mb-1 ${log.includes('BLOCK') || log.includes('MALICIOUS') ? 'text-cyber-red' : 'text-cyber-green'}`}>
          {log}
        </div>
      ))}
      <div className="w-2 h-4 bg-cyber-accent animate-pulse inline-block align-middle ml-1" />
    </div>
  );
};

// --- MAIN APP ---

const App = () => {
  const [token, setToken] = useState(localStorage.getItem('aegis_token'));
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [logs, setLogs] = useState([]);
  const [terminalLogs, setTerminalLogs] = useState([`[${new Date().toLocaleTimeString()}] SYSTEM BOOT... AEGIS SENTINEL ONLINE.`]);
  const [loading, setLoading] = useState(false);
  const [wsStatus, setWsStatus] = useState('offline');

  const addTermLog = (msg) => {
    const ts = new Date().toLocaleTimeString();
    setTerminalLogs(prev => [...prev.slice(-30), `[${ts}] ${msg}`]);
  };

  useEffect(() => {
    if (token) {
      // Initial Logs
      getLogs(15).then(setLogs);
      
      const ws = new WebSocket(WS_URL);
      ws.onopen = () => {
        setWsStatus('online');
        addTermLog("WebSocket Uplink: ESTABLISHED");
      }
      ws.onmessage = (e) => {
        const d = JSON.parse(e.data);
        setLogs(prev => [d, ...prev.slice(0, 14)]);
        if (d.prediction === 1) addTermLog(`ALERT: Malicious activity detected from ${d.source_ip}`);
      };
      ws.onclose = () => setWsStatus('offline');
      return () => ws.close();
    }
  }, [token]);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      await login(username, password);
      setToken(localStorage.getItem('aegis_token'));
      addTermLog(`Operator '${username}' authorized successfully.`);
    } catch (err) {
      alert("Invalid Credentials");
    }
  };

  const handlePredict = async () => {
    if (!query.trim()) return;
    setLoading(true);
    addTermLog(`Analyzing payload: ${query.substring(0, 30)}...`);
    try {
      const res = await predict(query);
      console.log("DEBUG [SENTINEL RESULT]:", res);
      setResult(res);
      addTermLog(`Scan Complete. Risk Level: ${res.risk_level}`);
      setTimeout(() => setLoading(false), 500);
    } catch (err) {
      setLoading(false);
      addTermLog("ERROR: API connection lost.");
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-cyber-black flex items-center justify-center p-4">
        <div className="w-full max-w-sm glass p-8 rounded-2xl border border-cyber-accent/20">
          <div className="flex flex-col items-center mb-8">
            < Shield size={48} className="text-cyber-accent" />
            <h1 className="text-2xl font-black mt-4 neon-text">AEGIS LOGIN</h1>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <input type="text" value={username} onChange={e=>setUsername(e.target.value)} className="w-full bg-black/40 border border-white/10 p-3 rounded" placeholder="Operator ID" />
            <input type="password" value={password} onChange={e=>setPassword(e.target.value)} className="w-full bg-black/40 border border-white/10 p-3 rounded" placeholder="Access Key" />
            <button className="w-full bg-cyber-accent text-cyber-black py-3 rounded font-bold uppercase tracking-widest text-xs">Authorize Access</button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#020c1b] text-[#ccd6f6] p-4 font-sans uppercase">
      {/* Header */}
      <header className="flex justify-between items-center mb-6 pl-2">
        <div className="flex items-center gap-3">
          <Shield className="text-[#64ffda]" />
          <h1 className="text-lg font-bold tracking-tighter">Aegis Sentinel AI Operations Center</h1>
        </div>
        <div className="flex items-center gap-4 text-[10px] font-mono">
           <span className="text-cyber-dim">Real-time Semantic SQL Injection Traffic Interception Dashboard</span>
           <button onClick={() => { localStorage.removeItem('aegis_token'); setToken(null); }} className="text-white bg-white/5 px-2 py-1 rounded">Logout</button>
        </div>
      </header>

      {/* Grid Layout inspired by your image */}
      <div className="grid grid-cols-12 gap-4">
        
        {/* Left Sidebar Info */}
        <aside className="col-span-2 space-y-4">
          <div className="glass p-4 rounded-lg flex flex-col items-center border-l-4 border-cyber-accent">
            <Shield size={24} className="text-cyber-accent mb-2" />
            <h3 className="text-[10px] font-bold">SYSTEM STATUS</h3>
          </div>
          <div className="glass p-3 rounded-lg border-l-4 border-cyber-green text-[9px] font-mono text-cyber-green">
            API OPERATIONAL
          </div>
          <div className="glass p-3 rounded-lg border-l-4 border-cyber-green text-[9px] font-mono text-cyber-green">
            CORE ML ENGINE
          </div>
          <div className="glass p-3 rounded-lg border-l-4 border-cyber-accent text-[9px] font-mono text-cyber-accent">
            ACTIVE MONITORING: {wsStatus}
          </div>
          <button className="w-full py-2 bg-cyber-accent/10 border border-cyber-accent/30 text-[9px] text-cyber-accent rounded mt-4">Terminate Session</button>
        </aside>

        {/* Main Content */}
        <main className="col-span-10 grid grid-cols-12 gap-4">
          
          {/* Row 1: Sandbox & Gauge */}
          <div className="col-span-8 glass p-5 rounded-xl">
             <h4 className="text-xs font-bold mb-4 flex items-center gap-2">Traffic Analysis Sandbox</h4>
             <textarea 
                value={query} onChange={e=>setQuery(e.target.value)}
                placeholder="'OR '1'='1' --"
                className="w-full h-[120px] bg-black/30 border border-white/5 p-4 font-mono text-xs rounded-lg focus:outline-none focus:border-cyber-accent transition-all"
             />
             <button 
                onClick={handlePredict}
                className="mt-4 px-4 py-2 bg-cyber-accent text-cyber-black font-bold text-[10px] rounded hover:scale-105 transition-all"
             >
                EXECUTE SENTINEL SCAN
             </button>
          </div>

          <div className="col-span-4 glass p-5 rounded-xl">
             <h4 className="text-xs font-bold mb-4">Sentinel Assessment</h4>
             <Gauge value={loading ? 45 : (result ? result.confidence * 100 : 0)} color={result?.prediction === 1 ? "#ff3131" : "#00ff9d"} />
             <div className="mt-4 text-center">
                <span className={`text-xs font-black px-3 py-1 rounded ${result?.prediction === 1 ? 'bg-cyber-red/20 text-cyber-red' : 'bg-cyber-green/20 text-cyber-green'}`}>
                   {loading ? "ANALYZING..." : (result?.prediction === 1 ? "🚨 THREAT DETECTED" : "✅ CLEAR CHANNEL")}
                </span>
             </div>
          </div>

          {/* Row 2: Radar & Logs */}
          <div className="col-span-5 glass p-5 rounded-xl">
             <h4 className="text-xs font-bold mb-4">Ensemble Model Consensus</h4>
             <RadarPanel key={JSON.stringify(result?.consensus_data)} data={result?.consensus_data} />
          </div>

          <div className="col-span-7 glass p-5 rounded-xl">
             <h4 className="text-xs font-bold mb-4">Audit Event Logs</h4>
             <div className="overflow-x-auto">
               <table className="w-full text-left text-[9px] font-mono">
                 <thead className="text-cyber-dim border-b border-white/5">
                   <tr><th className="p-2">Timestamp</th><th className="p-2">Query</th><th className="p-2">Verdict</th><th className="p-2">Confidence</th></tr>
                 </thead>
                 <tbody>
                   {logs.map((l, i) => (
                     <tr key={i} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                       <td className="p-2 whitespace-nowrap">{l.timestamp?.replace('T', ' ')}</td>
                       <td className="p-2 truncate max-w-[150px]">{l.query}</td>
                       <td className="p-2">
                          <span className={l.prediction === 1 ? 'text-cyber-red' : 'text-cyber-green'}>
                             {l.prediction === 1 ? '🚨 MALICIOUS' : '✅ SAFE'}
                          </span>
                       </td>
                       <td className="p-2">{(l.confidence || 0).toFixed(4)}</td>
                     </tr>
                   ))}
                 </tbody>
               </table>
             </div>
          </div>

          {/* Row 3: Terminal */}
          <div className="col-span-12">
            <h4 className="text-xs font-bold mb-2 flex items-center gap-2">
               📟 Aegis Sentinel System Terminal
            </h4>
            <Terminal logs={terminalLogs} />
          </div>

        </main>
      </div>
    </div>
  );
}

export default App;
