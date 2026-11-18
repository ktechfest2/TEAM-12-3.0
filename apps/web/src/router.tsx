import { createBrowserRouter } from "react-router";
import { AppLayout } from "./components/app-layout";
import { BroadcastBoardPage } from "./pages/broadcast-board-page";
import { PublicCorrectionPage } from "./pages/public-correction-page";
import { ReviewQueuePage } from "./pages/review-queue-page";
import { SubmitClaimPage } from "./pages/submit-claim-page";

export const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
      { index: true, element: <SubmitClaimPage /> },
      { path: "review", element: <ReviewQueuePage /> },
      { path: "board", element: <BroadcastBoardPage /> },
      { path: "c/:messageId", element: <PublicCorrectionPage /> },
    ],
  },
]);
