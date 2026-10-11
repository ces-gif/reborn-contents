// 제품 카탈로그. 문구는 DESIGN.md(네이버웍스 "제품정보" 폴더의 Stryker 브로슈어·용도설명서 기반)에 적힌 내용만 사용한다.
// TODO: 게시 전 모든 summary/features를 한국스트라이커와 광고 심의 기준으로 검수.

export type Specialty = "OS" | "NS" | "GS";
export type CategoryId = "arthro" | "laparo" | "instrument";

export type Product = {
  id: string;
  slug: string;
  name: string;
  category: CategoryId;
  group: string;
  specialty: Specialty[];
  summary: string;
  features: string[];
  specs?: { label: string; value: string }[];
  keywords: string[];
  libraryDocIds: string[];
};

export const CATEGORIES: Record<
  CategoryId,
  { id: CategoryId; name: string; ko: string; tagline: string; description: string; specialty: Specialty[]; color: string; groups: string[] }
> = {
  arthro: {
    id: "arthro",
    name: "ARTHRO",
    ko: "관절경",
    tagline: "관절경 수술의 모든 것",
    description:
      "4K 관절경 영상 시스템부터 셰이버·RF 통합 콘솔, 관류 펌프, 스포츠메디슨 앵커까지 정형외과 관절경 수술에 필요한 Stryker 장비를 공급합니다. 척추 내시경(BESS) 장비도 함께 다룹니다.",
    specialty: ["OS", "NS"],
    color: "var(--color-arthro)",
    groups: ["영상 시스템", "절제·지혈", "관류 펌프", "광원", "스포츠메디슨", "척추 내시경"],
  },
  laparo: {
    id: "laparo",
    name: "LAPARO",
    ko: "복강경",
    tagline: "4K 형광 복강경 수술",
    description:
      "1788 AIM 4K 플랫폼과 SPY 형광 영상, 광원, 기복기, 세척 펌프, 복강경 스코프와 기구까지 일반외과 복강경 수술 환경을 구성하는 Stryker 장비를 공급합니다.",
    specialty: ["GS"],
    color: "var(--color-laparo)",
    groups: ["형광 영상", "광원", "기복기", "세척 펌프", "복강경 스코프", "복강경 기구", "영상 관리"],
  },
  instrument: {
    id: "instrument",
    name: "INSTRUMENT",
    ko: "수술 도구",
    tagline: "정밀한 파워, 수술 도구",
    description:
      "System 9 파워툴, Signature 2 고속 드릴, TPX 소형 뼈 파워툴, 신경외과 바이폴라 기구, 피부 봉합과 감염 방지 시스템까지 정형외과·신경외과 수술 도구를 공급합니다.",
    specialty: ["OS", "NS"],
    color: "var(--color-instrument)",
    groups: ["파워툴", "고속 드릴", "소형 뼈 파워툴", "신경외과", "피부 봉합", "감염 방지", "ENT"],
  },
};

export const SPECIALTY_LABEL: Record<Specialty, string> = { OS: "정형외과", NS: "신경외과", GS: "일반외과" };

export const PRODUCTS: Product[] = [
  // ── ARTHRO ─────────────────────────────
  {
    id: "1688-aim-4k", slug: "1688-aim-4k", name: "1688 AIM 4K Arthroscopy", category: "arthro", group: "영상 시스템", specialty: ["OS"],
    summary: "1688 AIM 4K는 3-CHIP 방식의 4K 관절경 영상 시스템입니다. 9개의 Specialty Mode와 Auto-Light, 음성 제어 기능을 갖추고 있습니다.",
    features: ["3-CHIP 4K 영상", "9개 Specialty Mode", "Auto-Light", "음성 제어"],
    keywords: ["4K 카메라", "관절경 카메라", "무릎 관절경", "어깨 관절경"], libraryDocIds: ["arthro-1688", "arthro-complete"],
  },
  {
    id: "crossfire-2", slug: "crossfire-2", name: "CrossFire 2", category: "arthro", group: "절제·지혈", specialty: ["OS"],
    summary: "CrossFire 2는 셰이버(Shaver)와 RF를 하나의 콘솔로 통합한 관절경 절제·지혈 시스템입니다. Hammer Mode와 Arc to Scope Detection 기능을 제공합니다.",
    features: ["Shaver + RF 통합 콘솔", "Hammer Mode", "Arc to Scope Detection"],
    keywords: ["셰이버", "RF", "절제", "지혈", "어깨 관절경", "무릎 관절경"], libraryDocIds: ["arthro-crossfire2"],
  },
  {
    id: "formula-shaver", slug: "formula-shaver", name: "Formula Shaver Handpiece", category: "arthro", group: "절제·지혈", specialty: ["OS"],
    summary: "Formula Shaver Handpiece는 관절경 수술용 셰이버 핸드피스입니다. 최대 12,000 RPM으로 회전합니다.",
    features: ["최대 12,000 RPM"], specs: [{ label: "최대 회전수", value: "12,000 RPM" }],
    keywords: ["셰이버", "핸드피스", "관절경"], libraryDocIds: ["arthro-shaver"],
  },
  {
    id: "formula-crossblade", slug: "formula-crossblade", name: "Formula / CrossBlade 커터·버", category: "arthro", group: "절제·지혈", specialty: ["OS"],
    summary: "Formula와 CrossBlade는 셰이버 핸드피스에 장착하는 관절경용 커터와 버입니다.",
    features: ["Formula 커터·버", "CrossBlade 커터·버"], keywords: ["커터", "버", "블레이드", "셰이버"], libraryDocIds: ["arthro-shaver"],
  },
  {
    id: "serfas", slug: "serfas-energy-probe", name: "SERFAS Energy Probe", category: "arthro", group: "절제·지혈", specialty: ["OS"],
    summary: "SERFAS Energy Probe는 관절경 수술에 사용하는 RF 에너지 프로브입니다.",
    features: ["관절경용 RF 프로브"], keywords: ["RF 프로브", "어깨 관절경"], libraryDocIds: [],
  },
  {
    id: "crossflow", slug: "crossflow", name: "CrossFlow Pump", category: "arthro", group: "관류 펌프", specialty: ["OS", "NS"],
    summary: "CrossFlow는 관절경 수술용 관류 펌프입니다. ReconiSense 기술과 Inflow/Outflow 제어, 의사별 프리셋 기능을 제공합니다.",
    features: ["ReconiSense", "Inflow / Outflow 제어", "의사별 프리셋"], keywords: ["관류 펌프", "펌프", "관절경", "척추 내시경"], libraryDocIds: ["arthro-crossflow"],
  },
  {
    id: "easyflo", slug: "easyflo", name: "EasyFlo Pump", category: "arthro", group: "관류 펌프", specialty: ["OS"],
    summary: "EasyFlo는 관절경 수술용 관류 펌프입니다.", features: ["관절경용 관류 펌프"], keywords: ["관류 펌프", "펌프", "무릎 관절경"], libraryDocIds: [],
  },
  {
    id: "precision-led", slug: "precision-led-light-source", name: "Precision LED Light Source", category: "arthro", group: "광원", specialty: ["OS"],
    summary: "Precision LED Light Source는 관절경 영상 시스템용 LED 광원입니다.", features: ["LED 광원"], keywords: ["광원", "LED"], libraryDocIds: [],
  },
  {
    id: "small-joint", slug: "small-joint-arthroscopy", name: "Small Joint Arthroscopy", category: "arthro", group: "영상 시스템", specialty: ["OS"],
    summary: "Small Joint Arthroscopy는 손·발 등 소관절 관절경 수술을 위한 구성입니다. TPS Small-Joint Shaver와 함께 사용합니다.",
    features: ["소관절 관절경", "TPS Small-Joint Shaver"], keywords: ["소관절", "수부", "족부", "손", "발"], libraryDocIds: [],
  },
  {
    id: "iconix", slug: "iconix", name: "ICONIX All-Suture Anchor", category: "arthro", group: "스포츠메디슨", specialty: ["OS"],
    summary: "ICONIX는 올-수처(All-Suture) 방식의 봉합 앵커입니다. 1.4mm와 2.3mm 규격이 있습니다.",
    features: ["All-Suture 앵커", "1.4mm / 2.3mm 규격"], specs: [{ label: "규격", value: "1.4mm / 2.3mm" }],
    keywords: ["앵커", "봉합 앵커", "회전근개", "어깨 봉합", "손", "발"], libraryDocIds: ["arthro-iconix"],
  },
  {
    id: "omega", slug: "omega-knotless-anchor", name: "Omega Knotless Anchor", category: "arthro", group: "스포츠메디슨", specialty: ["OS"],
    summary: "Omega는 매듭이 필요 없는 노트리스(Knotless) 봉합 앵커입니다.", features: ["Knotless 앵커"], keywords: ["앵커", "노트리스", "어깨 봉합"], libraryDocIds: ["arthro-omega"],
  },
  {
    id: "alphavent", slug: "alphavent-anchor", name: "Alphavent Anchor", category: "arthro", group: "스포츠메디슨", specialty: ["OS"],
    summary: "Alphavent는 스포츠메디슨 수술에 사용하는 봉합 앵커입니다.", features: ["스포츠메디슨 앵커"], keywords: ["앵커", "어깨 봉합"], libraryDocIds: ["arthro-alphavent"],
  },
  {
    id: "bess", slug: "bess", name: "BESS 척추 내시경 장비", category: "arthro", group: "척추 내시경", specialty: ["NS", "OS"],
    summary: "BESS(양방향 척추 내시경 수술)에 사용하는 장비 구성입니다. 4K 관절경 영상 시스템과 CrossFlow 관류 펌프, 셰이버를 함께 사용합니다.",
    features: ["양방향 척추 내시경(BESS)", "1788/1688 영상 시스템 연동", "CrossFlow · Shaver 구성"], keywords: ["척추 내시경", "BESS", "척추"], libraryDocIds: [],
  },
  // ── LAPARO ─────────────────────────────
  {
    id: "spy-fluorescence", slug: "spy-fluorescence", name: "SPY 형광 영상", category: "laparo", group: "형광 영상", specialty: ["GS"],
    summary: "SPY 형광 영상은 1788 플랫폼에서 형광(ICG) 영상을 Overlay, ENV, Contrast 세 가지 모드로 보여주는 기능입니다.",
    features: ["Overlay: 형광 영상을 일반 영상 위에 겹쳐 4K로 동시 표현", "ENV: 형광을 회색과 초록색으로 구분해 4K로 표현", "Contrast: 형광을 흑과 백으로 구분해 4K로 표현"],
    keywords: ["형광", "ICG", "복강경 형광 영상"], libraryDocIds: ["1788-brochure", "1788-laparo"],
  },
  {
    id: "spy-phi", slug: "spy-phi", name: "SPY-PHI", category: "laparo", group: "형광 영상", specialty: ["GS"],
    summary: "SPY-PHI는 개복 수술에서 사용하는 휴대형 형광 영상 장비입니다.", features: ["개복용 휴대 형광 영상"], keywords: ["형광", "개복", "휴대형"], libraryDocIds: [],
  },
  {
    id: "l11-l12", slug: "l11-l12-led-light-source", name: "L11 / L12 LED Light Source with AIM", category: "laparo", group: "광원", specialty: ["GS"],
    summary: "L11과 L12는 AIM 기술을 지원하는 LED 광원입니다.", features: ["AIM 지원 LED 광원"], keywords: ["광원", "LED", "복강경"], libraryDocIds: ["1788-ifu"],
  },
  {
    id: "pneumoclear", slug: "pneumoclear", name: "PneumoClear", category: "laparo", group: "기복기", specialty: ["GS"],
    summary: "PneumoClear는 가온·가습·연기 배출 기능을 하나로 통합한 복강경 기복기입니다.",
    features: ["가온", "가습", "연기 배출 통합"], keywords: ["기복기", "연기 배출", "스모크", "복강경"], libraryDocIds: ["laparo-pneumoclear"],
  },
  {
    id: "ahto", slug: "ahto-irrigation-pump", name: "AHTO Irrigation Pump", category: "laparo", group: "세척 펌프", specialty: ["GS"],
    summary: "AHTO는 무선 방식의 복강경 세척 펌프입니다. 2, 3, 4 L/min 유량을 선택할 수 있습니다.",
    features: ["무선", "2 / 3 / 4 L/min"], specs: [{ label: "유량", value: "2 / 3 / 4 L/min" }], keywords: ["세척 펌프", "복강경"], libraryDocIds: ["laparo-ahto"],
  },
  {
    id: "pm304", slug: "pm304", name: "PM304 Multi-flow Irrigation Pump", category: "laparo", group: "세척 펌프", specialty: ["GS"],
    summary: "PM304는 멀티플로우 방식의 세척 펌프입니다.", features: ["Multi-flow 세척"], keywords: ["세척 펌프"], libraryDocIds: [],
  },
  {
    id: "spy-laparoscope", slug: "spy-laparoscope", name: "SPY Laparoscope", category: "laparo", group: "복강경 스코프", specialty: ["GS"],
    summary: "SPY Laparoscope는 형광 영상을 지원하는 복강경 스코프입니다. 5.4mm와 10mm, 0°·30°·45° 각도가 있으며 Bariatric(45cm)과 소아용 2.9mm 스코프도 있습니다.",
    features: ["5.4mm / 10mm", "0° · 30° · 45°", "Bariatric 45cm", "소아용 2.9mm"],
    specs: [{ label: "직경", value: "5.4mm / 10mm" }, { label: "각도", value: "0° · 30° · 45°" }, { label: "Bariatric", value: "45cm" }, { label: "소아용", value: "2.9mm" }],
    keywords: ["복강경 스코프", "스코프", "비만 수술", "소아"], libraryDocIds: ["1788-laparo"],
  },
  {
    id: "lap-instruments", slug: "laparoscopic-instruments", name: "Stryker Laparoscopic Instruments", category: "laparo", group: "복강경 기구", specialty: ["GS"],
    summary: "Stryker 복강경 기구는 3mm, 5mm, 10mm 규격의 모듈형 수술 기구입니다.",
    features: ["3mm / 5mm / 10mm", "모듈형"], keywords: ["복강경 기구"], libraryDocIds: ["laparo-instruments"],
  },
  {
    id: "laparoclick", slug: "laparoclick-ezx", name: "LaparoTools LaparoClick EZX", category: "laparo", group: "복강경 기구", specialty: ["GS"],
    summary: "LaparoClick EZX는 LaparoTools의 복강경 수술 기구입니다.", features: ["LaparoTools 복강경 기구"], keywords: ["복강경 기구"], libraryDocIds: ["laparo-laparotools"],
  },
  {
    id: "connected-or-hub", slug: "connected-or-hub", name: "Connected OR Hub", category: "laparo", group: "영상 관리", specialty: ["GS", "OS"],
    summary: "Connected OR Hub는 수술 영상의 기록과 관리를 위한 장비입니다.", features: ["영상 기록·관리"], keywords: ["영상 기록", "녹화"], libraryDocIds: ["1788-ifu"],
  },
  {
    id: "sdc4k", slug: "sdc4k", name: "SDC4K", category: "laparo", group: "영상 관리", specialty: ["GS"],
    summary: "SDC4K는 4K 수술 영상 기록 장비입니다.", features: ["4K 영상 기록"], keywords: ["영상 기록", "4K"], libraryDocIds: ["1788-ifu"],
  },
  {
    id: "oled-display", slug: "4k-oled-surgical-display", name: '32" 4K OLED Surgical Display', category: "laparo", group: "영상 관리", specialty: ["GS", "OS"],
    summary: '32" 4K OLED Surgical Display는 1788 플랫폼과 함께 쓰는 32인치 4K OLED 수술용 모니터입니다.',
    features: ['32" 4K OLED'], keywords: ["모니터", "OLED", "디스플레이"], libraryDocIds: ["1788-brochure"],
  },
  // ── INSTRUMENT ─────────────────────────
  {
    id: "system-9", slug: "system-9", name: "System 9", category: "instrument", group: "파워툴", specialty: ["OS"],
    summary: "System 9는 Stryker의 정형외과용 파워툴 시스템입니다. 1983년 OP90에서 시작한 Stryker 파워툴 계보를 잇습니다.",
    features: ["SABO Saw", "Precision Oscillating Tip Saw", "Sagittal / Reciprocating / Sternum Saw", "Cordless Driver", "Rotary Drill", "EZout"],
    keywords: ["파워툴", "톱", "드릴", "인공관절", "무릎"], libraryDocIds: ["inst-system9"],
  },
  {
    id: "signature-2", slug: "signature-2", name: "Signature 2 고속 드릴", category: "instrument", group: "고속 드릴", specialty: ["NS", "OS"],
    summary: "Signature 2는 신경외과·척추·ENT 수술용 고속 드릴 포트폴리오입니다. CORE 2 콘솔과 πdrive 2 모터로 구성됩니다.",
    features: ["CORE 2 Console", "πdrive 2 Motor", "모터 8종", "어태치먼트 40종", "커팅 액세서리 700종 이상"],
    specs: [{ label: "모터", value: "8종" }, { label: "어태치먼트", value: "40종" }, { label: "커팅 액세서리", value: "700종+" }],
    keywords: ["고속 드릴", "척추 수술", "개두술", "뇌", "드릴"], libraryDocIds: ["inst-pidrive", "inst-hsd"],
  },
  {
    id: "tpx", slug: "tpx", name: "TPX", category: "instrument", group: "소형 뼈 파워툴", specialty: ["OS"],
    summary: "TPX는 손·발 등 소형 뼈 수술용 파워툴입니다. Micro Drill과 Sagittal Saw를 포함합니다.",
    features: ["Micro Drill", "Sagittal Saw"], keywords: ["소형 뼈", "수부", "족부", "손", "발", "파워툴"], libraryDocIds: ["inst-tpx"],
  },
  {
    id: "bipolar-forceps", slug: "bipolar-forceps", name: "Spetzler-Malis / SILVERGlide Bipolar Forceps", category: "instrument", group: "신경외과", specialty: ["NS"],
    summary: "Spetzler-Malis와 SILVERGlide는 신경외과 수술용 바이폴라 포셉입니다.", features: ["Spetzler-Malis", "SILVERGlide"],
    keywords: ["바이폴라", "포셉", "신경외과", "뇌", "척추"], libraryDocIds: ["inst-bipolar"],
  },
  {
    id: "malis", slug: "malis-bipolar-generator", name: "Malis Bipolar Generator", category: "instrument", group: "신경외과", specialty: ["NS"],
    summary: "Malis Bipolar Generator는 바이폴라 기구에 사용하는 제너레이터입니다.", features: ["바이폴라 제너레이터"], keywords: ["바이폴라", "제너레이터", "신경외과"], libraryDocIds: [],
  },
  {
    id: "colorado", slug: "colorado-microdissection-needle", name: "Colorado MicroDissection Needle", category: "instrument", group: "신경외과", specialty: ["NS"],
    summary: "Colorado MicroDissection Needle은 신경외과 수술용 미세 박리 니들입니다.", features: ["미세 박리 니들"], keywords: ["니들", "신경외과", "뇌"], libraryDocIds: ["inst-colorado"],
  },
  {
    id: "zip", slug: "zip-skin-closure", name: "Zip Surgical Skin Closure", category: "instrument", group: "피부 봉합", specialty: ["OS"],
    summary: "Zip은 수술 후 피부를 닫는 피부 봉합 장치입니다.", features: ["피부 봉합"], keywords: ["피부 봉합", "봉합"], libraryDocIds: ["inst-zip"],
  },
  {
    id: "flyte", slug: "flyte-steri-shield", name: "Flyte Steri-Shield", category: "instrument", group: "감염 방지", specialty: ["OS", "NS", "GS"],
    summary: "Flyte Steri-Shield는 수술실 의료진을 위한 개인 보호 시스템(Personal Protection System)입니다.", features: ["Personal Protection System"],
    keywords: ["감염 방지", "보호", "수술실"], libraryDocIds: ["inst-flyte"],
  },
  {
    id: "ent-drill", slug: "ent-drill-portfolio", name: "ENT Drill Portfolio", category: "instrument", group: "ENT", specialty: ["NS"],
    summary: "ENT Drill Portfolio는 이비인후과 수술용 드릴 제품군입니다.", features: ["ENT 드릴"], keywords: ["ENT", "이비인후과", "드릴"], libraryDocIds: ["inst-ent"],
  },
];

export const getProduct = (category: string, slug: string) => PRODUCTS.find((p) => p.category === category && p.slug === slug);
export const getProductById = (id: string) => PRODUCTS.find((p) => p.id === id);
export const productPath = (p: Product) => `/products/${p.category}/${p.slug}`;
export const isCategory = (c: string | undefined): c is CategoryId => !!c && c in CATEGORIES;

// 1788 전용 페이지 데이터 (DESIGN.md "3. 1788 전용 페이지")
export const P1788 = {
  specs: [
    { value: "4K", unit: "", label: "해상도" },
    { value: "10억+", unit: "COLORS", label: "컬러 표현" },
    { value: "1,000,000:1", unit: "", label: "명암비" },
    { value: "4,096×2,160", unit: "PX", label: "최대 해상도" },
  ],
  modes: [
    { id: "white", name: "White Light", desc: "일반 백색광 영상을 4K로 표현" },
    { id: "overlay", name: "Overlay", desc: "형광 영상을 일반 영상 위에 겹쳐 4K로 동시 표현" },
    { id: "env", name: "ENV", desc: "형광을 회색과 초록색으로 구분해 4K로 표현" },
    { id: "contrast", name: "Contrast", desc: "형광을 흑과 백으로 구분해 4K로 표현" },
  ] as const,
  specialties: ["일반외과", "비뇨의학과", "정형외과", "산부인과", "이비인후과 / 신경외과", "흉부외과"],
  functions: [
    { name: "IRIS", desc: "요관 위치 확인" },
    { name: "SPY CSI", desc: "" },
    { name: "SPY CSF", desc: "" },
    { name: "Tone Mode", desc: "" },
    { name: "HDR", desc: "" },
  ],
  components: [
    { key: "A", name: "4K OLED surgical display" },
    { key: "B", name: "Connected OR Hub" },
    { key: "C", name: "PneumoClear Insufflator" },
    { key: "D", name: "1788 AIM 4K CCU" },
    { key: "E", name: "1788 AIM 4K Camera head" },
    { key: "F", name: "L12 LED Light Source" },
    { key: "G", name: "VPI" },
    { key: "H", name: "SPY-PHI" },
    { key: "I", name: "PM304 Multi-flow Irrigation Pump" },
  ],
  parts: [
    { code: "1788-010-000I", name: "1788 AIM 4K CCU" },
    { code: "1788-020-122I", name: "Coupler Kit" },
    { code: "1788-210-105I", name: "Camera Head" },
    { code: "0220-230-300I", name: "L11 LED Light Source with AIM" },
    { code: "0240-031-300I", name: '32" 4K OLED Display' },
    { code: "0240-200-100I", name: "Connected OR Hub" },
    { code: "0240-300-100I", name: "SDC4K" },
    { code: "0502-937 / 537", name: "AIM Laparoscope (10mm / 5mm, 0° / 30°)" },
    { code: "0620-050-060", name: "PneumoClear" },
  ],
};
