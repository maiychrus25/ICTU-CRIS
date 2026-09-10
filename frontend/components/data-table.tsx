// Copyright (c) 2026 ICTU-CRIS contributors
// SPDX-License-Identifier: Apache-2.0

"use client";

import {
  createSortedRowModel, rowSelectionFeature, rowSortingFeature, tableFeatures, useTable,
  type ColumnDef, type OnChangeFn, type RowSelectionState,
} from "@tanstack/react-table";
import { ArrowDown, ArrowUp, ChevronsUpDown } from "lucide-react";
import { useMemo } from "react";

import { Pager } from "@/components/pager";
import { Checkbox } from "@/components/ui/checkbox";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export const dataTableFeatures = tableFeatures({ rowSortingFeature, sortedRowModel: createSortedRowModel(), rowSelectionFeature });
export type DataTableColumn<TData extends object> = ColumnDef<typeof dataTableFeatures, TData>;

interface DataTableProps<TData extends object> {
  columns: DataTableColumn<TData>[];
  data: TData[];
  emptyMessage?: string;
  getRowId?: (row: TData) => string;
  rowSelection?: RowSelectionState;
  onRowSelectionChange?: OnChangeFn<RowSelectionState>;
  page?: { page: number; perPage: number; total: number; onPageChange: (page: number) => void };
}

export function DataTable<TData extends object>({ columns, data, emptyMessage = "Không có dữ liệu phù hợp.", getRowId, rowSelection, onRowSelectionChange, page }: DataTableProps<TData>) {
  const selectable = rowSelection !== undefined && onRowSelectionChange !== undefined;
  const selectionColumn = useMemo<DataTableColumn<TData>>(() => ({
    id: "select", enableSorting: false,
    header: ({ table }) => <Checkbox aria-label="Chọn tất cả" checked={table.getIsAllRowsSelected()} indeterminate={!table.getIsAllRowsSelected() && table.getIsSomeRowsSelected()} onCheckedChange={(checked) => table.toggleAllRowsSelected(Boolean(checked))} />,
    cell: ({ row }) => <Checkbox aria-label="Chọn hàng" checked={row.getIsSelected()} onCheckedChange={(checked) => row.toggleSelected(Boolean(checked))} />,
  }), []);
  const resolvedColumns = useMemo(() => selectable ? [selectionColumn, ...columns] : columns, [columns, selectable, selectionColumn]);
  const table = useTable({ features: dataTableFeatures, columns: resolvedColumns, data, getRowId, enableRowSelection: selectable, ...(selectable ? { state: { rowSelection }, onRowSelectionChange } : {}) });

  return (
    <div className="overflow-hidden rounded-lg border bg-card">
      <Table>
        <TableHeader>{table.getHeaderGroups().map((group) => <TableRow key={group.id}>{group.headers.map((header) => {
          const sorted = header.column.getIsSorted();
          return <TableHead key={header.id}>{header.isPlaceholder ? null : header.column.getCanSort() ? <button type="button" className="inline-flex items-center gap-1.5" onClick={header.column.getToggleSortingHandler()}><table.FlexRender header={header} />{sorted === "asc" ? <ArrowUp className="size-3.5" /> : sorted === "desc" ? <ArrowDown className="size-3.5" /> : <ChevronsUpDown className="size-3.5 text-muted-foreground" />}</button> : <table.FlexRender header={header} />}</TableHead>;
        })}</TableRow>)}</TableHeader>
        <TableBody>{table.getRowModel().rows.length ? table.getRowModel().rows.map((row) => <TableRow key={row.id} data-state={row.getIsSelected() ? "selected" : undefined}>{row.getAllCells().map((cell) => <TableCell key={cell.id}><table.FlexRender cell={cell} /></TableCell>)}</TableRow>) : <TableRow><TableCell colSpan={resolvedColumns.length} className="h-28 text-center text-muted-foreground">{emptyMessage}</TableCell></TableRow>}</TableBody>
      </Table>
      {page && <Pager {...page} />}
    </div>
  );
}
