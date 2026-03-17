import { useEffect, useState } from "react"
import API from "../api/api"
import Navbar from "../components/Navbar"
import "../styles/files.css"

function LogDashboard(){

const [logs,setLogs] = useState([])

useEffect(()=>{
fetchLogs()
},[])


// FETCH LOGS
const fetchLogs = async()=>{
try{
const res = await API.get("/logs/")
setLogs(res.data || [])
}catch(err){
console.error(err)
}
}


return(

<div className="files-page">

<Navbar/>

<div className="files-container">

<h2 className="page-title">Download Logs</h2>


<div className="table-container">

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

{logs.length === 0 ? (
<tr>
<td colSpan="4">No logs found</td>
</tr>
) : (
logs.map((log,i)=>{

const rowClass =
log.status === "active"
? "log-success"
: "log-deleted"

return(
<tr key={i} className={rowClass}>
<td>{log.file_name}</td>
<td>{log.trade_date}</td>
<td>{log.status}</td>
<td>{log.download_time}</td>
</tr>
)

})
)}

</tbody>

</table>

</div>

</div>

</div>

)

}

export default LogDashboard