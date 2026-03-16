import { useState } from "react";
import API from "../api/api";
import { useNavigate, Link } from "react-router-dom";
// import "./auth.css";

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