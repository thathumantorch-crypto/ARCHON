import {
  AbsoluteFill,
  interpolate,
  Easing,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const features = [
  {
    title: "Autonomous Learning",
    detail: "Supabase masterclasses, Moltbook peers, and on-demand web research",
  },
  {
    title: "Social Presence",
    detail: "Scheduled Moltbook loops, intelligent replies, and knowledge logging",
  },
  {
    title: "Developer Speed",
    detail: "FastAPI, Streamlit UI, and self-healing tooling orchestrated in Python",
  },
];

const FadeInText: React.FC<{ start: number; children: React.ReactNode }> = ({
  start,
  children,
}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(
    frame,
    [start, start + 20],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.ease,
    }
  );

  const translateY = interpolate(
    frame,
    [start, start + 20],
    [30, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.exp),
    }
  );

  return (
    <div style={{ opacity, transform: `translateY(${translateY}px)` }}>{children}</div>
  );
};

const FeatureCard: React.FC<{ feature: (typeof features)[number]; index: number }> = ({
  feature,
  index,
}) => {
  const frame = useCurrentFrame();
  const base = 70 + index * 45;
  const opacity = interpolate(
    frame,
    [base, base + 20],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.ease,
    }
  );

  return (
    <div
      style={{
        opacity,
        background: "rgba(8, 8, 16, 0.7)",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: 18,
        padding: "18px 22px",
        marginBottom: 16,
        boxShadow: "0 12px 40px rgba(0,0,0,0.35)",
      }}
    >
      <div
        style={{
          fontSize: 22,
          fontWeight: 700,
          letterSpacing: 0.5,
          textTransform: "uppercase",
          color: "#9BE8FF",
          marginBottom: 8,
        }}
      >
        {feature.title}
      </div>
      <div style={{ fontSize: 20, color: "#F8FAFF", lineHeight: 1.4 }}>
        {feature.detail}
      </div>
    </div>
  );
};

export const ArchonShowcase: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const glowShift = interpolate(frame, [0, durationInFrames], [0, 12]);

  return (
    <AbsoluteFill
      style={{
        fontFamily: "'Space Grotesk', 'Segoe UI', sans-serif",
        color: "white",
        background: "radial-gradient(circle at 20% 20%, #1a2b63, #060812)",
        overflow: "hidden",
        padding: "80px 120px",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(circle at 70% 30%, rgba(142, 62, 255, 0.35), transparent ${
            30 + glowShift
          }%), radial-gradient(circle at 30% 70%, rgba(58, 201, 255, 0.25), transparent ${
            25 + glowShift
          }%)`,
          filter: "blur(120px)",
          pointerEvents: "none",
        }}
      />

      <Sequence from={0} durationInFrames={120}>
        <FadeInText start={0}>
          <div style={{ fontSize: 22, letterSpacing: 4, textTransform: "uppercase", color: "#8BD3FF" }}>
            Autonomous Recursive Cognitive Heuristic Operations Network
          </div>
          <div style={{ fontSize: 72, fontWeight: 700, marginTop: 12 }}>ARCHON SHOWCASE</div>
        </FadeInText>
      </Sequence>

      <Sequence from={20}>
        <FadeInText start={20}>
          <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
            <div style={{ fontSize: 28, maxWidth: 600, lineHeight: 1.4 }}>
              ARCHON ingests expert lessons, Moltbook context, and Supabase masterclasses to act as a
              senior Python engineer and social collaborator.
            </div>
            <div style={{ fontSize: 22, opacity: 0.8 }}>
              • FastAPI + Streamlit
              <br />• Supabase mentor API
              <br />• Milvus / fallback knowledgebase
            </div>
          </div>
        </FadeInText>

        <div style={{ marginTop: 56 }}>
          {features.map((feature, index) => (
            <FeatureCard feature={feature} index={index} key={feature.title} />
          ))}
        </div>
      </Sequence>

      <Sequence from={180}>
        <FadeInText start={180}>
          <div style={{ marginTop: 40, fontSize: 28, opacity: 0.9 }}>
            "Humanity's best friend" means persistent learning, graceful self-healing, and transparent telemetry.
          </div>
          <div style={{ fontSize: 22, marginTop: 18, color: "#9BE8FF" }}>
            Initiate the Supabase masterclass loop or Moltbook social cycle directly from the ARCHON console.
          </div>
        </FadeInText>
      </Sequence>
    </AbsoluteFill>
  );
};
