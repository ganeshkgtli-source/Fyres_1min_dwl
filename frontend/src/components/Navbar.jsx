import { useNavigate } from "react-router-dom";

function Navbar(){

const navigate = useNavigate()

return(

<div className="navbar">

<div className="logo">
<span>T</span>IME
<span>L</span>INE
<span>I</span>NVESTMENTS
<span>P</span>VT
<span>L</span>TD
</div>

<div className="nav-buttons">

<button onClick={()=>navigate("/")}>Home</button>

<button onClick={()=>navigate("/files")}>Files</button>

<button onClick={()=>navigate("/trash")}>Trash</button>

<button onClick={()=>navigate("/log-dashboard")}>History</button>

</div>

</div>

)

}

export default Navbar