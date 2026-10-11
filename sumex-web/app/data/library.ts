import type { Specialty } from "./products";

// 제품 자료실 (DESIGN.md "5. 제품 자료실" B안: 수동 등록).
// driveId는 Google Drive 업로드 후 채운다. null이면 화면에서 "자료 준비중"으로 안내한다.
// 업로드 전 한국스트라이커에 외부 공개 배포 가능 여부 확인 필요.
export type DocType = "brochure" | "catalog" | "ifu-summary" | "spec";
export type LibraryDoc = {
  id: string;
  title: string;
  file: string;
  category: "1788" | "ARTHRO" | "LAPARO" | "INSTRUMENT";
  specialty: Specialty[];
  docType: DocType;
  productIds: string[];
  driveId: string | null;
};

export const DOC_TYPE_LABEL: Record<DocType, string> = { brochure: "브로슈어", catalog: "카탈로그", "ifu-summary": "용도설명서", spec: "규격서" };

export const LIBRARY: LibraryDoc[] = [
  { id: "1788-brochure", title: "1788 Platform Brochure", file: "1788 Platform Brochure.pdf", category: "1788", specialty: ["GS", "OS"], docType: "brochure", productIds: ["spy-fluorescence", "oled-display"], driveId: null },
  { id: "1788-laparo", title: "1788 Laparoscopy", file: "1788 Laparoscopy.pdf", category: "1788", specialty: ["GS"], docType: "catalog", productIds: ["spy-fluorescence", "spy-laparoscope"], driveId: null },
  { id: "1788-ifu", title: "1788 4K OLED Platform 용도설명서", file: "1788 4K OLED Platform 용도설명서.pdf", category: "1788", specialty: ["GS"], docType: "ifu-summary", productIds: ["l11-l12", "connected-or-hub", "sdc4k"], driveId: null },
  { id: "arthro-1688", title: "1688 4K Arthroscopy System Brochure", file: "1688 4K Arthroscopy system_Brochure.pdf", category: "ARTHRO", specialty: ["OS"], docType: "brochure", productIds: ["1688-aim-4k"], driveId: null },
  { id: "arthro-complete", title: "Complete Arthroscopy Solutions", file: "Complete Arthroscopy Solutions.pdf", category: "ARTHRO", specialty: ["OS"], docType: "catalog", productIds: ["1688-aim-4k"], driveId: null },
  { id: "arthro-crossfire2", title: "CrossFire 2 Brochure", file: "crossfire-2-brochure.pdf", category: "ARTHRO", specialty: ["OS"], docType: "brochure", productIds: ["crossfire-2"], driveId: null },
  { id: "arthro-crossflow", title: "CrossFlow Brochure", file: "CrossFlow-Brochure.pdf", category: "ARTHRO", specialty: ["OS"], docType: "brochure", productIds: ["crossflow"], driveId: null },
  { id: "arthro-shaver", title: "Shaver", file: "Shaver PDF.pdf", category: "ARTHRO", specialty: ["OS"], docType: "catalog", productIds: ["formula-shaver", "formula-crossblade"], driveId: null },
  { id: "arthro-iconix", title: "ICONIX Platform Brochure", file: "ICONIX_Platform_Brochure.pdf", category: "ARTHRO", specialty: ["OS"], docType: "brochure", productIds: ["iconix"], driveId: null },
  { id: "arthro-alphavent", title: "Alphavent Brochure", file: "Alphavent brochure.pdf", category: "ARTHRO", specialty: ["OS"], docType: "brochure", productIds: ["alphavent"], driveId: null },
  { id: "arthro-omega", title: "Omega Product Brochure", file: "Omega Product Brochure.pdf", category: "ARTHRO", specialty: ["OS"], docType: "brochure", productIds: ["omega"], driveId: null },
  { id: "laparo-pneumoclear", title: "PneumoClear Presentation", file: "PneumoClear presentation.pdf", category: "LAPARO", specialty: ["GS"], docType: "brochure", productIds: ["pneumoclear"], driveId: null },
  { id: "laparo-ahto", title: "AHTO Irrigation Pump", file: "AHTOIrrigationpump.pdf", category: "LAPARO", specialty: ["GS"], docType: "brochure", productIds: ["ahto"], driveId: null },
  { id: "laparo-instruments", title: "Stryker Laparoscopic Instruments", file: "Stryker laparoinstruments.pdf", category: "LAPARO", specialty: ["GS"], docType: "catalog", productIds: ["lap-instruments"], driveId: null },
  { id: "laparo-laparotools", title: "LaparoTools 카탈로그", file: "laparotools카다록.pdf", category: "LAPARO", specialty: ["GS"], docType: "catalog", productIds: ["laparoclick"], driveId: null },
  { id: "inst-system9", title: "System 9 General Brochure (KR)", file: "System9 general Brochure_KR.pdf", category: "INSTRUMENT", specialty: ["OS"], docType: "brochure", productIds: ["system-9"], driveId: null },
  { id: "inst-pidrive", title: "πdrive 2 Motor Brochure", file: "Pi drive motor 2 Brochure.pdf", category: "INSTRUMENT", specialty: ["NS"], docType: "brochure", productIds: ["signature-2"], driveId: null },
  { id: "inst-hsd", title: "High Speed Drills Platform Brochure", file: "High Speed Drills Platform Brochure.pdf", category: "INSTRUMENT", specialty: ["NS", "OS"], docType: "brochure", productIds: ["signature-2"], driveId: null },
  { id: "inst-tpx", title: "Stryker TPX Brochure", file: "Brochure_Stryker-TPX.pdf", category: "INSTRUMENT", specialty: ["OS"], docType: "brochure", productIds: ["tpx"], driveId: null },
  { id: "inst-zip", title: "Zip Brochure", file: "zip-brochure.pdf", category: "INSTRUMENT", specialty: ["OS"], docType: "brochure", productIds: ["zip"], driveId: null },
  { id: "inst-flyte", title: "Flyte Steri-Shield System Brochure", file: "flyte-sterishield-system-brochure.pdf", category: "INSTRUMENT", specialty: ["OS", "NS", "GS"], docType: "brochure", productIds: ["flyte"], driveId: null },
  { id: "inst-colorado", title: "Colorado Needle Flyer", file: "colorado-needle-flyer.pdf", category: "INSTRUMENT", specialty: ["NS"], docType: "brochure", productIds: ["colorado"], driveId: null },
  { id: "inst-bipolar", title: "Bipolar Forceps Brochure", file: "Bipolar Forceps Brochure.pdf", category: "INSTRUMENT", specialty: ["NS"], docType: "brochure", productIds: ["bipolar-forceps"], driveId: null },
  { id: "inst-ent", title: "ENT Portfolio Brochure", file: "ENT-portfolio-brochure.pdf", category: "INSTRUMENT", specialty: ["NS"], docType: "brochure", productIds: ["ent-drill"], driveId: null },
];

export const getDoc = (id: string) => LIBRARY.find((d) => d.id === id);
