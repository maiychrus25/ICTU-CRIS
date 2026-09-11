// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import type { CoauthorsOut } from "@/lib/types";

const layoutCache = new Map<string, Map<number, { x: number; y: number }>>();

function layoutGraph(data: CoauthorsOut) {
  const key = data.nodes.map((node) => node.person_id).join(",");
  const cached = layoutCache.get(key); if (cached) return cached;
  const positions = new Map(data.nodes.map((node, index) => [node.person_id, { x: Math.cos(index / data.nodes.length * Math.PI * 2) * 0.38, y: Math.sin(index / data.nodes.length * Math.PI * 2) * 0.38 }]));
  // ponytail: O(n²) repulsion is bounded at 300 nodes; switch to a spatial index only if this endpoint grows.
  if (data.nodes.length <= 300) for (let step = 0; step < 200; step += 1) {
    const force = new Map(data.nodes.map((node) => [node.person_id, { x: 0, y: 0 }]));
    for (let i = 0; i < data.nodes.length; i += 1) for (let j = i + 1; j < data.nodes.length; j += 1) {
      const a = positions.get(data.nodes[i].person_id)!; const b = positions.get(data.nodes[j].person_id)!;
      const dx = a.x - b.x; const dy = a.y - b.y; const distance = Math.max(0.02, dx * dx + dy * dy); const power = 0.00018 / distance;
      force.get(data.nodes[i].person_id)!.x += dx * power; force.get(data.nodes[i].person_id)!.y += dy * power;
      force.get(data.nodes[j].person_id)!.x -= dx * power; force.get(data.nodes[j].person_id)!.y -= dy * power;
    }
    for (const edge of data.edges) {
      const a = positions.get(edge.a); const b = positions.get(edge.b); if (!a || !b) continue;
      const dx = b.x - a.x; const dy = b.y - a.y; const pull = 0.004;
      force.get(edge.a)!.x += dx * pull; force.get(edge.a)!.y += dy * pull; force.get(edge.b)!.x -= dx * pull; force.get(edge.b)!.y -= dy * pull;
    }
    for (const node of data.nodes) { const point = positions.get(node.person_id)!; const next = force.get(node.person_id)!; point.x = Math.max(-0.46, Math.min(0.46, (point.x + next.x) * 0.997)); point.y = Math.max(-0.46, Math.min(0.46, (point.y + next.y) * 0.997)); }
  }
  layoutCache.set(key, positions); return positions;
}

export function CoauthorGraph({ data }: { data: CoauthorsOut }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const positions = useMemo(() => layoutGraph(data), [data]);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; text: string } | null>(null);
  const hovered = useRef<number | null>(null);
  const router = useRouter();

  const draw = useCallback(() => {
    const canvas = canvasRef.current; if (!canvas) return;
    const rect = canvas.getBoundingClientRect(); const ratio = window.devicePixelRatio || 1;
    canvas.width = Math.round(rect.width * ratio); canvas.height = Math.round(rect.height * ratio);
    const context = canvas.getContext("2d"); if (!context) return;
    context.setTransform(ratio, 0, 0, ratio, 0, 0); context.clearRect(0, 0, rect.width, rect.height);
    const screen = (id: number) => { const point = positions.get(id)!; return { x: (point.x + 0.5) * rect.width, y: (point.y + 0.5) * rect.height }; };
    context.strokeStyle = "rgba(59, 130, 246, .28)";
    for (const edge of data.edges) { if (!positions.has(edge.a) || !positions.has(edge.b)) continue; const a = screen(edge.a); const b = screen(edge.b); context.lineWidth = Math.min(7, 0.6 + edge.weight * 0.7); context.beginPath(); context.moveTo(a.x, a.y); context.lineTo(b.x, b.y); context.stroke(); }
    for (const node of data.nodes) { const point = screen(node.person_id); const radius = Math.min(15, 5 + Math.sqrt(node.works)); context.fillStyle = hovered.current === node.person_id ? "#1d4ed8" : "#2563eb"; context.beginPath(); context.arc(point.x, point.y, radius, 0, Math.PI * 2); context.fill(); context.strokeStyle = "#fff"; context.lineWidth = 2; context.stroke(); }
  }, [data.edges, data.nodes, positions]);

  useEffect(() => { draw(); const canvas = canvasRef.current; if (!canvas) return; const observer = new ResizeObserver(draw); observer.observe(canvas); return () => observer.disconnect(); }, [draw]);

  function nearest(event: React.MouseEvent<HTMLCanvasElement>) {
    const rect = event.currentTarget.getBoundingClientRect(); let id: number | null = null; let best = 22;
    for (const node of data.nodes) { const point = positions.get(node.person_id)!; const distance = Math.hypot((point.x + 0.5) * rect.width - (event.clientX - rect.left), (point.y + 0.5) * rect.height - (event.clientY - rect.top)); if (distance < best) { id = node.person_id; best = distance; } }
    return id;
  }

  return <div className="relative overflow-hidden rounded-lg border bg-card"><canvas ref={canvasRef} data-testid="coauthor-canvas" role="img" aria-label="Mạng lưới đồng tác giả" className="block h-[520px] w-full cursor-pointer" onPointerMove={(event) => { const id = nearest(event); hovered.current = id; const rect = event.currentTarget.getBoundingClientRect(); const node = data.nodes.find((item) => item.person_id === id); setTooltip(node ? { x: event.clientX - rect.left + 10, y: event.clientY - rect.top + 10, text: `${node.display_name} · ${node.works} công trình` } : null); draw(); }} onPointerLeave={() => { hovered.current = null; setTooltip(null); draw(); }} onClick={(event) => { const id = nearest(event); if (id) router.push(`/giang-vien/?id=${id}`); }} />{tooltip && <div role="tooltip" className="pointer-events-none absolute rounded-md border bg-popover px-2.5 py-1.5 text-xs shadow-md" style={{ left: tooltip.x, top: tooltip.y }}>{tooltip.text}</div>}</div>;
}
