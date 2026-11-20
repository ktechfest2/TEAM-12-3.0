/** Shared look for text inputs, selects and textareas. 44 px tall, labelled by the caller. */
export const controlClass =
  "min-h-11 w-full rounded-control border border-border-strong bg-surface px-3 text-foreground placeholder:text-muted focus:border-brand";

type InputProps = React.InputHTMLAttributes<HTMLInputElement>;
type SelectProps = React.SelectHTMLAttributes<HTMLSelectElement>;

export function Input({ className = "", ...props }: InputProps) {
  return <input {...props} className={`${controlClass} ${className}`} />;
}

export function Select({ className = "", ...props }: SelectProps) {
  return <select {...props} className={`${controlClass} ${className}`} />;
}
