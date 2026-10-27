import { ICONS } from "./icons";

export function Icon({ name, label, spin, fill }: { name: string; label?: string; spin?: boolean; fill?: boolean }) {
  const cls = ["ic", spin ? "spin" : "", fill ? "ic--fill" : ""].filter(Boolean).join(" ");
  const a11y = label ? { role: "img", "aria-label": label } : { "aria-hidden": true, focusable: "false" as const };
  return <svg className={cls} viewBox="0 0 24 24" {...a11y} dangerouslySetInnerHTML={{ __html: ICONS[name] ?? "" }} />;
}
