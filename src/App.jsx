import { useEffect, useMemo, useState } from "react";
import { Link, NavLink, Route, Routes, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import {
  BarChart3,
  BookOpenCheck,
  Brain,
  CheckCircle2,
  ClipboardList,
  Gauge,
  Home,
  Info,
  Loader2,
  Moon,
  Sparkles,
  Sun,
  Trash2,
  XCircle,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { deleteEvaluation, evaluateAnswer, fetchEvaluation, fetchHistory } from "./api/client";

const navItems = [
  { to: "/", label: "Landing", icon: Home },
  { to: "/dashboard", label: "Dashboard", icon: Gauge },
  { to: "/history", label: "History", icon: ClipboardList },
  { to: "/about", label: "About", icon: Info },
];

const emptyForm = {
  question: "",
  reference_answer: "",
  student_answer: "",
  subject: "Computer Science",
  difficulty: "Medium",
  rubric: "Balanced",
};

function App() {
  const [dark, setDark] = useState(false);
  const [toast, setToast] = useState("");

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  const notify = (message) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2800);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950 transition-colors dark:bg-slate-950 dark:text-slate-100">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-64 border-r border-slate-200 bg-white/90 px-4 py-5 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90 lg:block">
        <Link to="/dashboard" className="flex items-center gap-3 px-2">
          <span className="grid h-10 w-10 place-items-center rounded-lg bg-emerald-600 text-white">
            <Brain size={22} />
          </span>
          <span>
            <span className="block text-sm font-semibold uppercase tracking-wide text-emerald-600">AI Evaluator</span>
            <span className="text-xs text-slate-500">Examiner dashboard</span>
          </span>
        </Link>
        <nav className="mt-8 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive
                    ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"
                    : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-900"
                }`
              }
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/85 px-4 py-3 backdrop-blur dark:border-slate-800 dark:bg-slate-950/85 lg:ml-64">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 lg:hidden">
            <Brain className="text-emerald-600" />
            <span className="font-semibold">AI Evaluator</span>
          </div>
          <div className="hidden text-sm text-slate-500 lg:block">Semantic grading, concept coverage, and examiner feedback</div>
          <button
            type="button"
            onClick={() => setDark((value) => !value)}
            className="grid h-10 w-10 place-items-center rounded-lg border border-slate-200 bg-white text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
            aria-label="Toggle dark mode"
          >
            {dark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
        <nav className="mt-3 flex gap-2 overflow-x-auto lg:hidden">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} className="rounded-lg px-3 py-2 text-sm text-slate-600 dark:text-slate-300">
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="lg:ml-64">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/dashboard" element={<Dashboard notify={notify} />} />
          <Route path="/result/:id" element={<Result notify={notify} />} />
          <Route path="/history" element={<History notify={notify} />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </main>

      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 16 }}
            className="fixed bottom-5 right-5 z-50 rounded-lg bg-slate-950 px-4 py-3 text-sm font-medium text-white shadow-soft dark:bg-white dark:text-slate-950"
          >
            {toast}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function Landing() {
  return (
    <section className="grid min-h-[calc(100vh-65px)] content-center overflow-hidden bg-[url('https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=1800&q=80')] bg-cover bg-center px-5 py-10">
      <div className="absolute inset-0 bg-slate-950/55 lg:left-64" />
      <div className="relative max-w-5xl">
        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} className="max-w-3xl">
          <p className="mb-4 inline-flex items-center gap-2 rounded-lg bg-white/12 px-3 py-2 text-sm font-medium text-white ring-1 ring-white/20">
            <Sparkles size={16} /> Semantic answer evaluation
          </p>
          <h1 className="text-5xl font-semibold leading-tight text-white sm:text-6xl">AI Question Evaluator</h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-100">
            Grade answers with semantic similarity, concept coverage, grammar signals, and examiner-style feedback.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/dashboard" className="rounded-lg bg-emerald-500 px-5 py-3 text-sm font-semibold text-white shadow-soft transition hover:bg-emerald-400">
              Open Dashboard
            </Link>
            <Link to="/history" className="rounded-lg bg-white/15 px-5 py-3 text-sm font-semibold text-white ring-1 ring-white/25 transition hover:bg-white/25">
              View History
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function Dashboard({ notify }) {
  const navigate = useNavigate();
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setLoading(true);
    try {
      const result = await evaluateAnswer(form);
      notify("Evaluation complete");
      navigate(`/result/${result.id}`);
    } catch (error) {
      notify(error.response?.data?.detail || "Evaluation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="mx-auto max-w-7xl px-5 py-8">
      <div className="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <h2 className="text-3xl font-semibold">Evaluation Dashboard</h2>
          <p className="mt-2 text-slate-500 dark:text-slate-400">Submit the question, ideal answer, and student response.</p>
        </div>
        <div className="flex gap-2">
          {["Balanced", "Strict", "Concept Heavy"].map((rubric) => (
            <button
              key={rubric}
              type="button"
              onClick={() => setForm({ ...form, rubric })}
              className={`rounded-lg px-3 py-2 text-sm font-medium ring-1 ${
                form.rubric === rubric
                  ? "bg-emerald-600 text-white ring-emerald-600"
                  : "bg-white text-slate-600 ring-slate-200 dark:bg-slate-900 dark:text-slate-300 dark:ring-slate-700"
              }`}
            >
              {rubric}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={submit} className="grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="space-y-4">
          <TextArea label="Question" value={form.question} onChange={(value) => setForm({ ...form, question: value })} rows={5} />
          <TextArea label="Reference Answer" value={form.reference_answer} onChange={(value) => setForm({ ...form, reference_answer: value })} rows={8} />
          <TextArea label="Student Answer" value={form.student_answer} onChange={(value) => setForm({ ...form, student_answer: value })} rows={8} />
        </div>
        <div className="space-y-4">
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-soft dark:border-slate-800 dark:bg-slate-900">
            <h3 className="mb-4 text-lg font-semibold">Evaluation Setup</h3>
            <Select label="Subject" value={form.subject} values={["General", "Computer Science", "Biology", "Mathematics", "History"]} onChange={(value) => setForm({ ...form, subject: value })} />
            <Select label="Difficulty" value={form.difficulty} values={["Easy", "Medium", "Hard"]} onChange={(value) => setForm({ ...form, difficulty: value })} />
            <button
              type="submit"
              disabled={loading}
              className="mt-5 flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {loading ? <Loader2 className="animate-spin" size={18} /> : <BookOpenCheck size={18} />}
              {loading ? "Evaluating answer..." : "Evaluate Answer"}
            </button>
          </div>
        </div>
      </form>
    </section>
  );
}

function Result({ notify }) {
  const id = window.location.pathname.split("/").pop();
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEvaluation(id)
      .then(setEvaluation)
      .catch(() => notify("Could not load evaluation"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <PageSkeleton />;
  if (!evaluation) return <EmptyState title="Evaluation not found" />;

  const result = evaluation.result;
  const scores = [
    { name: "Correctness", score: result.correctness },
    { name: "Completeness", score: result.completeness },
    { name: "Relevance", score: result.relevance },
    { name: "Clarity", score: result.clarity },
    { name: "Grammar", score: result.grammar },
  ];

  return (
    <section className="mx-auto max-w-7xl px-5 py-8">
      <div className="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="text-sm font-medium text-emerald-600">{evaluation.subject} · {evaluation.difficulty} · {evaluation.rubric}</p>
          <h2 className="mt-1 text-3xl font-semibold">Evaluation Result</h2>
        </div>
        <button onClick={() => window.print()} className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold dark:border-slate-700">
          Export PDF
        </button>
      </div>

      <div className="grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
        <ScorePanel score={result.overall_score} confidence={result.confidence_score} similarity={result.semantic_similarity} />
        <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-soft dark:border-slate-800 dark:bg-slate-900">
          <h3 className="mb-3 text-lg font-semibold">Score Breakdown</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={scores}>
                <PolarGrid />
                <PolarAngleAxis dataKey="name" tick={{ fill: "currentColor", fontSize: 12 }} />
                <Radar dataKey="score" stroke="#059669" fill="#10b981" fillOpacity={0.28} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-3">
        <ConceptList title="Correct Concepts" icon={CheckCircle2} items={result.correct_concepts} tone="green" />
        <ConceptList title="Missing Concepts" icon={XCircle} items={result.missing_concepts} tone="amber" />
        <ConceptList title="Incorrect Concepts" icon={XCircle} items={result.incorrect_concepts} tone="red" />
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <Feedback title="Personalized Feedback" body={result.feedback} items={result.strengths} />
        <Feedback title="Suggested Improvements" body={result.grammar_feedback} items={result.suggestions} />
      </div>
    </section>
  );
}

function History({ notify }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => fetchHistory().then(setItems).finally(() => setLoading(false));

  useEffect(() => {
    load();
  }, []);

  const remove = async (id) => {
    await deleteEvaluation(id);
    notify("Evaluation deleted");
    load();
  };

  const chartData = useMemo(() => items.slice().reverse().map((item) => ({ name: `#${item.id}`, score: item.overall_score })), [items]);

  return (
    <section className="mx-auto max-w-7xl px-5 py-8">
      <h2 className="text-3xl font-semibold">Evaluation History</h2>
      {loading ? <PageSkeleton /> : items.length === 0 ? <EmptyState title="No evaluations yet" /> : (
        <>
          <div className="mt-5 h-64 rounded-lg border border-slate-200 bg-white p-4 shadow-soft dark:border-slate-800 dark:bg-slate-900">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="score" fill="#059669" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-5 grid gap-3">
            {items.map((item) => (
              <div key={item.id} className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-soft dark:border-slate-800 dark:bg-slate-900 md:flex-row md:items-center md:justify-between">
                <Link to={`/result/${item.id}`} className="min-w-0">
                  <p className="truncate font-semibold">{item.question}</p>
                  <p className="mt-1 text-sm text-slate-500">{item.subject} · {item.difficulty} · Score {item.overall_score}</p>
                </Link>
                <button onClick={() => remove(item.id)} className="grid h-10 w-10 place-items-center rounded-lg border border-slate-200 text-slate-500 hover:text-red-600 dark:border-slate-700" aria-label="Delete evaluation">
                  <Trash2 size={18} />
                </button>
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  );
}

function About() {
  return (
    <section className="mx-auto max-w-5xl px-5 py-8">
      <h2 className="text-3xl font-semibold">About</h2>
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        {[
          ["Embedding Service", "Creates semantic vectors with all-MiniLM-L6-v2 when available."],
          ["Similarity Engine", "Computes cosine similarity between reference and student answers."],
          ["Gemini Engine", "Uses a strict JSON-only examiner prompt when an API key is configured."],
          ["History Store", "Persists every evaluation in SQLite for review and analytics."],
        ].map(([title, body]) => (
          <div key={title} className="rounded-lg border border-slate-200 bg-white p-5 shadow-soft dark:border-slate-800 dark:bg-slate-900">
            <BarChart3 className="mb-4 text-emerald-600" />
            <h3 className="text-lg font-semibold">{title}</h3>
            <p className="mt-2 text-slate-500 dark:text-slate-400">{body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function TextArea({ label, value, onChange, rows }) {
  return (
    <label className="block rounded-lg border border-slate-200 bg-white p-4 shadow-soft dark:border-slate-800 dark:bg-slate-900">
      <span className="text-sm font-semibold">{label}</span>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        rows={rows}
        className="mt-3 w-full resize-y rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm leading-6 outline-none transition focus:border-emerald-500 dark:border-slate-700 dark:bg-slate-950"
      />
    </label>
  );
}

function Select({ label, value, values, onChange }) {
  return (
    <label className="mb-4 block">
      <span className="text-sm font-semibold">{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)} className="mt-2 h-11 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 text-sm dark:border-slate-700 dark:bg-slate-950">
        {values.map((item) => <option key={item}>{item}</option>)}
      </select>
    </label>
  );
}

function ScorePanel({ score, confidence, similarity }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-soft dark:border-slate-800 dark:bg-slate-900">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Overall Score</h3>
        <Brain className="text-emerald-600" />
      </div>
      <div className="mx-auto my-8 grid h-52 w-52 place-items-center rounded-full bg-conic-score">
        <div className="grid h-40 w-40 place-items-center rounded-full bg-white dark:bg-slate-900">
          <span className="text-5xl font-semibold">{score}</span>
          <span className="-mt-10 text-sm text-slate-500">out of 100</span>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <MiniMetric label="Confidence" value={`${confidence}%`} />
        <MiniMetric label="Similarity" value={`${Math.round(similarity * 100)}%`} />
      </div>
    </div>
  );
}

function MiniMetric({ label, value }) {
  return (
    <div className="rounded-lg bg-slate-100 p-3 dark:bg-slate-950">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-semibold">{value}</p>
    </div>
  );
}

function ConceptList({ title, icon: Icon, items, tone }) {
  const color = {
    green: "text-emerald-700 bg-emerald-50 dark:bg-emerald-950 dark:text-emerald-300",
    amber: "text-amber-700 bg-amber-50 dark:bg-amber-950 dark:text-amber-300",
    red: "text-red-700 bg-red-50 dark:bg-red-950 dark:text-red-300",
  }[tone];
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-soft dark:border-slate-800 dark:bg-slate-900">
      <h3 className="mb-3 flex items-center gap-2 text-lg font-semibold"><Icon size={18} /> {title}</h3>
      <div className="flex flex-wrap gap-2">
        {(items.length ? items : ["None detected"]).map((item) => (
          <span key={item} className={`rounded-lg px-3 py-2 text-sm font-medium ${color}`}>{item}</span>
        ))}
      </div>
    </div>
  );
}

function Feedback({ title, body, items }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-soft dark:border-slate-800 dark:bg-slate-900">
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-3 leading-7 text-slate-600 dark:text-slate-300">{body}</p>
      <ul className="mt-4 space-y-2">
        {items.map((item) => <li key={item} className="rounded-lg bg-slate-100 px-3 py-2 text-sm dark:bg-slate-950">{item}</li>)}
      </ul>
    </div>
  );
}

function PageSkeleton() {
  return <div className="mx-auto max-w-7xl px-5 py-8"><div className="h-64 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-800" /></div>;
}

function EmptyState({ title }) {
  return <div className="mt-8 rounded-lg border border-dashed border-slate-300 p-10 text-center text-slate-500 dark:border-slate-700">{title}</div>;
}

export default App;
