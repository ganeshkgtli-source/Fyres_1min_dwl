import { useNavigate } from "react-router-dom";
import "../styles/navbar.css";

function Navbar(){

const navigate = useNavigate();

return(

<div className="navbar">

{/* COMPANY NAME */}

<div className="logo" onClick={()=>navigate("/")} >

<span className="logo-red">T</span>ime&nbsp;
<span className="logo-red">L</span>ine&nbsp;
<span className="logo-red">I</span>nvestments&nbsp;
<span className="logo-red">P</span>vt&nbsp;
<span className="logo-red">L</span>td

</div>


{/* NAV BUTTONS */}

<div className="nav-buttons">

<button onClick={()=>navigate("/")}>Home</button>

<button onClick={()=>navigate("/files")}>Files</button>
<button onClick={() => navigate("/1min-data")}>1 Min Data</button>

<button onClick={()=>navigate("/trash")}>Trash</button>

<button onClick={()=>navigate("/log-dashboard")}>History</button>


</div>

</div>

)

}

export default Navbar