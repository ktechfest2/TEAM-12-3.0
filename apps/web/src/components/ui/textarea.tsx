import { controlClass } from "./input";

type TextareaProps = React.TextareaHTMLAttributes<HTMLTextAreaElement>;

export function Textarea({ className = "", ...props }: TextareaProps) {
  return <textarea {...props} className={`${controlClass} py-3 ${className}`} />;
}
