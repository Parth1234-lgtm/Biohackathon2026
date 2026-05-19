import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ResultsProvider } from "./context/ResultsContext";
import FormPage from "./pages/FormPage";
import ResultsPage from "./pages/ResultsPage";

export default function App() {
  return (
    <ResultsProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<FormPage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ResultsProvider>
  );
}
