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
import data from "./struct.json";

type Item = { facet?: string; reading?: string; text: string };
type Step = { measures: string; start: number; end: number; music: string; now: Item[]; also: Item[] };
type Reading = Item & { start: number; end: number; n: number; of: number };
type Seg = {
  id: string; measures: string; label: string; start: number; end: number; title: string;
  steps: Step[]; base: Item[]; readings: Reading[]; carryover: Item[];
};

const FPS = data.fps;
const SEGS = data.segments as Seg[];
const MEASURES = data.measures as [number, number][];
const FONT = '"Noto Sans SC", "Microsoft YaHei", sans-serif';
const BRIGHT = "#eef1f6";
const SOFT = "rgba(214,220,232,0.78)";
const FAINT = "rgba(170,178,196,0.6)";
const ACCENT = "#d6b67e";
const ALSO = "#9fc3d8";
const PAD = 120;
const LEFT_W = 960;
const RIGHT_X = PAD + LEFT_W + 60;
const RIGHT_W = 1920 - RIGHT_X - PAD;
const f = (s: number) => Math.round(s * FPS);

// pick a font size so the items fit the box (deterministic estimate)
const fit = (items: Item[], width: number, height: number, max: number, min: number) => {
  for (let size = max; size >= min; size -= 1) {
    const perLine = Math.floor(width / size) - 1;
    const h = items.reduce((acc, it) => acc + Math.ceil(it.text.length / perLine) * size * 1.45 + size * 0.55, 0);
    if (h <= height) return size;
  }
  return min;
};

const measureAt = (t: number) => {
  let m = 1;
  for (const [n, s] of MEASURES) if (s <= t) m = n;
  return m;
};

const Reveal: React.FC<{ delay: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ delay, children, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const k = spring({ frame: frame - delay, fps, config: { damping: 200 }, durationInFrames: 14 });
  return <div style={{ ...style, opacity: k, transform: `translateY(${(1 - k) * 10}px)` }}>{children}</div>;
};

const StepView: React.FC<{ step: Step }> = ({ step }) => {
  const frame = useCurrentFrame();
  const dur = f(step.end) - f(step.start);
  const out = interpolate(frame, [dur - 8, dur], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const nowSize = fit(step.now, LEFT_W, 400, 38, 22);
  const alsoSize = fit(step.also, RIGHT_W, 250, 30, 18);
  const n = step.now.length + step.also.length;
  const gap = Math.max(4, Math.min(24, Math.floor((dur * 0.45) / Math.max(1, n))));
  return (
    <AbsoluteFill style={{ opacity: out, fontFamily: FONT }}>
      <Reveal delay={0} style={{ position: "absolute", left: PAD, top: 196, width: LEFT_W, color: ACCENT, fontSize: 25 }}>
        第{step.measures}小节　{step.music}
      </Reveal>
      <div style={{ position: "absolute", left: PAD, top: 246, width: LEFT_W }}>
        {step.now.map((it, i) => (
          <Reveal key={i} delay={6 + i * gap} style={{ color: BRIGHT, fontSize: nowSize, lineHeight: 1.45, marginBottom: nowSize * 0.55 }}>
            {it.text}
          </Reveal>
        ))}
      </div>
      {step.also.length > 0 && (
        <div style={{ position: "absolute", left: RIGHT_X, top: 196, width: RIGHT_W }}>
          <div style={{ color: FAINT, fontSize: 22, marginBottom: 12, letterSpacing: 2 }}>也可以听成</div>
          {step.also.map((it, i) => (
            <Reveal key={i} delay={6 + (step.now.length + i) * gap} style={{ color: ALSO, fontSize: alsoSize, lineHeight: 1.45, marginBottom: alsoSize * 0.5 }}>
              {it.text}
            </Reveal>
          ))}
        </div>
      )}
    </AbsoluteFill>
  );
};

const ReadingView: React.FC<{ r: Reading }> = ({ r }) => {
  const frame = useCurrentFrame();
  const dur = f(r.end) - f(r.start);
  const op = interpolate(frame, [0, 8, dur - 8, dur], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", left: RIGHT_X, top: 480, width: RIGHT_W, opacity: op, fontFamily: FONT }}>
      <div style={{ color: FAINT, fontSize: 20, marginBottom: 8, letterSpacing: 2 }}>完整听法 {r.n}/{r.of}</div>
      <div style={{ color: SOFT, fontSize: 24, lineHeight: 1.45 }}>{r.text}</div>
    </div>
  );
};

const SegmentView: React.FC<{ seg: Seg }> = ({ seg }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const dur = f(seg.end) - f(seg.start);
  const k = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 18 });
  const out = interpolate(frame, [dur - 10, dur], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const baseText = seg.base.map((b) => b.text);
  const baseSize = fit([{ text: baseText.join("　·　") }], 1920 - PAD * 2, 74, 21, 14);
  const carryOp = interpolate(frame, [0, 10, f(6), f(7)], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ fontFamily: FONT, opacity: out }}>
      <div style={{ position: "absolute", left: PAD, top: 72, color: "rgba(176,184,204,0.9)", fontSize: 24, opacity: k }}>
        {seg.id} · 第{seg.measures}小节 · {seg.label}
      </div>
      <div style={{ position: "absolute", left: PAD, top: 106, color: BRIGHT, fontSize: 46, fontWeight: 700, opacity: k }}>{seg.title}</div>
      {seg.carryover.length > 0 && (
        <div style={{ position: "absolute", left: RIGHT_X, top: 110, width: RIGHT_W, color: FAINT, fontSize: 19, lineHeight: 1.4, opacity: carryOp }}>
          {seg.carryover.map((c) => c.text).join("　")}
        </div>
      )}
      {seg.steps.map((st, i) => (
        <Sequence key={i} from={f(st.start) - f(seg.start)} durationInFrames={Math.max(1, f(st.end) - f(st.start))} name={`step ${st.measures}`}>
          <StepView step={st} />
        </Sequence>
      ))}
      {seg.readings.map((r, i) => (
        <Sequence key={`r${i}`} from={f(r.start) - f(seg.start)} durationInFrames={Math.max(1, f(r.end) - f(r.start))} name={`reading ${r.n}`}>
          <ReadingView r={r} />
        </Sequence>
      ))}
      {baseText.length > 0 && (
        <div style={{ position: "absolute", left: PAD, right: PAD, top: 622, opacity: k }}>
          <span style={{ color: ACCENT, fontSize: 18, letterSpacing: 2, marginRight: 14 }}>整段底色</span>
          <span style={{ color: FAINT, fontSize: baseSize, lineHeight: 1.5 }}>{baseText.join("　·　")}</span>
        </div>
      )}
    </AbsoluteFill>
  );
};

const Progress: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const usable = 1920 - PAD * 2;
  return (
    <div style={{ position: "absolute", top: 40, left: PAD, width: usable, height: 6 }}>
      {SEGS.map((s) => {
        const x = (s.start / data.duration) * usable;
        const w = ((s.end - s.start) / data.duration) * usable - 5;
        const fill = Math.min(1, Math.max(0, (t - s.start) / (s.end - s.start)));
        return (
          <div key={s.id} style={{ position: "absolute", left: x, width: w, height: 5, background: "#383e4c", borderRadius: 3 }}>
            <div style={{ width: `${fill * 100}%`, height: "100%", background: ACCENT, borderRadius: 3 }} />
          </div>
        );
      })}
    </div>
  );
};

const Counter: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <div style={{ position: "absolute", left: PAD, bottom: 34, fontFamily: FONT, color: "rgba(190,198,214,0.75)", fontSize: 24 }}>
      第 <span style={{ color: ACCENT }}>{measureAt(frame / FPS)}</span> / 116 小节
    </div>
  );
};

export const BarcarolleStruct: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#11141c" }}>
    <OffthreadVideo src={staticFile("bg.mp4")} muted />
    <Audio src={staticFile("audio.m4a")} />
    <Progress />
    {SEGS.map((s) => (
      <Sequence key={s.id} from={f(s.start)} durationInFrames={f(s.end) - f(s.start)} name={`${s.id} ${s.title}`}>
        <SegmentView seg={s} />
      </Sequence>
    ))}
    <Counter />
    <div style={{ position: "absolute", right: PAD, bottom: 34, fontFamily: FONT, color: "rgba(170,178,196,0.7)", fontSize: 22 }}>{data.credits}</div>
  </AbsoluteFill>
);

export const StructComposition = () => (
  <Composition id="BarcarolleStruct" component={BarcarolleStruct} durationInFrames={Math.round(data.duration * FPS)} fps={FPS} width={1920} height={1080} />
);
