import React from "react";
import {
  AbsoluteFill,
  Audio,
  Composition,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import data from "./data.json";

type Para = { text: string; start: number; end: number };
type Seg = {
  id: string;
  measures: string;
  label: string;
  start: number;
  end: number;
  title: string;
  paragraphs: Para[];
};

const FPS = data.fps;
const SEGS = data.segments as Seg[];
const MEASURES = data.measures as [number, number][];
const FONT = '"Noto Sans SC", "Microsoft YaHei", sans-serif';
const BRIGHT = "#eef1f6";
const DIM = "rgba(200,206,220,0.42)";
const ACCENT = "#d6b67e";
const PAD_X = 140;
const TEXT_BOTTOM = 690;

const f = (s: number) => Math.round(s * FPS);

const measureAt = (t: number) => {
  let m = 1;
  for (const [n, s] of MEASURES) if (s <= t) m = n;
  return m;
};

const Progress: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const usable = 1920 - PAD_X * 2;
  return (
    <div style={{ position: "absolute", top: 40, left: PAD_X, width: usable, height: 6 }}>
      {SEGS.map((s) => {
        const x = (s.start / data.duration) * usable;
        const w = ((s.end - s.start) / data.duration) * usable - 5;
        const fill = Math.min(1, Math.max(0, (t - s.start) / (s.end - s.start)));
        return (
          <div key={s.id} style={{ position: "absolute", left: x, width: w, height: 5, background: "#383e4c", borderRadius: 3 }}>
            <div style={{ width: `${fill * 100}%`, height: "100%", background: ACCENT, borderRadius: 3, opacity: t < s.end ? 1 : 0.45 }} />
          </div>
        );
      })}
    </div>
  );
};

const MeasureCounter: React.FC = () => {
  const frame = useCurrentFrame();
  const m = measureAt(frame / FPS);
  return (
    <div style={{ position: "absolute", left: PAD_X, bottom: 34, fontFamily: FONT, color: "rgba(190,198,214,0.75)", fontSize: 26, letterSpacing: 1 }}>
      第 <span style={{ color: ACCENT, fontVariantNumeric: "tabular-nums" }}>{m}</span> / 116 小节
    </div>
  );
};

const Paragraph: React.FC<{ p: Para; segStart: number; current: boolean }> = ({ p, segStart, current }) => {
  const frame = useCurrentFrame(); // relative to segment sequence
  const { fps } = useVideoConfig();
  const local = frame - f(p.start - segStart);
  const enter = spring({ frame: local, fps, config: { damping: 200 }, durationInFrames: 18 });
  return (
    <p
      style={{
        margin: "0 0 22px 0",
        fontSize: 32,
        lineHeight: 1.6,
        color: current ? BRIGHT : DIM,
        opacity: enter,
        transform: `translateY(${(1 - enter) * 14}px)`,
        transition: "none",
      }}
    >
      {p.text}
    </p>
  );
};

const SegmentScene: React.FC<{ seg: Seg }> = ({ seg }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const dur = f(seg.end) - f(seg.start);
  const t = seg.start + frame / fps;
  const titleIn = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 20 });
  const out = interpolate(frame, [dur - 12, dur], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const shown = seg.paragraphs.filter((p) => p.start <= t + 1e-6);
  const currentIdx = shown.length - 1;
  // keep the newest paragraphs; drop the oldest when they no longer fit (deterministic line estimate)
  const perLine = Math.floor((1920 - PAD_X * 2) / 32);
  const h = (p: Para) => Math.ceil(p.text.length / perLine) * 51 + 22;
  let first = 0;
  while (first < shown.length - 1 && shown.slice(first).reduce((a, p) => a + h(p), 0) > TEXT_BOTTOM - 210) first++;
  const visible = shown.slice(first);
  return (
    <AbsoluteFill style={{ opacity: out, fontFamily: FONT }}>
      <div style={{ position: "absolute", left: PAD_X, top: 72, color: "rgba(176,184,204,0.9)", fontSize: 26, opacity: titleIn }}>
        {seg.id} · 第{seg.measures}小节 · {seg.label}
      </div>
      <div
        style={{
          position: "absolute",
          left: PAD_X,
          top: 112,
          color: BRIGHT,
          fontSize: 48,
          fontWeight: 700,
          opacity: titleIn,
          transform: `translateX(${(1 - titleIn) * -24}px)`,
        }}
      >
        {seg.title}
      </div>
      <div style={{ position: "absolute", left: PAD_X, right: PAD_X, top: 210, height: TEXT_BOTTOM - 210, overflow: "hidden" }}>
        <div>
          {visible.map((p, i) => (
            <Paragraph key={first + i} p={p} segStart={seg.start} current={first + i === currentIdx} />
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const Barcarolle: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#11141c" }}>
      <OffthreadVideo src={staticFile("bg.mp4")} muted />
      <Audio src={staticFile("audio.m4a")} />
      <Progress />
      {SEGS.map((s) => (
        <Sequence key={s.id} from={f(s.start)} durationInFrames={f(s.end) - f(s.start)} name={`${s.id} ${s.title}`}>
          <SegmentScene seg={s} />
        </Sequence>
      ))}
      <MeasureCounter />
      <div style={{ position: "absolute", right: PAD_X, bottom: 34, fontFamily: FONT, color: "rgba(170,178,196,0.7)", fontSize: 24 }}>
        {data.credits}
      </div>
    </AbsoluteFill>
  );
};

export const MyComposition = () => {
  return (
    <Composition
      id="Barcarolle"
      component={Barcarolle}
      durationInFrames={Math.round(data.duration * FPS)}
      fps={FPS}
      width={1920}
      height={1080}
    />
  );
};
