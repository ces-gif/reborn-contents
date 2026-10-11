import { Download, Eye, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router";
import { DOC_TYPE_LABEL, type LibraryDoc } from "~/data/library";
import { getProductById, productPath } from "~/data/products";
import { TriSpinner, cx, useToast } from "./ui";

/** PDF 문서 목록 + 뷰어. driveId가 없으면 "자료 준비중" 안내 */
export function DocList({ docs, view = "list" }: { docs: LibraryDoc[]; view?: "list" | "card" }) {
  const toast = useToast();
  const [open, setOpen] = useState<LibraryDoc | null>(null);
  const viewDoc = (d: LibraryDoc) => (d.driveId ? setOpen(d) : toast("자료를 준비중입니다. 담당자에게 요청해 주세요."));
  const download = (d: LibraryDoc) =>
    d.driveId ? window.open(`https://drive.google.com/uc?export=download&id=${d.driveId}`, "_blank", "noopener") : toast("자료를 준비중입니다. 담당자에게 요청해 주세요.");

  if (docs.length === 0) return <p className="t-body text-muted">등록된 자료가 없습니다.</p>;

  return (
    <>
      {view === "list" ? (
        <div className="overflow-x-auto rounded-sm border border-line">
          <table className="w-full min-w-[640px] text-left">
            <thead className="bg-surface">
              <tr>
                {["종류", "문서명", "관련 제품", "진료과", ""].map((h) => (
                  <th key={h} scope="col" className="t-label-sm px-5 py-4 text-subtle">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {docs.map((d) => (
                <tr key={d.id} className="border-t border-line">
                  <td className="px-5 py-4"><span className="t-label-sm inline-flex h-7 items-center rounded-full border border-line px-3 text-muted">{DOC_TYPE_LABEL[d.docType]}</span></td>
                  <td className="t-body px-5 py-4">{d.title}</td>
                  <td className="t-body-sm px-5 py-4 text-muted">
                    {d.productIds.map((id, i) => {
                      const p = getProductById(id);
                      return p ? <span key={id}>{i > 0 && ", "}<Link to={productPath(p)} className="hover:text-fg hover:underline">{p.name}</Link></span> : null;
                    })}
                  </td>
                  <td className="t-body-sm px-5 py-4 text-muted">{d.specialty.join(" · ")}</td>
                  <td className="px-5 py-4">
                    <div className="flex justify-end gap-2">
                      <IconBtn label={`${d.title} 보기`} onClick={() => viewDoc(d)}><Eye size={16} strokeWidth={1.5} /></IconBtn>
                      <IconBtn label={`${d.title} 다운로드`} onClick={() => download(d)}><Download size={16} strokeWidth={1.5} /></IconBtn>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {docs.map((d) => (
            <li key={d.id} className="flex flex-col gap-4 rounded-sm border border-line bg-surface p-4">
              <div className="grid aspect-[3/4] place-items-center rounded-xs bg-black p-6">
                <div className="flex h-full w-full flex-col justify-between bg-fg p-4 text-black">
                  <span className="text-[10px] font-semibold tracking-[0.18em]">{DOC_TYPE_LABEL[d.docType]}</span>
                  <span className="text-[15px] font-bold leading-tight">{d.title}</span>
                  <span className="text-[9px] tracking-[0.18em] text-black/60">STRYKER · {d.category}</span>
                </div>
              </div>
              <p className="t-body-sm line-clamp-2 min-h-[2.8em]">{d.title}</p>
              <div className="mt-auto flex gap-2">
                <button type="button" onClick={() => viewDoc(d)} className="t-label-sm flex h-10 flex-1 items-center justify-center gap-2 rounded-xs border border-line hover:border-fg"><Eye size={14} strokeWidth={1.5} /> 보기</button>
                <button type="button" onClick={() => download(d)} className="t-label-sm flex h-10 flex-1 items-center justify-center gap-2 rounded-xs bg-primary text-black hover:bg-primary-hover"><Download size={14} strokeWidth={1.5} /> 받기</button>
              </div>
            </li>
          ))}
        </ul>
      )}
      {open && <PdfViewer doc={open} onClose={() => setOpen(null)} />}
    </>
  );
}

function IconBtn({ label, onClick, children }: { label: string; onClick: () => void; children: React.ReactNode }) {
  return (
    <button type="button" aria-label={label} onClick={onClick} className="grid size-9 place-items-center rounded-xs border border-line text-muted hover:border-fg hover:text-fg">
      {children}
    </button>
  );
}

function PdfViewer({ doc, onClose }: { doc: LibraryDoc; onClose: () => void }) {
  const [loaded, setLoaded] = useState(false);
  useEffect(() => {
    const k = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", k);
    return () => window.removeEventListener("keydown", k);
  }, [onClose]);
  return (
    <div role="dialog" aria-modal="true" aria-label={doc.title} className="fixed inset-0 z-[90] flex flex-col bg-black/90">
      <div className="flex h-16 items-center justify-between gap-4 border-b border-line bg-surface px-5">
        <p className="t-body truncate">{doc.title}</p>
        <div className="flex items-center gap-2">
          <a href={`https://drive.google.com/uc?export=download&id=${doc.driveId}`} target="_blank" rel="noopener noreferrer" className="t-label flex h-10 items-center gap-2 rounded-xs bg-primary px-4 text-black"><Download size={16} strokeWidth={1.5} /> 다운로드</a>
          <button type="button" onClick={onClose} aria-label="닫기" className="grid size-10 place-items-center rounded-xs border border-line"><X size={18} strokeWidth={1.5} /></button>
        </div>
      </div>
      <div className={cx("relative flex-1")}>
        {!loaded && <div className="absolute inset-0 grid place-items-center"><TriSpinner /></div>}
        <iframe title={doc.title} src={`https://drive.google.com/file/d/${doc.driveId}/preview`} onLoad={() => setLoaded(true)} className="h-full w-full" allow="autoplay" />
      </div>
    </div>
  );
}
