import { useEffect, useState } from "react";
import API from "../api/api";
import "../styles/dashboard.css";
import { FiEye, FiEyeOff } from "react-icons/fi";
import Navbar from "../components/Navbar";
function UserDashboard() {

  const clientId = localStorage.getItem("client_id");

  const [data, setData] = useState(null);
  const [remaining, setRemaining] = useState(0);

  const [showKey, setShowKey] = useState(false);
  const [showOldPass, setShowOldPass] = useState(false);
  const [showNewPass, setShowNewPass] = useState(false);

  const [oldPass, setOldPass] = useState("");
  const [newPass, setNewPass] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const res = await API.get(`user/dashboard/?client_id=${clientId}`);
      setData(res.data);
      setRemaining(res.data.remaining_seconds);
    } catch {
      alert("Failed to load data");
    }
  };

  // ⏱️ Live countdown
  useEffect(() => {
    if (!remaining) return;

    const timer = setInterval(() => {
      setRemaining((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);

    return () => clearInterval(timer);
  }, [remaining]);

  const changePassword = async () => {
    try {
      await API.post("/user/change-password/", {
        client_id: clientId,
        old_password: oldPass,
        new_password: newPass
      });

      alert("Password updated");
      setOldPass("");
      setNewPass("");
    } catch {
      alert("Wrong password");
    }
  };

  const formatTime = (sec) => {
    if (!sec) return "00:00:00";

    const h = String(Math.floor(sec / 3600)).padStart(2, "0");
    const m = String(Math.floor((sec % 3600) / 60)).padStart(2, "0");
    const s = String(sec % 60).padStart(2, "0");

    return `${h}:${m}:${s}`;
  };

  if (!data) return <div className="loader">Loading...</div>;

  return (<>
<Navbar/>
    <div className="dashboard-container">
      <div className="dashboard-box">

        <h2>User Dashboard</h2>

        {/* USER INFO */}
        <div className="grid">

          <div className="card">
            <span>Name</span>
            <h3>{data.username}</h3>
          </div>

          <div className="card">
            <span>Email</span>
            <h3>{data.email}</h3>
          </div>

          <div className="card">
            <span>Client ID</span>
            <h3>{data.client_id}</h3>
          </div>

          <div className="card">
  <span>Secret Key</span>

  <div className="input-wrappera">
    <input
      type={showKey ? "text" : "password"}
      value={data.secret_key}
      readOnly
    />

    <span
      className="eye-icon"
      onClick={() => setShowKey(!showKey)}
    >
      {showKey ? <FiEyeOff /> : <FiEye />}
    </span>
  </div>
</div>

        </div>

        {/* TOKEN */}
        <div className="section">
          <h3>Access Token</h3>

          <p>
            Status:
            <span className={data.token_valid ? "active" : "expired"}>
              {data.token_valid ? " Active" : " Expired"}
            </span>
          </p>

          <p>
            Remaining: <b>{formatTime(remaining)}</b>
          </p>
        </div>

        {/* PASSWORD */}
   <div className="section">
  <h3>Change Password</h3>

  <div className="password-group">

    {/* OLD PASSWORD */}
    <div className="input-wrapper">
      <input
        type={showOldPass ? "text" : "password"}
        placeholder="Old Password"
        value={oldPass}
        onChange={(e) => setOldPass(e.target.value)}
      />

      {/* <span
        className="eye-icon"
        onClick={() => setShowOldPass(!showOldPass)}
      >
        {showOldPass ? <FiEyeOff /> : <FiEye />}
      </span> */}
    </div>

    {/* NEW PASSWORD */}
    <div className="input-wrapper">
      <input
        type={showNewPass ? "text" : "password"}
        placeholder="New Password"
        value={newPass}
        onChange={(e) => setNewPass(e.target.value)}
      />

    
    </div>

    <button className="primary-btn" onClick={changePassword}>
      Update Password
    </button>

  </div>
</div>
      </div>
    </div>
    </>
  );
}

export default UserDashboard;