import { createContext, useState, useContext } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {

  const [token, setToken] = useState(localStorage.getItem("token"));

  const login = (tokenValue) => {

    localStorage.setItem("token", tokenValue);
    setToken(tokenValue);

  };

  const logout = () => {

    localStorage.removeItem("token");
    setToken(null);

  };

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );

}

export const useAuth = () => useContext(AuthContext);