// Sanadi AI's mark: a simple circular monogram. Used in the sidebar and as
// the assistant's avatar so the brand mark and the "who's speaking"
// indicator are the same shape.

interface MonogramProps {
  size?: number;
  inverted?: boolean;
}

export default function Monogram({ size = 32, inverted = false }: MonogramProps) {
  return (
    <div
      className={`flex items-center justify-center rounded-full shrink-0 ${
        inverted ? "bg-sanadi-cream text-sanadi-black" : "bg-sanadi-black text-sanadi-cream"
      }`}
      style={{ width: size, height: size }}
    >
      <span
        className="font-sans font-semibold"
        style={{ fontSize: size * 0.42, letterSpacing: "-0.02em" }}
      >
        S
      </span>
    </div>
  );
}
