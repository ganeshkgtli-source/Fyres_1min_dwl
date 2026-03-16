import { useEffect, useState } from "react";
import API from "../api/api";
import Navbar from "../components/Navbar";
import "../styles//files.css";

function LogDashboard(){

const [logs,setLogs] = useState([]);
const [year,setYear] = useState("");
const [month,setMonth] = useState("");

useEffect(()=>{

fetchLogs();

},[]);


const fetchLogs = async()=>{

const res = await API.get("/logs/");

setLogs(res.data);

};


const applyFilter = async()=>{

const res = await API.get(`/logs/?year=${year}&month=${month}`);

setLogs(res.data);

};


const resetFilter = ()=>{

setYear("");
setMonth("");

fetchLogs();

};


return(

<div className="files-page">

<Navbar/>

<div className="files-container">

<h2 className="page-title">Download Logs</h2>


<div className="filters">

<select value={year} onChange={e=>setYear(e.target.value)}>
<option value="">Year</option>
<option>2025</option>
<option>2024</option>
<option>2023</option>
</select>

<select value={month} onChange={e=>setMonth(e.target.value)}>
<option value="">Month</option>
<option>01</option>
<option>02</option>
<option>03</option>
<option>04</option>
<option>05</option>
<option>06</option>
<option>07</option>
<option>08</option>
<option>09</option>
<option>10</option>
<option>11</option>
<option>12</option>
</select>

<button className="btn filter" onClick={applyFilter}>Filter</button>

<button className="btn reset" onClick={resetFilter}>Reset</button>

</div>


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

{logs.map((log,i)=>{

const rowClass =
log.status === "SUCCESS"
? "log-success"
: "log-failed";

return(

<tr key={i} className={rowClass}>

<td>{log.file}</td>
<td>{log.date}</td>
<td>{log.status}</td>
<td>{log.time}</td>

</tr>

);

})}

</tbody>

</table>

</div>

</div>

</div>

);

}

export default LogDashboard;