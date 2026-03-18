import { useEffect, useState } from "react";
import API from "../api/api";
import { useNavigate } from "react-router-dom";
import "../styles/home.css";

function Home() {

  const navigate = useNavigate();

  const [showPopup, setShowPopup] = useState(false);
  const [loading, setLoading] = useState(false);

  const [year, setYear] = useState("");
  const [date, setDate] = useState("");

  const clientId = localStorage.getItem("client_id");

  useEffect(() => {

    if (!clientId) {
      navigate("/login");
      return;
    }

    const checkToken = async () => {
      try {
        const res = await API.get(`/check-token/${clientId}/`);

        if (!res.data.token_exists) {
          setShowPopup(true);
        }

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
    localStorage.removeItem("client_id");
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
    }
    setLoading(false);
  };

  // ================= DOWNLOAD 1 MIN =================
  const download1Min = async () => {
    try {
      setLoading(true);
      await API.get(`/download-1min/?client_id=${clientId}`);

      // ✅ redirect to logs
      // navigate("/logs");

    } catch {
      alert("Download failed");
    }
    setLoading(false);
  };

  // ================= DAY =================
  const downloadDay = async () => {

    if (!date) {
      alert("Select date");
      return;
    }

    try {
      setLoading(true);

      const res = await API.post("/download-day/", {
        date: date
      });

      alert(res.data.message);

    } catch {
      alert("Download failed");
    }

    setLoading(false);
  };

  // ================= YEAR =================
  const downloadYear = () => {

    if (!year) {
      alert("Enter year");
      return;
    }

    navigate(`/logs?year=${year}`);
  };

  // ================= ALL =================
  const downloadAll = () => {
    navigate(`/logs?all=true`);
  };

  return (

    <div className="dashboard">

      {/* SIDEBAR */}
      <div className="sidebar">

        <h2 className="logo">TLI</h2>

        <ul>
          <li onClick={() => navigate("/")}>Dashboard</li>
          <li onClick={() => navigate("/files")}>Files</li>
          <li onClick={() => navigate("/1min-data")}>1 Min Data</li> {/* ✅ ADDED */}
          <li onClick={() => navigate("/matrix")}>Matrix</li>
          <li onClick={() => navigate("/trash")}>Trash</li>
        </ul>

      </div>

      {/* MAIN */}
      <div className="main">

        {/* TOPBAR */}
        <div className="topbar">
          <div className="logo" onClick={()=>navigate("/")} >

<span className="logo-red">T</span>ime&nbsp;
<span className="logo-red">L</span>ine&nbsp;
<span className="logo-red">I</span>nvestments&nbsp;
<span className="logo-red">P</span>vt&nbsp;
<span className="logo-red">L</span>td

</div>

          <button onClick={logout} className="logout-btn">
            Logout
          </button>
        </div>

        {/* CARDS */}
        <div className="cards">
          <div className="card">
            <h3>Status</h3>
            <p>Active</p>
          </div>

          <div className="card">
            <h3>Broker</h3>
            <p>Fyers</p>
          </div>

          <div className="card">
            <h3>Session</h3>
            <p>Live</p>
          </div>
        </div>

        {/* FYERS */}
        <div className="section">

          <h3>Fyers Data</h3>

          <div className="btn-group">

            <button className="btn" onClick={downloadBSE} disabled={loading}>
              Download BSE Symbols
            </button>

            <button className="btn" onClick={download1Min} disabled={loading}>
              Download 1 Minute Data
            </button>

          </div>

        </div>

        {/* DAY */}
        <div className="section">

          <h3>BSE Day Downloader</h3>

          <div className="year-download">

            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />

            <button className="btn" onClick={downloadDay} disabled={loading}>
              Download Day
            </button>

          </div>

        </div>

        {/* YEAR */}
        <div className="section">

          <h3>BSE Year Downloader</h3>

          <div className="year-download">

            <input
              type="number"
              placeholder="Enter Year (ex: 2024)"
              value={year}
              onChange={(e) => setYear(e.target.value)}
            />

            <button className="btn" onClick={downloadYear} disabled={loading}>
              Start Download
            </button>

          </div>

        </div>

        {/* ALL */}
        <div className="section">

          <h3>Download All Data</h3>

          <button className="btn" onClick={downloadAll} disabled={loading}>
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
            <button onClick={generateToken}>
              Generate Token
            </button>
          </div>
        </div>
      )}

    </div>
  );
}

export default Home;