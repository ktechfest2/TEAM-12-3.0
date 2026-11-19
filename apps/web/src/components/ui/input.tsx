type InputProps = React.InputHTMLAttributes<HTMLInputElement>;

export function Input(props: InputProps) {
  return (
    <input
      {...props}
      className={`min-h-11 w-full rounded-[10px] border border-border bg-white px-3 text-foreground placeholder:text-muted ${props.className ?? ""}`}
    />
  );
}
