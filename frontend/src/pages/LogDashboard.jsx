import { useEffect,useState } from "react"
import API from "../api/api"
import Navbar from "../components/Navbar"

function LogDashboard(){

const [logs,setLogs] = useState([])

useEffect(()=>{

API.get("/logs/")
.then(res=>setLogs(res.data))

},[])

return(

<div>

<Navbar/>

<h2>Download Logs</h2>

<table>

<thead>

<tr>
<th>File</th>
<th>Date</th>
<th>Status</th>
<th>Time</th>
</tr>

</thead>

<tbody>

{logs.map((log,i)=>(

<tr key={i}>

<td>{log.file}</td>
<td>{log.date}</td>
<td>{log.status}</td>
<td>{log.time}</td>

</tr>

))}

</tbody>

</table>

</div>

)

}

export default LogDashboard