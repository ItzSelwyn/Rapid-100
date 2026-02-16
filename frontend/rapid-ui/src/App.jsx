import { useEffect, useState } from "react";

export default function App() {

  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let ws;
    let retryTimer;

    const connect = () => {
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      ws = new WebSocket(`${protocol}://${window.location.hostname}:8000/live`);

      ws.onopen = () => {
        console.log("Dashboard connected");
        setConnected(false); // wait for call_started event
      };

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);

        // CALL EVENTS
        if (msg.event === "call_started") {
          setConnected(true);
          setData(null);
          return;
        }

        if (msg.event === "call_ended") {
          setConnected(false);
          setData(null);
          return;
        }

        // Ignore partial packets
        if (!msg.transcript) return;

        msg.risks = msg.risks || [];
        setData(msg);
      };

      ws.onclose = () => {
        console.log("Dashboard disconnected — retrying...");
        retryTimer = setTimeout(connect, 1000); // reconnect after 1s
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    connect();

    return () => {
      clearTimeout(retryTimer);
      ws?.close();
    };
  }, []);

  const severityStyle = {
    low: "bg-yellow-400 text-black",
    medium: "bg-orange-400 text-white",
    high: "bg-red-500 text-white",
    critical: "bg-red-700 text-white animate-pulse"
  };

  const typeStyle = {
    fire: "bg-red-600",
    medical: "bg-blue-600",
    crime: "bg-purple-600",
    accident: "bg-orange-600",
    analyzing: "bg-emerald-500",
    unknown: "bg-gray-500"
  };

  return (
    <div className="min-h-screen bg-[#e7f1ef] p-8 text-slate-800">

      {/* HEADER */}
      <div className="bg-[#2f6f6a] text-white rounded-3xl px-10 py-8 mb-8 shadow-xl">
        <h1 className="text-7xl font-extrabold tracking-wide">RAPID-100</h1>
        <div className="h-1 bg-white/60 rounded-full w-96 my-3"></div>
        <p className="text-xl opacity-90">emergency helpline: +12564879266</p>
      </div>

      <div className="grid grid-cols-2 gap-8">

        {/* LEFT PANEL */}
        <div>

          {/* CALL STATUS */}
          <div className={`rounded-full py-4 text-center font-semibold text-xl mb-8 shadow-md transition-all
            ${connected
              ? "bg-emerald-600 text-white shadow-emerald-300/50"
              : "bg-slate-300 text-slate-700"}`}>
            {connected ? "Call Ongoing" : "No Ongoing Call"}
          </div>

          {/* TRANSCRIPTION */}
          <div className="bg-[#5e8f92] rounded-3xl p-6 text-white shadow-xl">
            <h2 className="bg-white text-black rounded-2xl text-center text-2xl font-semibold py-2 mb-5 shadow">
              Transcription
            </h2>

            <div className="min-h-[160px] max-h-[240px] overflow-y-auto whitespace-pre-wrap text-lg leading-relaxed opacity-95">
              {data?.transcript || "Waiting for caller..."}
            </div>
          </div>

          {/* TYPE & SEVERITY */}
          <div className="grid grid-cols-2 gap-14 mt-10">

            {/* TYPE */}
            <div>
              <h3 className="text-2xl font-semibold mb-4">Type</h3>

              <div className={`inline-flex items-center px-5 py-2 rounded-full text-white font-semibold text-lg shadow-md
                ${data ? typeStyle[data.type] || typeStyle.unknown : "bg-gray-400"}`}>

                {data ? data.type.toUpperCase() : "UNKNOWN"}
              </div>
            </div>

            {/* SEVERITY */}
            <div>
              <h3 className="text-2xl font-semibold mb-4">Severity</h3>

              <div className={`inline-flex px-5 py-2 rounded-full font-bold text-lg shadow-md
                ${data ? severityStyle[data.severity] : "bg-gray-400 text-black"}`}>

                {data ? data.severity.toUpperCase() : "—"}
              </div>
            </div>

          </div>
        </div>

        {/* RIGHT PANEL */}
        <div className="bg-[#5e8f92] rounded-3xl p-7 text-white shadow-2xl">
          <h2 className="bg-white text-black rounded-2xl text-2xl font-semibold py-2 px-4 mb-6 shadow">
            Summary
          </h2>

          {data ? (
            <div className="space-y-4 text-lg leading-relaxed">

              <div className="bg-black/20 rounded-xl p-4">
                <b>Department:</b> {data.department}
              </div>

              <div className="bg-black/20 rounded-xl p-4">
                <b>Risks:</b> {(data?.risks?.length ?? 0) > 0 ? data.risks.join(", ") : "None"}
              </div>

              <div className="bg-black/20 rounded-xl p-4">
                <b>Risks:</b> {(data?.risks?.length ?? 0) > 0 ? data.risks.join(", ") : "None"}
              </div>

              <div className="bg-black/20 rounded-xl p-4">
                <b>Victims:</b> {data?.location || "Unknown"}
              </div>

              <div className="bg-black/20 rounded-xl p-4">
                <b>Location:</b> {data?.location || "Unknown"}
              </div>

              <div>
                <b>Full Transcript:</b>
                <div className="bg-black/30 p-4 rounded-xl mt-2 max-h-[260px] overflow-y-auto">
                  {data.transcript}
                </div>
              </div>

            </div>
          ) : (
            <p className="opacity-80">Waiting for incident data...</p>
          )}
        </div>

      </div>
    </div>
  );
}
