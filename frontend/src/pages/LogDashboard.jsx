import { useEffect, useState } from "react"
import API from "../api/api"
import Navbar from "../components/Navbar"
import "../styles/files.css"

function LogDashboard(){

const [logs,setLogs] = useState([])

useEffect(()=>{
fetchLogs()
},[])


// 🔄 FETCH LOGS
const fetchLogs = async()=>{
try{
const res = await API.get("/logs/")
setLogs(res.data || [])
}catch(err){
console.error("Error fetching logs:", err)
}
}


// ⏱ FORMAT TIME (NO DECIMALS)
const formatDateTime = (iso) => {
  if (!iso) return ""

  const date = new Date(iso)

  // DATE → DD-MM-YY
  const day = String(date.getDate()).padStart(2, "0")
  const month = String(date.getMonth() + 1).padStart(2, "0")
  const year = String(date.getFullYear()).slice(-2)

  // TIME → HH:MM:SS
  const time = date.toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  })

  return `${day}-${month}-${year}, ${time}`
}


// 🎯 STATUS CLASS
const getStatusClass = (status) => {
if (!status) return ""

const s = status.toLowerCase()

if (s.includes("download")) return "success"
if (s.includes("not") || s.includes("delete")) return "failed"

return ""
}


return(

<div className="files-page">

<Navbar/>

<div className="files-container">

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
logs.map((log,i)=>(
<tr key={i}>

<td>{log.file_name}</td>

<td>{log.trade_date}</td>

<td>
<span className={`status-badge ${getStatusClass(log.status)}`}>
{log.status}
</span>
</td>

<td>{formatDateTime(log.download_time)}</td>

</tr>
))
)}

</tbody>

</table>

</div>

</div>

</div>

)

}

export default LogDashboard