import { Link } from "react-router-dom";

export default function CardVagas({ to, icone, titulo, descricao, corHover }) {
  return (
    <Link to={to} className="no-underline w-full max-w-70">
      <div
        className="w-full h-full flex flex-col items-center justify-center gap-4 p-10 rounded-[20px] cursor-pointer transition-all duration-300"
        style={{
          background: "rgba(255,255,255,0.04)",
          border: "1px solid rgba(255,255,255,0.09)",
          backdropFilter: "blur(16px)",
          boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
          minHeight: "210px",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.border = `1px solid ${corHover}99`;
          e.currentTarget.style.boxShadow = `0 8px 48px ${corHover}26`;
          e.currentTarget.style.background = `${corHover}0f`;
          e.currentTarget.style.transform = "scale(1.03)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.border = "1px solid rgba(255,255,255,0.09)";
          e.currentTarget.style.boxShadow = "0 8px 32px rgba(0,0,0,0.4)";
          e.currentTarget.style.background = "rgba(255,255,255,0.04)";
          e.currentTarget.style.transform = "scale(1)";
        }}
      >
        {icone}
        <span className="text-[20px] font-semibold text-white text-center">{titulo}</span>
        <span className="text-[13px] font-normal text-[#A0AEC0] text-center leading-relaxed">{descricao}</span>
      </div>
    </Link>
  );
}
