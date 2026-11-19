type TextareaProps = React.TextareaHTMLAttributes<HTMLTextAreaElement>;

export function Textarea(props: TextareaProps) {
  return (
    <textarea
      {...props}
      className={`w-full rounded-[10px] border border-border bg-white px-3 py-3 text-foreground placeholder:text-muted ${props.className ?? ""}`}
    />
  );
}
