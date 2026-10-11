import tailwindcss from "@tailwindcss/vite";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { defineConfig, type Plugin } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";
import tsconfigPaths from "vite-tsconfig-paths";

// public/ 의 절대경로 이미지를 data URI로 바꿔 한 파일에 담는다
const inlinePublic = (): Plugin => {
  const logo = "data:image/png;base64," + readFileSync("public/brand/sumex-logo-white.png").toString("base64");
  return {
    name: "inline-public",
    transform(code, id) {
      if (!/\.(t|j)sx?$/.test(id) || !code.includes("/brand/")) return;
      return code.replaceAll('"/brand/sumex-logo-white.png"', JSON.stringify(logo));
    },
  };
};

export default defineConfig({
  root: "preview",
  plugins: [tailwindcss(), tsconfigPaths({ root: ".." }), inlinePublic(), viteSingleFile()],
  resolve: {
    alias: {
      "pretendard/dist/web/variable/pretendardvariable-dynamic-subset.css": fileURLToPath(new URL("./preview/font.css", import.meta.url)),
      "pretendard/dist/web/variable/woff2/PretendardVariable.woff2": fileURLToPath(new URL("./node_modules/pretendard/dist/web/variable/woff2/PretendardVariable.woff2", import.meta.url)),
    },
  },
  build: { outDir: "../build-preview", emptyOutDir: true, assetsInlineLimit: 100_000_000 },
});
