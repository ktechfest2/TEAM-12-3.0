import { PageTitle } from "../components/ui/page-header";
import { LoginForm } from "../features/auth/login-form";
import { BroadcastBoard } from "../features/board/broadcast-board";
import { useSession } from "../lib/auth/session";

export function BroadcastBoardPage() {
  const session = useSession();
  return (
    <section className="space-y-6">
      <PageTitle title="Broadcast board" />
      {session ? <BroadcastBoard /> : <LoginForm />}
    </section>
  );
}
