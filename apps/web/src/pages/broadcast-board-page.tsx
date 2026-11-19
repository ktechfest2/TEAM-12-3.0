import { PageHeader } from "../components/ui/surface";
import { LoginForm } from "../features/auth/login-form";
import { BroadcastBoard } from "../features/board/broadcast-board";
import { useSession } from "../lib/auth/session";

export function BroadcastBoardPage() {
  const session = useSession();
  return (
    <section className="space-y-8">
      <PageHeader title="Broadcast board" />
      {session ? <BroadcastBoard /> : <LoginForm />}
    </section>
  );
}
