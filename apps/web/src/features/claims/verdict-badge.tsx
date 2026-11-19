import { Icon, type IconName } from "../../components/icons";
import { type Verdict, verdictLabel, verdictTone } from "./verdict";

const verdictIcon: Record<Verdict, IconName> = {
  confirmed: "checkCircle",
  contradicted: "xCircle",
  no_official_statement: "searchOff",
};

type Props = { verdict: Verdict; large?: boolean };

export function VerdictBadge({ verdict, large = false }: Props) {
  return (
    <p
      className={`inline-flex items-center gap-2 rounded-full border font-bold ${
        large ? "px-4 py-2 text-base" : "px-3 py-1 text-sm"
      } ${verdictTone[verdict]}`}
    >
      <Icon name={verdictIcon[verdict]} size={large ? 22 : 18} />
      {verdictLabel[verdict]}
    </p>
  );
}
