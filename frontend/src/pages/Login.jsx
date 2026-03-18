import { useState } from "react";
import API from "../api/api";
import { useNavigate, Link } from "react-router-dom";
import "../styles/files.css"

function Login(){

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

    const {status, client_id, auth_url} = res.data;

    localStorage.setItem("client_id",client_id);

    if(status === "login_success"){
      navigate("/");
    }

    if(status === "redirect_fyers"){
      window.location.href = auth_url;
    }

  }catch{
    alert("Invalid credentials");
  }
};

return(

<div className="auth-wrapper">

  {/* LOGO */}
  <div className="logo" onClick={()=>navigate("/")}>
    <span className="logo-red">T</span>ime&nbsp;
    <span className="logo-red">L</span>ine&nbsp;
    <span className="logo-red">I</span>nvestments&nbsp;
    <span className="logo-red">P</span>vt&nbsp;
    <span className="logo-red">L</span>td
  </div>

  <div className="auth-card">

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
      Don't have an account? <Link to="/register">Register</Link>
    </div>

  </div>

</div>

);

}

export default Login;