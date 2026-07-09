import { createFileRoute } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { useCallback, useEffect, useState } from "react";
import { getKPIs } from "../api/kpi";
import { getStatus } from "@/api/status";
import { getInsights } from "@/api/insights";
import { getActivity } from "@/api/activity";
import {
    getPipelineStatus,
    startPipeline,
    stopPipeline,
} from "@/api/pipeline";
import { lazy, Suspense } from "react";
import PowerBIClient from "@/components/PowerBIClient";
import {
  Activity,
  ArrowRight,
  BarChart3,
  Cloud,
  Database,
  Filter,
  Gauge,
  Globe2,
  Layers,
  LayoutDashboard,
  LineChart,
  Lock,
  Map,
  RefreshCw,
  Repeat,
  Rocket,
  ShieldCheck,
  Sliders,
  Sparkles,
  UploadCloud,
  Workflow,
  Zap,
} from "lucide-react";
import dashboardOverview from "@/assets/dashboard-overview.png";
import dashboardSales from "@/assets/dashboard-trends.png";
import dashboardProducts from "@/assets/dashboard-products.png";
import dashboardRegions from "@/assets/dashboard-regions.png";
import dashboardCustomers from "@/assets/dashboard-customers.png";
import dashboardOperations from "@/assets/dashboard-operations.png";

const PowerBIReport = lazy(() =>
  import("powerbi-client-react").then((module) => ({
    default: module.PowerBIEmbed,
  }))
);

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "SalesPulse 360 — Enterprise Cloud Analytics Platform" },
      {
        name: "description",
        content:
          "End-to-end enterprise cloud analytics: Python replay events → AWS S3 → Snowpipe → Snowflake → Power BI → Executive Analytics Portal.",
      },
      { property: "og:title", content: "SalesPulse 360 — Enterprise Cloud Analytics Platform" },
      {
        property: "og:description",
        content:
          "End-to-end cloud analytics pipeline: Python → AWS S3 → Snowpipe → Snowflake → Power BI .",
      },
      { property: "og:type", content: "website" },
      { property: "og:image", content: dashboardOverview },
      { name: "twitter:card", content: "summary_large_image" },
      { name: "twitter:image", content: dashboardOverview },
    ],
  }),
  component: Index,
});

/* ---------- Tech logos (with safe fallback) ---------- */

import pythonLogo from "@/assets/logos/python.svg";
import awsLogo from "@/assets/logos/aws.svg";
import snowflakeLogo from "@/assets/logos/snowflake.svg";
import powerbiLogo from "@/assets/logos/powerbi.svg";

const LOGO = {
  python: pythonLogo,
  s3: awsLogo,
  snowflake: snowflakeLogo,
  snowpipe: snowflakeLogo,
  powerbi: powerbiLogo,
  sql: snowflakeLogo,
};

function TechLogo({ src, alt, className = "h-7 w-7" }: { src: string; alt: string; className?: string }) {
  // Fallback to a colored letter chip if the CDN image fails (keeps layout intact)
  const [errored, setErrored] = useState(false);
  if (errored) {
    return (
      <span
        className={`grid place-items-center rounded-md bg-violet-gradient font-display text-[10px] font-bold text-primary-foreground ${className}`}
        aria-label={alt}
      >
        {alt.slice(0, 2).toUpperCase()}
      </span>
    );
  }
  return (
    <img
      src={src}
      alt={alt}
      className={className}
      loading="lazy"
      onError={() => setErrored(true)}
    />
  );
}

/* ---------- Static content ---------- */

const dashboards = [
  { title: "Overview", desc: "Executive KPIs, revenue trends, top regions and channels.", img: dashboardOverview },
  { title: "Sales Trends", desc: "Multi-year monthly trends, quarterly growth and margin shifts.", img: dashboardSales },
  { title: "Products", desc: "Revenue vs profit matrix, margin leaders and unit economics.", img: dashboardProducts },
  { title: "Regions", desc: "Channel × city mix, order volume and delivery performance.", img: dashboardRegions },
  { title: "Customers", desc: "Top accounts, profit profile and customer performance matrix.", img: dashboardCustomers },
  { title: "Operations", desc: "Warehouse throughput, delivery SLAs and operational margins.", img: dashboardOperations },
];

const features = [
  { icon: Repeat, title: "Replay Event Streaming", desc: "A Python generator replays historical sales events in scheduled batches to simulate a live source system." },
  { icon: UploadCloud, title: "Snowpipe Auto-Ingestion", desc: "S3 object notifications trigger Snowpipe to land new files into RAW_SCHEMA automatically." },
  { icon: Database, title: "SQL Transformations", desc: "RAW → STAGING → ANALYTICS layers are built end-to-end with native Snowflake SQL." },
  { icon: Layers, title: "Star Schema Modelling", desc: "ANALYTICS_SCHEMA exposes governed fact and dimension tables ready for BI consumption." },
  { icon: BarChart3, title: "Power BI Reporting", desc: "Six interconnected report pages cover overview, trends, products, customers, regions and operations." },
  { icon: Globe2, title: "Executive Analytics Portal", desc: "A React-based Executive Analytics Portal embeds the Power BI report and provides a single interface for monitoring business KPIs and operational dashboards." },
  { icon: Filter, title: "Global Filter Context", desc: "Currency, period, region and channel slicers propagate across every Power BI page." },
  { icon: Cloud, title: "Fully Cloud-Native", desc: "Python, AWS S3, Snowpipe and Snowflake compose a 100% cloud ingestion and analytics path." },
];

const techStack = [
  { name: "Python", logo: LOGO.python, role: "Event Generator" },
  { name: "AWS S3", logo: LOGO.s3, role: "Cloud Storage" },
  { name: "Snowpipe", logo: LOGO.snowpipe, role: "Auto-Ingestion" },
  { name: "Snowflake", logo: LOGO.snowflake, role: "Cloud Warehouse" },
  { name: "SQL", logo: LOGO.sql, role: "Transformations" },
  { name: "Power BI", logo: LOGO.powerbi, role: "BI & Reporting" },
];

const architecture = [
  {
    title: "Python Generator",
    desc: "Generates historical and simulated sales events in replay batches.",
    logo: LOGO.python,
    schema: "Replay Engine",
    stage: "01",
  },
  {
    title: "AWS S3",
    desc: "Stores generated CSV batches in the cloud landing zone.",
    logo: LOGO.s3,
    schema: "Raw Storage",
    stage: "02",
  },
  {
    title: "Snowpipe",
    desc: "Automatically detects and ingests new files into Snowflake.",
    logo: LOGO.snowpipe,
    schema: "Continuous Ingestion",
    stage: "03",
  },
  {
    title: "Snowflake",
    desc: "Enterprise cloud warehouse storing RAW and transformed datasets.",
    logo: LOGO.snowflake,
    schema: "Warehouse",
    stage: "04",
  },
  {
    title: "SQL Transformations",
    desc: "Converts RAW data into STAGING and ANALYTICS schemas.",
    logo: LOGO.sql,
    schema: "Business Logic",
    stage: "05",
  },
  {
    title: "Power BI",
    desc: "Interactive dashboards for executive business insights.",
    logo: LOGO.powerbi,
    schema: "Visualization",
    stage: "06",
  },
];

const pipelineComponents = [
  { key: "py", name: "Python Generator", role: "Replay batches", logo: LOGO.python, healthy: "Running" },
  { key: "s3", name: "AWS S3", role: "Raw landing zone", logo: LOGO.s3, healthy: "Connected" },
  { key: "pipe", name: "Snowpipe", role: "Auto-ingest", logo: LOGO.snowpipe, healthy: "Listening" },
  { key: "sf", name: "Snowflake", role: "Cloud warehouse", logo: LOGO.snowflake, healthy: "Active" },
  { key: "sql", name: "SQL Transforms", role: "RAW → STG → ANALYTICS", logo: LOGO.sql, healthy: "Healthy" },
  { key: "pbi", name: "Power BI", role: "Reporting layer", logo: LOGO.powerbi, healthy: "Connected" },
];

/* ---------- Nav ---------- */

const navLinks: { href: string; label: string; icon: typeof Gauge }[] = [
  { href: "#challenge", label: "Challenge", icon: Sparkles },
  { href: "#architecture", label: "Architecture", icon: Workflow },
  { href: "#pipeline", label: "Pipeline", icon: Gauge },
  { href: "#stack", label: "Stack", icon: Layers },
  { href: "#features", label: "Capabilities", icon: Rocket },
  { href: "#dashboards", label: "Dashboards", icon: LayoutDashboard },
  { href: "#embed", label: "Portal", icon: Globe2 },
];

/* ---------- Page ---------- */

function Index() {
  // Interactive mock-live state — refreshed by the global Refresh button.
  const [refreshing, setRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date>(() => new Date());
  const [status, setStatus] = useState<any>(null);
  const [pipeline, setPipeline] = useState<any>(null);
  const [insights, setInsights] = useState<any[]>([]);
  const [activity, setActivity] = useState<any[]>([]);

  const refresh = useCallback(async () => {

    if (refreshing) return;

    setRefreshing(true);

    // REMOVE THIS
    // await startPipeline();

    await loadKPIs();
    await loadStatus();
    await loadPipeline();
    await loadInsights();
    await loadActivity();

    setLastRefresh(new Date());

    setRefreshing(false);

}, [refreshing]);

  // Deterministic-ish variation seeded by tick so values change on each refresh.
  const [kpis, setKpis] = useState<any>(null);
  useEffect(() => {

    loadKPIs();

    loadStatus();

    loadPipeline();

    loadInsights();
    loadActivity();

    const interval = setInterval(() => {

        loadKPIs();

        loadStatus();

        loadPipeline();

        loadInsights();
        loadActivity();

    },5000);

    return () => clearInterval(interval);

},[]);
const loadKPIs = async () => {
    try {
        console.log("Loading KPIs...");

        const data = await getKPIs();

        console.log("API returned:", data);

        setKpis(data);

        console.log("State updated");
    } catch (err) {
        console.error("API Error:", err);
    }
};

const loadStatus = async () => {
    try {
        const data = await getStatus();
        setStatus(data);
    } catch (err) {
        console.error(err);
    }
};

const loadPipeline = async () => {
    try {
        const data = await getPipelineStatus();

        setPipeline(data);

    } catch (err) {

        console.error(err);

    }
};

const handleStartPipeline = async () => {

    await startPipeline();

    await loadPipeline();

};

const handleStopPipeline = async () => {

    await stopPipeline();

    await loadPipeline();

};

const loadInsights = async () => {
    try {

        const data = await getInsights();

        setInsights(data.insights);

    } catch (err) {

        console.error(err);

    }
};

const loadActivity = async () => {
    try {
        const data = await getActivity();
        console.log("Activity data:", data);
        setActivity(data);
    } catch (err) {
        console.error(err);
    }
};

  return (
    <div className="min-h-screen bg-background text-foreground antialiased">
      <Nav onRefresh={refresh} refreshing={refreshing} lastRefresh={lastRefresh} />
      <Hero
  kpis={
    kpis
      ? [
          {
            k: `${(kpis.total_sales / 10000000).toFixed(1)} M`,
            v: "Total Revenue",
          },
          {
            k: kpis.total_orders.toLocaleString(),
            v: "Orders Processed",
          },
          {
    k: `${(kpis.total_profit / 1000000).toFixed(2)}M`,
    v: "Total Profit",
},
          {
            k: `${kpis.avg_profit_margin.toFixed(1)}%`,
            v: "Avg Profit Margin",
          },
        ]
      : [
          { k: "...", v: "Revenue Tracked" },
          { k: "...", v: "Orders Analysed" },
          { k: "...", v: "Total Profit" },
          { k: "...", v: "Avg Profit Margin" },
        ]
  }
  batches={pipeline?.total_batches || 0}
/>
      <AIInsights insights={insights} />
      <BusinessChallenge />
      <Architecture />
      <LivePipeline
        filesPerStage={[
    pipeline?.current_batch || 0,
    pipeline?.current_batch || 0,
    pipeline?.current_batch || 0,
    pipeline?.current_batch || 0,
    pipeline?.current_batch || 0,
    pipeline?.current_batch || 0,
]}
        lastRefresh={lastRefresh}
        onRefresh={refresh}
        refreshing={refreshing}
        status={status}
        pipeline={pipeline}
        onStart={handleStartPipeline}
        onStop={handleStopPipeline}
      />
      <TechStack />
      <Features />
      <DashboardPreview />
      <PowerBIEmbed lastRefresh={lastRefresh} />
      <Footer />
    </div>
  );
}

/* ---------- Sections ---------- */

function Nav({
  onRefresh,
  refreshing,
  lastRefresh,
}: {
  onRefresh: () => Promise<void> | void;
  refreshing: boolean;
  lastRefresh: Date;
}) {
  return (
    <header className="fixed top-0 inset-x-0 z-50">
      <div className="mx-auto mt-4 max-w-7xl px-4">
        <div className="glass-panel flex items-center gap-3 rounded-2xl px-4 py-2.5">
          <a href="#top" className="flex shrink-0 items-center gap-2.5">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-violet-gradient shadow-glow">
              <Activity className="h-4 w-4 text-primary-foreground" strokeWidth={2.5} />
            </span>
            <span className="font-display text-sm font-semibold tracking-wide">
              SALESPULSE <span className="text-gradient-violet">360</span>
            </span>
          </a>

          <nav className="ml-2 hidden flex-1 items-center justify-center gap-1 text-sm text-muted-foreground lg:flex">
            {navLinks.map((l) => (
              <a
                key={l.href}
                href={l.href}
                className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-[13px] transition hover:bg-white/5 hover:text-foreground"
              >
                <l.icon className="h-3.5 w-3.5 text-primary/80" strokeWidth={2} />
                {l.label}
              </a>
            ))}
          </nav>

          <div className="ml-auto flex items-center gap-2">
            <button
              onClick={onRefresh}
              disabled={refreshing}
              className="hidden items-center gap-1.5 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-[12px] font-medium text-foreground transition hover:bg-white/10 disabled:opacity-60 md:inline-flex"
              title={`Last Successful Refresh: ${lastRefresh.toLocaleTimeString()}`}
            >
              <RefreshCw className={`h-3.5 w-3.5 text-primary ${refreshing ? "animate-spin" : ""}`} />
              {refreshing ? "Refreshing…" : "Refresh"}
            </button>
            <a
              href="#embed"
              className="group inline-flex items-center gap-1.5 rounded-xl bg-violet-gradient px-4 py-2 text-xs font-medium text-primary-foreground shadow-glow transition hover:brightness-110 md:text-sm"
            >
              Open Portal 
              <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}

function AIInsights({
    insights,
}: {
    insights: any[];
}) {
    return (
        <section className="py-12">
            <div className="mx-auto max-w-7xl px-6">

                <div className="glass-card rounded-3xl p-8">

                    <h2 className="text-3xl font-bold text-gradient-violet">
                        Executive Insights
                    </h2>

                    <p className="mt-2 text-muted-foreground">
                        Business insights generated from the latest sales data and KPI metrics.
                    </p>

                    <div className="mt-8 grid gap-4 md:grid-cols-2">

                        {insights.map((item, index) => (

                            <div
                                key={index}
                                className="rounded-2xl border border-white/10 bg-white/5 p-5"
                            >
                                <div className="text-base">
                                    {item}
                                </div>
                            </div>

                        ))}

                    </div>

                </div>

            </div>
        </section>
    );
}

function Hero({ kpis, batches }: { kpis: { k: string; v: string }[]; batches: number }) {
  return (
    <section id="top" className="bg-hero relative overflow-hidden pt-40 pb-28">
      <div className="absolute inset-0 grid-bg opacity-40" />
      <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent" />

      <div className="relative mx-auto max-w-7xl px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="mx-auto max-w-3xl text-center"
        >
          <div className="mx-auto inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3.5 py-1.5 text-xs text-muted-foreground backdrop-blur">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-success" />
            </span>
            Live · {batches.toLocaleString()} batches streamed
          </div>

          <h1 className="mt-6 font-display text-5xl font-semibold leading-[1.05] tracking-tight md:text-7xl">
            <span className="text-gradient">Sales intelligence,</span>
            <br />
            <span className="text-gradient-violet">streamed from cloud to dashboard.</span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-muted-foreground md:text-lg">
            SalesPulse360 demonstrates a complete cloud analytics workflow. Historical sales events are replayed using Python, stored in AWS S3, automatically ingested into Snowflake through Snowpipe, transformed using SQL, and visualized in Power BI through a web-based Executive Analytics Portal.
          </p>

          <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
            <a
              href="#embed"
              className="group inline-flex items-center gap-2 rounded-xl bg-violet-gradient px-6 py-3 text-sm font-medium text-primary-foreground shadow-glow transition hover:brightness-110"
            >
             Open Portal
              <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
            </a>
            <a
              href="#architecture"
              className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-6 py-3 text-sm font-medium text-foreground backdrop-blur transition hover:bg-white/10"
            >
              View Architecture
            </a>
          </div>
        </motion.div>

        <motion.div
          key={kpis.map((k) => k.k).join("|")}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mx-auto mt-16 grid max-w-4xl grid-cols-2 gap-3 md:grid-cols-4"
        >
          {kpis.map((s) => (
            <div key={s.v} className="glass-card rounded-2xl p-5 text-center">
              <div className="font-display text-2xl font-semibold text-gradient-violet">{s.k}</div>
              <div className="mt-1 text-xs uppercase tracking-wider text-muted-foreground">{s.v}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}


function BusinessChallenge() {
  const points = [
    {
      icon: Map,
      title: "Fragmented data",
      desc: "Sales events live across operational systems with inconsistent formats and no single source of truth.",
    },
    {
      icon: Gauge,
      title: "Delayed reporting",
      desc: "Manual exports and batch reports give executives a view of the business that is already days out of date.",
    },
    {
      icon: LineChart,
      title: "Limited visibility",
      desc: "Disconnected dashboards make it hard to follow revenue, margins, customers and operations in one place.",
    },
  ];
  return (
    <section id="challenge" className="relative py-24">
      <div className="mx-auto max-w-6xl px-6">
        <SectionHeader
          tag="Business Challenge"
          title="From scattered sales data to a unified analytics experience"
          subtitle="The Campfly dataset was a static Excel file with no pipeline, no automation and no live view. SalesPulse360 demonstrates how to build a complete cloud analytics platform that ingests, transforms and visualizes sales data in near real-time."
        />
        <div className="mt-12 grid grid-cols-1 gap-4 md:grid-cols-3">
          {points.map((p, i) => (
            <motion.div
              key={p.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.07 }}
              className="glass-card rounded-2xl p-6"
            >
              <div className="mb-4 grid h-10 w-10 place-items-center rounded-lg bg-violet-gradient shadow-glow">
                <p.icon className="h-4 w-4 text-primary-foreground" />
              </div>
              <div className="font-display text-base font-semibold">{p.title}</div>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{p.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Architecture() {
  return (
    <section id="architecture" className="relative py-28 bg-gradient-to-b from-background via-background to-surface/30">
      <div className="mx-auto max-w-7xl px-6">
        <SectionHeader
  tag="Architecture"
  title="System Architecture "
  subtitle="An end-to-end enterprise cloud analytics platform demonstrating how replay-generated sales events move through cloud storage, automated ingestion, SQL transformations and executive reporting."
/>
    

        <div className="mt-14 grid grid-cols-2 gap-4 md:grid-cols-4">
          {architecture.map((a, i) => (
            <motion.div
              key={a.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, delay: i * 0.06 }}
              className="glass-card group relative overflow-hidden rounded-2xl border border-white/5 p-6 transition-all duration-300 hover:-translate-y-2 hover:border-violet-500/50 hover:shadow-[0_0_35px_rgba(139,92,246,0.35)]"
            >
              <>
  <div className="absolute right-4 top-4 rounded-full bg-violet-500/15 px-3 py-1 text-[10px] font-bold text-violet-300">
    STEP {String(i + 1).padStart(2, "0")}
  </div>

  <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-white/5 transition-all duration-300 group-hover:scale-110">
    <TechLogo
    src={a.logo}
    alt={a.title}
    className="h-8 w-8 transition-all duration-500 group-hover:scale-125 group-hover:rotate-6"
/>
  </div>

  <h3 className="font-display text-lg font-bold tracking-wide group-hover:text-violet-300 transition-colors">
    {a.title}
  </h3>

  <p className="mt-3 text-sm leading-6 text-muted-foreground group-hover:text-gray-300 transition-colors">
    {a.desc}
  </p>

  <div className="mt-5 rounded-xl border border-violet-500/20 bg-violet-500/5 px-4 py-3 transition-all duration-300 group-hover:border-violet-400/50 group-hover:bg-violet-500/10">
    <div className="text-[10px] uppercase tracking-widest text-primary">
      Responsibility
    </div>

    <div className="mt-1 text-sm font-medium">
      {a.schema}
    </div>
  </div>
</>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* Merged Pipeline Monitor + System Status — one interactive live view */
function LivePipeline({
  filesPerStage,
  lastRefresh,
  onRefresh,
  refreshing,
  status,
  pipeline,
  onStart,
  onStop,
}: {
  filesPerStage: number[];
  lastRefresh: Date;
  onRefresh: () => Promise<void> | void;
  refreshing: boolean;
  status: any;
  pipeline?: any;
  onStart: () => Promise<void>;

  onStop: () => Promise<void>;
}) {
  return (
    <section id="pipeline" className="relative py-24">
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 text-xs font-medium uppercase tracking-widest text-primary">
              <span className="h-px w-6 bg-primary" /> Enterprise Monitoring
            </div>
            <h2 className="mt-3 font-display text-3xl font-semibold md:text-4xl">
              Enterprise Data <span className="text-gradient-violet">Pipeline Health</span>
            </h2>
            <p className="mt-2 max-w-xl text-sm text-muted-foreground">
              Monitor every stage of the SalesPulse360 cloud analytics pipeline. Refresh the portal to retrieve the latest KPI values and infrastructure status from the backend.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden text-right text-[11px] text-muted-foreground sm:block">
              <div className="uppercase tracking-widest">Last Successful Refresh</div>
              <div className="font-mono text-foreground">{lastRefresh.toLocaleTimeString()}</div>
            </div>
              <button
    onClick={async () => {
        await onStart();
        await onRefresh();
    }}
    disabled={refreshing}
    className="rounded-xl bg-green-600 px-4 py-2 text-xs text-white disabled:opacity-50"
>
    Start
</button>
  <button
    onClick={async () => {
        await onStop();
        await onRefresh();
    }}
    disabled={refreshing}
    className="rounded-xl bg-red-600 px-4 py-2 text-xs text-white disabled:opacity-50"
>
    Stop
</button>

            <button
              onClick={onRefresh}
              disabled={refreshing}
              className="inline-flex items-center gap-2 rounded-xl bg-violet-gradient px-4 py-2.5 text-xs font-medium text-primary-foreground shadow-glow transition hover:brightness-110 disabled:opacity-60"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? "animate-spin" : ""}`} />
              {refreshing ? "Fetching latest…" : "Refresh Pipeline"}
            </button>
          </div>
        </div>

        <div className="glass-card mt-10 overflow-hidden rounded-3xl p-6 md:p-10">
          {/* Animated flow */}
          <div className="mb-8 rounded-2xl border border-white/10 bg-white/5 p-5">
  <div className="flex items-center justify-between">

    <div>
      <div className="text-sm text-muted-foreground">
        Current Stage
      </div>

      <div className="text-xl font-semibold text-white">
        {pipeline?.current_stage}
      </div>
    </div>

    <div className="text-right">
      <div className="text-sm text-muted-foreground">
        Batch Progress
      </div>

      <div className="text-xl font-semibold text-primary">
        {pipeline?.current_batch} / {pipeline?.total_batches}
      </div>
    </div>

  </div>

  <div className="mt-4 h-3 overflow-hidden rounded-full bg-white/10">
    <div
      className="h-full rounded-full bg-violet-500 transition-all duration-700"
      style={{
        width: `${
          pipeline?.total_batches
            ? (pipeline.current_batch / pipeline.total_batches) * 100
            : 0
        }%`,
      }}
    />
  </div>

  <div className="mt-2 text-xs text-muted-foreground">
    {pipeline?.uploaded_rows} Rows Processed
  </div>
</div>
          <div className="relative flex flex-wrap items-center justify-between gap-y-8">
            {pipelineComponents.map((s, i) => (
              <div key={s.key} className="relative flex items-center gap-3 md:gap-4">
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: i * 0.08 }}
                  className="flex flex-col items-center gap-2"
                >
                  <div className="relative grid h-14 w-14 place-items-center rounded-2xl bg-white/5 ring-1 ring-white/10 shadow-glow">
                    <TechLogo src={s.logo} alt={s.name} className="h-7 w-7" />
                    <span className="absolute -top-1 -right-1 flex h-3 w-3">
                      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-70" />
                      <span className="relative inline-flex h-3 w-3 rounded-full bg-success" />
                    </span>
                  </div>
                  <div className="text-[11px] font-medium text-muted-foreground">{s.name}</div>
                </motion.div>
                {i < pipelineComponents.length - 1 && (
                  <div className="relative mx-1 hidden h-px w-10 overflow-hidden bg-white/10 md:block lg:w-14">
                    <motion.div
                      className="absolute inset-y-0 left-0 w-1/3 bg-gradient-to-r from-transparent via-primary to-transparent"
                      animate={{ x: ["-100%", "300%"] }}
                      transition={{ duration: 2.2, repeat: Infinity, ease: "linear", delay: i * 0.25 }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Component status grid */}
          <div className="mt-10 grid grid-cols-1 gap-3 border-t border-white/5 pt-6 sm:grid-cols-2 lg:grid-cols-4">
            {pipelineComponents.map((c, i) => (
              <div
                key={c.key}
                className="rounded-xl border border-white/5 bg-white/[0.03] p-4 transition hover:border-primary/40 hover:shadow-glow"
              >
                <div className="flex items-center gap-3">
                  <div className="grid h-8 w-8 place-items-center rounded-lg bg-white/5 ring-1 ring-white/10">
                    <TechLogo src={c.logo} alt={c.name} className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">

  <div className="text-[12px] font-semibold text-foreground">
    {c.name}
  </div>

  <div className="text-[10px] text-muted-foreground">
    {c.role}
  </div>

  <div className="mt-2 space-y-1">

    <div className="flex items-center justify-between text-[10px]">
      <span className="text-muted-foreground">
        Status
      </span>

      <span
  className={`font-medium ${
    ({
      py: pipeline?.python,
      s3: pipeline?.s3,
      pipe: pipeline?.snowpipe,
      sf: pipeline?.snowflake,
      sql: pipeline?.sql,
      pbi: pipeline?.powerbi,
    }[c.key] === "Running")
      ? "text-yellow-400"
      : "text-success"
  }`}
>
  {({
    py: pipeline?.python,
    s3: pipeline?.s3,
    pipe: pipeline?.snowpipe,
    sf: pipeline?.snowflake,
    sql: pipeline?.sql,
    pbi: pipeline?.powerbi,
  }[c.key] || "Idle")}
</span>
    </div>

    <div className="flex items-center justify-between text-[10px]">
      <span className="text-muted-foreground">
        Last Sync
      </span>

      <span className="font-mono text-foreground">
        {lastRefresh.toLocaleTimeString()}
      </span>
    </div>

  </div>

</div>  

      </div>       

    </div>         

  ))}

          </div>
        </div>
      </div>
    </section>
  );
}

function TechStack() {
  return (
    <section id="stack" className="relative py-24">
      <div className="mx-auto max-w-7xl px-6">
        <SectionHeader
          tag="Technology Stack"
          title="Six technologies, one cohesive platform"
          subtitle="The exact tools used to build SalesPulse 360 — nothing more, nothing less."
        />

        <div className="mt-14 mx-auto grid max-w-7xl grid-cols-1 gap-5 sm:grid-cols-1 lg:grid-cols-6 place-items-center">
          {techStack.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.07 }}
              className="glass-card group relative flex flex-col items-center gap-3 rounded-2xl p-6 transition hover:-translate-y-1 hover:shadow-glow"
            >
              <div className="relative grid h-16 w-16 place-items-center rounded-2xl bg-white/5 ring-1 ring-white/10 transition group-hover:ring-primary/40">
                <TechLogo src={t.logo} alt={t.name} className="h-9 w-9 transition duration-500 group-hover:scale-110" />
                <div
                  className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition group-hover:opacity-100"
                  style={{ boxShadow: "0 0 40px 4px rgb(139 92 246 / 0.35) inset" }}
                />
              </div>
              <div className="text-center">
                <div className="font-display text-sm font-semibold">{t.name}</div>
                <div className="text-[11px] text-muted-foreground">{t.role}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Features() {
  return (
    <section id="features" className="relative py-28">
      <div className="mx-auto max-w-7xl px-6">
        <SectionHeader
          tag="Project Capabilities"
          title="What SalesPulse 360 actually delivers"
          subtitle="Each capability maps to a real component shipped in the project."
        />

        <div className="mt-14 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.05 }}
              className="glass-card group relative overflow-hidden rounded-2xl p-6 transition hover:-translate-y-0.5"
            >
              <div className="mb-5 grid h-11 w-11 place-items-center rounded-xl bg-violet-gradient shadow-glow">
                <f.icon className="h-5 w-5 text-primary-foreground" />
              </div>
              <h3 className="font-display text-base font-semibold">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{f.desc}</p>
              <div className="pointer-events-none absolute -right-16 -top-16 h-40 w-40 rounded-full bg-primary/15 opacity-0 blur-3xl transition group-hover:opacity-100" />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function DashboardPreview() {
  return (
    <section id="dashboards" className="relative py-28">
      <div className="mx-auto max-w-7xl px-6">
        <SectionHeader
  tag="Executive Dashboards"
  title="Interactive Business Intelligence"
  subtitle="Explore six enterprise dashboards powered by Snowflake analytics and designed for executive decision-making."
/>

        <div className="mt-14 grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
          {dashboards.map((d, i) => (
            <motion.a
href="#embed"
              key={d.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.55, delay: i * 0.06 }}
              className="glass-card group relative overflow-hidden rounded-2xl border border-white/5 transition-all duration-500 hover:-translate-y-2 hover:border-violet-500/40 hover:shadow-[0_0_40px_rgba(139,92,246,.35)]"
            >
              
              <div className="relative h-64 overflow-hidden bg-surface">
                <div className="mb-3 inline-flex items-center rounded-full bg-violet-500/15 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-violet-300">
    Dashboard {i + 1}
</div>
                <img
                  src={d.img}
                  
                  alt={`${d.title} dashboard`}
                  className="h-full w-full object-cover transition duration-700 group-hover:scale-[1.12]"
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-background/80 via-background/10 to-transparent" />
                <div
                  className="pointer-events-none absolute inset-0 opacity-0 transition duration-500 group-hover:opacity-100"
                  style={{ background: "radial-gradient(circle at 50% 100%, rgb(139 92 246 / 0.35), transparent 60%)" }}
                />
        
                <div className="absolute left-4 top-4 inline-flex items-center gap-1.5 rounded-full bg-black/40 px-2.5 py-1 text-[10px] font-medium uppercase tracking-wider backdrop-blur">
                  <span className="h-1.5 w-1.5 rounded-full bg-success" />
                  Page {i + 1}
                </div>
              </div>
              <div className="p-5">
                <div className="font-display text-base font-semibold">{d.title}</div>
                <div className="mt-2 text-sm leading-6 text-muted-foreground">

    {d.desc}

</div>
                <div className="mt-4 flex items-center justify-between">

<span className="text-xs text-violet-300">
Executive Dashboard
</span>

<div className="flex items-center gap-2 text-xs font-semibold text-primary group-hover:translate-x-1 transition-all">

Open Dashboard

<ArrowRight className="h-3 w-3"/>

</div>

</div>
               
              </div>
              <div className="absolute bottom-0 left-0 h-[3px] w-0 bg-gradient-to-r from-violet-500 to-cyan-400 transition-all duration-500 group-hover:w-full"/>
            </motion.a>
          ))}
        </div>
      </div>
    </section>
  );
}



function PowerBIEmbed({ lastRefresh }: { lastRefresh: Date }) {

  return (
    <section id="embed" className="relative py-28">
      <div className="mx-auto max-w-7xl px-6">
        <SectionHeader
          tag="Executive Analytics Portal"
          title="Interactive Power BI Dashboard"
          subtitle="The embedded Power BI dashboard allows business users to analyze revenue, profitability, products, customers, regions and operational performance from a single interface."
        />

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.7 }}
          className="mt-12"
        >
          <div className="glass-card relative overflow-hidden rounded-3xl p-3 shadow-elevated">
            <div className="flex items-center justify-between px-4 py-2.5">
              <div className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-destructive/70" />
                <span className="h-2.5 w-2.5 rounded-full bg-warning/80" />
                <span className="h-2.5 w-2.5 rounded-full bg-success/80" />
              </div>
              <div className="flex items-center gap-2 text-[11px] font-mono text-muted-foreground">
                <Lock className="h-3 w-3" /> salespulse360 · powerbi-embed
              </div>
              <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                <Zap className="h-3 w-3 text-primary" /> Embedded
              </div>
            </div>

            <div className="relative overflow-hidden rounded-2xl border border-white/5 bg-surface">
              <div className="relative aspect-[16/9] w-full">
                <PowerBIClient />
                <div className="absolute inset-0 bg-gradient-to-t from-background/40 via-transparent to-transparent" />
                <div className="absolute bottom-5 left-5 right-5 flex flex-wrap items-center justify-between gap-3">
                  <div className="glass-panel inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs">
                    <span className="h-1.5 w-1.5 rounded-full bg-success animate-pulse-glow" />
                    Connected to ANALYTICS_SCHEMA via Power BI
                  </div>
                  <a
    href="/report"
    target="_blank"
    rel="noopener noreferrer"
    className="inline-flex items-center gap-1.5 rounded-full bg-violet-gradient px-4 py-2 text-xs font-medium text-primary-foreground shadow-glow hover:brightness-110"
>
                    Open full report <ArrowRight className="h-3.5 w-3.5" />
                  </a>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2 px-4 py-3">
              {["Period: All", "Currency: All", "Region: Global", "Channel: All"].map((c) => (
                <span
                  key={c}
                  className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] text-muted-foreground"
                >
                  <Sliders className="h-3 w-3 text-primary/80" />
                  {c}
                </span>
              ))}
              <span className="ml-auto inline-flex items-center gap-1.5 text-[11px] text-muted-foreground">
                <LineChart className="h-3.5 w-3.5 text-primary" />
                6 report pages · refreshed {lastRefresh.toLocaleTimeString()}
              </span>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="relative border-t border-white/5 bg-surface/40 pt-16 pb-10">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid grid-cols-1 gap-10 md:grid-cols-4">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2.5">
              <span className="grid h-8 w-8 place-items-center rounded-lg bg-violet-gradient shadow-glow">
                <Activity className="h-4 w-4 text-primary-foreground" strokeWidth={2.5} />
              </span>
              <span className="font-display text-sm font-semibold">
                SALESPULSE <span className="text-gradient-violet">360</span>
              </span>
            </div>
            <p className="mt-4 max-w-md text-sm leading-relaxed text-muted-foreground">
              SalesPulse360 is a cloud analytics project demonstrating how historical sales events move through Python, AWS S3, Snowpipe, Snowflake and Power BI to produce interactive business dashboards.
            </p>
            <div className="mt-5 flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground">
              <span className="rounded-full border border-success/30 bg-success/10 px-2.5 py-1 text-success">
                Live
              </span>
              <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1">
                Version 1.0 • Production Demo
              </span>
              <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1">
                Real-Time Analytics Platform
              </span>
            </div>
          </div>

          <div>
            <div className="text-xs font-semibold uppercase tracking-widest text-foreground">
              Technology Stack
            </div>
            <ul className="mt-4 space-y-2 text-sm text-muted-foreground">
              {techStack.map((t) => (
                <li key={t.name} className="flex items-center gap-2.5">
                  <TechLogo src={t.logo} alt={t.name} className="h-4 w-4" />
                  <span>{t.name}</span>
                  <span className="text-[11px] text-muted-foreground/60">· {t.role}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <div className="text-xs font-semibold uppercase tracking-widest text-foreground">
              Navigate
            </div>
            <ul className="mt-4 space-y-2 text-sm text-muted-foreground">
              {navLinks.map((l) => (
                <li key={l.href}>
                  <a href={l.href} className="hover:text-foreground transition">{l.label}</a>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="mt-6 text-sm text-muted-foreground">
    Developed by <span className="text-white font-medium">Karthikeya Sriramoju</span>
</div>

        <div className="mt-12 flex flex-wrap items-center justify-between gap-3 border-t border-white/5 pt-6 text-[11px] text-muted-foreground">
          <div>© {new Date().getFullYear()} SalesPulse 360 · Enterprise Cloud Analytics Platform</div>
          <div className="flex items-center gap-2 font-mono">
            <ShieldCheck className="h-3.5 w-3.5 text-primary" />
            Python · AWS S3 · Snowpipe · Snowflake · SQL · Power BI · React
          </div>
        </div>
      </div>
    </footer>
  );
}

function SectionHeader({ tag, title, subtitle }: { tag: string; title: string; subtitle: string }) {
  return (
    <div className="mx-auto max-w-2xl text-center">
      <div className="inline-flex items-center gap-2 text-xs font-medium uppercase tracking-widest text-primary">
        <span className="h-px w-6 bg-primary" /> {tag} <span className="h-px w-6 bg-primary" />
      </div>
      <h2 className="mt-3 font-display text-3xl font-semibold md:text-5xl">
        {title.split(" ").map((w, i, arr) =>
          i === arr.length - 1 ? <span key={i} className="text-gradient-violet"> {w}</span> : ` ${w}`,
        )}
      </h2>
      <p className="mx-auto mt-4 max-w-xl text-sm leading-relaxed text-muted-foreground md:text-base">
        {subtitle}
      </p>
    </div>
  );
}
