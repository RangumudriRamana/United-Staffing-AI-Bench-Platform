import { Plus, Search } from "lucide-react";

interface Props {
  search: string;
  onSearchChange: (value: string) => void;
  onAdd: () => void;
}

export default function ConsultantToolbar({
  search,
  onSearchChange,
  onAdd,
}: Props) {
  return (
    <div className="flex items-center justify-between rounded-lg border bg-white p-4 shadow-sm">
      <div className="relative w-96">
        <Search
          className="absolute left-3 top-3 text-slate-400"
          size={18}
        />

        <input
          value={search}
          onChange={(e) =>
            onSearchChange(e.target.value)
          }
          placeholder="Search consultants..."
          className="w-full rounded-lg border py-2 pl-10 pr-3 outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <button
        onClick={onAdd}
        className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
      >
        <Plus size={18} />
        Add Consultant
      </button>
    </div>
  );
}