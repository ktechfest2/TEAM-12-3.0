import { createBrowserRouter, Navigate } from "react-router";
import { DashboardLayout } from "./components/dashboard-layout";
import { PublicLayout } from "./components/public-layout";
import { BroadcastBoardPage } from "./pages/broadcast-board-page";
import { ClaimsTablePage } from "./pages/claims-table-page";
import { DashboardOverviewPage } from "./pages/dashboard-overview-page";
import { EvidenceLibraryPage } from "./pages/evidence-library-page";
import { FactCheckDetailPage } from "./pages/fact-check-detail-page";
import { FactCheckListingPage } from "./pages/fact-check-listing-page";
import { GuidePage } from "./pages/guide-page";
import { Homepage } from "./pages/homepage";
import { InformationDetailPage } from "./pages/information-detail-page";
import { InformationHubPage } from "./pages/information-hub-page";
import { PublicCorrectionPage } from "./pages/public-correction-page";
import { SubmitClaimPage } from "./pages/submit-claim-page";
import { SubscribePage } from "./pages/subscribe-page";
import { VerificationPage } from "./pages/verification-page";

export const router = createBrowserRouter([
  {
    element: <PublicLayout />,
    children: [
      { index: true, element: <Homepage /> },
      { path: "check", element: <SubmitClaimPage /> },
      { path: "guide", element: <GuidePage /> },
      { path: "subscribe", element: <SubscribePage /> },
      { path: "information", element: <InformationHubPage /> },
      { path: "information/:slug", element: <InformationDetailPage /> },
      { path: "fact-checks", element: <FactCheckListingPage /> },
      { path: "fact-checks/:slug", element: <FactCheckDetailPage /> },
      { path: "c/:messageId", element: <PublicCorrectionPage /> },
    ],
  },
  {
    path: "dashboard",
    element: <DashboardLayout />,
    children: [
      { index: true, element: <DashboardOverviewPage /> },
      { path: "claims", element: <ClaimsTablePage /> },
      { path: "verification", element: <VerificationPage /> },
      { path: "verification/:messageId", element: <VerificationPage /> },
      { path: "evidence", element: <EvidenceLibraryPage /> },
      { path: "board", element: <BroadcastBoardPage /> },
    ],
  },
  // Links shared before the dashboard moved still work.
  { path: "review", element: <Navigate to="/dashboard/verification" replace /> },
  { path: "board", element: <Navigate to="/dashboard/board" replace /> },
]);
