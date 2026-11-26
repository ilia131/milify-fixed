interface MetricRowProps {
    label: string;
    value: string;
  }
  
  export default function MetricRow({
    label,
    value,
  }: MetricRowProps) {
    return (
      <div className="flex items-center justify-between">
        <span className="text-xs text-zinc-600">
          {label}
        </span>
  
        <span className="text-xs font-medium text-zinc-400">
          {value}
        </span>
      </div>
    );
  }