import { useState } from "react";
import API from "../api/api";
import { useNavigate } from "react-router-dom";
import "../styles/auth.css";

function Login() {

  const navigate = useNavigate();

  const [email,setEmail] = useState("");
  const [password,setPassword] = useState("");

  const handleSubmit = async (e)=>{
    e.preventDefault();

    try{
      const res = await API.post("/login/",{
        email,
        password
      });

      const {status, client_id, auth_url, is_admin} = res.data;

      localStorage.setItem("client_id", client_id);
      localStorage.setItem("is_admin", is_admin);

      if (status === "login_success") {
        if (is_admin) {
          navigate("/admin");   // 🔥 admin
        } else {
          navigate("/");        // user
        }
      }

      if (status === "fyers_login") {
        window.location.href = auth_url;
      }

    }catch{
      alert("Invalid credentials");
    }
  };

  return(
    <div className="auth-wrapper">

      <div className="auth-card">

        <div className="logo">
          <span className="logo-red">T</span>ime&nbsp;
          <span className="logo-red">L</span>ine&nbsp;
          <span className="logo-red">I</span>nvestments&nbsp;
          <span className="logo-red">P</span>vt&nbsp;
          <span className="logo-red">L</span>td
        </div>

        <h2 className="auth-title">Login</h2>

        <form onSubmit={handleSubmit}>

          <input
            className="auth-input"
            type="email"
            placeholder="Email"
            onChange={(e)=>setEmail(e.target.value)}
            required
          />

          <input
            className="auth-input"
            type="password"
            placeholder="Password"
            onChange={(e)=>setPassword(e.target.value)}
            required
          />

          <button className="auth-button" type="submit">
            Login
          </button>

        </form>

        <div className="auth-footer">
          Contact admin for account access
        </div>

      </div>

    </div>
  );
}

export default Login;