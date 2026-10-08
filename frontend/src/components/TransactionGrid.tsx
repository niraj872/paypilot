import { useMemo } from 'react';
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
import type { ColDef } from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import type { Transaction } from '../types';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-quartz.css';

ModuleRegistry.registerModules([AllCommunityModule]);

export function TransactionGrid({ rows }: { rows: Transaction[] }) {
  const columnDefs = useMemo<ColDef<Transaction>[]>(() => [
    { field: 'id', headerName: 'TX ID', width: 90 },
    { field: 'paypal_order_id', headerName: 'PayPal Order', flex: 1 },
    {
      field: 'amount',
      headerName: 'Amount',
      valueFormatter: (p: any) => `$${Number(p.value).toFixed(2)}`,
      width: 120,
    },
    {
      field: 'risk_score',
      headerName: 'Risk',
      width: 100,
      sortable: true,
      filter: true,
    },
    {
      field: 'verification_score',
      headerName: 'Verification',
      valueFormatter: (p: any) => `${p.value}%`,
      width: 130,
    },
    {
      field: 'status',
      headerName: 'Status',
      flex: 1,
      filter: true,
    },
    {
      field: 'created_at',
      headerName: 'Created',
      flex: 1,
    },
  ], []);

  return (
    <div
      className="ag-theme-quartz-dark h-[430px] w-full overflow-hidden rounded-xl"
      style={
        {
          '--ag-background-color': '#0d1a2b',
          '--ag-header-background-color': '#0a1524',
          '--ag-border-color': '#203149',
        } as React.CSSProperties
      }
    >
      <AgGridReact<Transaction>
        rowData={rows}
        columnDefs={columnDefs}
        animateRows
        pagination
        paginationPageSize={8}
      />
    </div>
  );
}