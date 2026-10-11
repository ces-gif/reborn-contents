import { Button, TechLabel } from "~/components/ui";

export const meta = () => [{ title: "페이지를 찾을 수 없습니다 | 수멕스(SUMEX)" }, { name: "robots", content: "noindex" }];

export default function NotFound() {
  return (
    <section className="wrap section flex flex-col gap-6">
      <TechLabel>ERROR · 404</TechLabel>
      <h1 className="flex flex-col"><span className="t-display">No Page,</span><span className="t-display-thin">Only Home.</span></h1>
      <p className="t-body text-muted">찾으시는 페이지가 없습니다. 주소를 다시 확인해 주세요.</p>
      <div className="flex flex-wrap gap-3"><Button to="/" arrow>홈으로</Button><Button to="/contact" variant="secondary">문의하기</Button></div>
    </section>
  );
}
