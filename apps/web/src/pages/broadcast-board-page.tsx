import { LoginForm } from "../features/auth/login-form";
import { BroadcastBoard } from "../features/board/broadcast-board";
import { useSession } from "../lib/auth/session";

export function BroadcastBoardPage() {
  const session = useSession();
  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-bold">Broadcast board</h1>
      {session ? <BroadcastBoard /> : <LoginForm />}
    </section>
  );
}
