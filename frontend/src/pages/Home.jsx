import { useEffect, useState } from "react";
import API from "../api/api";
import { useNavigate, useLocation } from "react-router-dom";
import "../styles/home.css";

function Home() {

  const navigate = useNavigate();
  const location = useLocation();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showPopup, setShowPopup] = useState(false);
  const [loading, setLoading] = useState(false);

  const [year, setYear] = useState("");
  const [date, setDate] = useState("");

  const clientId = localStorage.getItem("client_id");

  // ================= AUTH =================
  useEffect(() => {
    if (!clientId) {
      navigate("/login");
      return;
    }

    const checkToken = async () => {
      try {
        const res = await API.get(`/check-token/${clientId}/`);
        if (!res.data.token_exists) setShowPopup(true);
      } catch {
        navigate("/login");
      }
    };

    checkToken();
  }, [clientId, navigate]);

  // ================= TOKEN =================
  const generateToken = () => {
    window.location.href =
      `http://127.0.0.1:8000/api/fyers-login/${clientId}/`;
  };

  // ================= LOGOUT =================
  const logout = () => {
    localStorage.clear();
    navigate("/login");
  };

  // ================= DOWNLOAD BSE =================
  const downloadBSE = async () => {
    try {
      setLoading(true);
      const res = await API.get("/download-bse/");
      alert(res.data.message);
    } catch {
      alert("Download failed");
    } finally {
      setLoading(false);
    }
  };

  // ================= DOWNLOAD 1 MIN =================
  const download1Min = async () => {
    try {
      setLoading(true);
      await API.get(`/download-1min/?client_id=${clientId}`);
      alert("1 Min Data Download Started");
    } catch {
      alert("Download failed");
    } finally {
      setLoading(false);
    }
  };

  // ================= DAY =================
  const downloadDay = async () => {
    if (!date) return alert("Select date");

    try {
      setLoading(true);
      const res = await API.post("/download-day/", { date });
      alert(res.data.message);
    } catch {
      alert("Download failed");
    } finally {
      setLoading(false);
    }
  };

  // ================= YEAR =================
  const downloadYear = () => {
    if (!year) return alert("Enter year");
    navigate(`/logs?year=${year}`);
  };

  // ================= ALL =================
  const downloadAll = () => {
    navigate(`/logs?all=true`);
  };

  return (
    <div className="dashboard">

      {/* MOBILE MENU */}
      <div className="mobile-menu">
        <div className="hamburger" onClick={() => setSidebarOpen(!sidebarOpen)}>
          ☰
        </div>

        <div className="mobile-links">
          <span onClick={() => navigate("/user-dashboard")}>Dashboard</span>
          <span onClick={() => navigate("/files")}>Files</span>
          <span onClick={() => navigate("/1min-data")}>1 Min</span>
          <span onClick={() => navigate("/matrix")}>Matrix</span>
          <span onClick={() => navigate("/trash")}>Trash</span>
        </div>
      </div>

      {/* SIDEBAR */}
      <div className={`sidebar ${sidebarOpen ? "open" : ""}`}>

        <div className="logo">
          <div className="logo-main">
            <span className="logo-red">T</span>ime <span className="logo-red">L</span>ine <span className="logo-red">I</span>nvestments
          </div>
          <div className="logo-sub"><span className="logo-red">P</span>vt <span className="logo-red">T</span>td</div>
        </div>

        <ul>
          <li className={location.pathname === "/user-dashboard" ? "active" : ""} onClick={() => navigate("/user-dashboard")}>Dashboard</li>
          <li onClick={() => navigate("/files")}>Files</li>
          <li onClick={() => navigate("/1min-data")}>1 Min Data</li>
          <li onClick={() => navigate("/matrix")}>Matrix</li>
          <li onClick={() => navigate("/trash")}>Trash</li>
        </ul>

        <div className="sidebar-bottom">
          <button className="logout-btn" onClick={logout}>
            Logout
          </button>
        </div>
      </div>

      {/* MAIN */}
      <div className="main">

        <div className="topbar">
     
        </div>

        {/* CARDS */}
        <div className="cards">
          <div className="card"><h3>Status</h3><p>Active</p></div>
          <div className="card"><h3>Broker</h3><p>Fyers</p></div>
          <div className="card"><h3>Session</h3><p>Live</p></div>
        </div>

        {/* FYERS */}
        <div className="section">
          <h3>Fyers Data</h3>

          <div className="btn-group">
            <button className="btn" onClick={downloadBSE} disabled={loading}>
              {loading ? "Processing..." : "Download BSE"}
            </button>

            <button className="btn" onClick={download1Min} disabled={loading}>
              {loading ? "Processing..." : "1 Min Data Download"}
            </button>
          </div>
        </div>

        {/* DAY */}
        <div className="section">
          <h3>BSE Day Downloader</h3>

          <div className="form-row">
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />

            <button className="btn" onClick={downloadDay} disabled={loading}>
              Download
            </button>
          </div>
        </div>

        {/* YEAR */}
        <div className="section">
          <h3>BSE Year Downloader</h3>

          <div className="form-row">
            <input
              type="number"
              placeholder="Enter Year"
              value={year}
              onChange={(e) => setYear(e.target.value)}
            />

            <button className="btn" onClick={downloadYear}>
              Start
            </button>
          </div>
        </div>

        {/* ALL DATA */}
        <div className="section center">
          <h3>Download All Data</h3>

          <button className="btn large" onClick={downloadAll}>
            Download All Data Till Today
          </button>
        </div>

      </div>

      {/* POPUP */}
      {showPopup && (
        <div className="popup-overlay">
          <div className="popup">
            <h3>Generate Fyers Token</h3>
            <p>Token required for today session</p>
            <button className="btn" onClick={generateToken}>
              Generate Token
            </button>
          </div>
        </div>
      )}

    </div>
  );
}

export default Home;