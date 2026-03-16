import { useState } from "react"
import Navbar from "../components/Navbar"

function Matrix(){

const [loaded,setLoaded] = useState(false)

return(

<div>

<Navbar/>

<div className="topbar">

<h2>Security Presence Matrix</h2>

<button onClick={()=>window.location="http://127.0.0.1:8000/api/download-matrix"}>
Download CSV
</button>

</div>

{!loaded &&

<div id="loader">

<div className="spinner"></div>
<br/>
Loading Matrix...

</div>

}

<iframe
src="http://127.0.0.1:8000/api/view-matrix"
style={{width:"100%",height:"88vh",border:"none"}}
onLoad={()=>setLoaded(true)}
/>

</div>

)

}

export default Matrix