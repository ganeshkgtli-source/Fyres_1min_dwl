import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { AuthProvider } from "./auth/AuthContext";
 
 
import "./styles/dashboard.css"
import "./styles/tli.css"
ReactDOM.createRoot(document.getElementById("root")).render(

  <AuthProvider>
    <App />
  </AuthProvider>

);