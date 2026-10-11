import { type RouteConfig, index, layout, route } from "@react-router/dev/routes";

export default [
  route("sitemap.xml", "routes/sitemap.ts"),
  layout("routes/_layout.tsx", [
    index("routes/home.tsx"),
    route("about", "routes/about.tsx"),
    route("products/1788", "routes/product-1788.tsx"),
    route("products/library", "routes/library.tsx"),
    route("products/:category", "routes/category.tsx"),
    route("products/:category/:slug", "routes/product.tsx"),
    route("explore", "routes/explore.tsx", { id: "explore-index" }),
    route("explore/:part", "routes/explore.tsx", { id: "explore-part" }),
    route("ai-search", "routes/ai-search.tsx"),
    route("newsletter", "routes/newsletter.tsx"),
    route("contact", "routes/contact.tsx"),
    route("*", "routes/not-found.tsx"),
  ]),
] satisfies RouteConfig;
