// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { LocateFixed } from "lucide-react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import type { MapColor, MapOut, MapPoint } from "@/lib/types";

const palette = ["#2563eb", "#7c3aed", "#0891b2", "#c2410c", "#4f46e5", "#0f766e", "#a21caf", "#0369a1", "#854d0e", "#be123c", "#4338ca", "#15803d"];

function valueOf(point: MapPoint, color: MapColor) {
  if (color === "topic") return point.topic_id === null ? "Khác" : String(point.topic_id);
  if (color === "unit") return point.unit_id === null ? "Khác" : String(point.unit_id);
  if (color === "year") return point.year === null ? "Khác" : String(point.year);
  return point.doc_type || "Khác";
}

export function KnowledgeMap({ data, color, query }: { data: MapOut; color: MapColor; query: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const transform = useRef({ scale: 1, x: 0, y: 0 });
  const pointers = useRef(new Map<number, { x: number; y: number }>());
  const drag = useRef({ x: 0, y: 0, moved: 0, distance: 0 });
  const hovered = useRef<MapPoint | null>(null);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; title: string } | null>(null);
  const [revision, setRevision] = useState(0);
  const router = useRouter();
  const normalizedQuery = query.trim().toLocaleLowerCase("vi");
  const values = useMemo(() => [...new Set(data.points.map((point) => valueOf(point, color)))], [data.points, color]);
  const colors = useMemo(() => new Map(values.map((value, index) => [value, palette[index % palette.length]])), [values]);
  const grid = useMemo(() => {
    const cells = new Map<string, MapPoint[]>();
    for (const point of data.points) {
      const key = `${Math.floor((point.x + 1) * 10)}:${Math.floor((point.y + 1) * 10)}`;
      const cell = cells.get(key); if (cell) cell.push(point); else cells.set(key, [point]);
    }
    return cells;
  }, [data.points]);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const ratio = window.devicePixelRatio || 1;
    if (canvas.width !== Math.round(rect.width * ratio) || canvas.height !== Math.round(rect.height * ratio)) {
      canvas.width = Math.round(rect.width * ratio); canvas.height = Math.round(rect.height * ratio);
    }
    const context = canvas.getContext("2d");
    if (!context) return;
    context.setTransform(ratio, 0, 0, ratio, 0, 0); context.clearRect(0, 0, rect.width, rect.height);
    const view = transform.current;
    for (const point of data.points) {
      const x = (point.x + 1) / 2 * rect.width * view.scale + view.x;
      const y = (point.y + 1) / 2 * rect.height * view.scale + view.y;
      if (x < -8 || y < -8 || x > rect.width + 8 || y > rect.height + 8) continue;
      const match = !normalizedQuery || point.title?.toLocaleLowerCase("vi").includes(normalizedQuery);
      context.globalAlpha = match ? 0.82 : 0.09;
      context.fillStyle = colors.get(valueOf(point, color)) ?? palette[0];
      context.beginPath(); context.arc(x, y, match && normalizedQuery ? 4.5 : 2.6, 0, Math.PI * 2); context.fill();
    }
    context.globalAlpha = 1;
    if (view.scale >= 1.4) {
      context.font = "600 12px 'Be Vietnam Pro', sans-serif"; context.textAlign = "center";
      for (const topic of data.topics) {
        const x = (topic.cx + 1) / 2 * rect.width * view.scale + view.x;
        const y = (topic.cy + 1) / 2 * rect.height * view.scale + view.y;
        context.fillStyle = "rgba(255,255,255,.92)"; context.strokeStyle = "rgba(15,23,42,.18)"; context.lineWidth = 3;
        context.strokeText(topic.label, x, y); context.fillStyle = "#172554"; context.fillText(topic.label, x, y);
      }
    }
  }, [color, colors, data.points, data.topics, normalizedQuery]);

  useEffect(() => {
    draw();
    const canvas = canvasRef.current;
    if (!canvas) return;
    const observer = new ResizeObserver(draw); observer.observe(canvas);
    return () => observer.disconnect();
  }, [draw, revision]);

  function nearest(clientX: number, clientY: number) {
    const canvas = canvasRef.current;
    if (!canvas) return null;
    const rect = canvas.getBoundingClientRect();
    const view = transform.current;
    const x = ((clientX - rect.left - view.x) / view.scale / rect.width) * 2 - 1;
    const y = ((clientY - rect.top - view.y) / view.scale / rect.height) * 2 - 1;
    const cellX = Math.floor((x + 1) * 10); const cellY = Math.floor((y + 1) * 10);
    let best: MapPoint | null = null; let distance = 0.075 / view.scale;
    for (let dx = -1; dx <= 1; dx += 1) for (let dy = -1; dy <= 1; dy += 1) for (const point of grid.get(`${cellX + dx}:${cellY + dy}`) ?? []) {
      const next = Math.hypot(point.x - x, point.y - y); if (next < distance) { best = point; distance = next; }
    }
    return best;
  }

  function pointerDown(event: React.PointerEvent<HTMLCanvasElement>) {
    event.currentTarget.setPointerCapture(event.pointerId);
    pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
    drag.current = { x: event.clientX, y: event.clientY, moved: 0, distance: drag.current.distance };
    if (pointers.current.size === 2) { const [a, b] = [...pointers.current.values()]; drag.current.distance = Math.hypot(a.x - b.x, a.y - b.y); }
  }

  function pointerMove(event: React.PointerEvent<HTMLCanvasElement>) {
    const old = pointers.current.get(event.pointerId);
    if (old) {
      pointers.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
      const points = [...pointers.current.values()];
      if (points.length === 2) {
        const distance = Math.hypot(points[0].x - points[1].x, points[0].y - points[1].y);
        const factor = drag.current.distance ? distance / drag.current.distance : 1;
        transform.current.scale = Math.min(8, Math.max(0.7, transform.current.scale * factor)); drag.current.distance = distance;
      } else {
        transform.current.x += event.clientX - old.x; transform.current.y += event.clientY - old.y;
        drag.current.moved += Math.hypot(event.clientX - old.x, event.clientY - old.y);
      }
      draw(); return;
    }
    const point = nearest(event.clientX, event.clientY); hovered.current = point;
    const rect = event.currentTarget.getBoundingClientRect();
    setTooltip(point ? { x: event.clientX - rect.left + 10, y: event.clientY - rect.top + 10, title: point.title ?? "Chưa có tiêu đề" } : null);
  }

  function pointerUp(event: React.PointerEvent<HTMLCanvasElement>) {
    pointers.current.delete(event.pointerId);
  }

  function wheel(event: React.WheelEvent<HTMLCanvasElement>) {
    event.preventDefault();
    const rect = event.currentTarget.getBoundingClientRect(); const view = transform.current;
    const next = Math.min(8, Math.max(0.7, view.scale * (event.deltaY < 0 ? 1.15 : 0.87)));
    const x = event.clientX - rect.left; const y = event.clientY - rect.top;
    view.x = x - (x - view.x) * next / view.scale; view.y = y - (y - view.y) * next / view.scale; view.scale = next; draw();
  }

  function reset() { transform.current = { scale: 1, x: 0, y: 0 }; setRevision((value) => value + 1); setTooltip(null); }

  const legend = values.slice(0, 12);
  return <div>
    <div className="relative overflow-hidden rounded-lg border bg-card"><canvas ref={canvasRef} data-testid="knowledge-map-canvas" role="img" aria-label="Bản đồ các công trình theo không gian chuyên môn" className="block h-[520px] w-full touch-none cursor-grab active:cursor-grabbing" onPointerDown={pointerDown} onPointerMove={pointerMove} onPointerUp={pointerUp} onPointerCancel={(event) => pointers.current.delete(event.pointerId)} onPointerLeave={() => { if (!pointers.current.size) setTooltip(null); }} onClick={(event) => { if (drag.current.moved < 5) { const point = nearest(event.clientX, event.clientY); if (point) router.push(`/cong-trinh/?id=${point.id}`); } }} onWheel={wheel} />{tooltip && <div role="tooltip" className="pointer-events-none absolute z-10 max-w-64 rounded-md border bg-popover px-2.5 py-1.5 text-xs shadow-md" style={{ left: tooltip.x, top: tooltip.y }}>{tooltip.title}</div>}<Button type="button" size="sm" variant="outline" className="absolute right-3 top-3 bg-background/90" onClick={reset}><LocateFixed />Về toàn cảnh</Button></div>
    <div aria-label="Chú giải màu" className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-xs text-muted-foreground">{legend.map((value) => <span key={value} className="inline-flex items-center gap-1.5"><i className="size-2.5 rounded-full" style={{ background: colors.get(value) }} />{color === "topic" ? data.topics.find((topic) => String(topic.id) === value)?.label ?? "Khác" : color === "unit" ? `Đơn vị ${value}` : value}</span>)}{values.length > 12 && <span>+ Khác</span>}</div>
  </div>;
}
