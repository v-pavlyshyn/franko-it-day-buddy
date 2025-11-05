import React, { useEffect, useRef, useState } from "react";

type Msg = { role: "user" | "assistant"; text: string };

export default function App() {
  const [apiBase, setApiBase] = useState("");
  const [user, setUser] = useState("student");
  const [model, setModel] = useState("gemini-2.5-flash");
  const [useRag, setUseRag] = useState(true);
  const [saving, setSaving] = useState(false);
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const logRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: "smooth" });
  }, [msgs, busy]);

  useEffect(() => {
    const raw = localStorage.getItem("franko_cfg");
    if (raw) {
      try {
        const cfg = JSON.parse(raw);
        setApiBase(cfg.apiBase || "");
        setUser(cfg.user || "student");
        setModel(cfg.model || "gemini-2.5-flash");
        setUseRag(cfg.useRag ?? true);
      } catch {}
    }
  }, []);

  function saveCfg() {
    setSaving(true);
    const cfg = { apiBase: apiBase.trim(), user: user.trim() || "student", model, useRag };
    localStorage.setItem("franko_cfg", JSON.stringify(cfg));
    setTimeout(() => setSaving(false), 600);
  }

  async function send() {
    if (!apiBase) return alert("Вкажіть API base URL у ⚙️");
    if (!input.trim()) return;
    const payload = { user, message: input.trim(), use_rag: useRag, model_name: model };
    setMsgs(m => [...m, { role: "user", text: payload.message }]);
    setInput("");
    setBusy(true);
    try {
      const r = await fetch(apiBase.replace(/\/$/, "") + "/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const j = await r.json();
      const answer = j.answer || JSON.stringify(j);
      setMsgs(m => [...m, { role: "assistant", text: answer }]);
      if (Array.isArray(j.sources) && j.sources.length) {
        const extra =
          "\n\nДжерела (RAG):\n" +
          j.sources.map((s: any, i: number) => `(${i + 1}) ${s.question || s.id || ""}`).join("\n");
        setMsgs(m => [...m, { role: "assistant", text: extra }]);
      }
    } catch (e: any) {
      setMsgs(m => [...m, { role: "assistant", text: "⚠️ Помилка: " + (e?.message || e) }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-10 backdrop-blur bg-white/70 border-b border-slate-200">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-500" />
            <div>
              <div className="font-semibold">Franko Buddy</div>
              <div className="text-xs text-slate-500">Cloud Run · Firestore · Vertex AI · MCP</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => setOpen(v => !v)} className="px-3 py-1.5 rounded-xl border border-slate-300 hover:bg-slate-100 text-sm">⚙️ Налаштування</button>
            <a href="https://cloud.google.com/vertex-ai/generative-ai/docs/models/" target="_blank" rel="noreferrer" className="px-3 py-1.5 rounded-xl border border-slate-300 hover:bg-slate-100 text-sm">Моделі</a>
          </div>
        </div>
      </header>
      {open && (
        <div className="bg-white/90 border-b border-slate-200">
          <div className="max-w-5xl mx-auto px-4 py-4 grid grid-cols-1 md:grid-cols-4 gap-3">
            <input className="col-span-2 px-3 py-2 rounded-xl border border-slate-300" placeholder="API base URL (https://...)" value={apiBase} onChange={e => setApiBase(e.target.value)} />
            <input className="px-3 py-2 rounded-xl border border-slate-300" placeholder="user id" value={user} onChange={e => setUser(e.target.value)} />
            <select className="px-3 py-2 rounded-xl border border-slate-300" value={model} onChange={(e) => setModel(e.target.value)}>
              <option value="gemini-2.5-flash">gemini-2.5-flash</option>
              <option value="gemini-2.5-flash-lite">gemini-2.5-flash-lite</option>
              <option value="gemini-2.5-pro">gemini-2.5-pro</option>
            </select>
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={useRag} onChange={e => setUseRag(e.target.checked)} /> Використовувати RAG</label>
            <button onClick={saveCfg} className="px-3 py-2 rounded-xl bg-slate-900 text-white hover:bg-slate-800 text-sm">{saving ? "Збережено ✔" : "Зберегти"}</button>
          </div>
        </div>
      )}
      <main className="max-w-5xl mx-auto px-4 py-6">
        <div ref={logRef} className="bg-white rounded-2xl shadow-sm border border-slate-200 p-4 h-[62vh] overflow-y-auto">
          {msgs.length === 0 ? (
            <div className="h-full grid place-items-center text-slate-500">
              <div className="text-center">
                <div className="text-xl font-semibold">Почнімо розмову</div>
                <div className="text-sm">Відкрийте ⚙️, введіть API URL та напишіть перше повідомлення.</div>
              </div>
            </div>
          ) : (
            <ul className="space-y-3">
              {msgs.map((m, i) => (
                <li key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`${m.role === "user" ? "bg-indigo-50" : "bg-cyan-50"} max-w-[80%] rounded-2xl px-4 py-2 text-[15px] leading-relaxed`}>{m.text}</div>
                </li>
              ))}
              {busy && <li className="text-sm text-slate-500">Мислю…</li>}
            </ul>
          )}
        </div>
        <div className="mt-4 flex items-center gap-3">
          <input className="flex-1 px-4 py-3 rounded-2xl border border-slate-300 shadow-sm" placeholder="Постав запитання про подію…" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }} />
          <button onClick={send} disabled={busy} className="px-5 py-3 rounded-2xl bg-gradient-to-br from-indigo-600 to-cyan-600 text-white shadow hover:opacity-95">Надіслати</button>
        </div>
        <div className="mt-3 text-xs text-slate-500">Порада: додайте свої матеріали у колекцію <code>faq</code> або підключіть SQL/pgvector для «своєї пам’яті» стартапу.</div>
      </main>
      <footer className="pb-6 text-center text-xs text-slate-400">© 2025 Franko IT Day Workshop</footer>
    </div>
  );
}