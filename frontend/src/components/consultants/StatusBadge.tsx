interface Props {
  status?: string;
}

const styles: Record<string, string> = {
  NEW: "bg-blue-100 text-blue-700",
  MARKETING: "bg-yellow-100 text-yellow-700",
  SUBMITTED: "bg-purple-100 text-purple-700",
  INTERVIEW: "bg-indigo-100 text-indigo-700",
  PLACED: "bg-green-100 text-green-700",
};

export default function StatusBadge({
  status,
}: Props) {
  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-semibold ${
        styles[status ?? ""] ??
        "bg-slate-100 text-slate-700"
      }`}
    >
      {status ?? "-"}
    </span>
  );
}