import type { Specialty } from "./products";

// DESIGN.md "부위별 제품 매핑 (초안, 영업팀 검수 필요)"
export type BodyPart = {
  id: "shoulder" | "brain" | "spine" | "knee" | "hand" | "foot" | "abdomen";
  label: string;
  labelEn: string;
  specialty: Specialty[];
  keywords: string[];
  productIds: string[];
  link1788?: boolean;
  /** 2D 인체 SVG(viewBox 0 0 200 440) 위 핫스팟 좌표 */
  spot: [number, number];
  color: "arthro" | "laparo" | "instrument";
};

export const BODY_PARTS: BodyPart[] = [
  {
    id: "brain", label: "뇌", labelEn: "BRAIN", specialty: ["NS"], spot: [100, 28], color: "instrument",
    keywords: ["개두술", "미세수술", "내시경 두개저 수술"],
    productIds: ["signature-2", "bipolar-forceps", "malis", "colorado", "ent-drill"], link1788: true,
  },
  {
    id: "shoulder", label: "어깨", labelEn: "SHOULDER", specialty: ["OS"], spot: [62, 92], color: "arthro",
    keywords: ["어깨 관절경", "회전근개 봉합", "불안정성 수술"],
    productIds: ["1688-aim-4k", "crossfire-2", "formula-shaver", "serfas", "crossflow", "iconix", "alphavent", "omega"], link1788: true,
  },
  {
    id: "spine", label: "척추", labelEn: "SPINE", specialty: ["NS", "OS"], spot: [100, 132], color: "instrument",
    keywords: ["척추 내시경(BESS)", "후궁절제술", "MIS 척추"],
    productIds: ["bess", "crossflow", "formula-shaver", "signature-2", "bipolar-forceps"],
  },
  {
    id: "abdomen", label: "복부", labelEn: "ABDOMEN", specialty: ["GS"], spot: [100, 182], color: "laparo",
    keywords: ["복강경 담낭 수술", "대장 수술", "비만 수술", "형광(ICG) 영상"],
    productIds: ["spy-fluorescence", "l11-l12", "pneumoclear", "ahto", "pm304", "spy-laparoscope", "lap-instruments", "laparoclick", "spy-phi"], link1788: true,
  },
  {
    id: "hand", label: "손가락", labelEn: "HAND", specialty: ["OS"], spot: [38, 232], color: "instrument",
    keywords: ["수부 수술", "소관절 관절경"],
    productIds: ["tpx", "small-joint", "iconix"],
  },
  {
    id: "knee", label: "무릎", labelEn: "KNEE", specialty: ["OS"], spot: [84, 318], color: "arthro",
    keywords: ["무릎 관절경", "인공관절 수술"],
    productIds: ["1688-aim-4k", "crossfire-2", "formula-shaver", "crossflow", "easyflo", "system-9", "zip"], link1788: true,
  },
  {
    id: "foot", label: "발가락", labelEn: "FOOT", specialty: ["OS"], spot: [124, 424], color: "instrument",
    keywords: ["족부 수술", "소관절 관절경"],
    productIds: ["tpx", "system-9", "small-joint", "iconix"],
  },
];

export const getBodyPart = (id: string | undefined) => BODY_PARTS.find((b) => b.id === id);
