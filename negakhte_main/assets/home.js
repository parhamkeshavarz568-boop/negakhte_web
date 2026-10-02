/* نگاخته — the homepage's only script. Without it the page is complete:
   everything is visible, the links wrap, the questions still open. */
(() => {
  /* things arrive as they come into view, once */
  const seen = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      e.target.classList.add("in");
      seen.unobserve(e.target);
    }
  }, { rootMargin: "0px 0px -10% 0px", threshold: 0.01 });
  document.querySelectorAll(".rv, .rv-img, .seq").forEach((el) => seen.observe(el));

  /* the header is clear over the hero and frosted after it */
  const top = document.querySelector(".top");
  const hero = document.querySelector(".hero");
  if (top && hero) {
    new IntersectionObserver(([e]) => top.classList.toggle("is-solid", !e.isIntersecting),
      { rootMargin: `-${top.offsetHeight}px 0px 0px 0px` }).observe(hero);
  }

  /* the link for the section you are reading */
  const links = [...document.querySelectorAll('.nav a[href^="#"]')];
  const byId = new Map(links.map((a) => [a.hash.slice(1), a]));
  const spy = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      links.forEach((a) => a.classList.remove("is-here"));
      byId.get(e.target.id || e.target.dataset.part)?.classList.add("is-here");
    }
  }, { rootMargin: "-45% 0px -50% 0px" });
  /* every block is watched; one without a link of its own clears the mark */
  document.querySelectorAll("main > section, main > .page").forEach((s) => spy.observe(s));

  /* the phone menu */
  const btn = document.querySelector(".menu-btn");
  const setMenu = (open) => {
    document.body.classList.toggle("menu-open", open);
    btn?.setAttribute("aria-expanded", String(open));
  };
  btn?.addEventListener("click", () => setMenu(!document.body.classList.contains("menu-open")));
  document.querySelectorAll(".nav a").forEach((a) => a.addEventListener("click", () => setMenu(false)));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") setMenu(false); });
  matchMedia("(min-width: 881px)").addEventListener("change", (m) => { if (m.matches) setMenu(false); });
})();
