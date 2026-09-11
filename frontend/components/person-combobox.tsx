// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import { Search } from "lucide-react";
import { useEffect, useId, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { usePersonSearch } from "@/lib/queries";
import type { PersonSearchRow } from "@/lib/types";

export function PersonCombobox({ id, onValueChange, onSelect }: { id?: string; onValueChange: (id: number | null) => void; onSelect?: (person: PersonSearchRow) => void }) {
  const generatedId = useId();
  const listId = useId();
  const inputId = id ?? generatedId;
  const [text, setText] = useState("");
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const people = usePersonSearch(query);

  useEffect(() => {
    const timeout = window.setTimeout(() => setQuery(text.trim()), 250);
    return () => window.clearTimeout(timeout);
  }, [text]);

  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-2.5 top-2.5 z-10 size-4 text-muted-foreground" />
      <Input
        id={inputId}
        role="combobox"
        aria-label="Tìm người"
        aria-autocomplete="list"
        aria-controls={listId}
        aria-expanded={open}
        value={text}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onChange={(event) => { setText(event.target.value); onValueChange(null); setOpen(true); }}
        className="pl-8"
        placeholder="Nhập tên giảng viên…"
        autoComplete="off"
      />
      {open && query && (
        <div id={listId} role="listbox" className="absolute z-50 mt-1 max-h-64 w-full overflow-y-auto rounded-lg border bg-popover p-1 text-popover-foreground shadow-md">
          {people.isFetching ? <p className="px-3 py-2 text-sm text-muted-foreground">Đang tìm người…</p>
            : people.isError ? <div className="flex items-center justify-between gap-2 px-3 py-2 text-sm text-destructive"><span>Không thể tìm người.</span><Button type="button" variant="ghost" size="sm" onMouseDown={(event) => event.preventDefault()} onClick={() => people.refetch()}>Thử lại</Button></div>
            : people.data?.length ? people.data.map((person) => (
              <button key={person.id} type="button" role="option" aria-selected="false" className="block w-full rounded-md px-3 py-2 text-left hover:bg-accent focus:bg-accent focus:outline-none" onMouseDown={(event) => event.preventDefault()} onClick={() => { setText(person.display_name); onValueChange(person.id); onSelect?.(person); setOpen(false); }}>
                <span className="block font-medium">{person.display_name}</span>
                <span className="block text-xs text-muted-foreground">{[person.degree, person.unit_code, `${person.works} công trình`].filter(Boolean).join(" · ")}</span>
              </button>
            )) : <p className="px-3 py-2 text-sm text-muted-foreground">Không tìm thấy người phù hợp.</p>}
        </div>
      )}
    </div>
  );
}
