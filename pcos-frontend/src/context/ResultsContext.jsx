import { createContext, useContext, useState, useCallback } from "react";

const ResultsContext = createContext(null);

const STORAGE_KEY = "pcos_diagnostic_results";

export function ResultsProvider({ children }) {
  const [results, setResultsState] = useState(() => {
    try {
      const stored = sessionStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  const setResults = useCallback((data) => {
    setResultsState(data);
    if (data) {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } else {
      sessionStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const clearResults = useCallback(() => {
    setResults(null);
  }, [setResults]);

  return (
    <ResultsContext.Provider value={{ results, setResults, clearResults }}>
      {children}
    </ResultsContext.Provider>
  );
}

export function useResults() {
  const ctx = useContext(ResultsContext);
  if (!ctx) throw new Error("useResults must be used within ResultsProvider");
  return ctx;
}
