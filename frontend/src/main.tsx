import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";

import "./index.css";

import App from "./App";
import { AuthProvider } from "./contexts/AuthContext";

const rootElement =
  document.getElementById("root");

if (!rootElement) {
  throw new Error(
    'Root element with id="root" was not found.',
  );
}

createRoot(rootElement).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
);