import { useState } from "react";
import API from "../api/api";
import { useNavigate, Link } from "react-router-dom";
// import "./auth.css";

function Register() {

  const navigate = useNavigate();

  const [form,setForm] = useState({
    username:"",
    email:"",
    password:"",
    client_id:"",
    secret_key:""
  });

  const [error,setError] = useState("");

  const handleChange = (e) => {

    setForm({
      ...form,
      [e.target.name]:e.target.value
    });

  };

  const handleSubmit = async (e) => {

    e.preventDefault();

    try{

      await API.post("/register/",form);

      navigate("/login");

    }catch (error) {

  if (error.response?.data) {

    const data = error.response.data;

    if (data.email) {
      setError(data.email[0]);
    } else if (data.client_id) {
      setError(data.client_id[0]);
    } else {
      setError("Registration failed");
    }

  }

}

  };

  return(

    <div className="auth-wrapper">

      <div className="auth-card">

        <h2 className="auth-title">Create Account</h2>

        {error && <p className="auth-error">{error}</p>}

        <form onSubmit={handleSubmit}>

          <input
            className="auth-input"
            name="username"
            placeholder="Username"
            onChange={handleChange}
            required
          />

          <input
            className="auth-input"
            name="email"
            type="email"
            placeholder="Email"
            onChange={handleChange}
            required
          />

          <input
            className="auth-input"
            name="password"
            type="password"
            placeholder="Password"
            onChange={handleChange}
            required
          />

          <input
            className="auth-input"
            name="client_id"
            placeholder="Fyers Client ID"
            onChange={handleChange}
            required
          />

          <input
            className="auth-input"
            name="secret_key"
            placeholder="Fyers Secret Key"
            onChange={handleChange}
            required
          />

          <button className="auth-button" type="submit">
            Register
          </button>

        </form>

        <div className="auth-footer">
          Already have an account? <Link to="/login">Login</Link>
        </div>

      </div>

    </div>

  );

}

export default Register;