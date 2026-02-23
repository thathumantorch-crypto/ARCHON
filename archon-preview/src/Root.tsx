import "./index.css";
import { Composition } from "remotion";
import { ArchonShowcase } from "./Composition";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ArchonShowcase"
        component={ArchonShowcase}
        durationInFrames={240}
        fps={30}
        width={1280}
        height={720}
      />
    </>
  );
};
