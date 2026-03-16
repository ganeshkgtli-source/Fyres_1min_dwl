import { useEffect, useState } from "react";
import API from "../api/api";
import Navbar from "../components/Navbar";
import "../styles//files.css";

function Files(){

const [files,setFiles] = useState([]);
const [years,setYears] = useState([]);
const [months,setMonths] = useState([]);

const [selected,setSelected] = useState([]);

const [year,setYear] = useState("");
const [month,setMonth] = useState("");

useEffect(()=>{

fetchFiles();

},[]);


const fetchFiles = async()=>{

const res = await API.get("/files/");

setFiles(res.data.files);
setYears(res.data.years);
setMonths(res.data.months);

};


// FILTER BUTTON
const applyFilter = async()=>{

const res = await API.get(`/files/?year=${year}&month=${month}`);

setFiles(res.data.files);

};


// RESET BUTTON
const resetFilter = async()=>{

setYear("");
setMonth("");

fetchFiles();

};


const toggleFile=(id)=>{

if(selected.includes(id))
setSelected(selected.filter(x=>x!==id));
else
setSelected([...selected,id]);

};


const selectAll=()=>{

setSelected(files.map(f=>f.id));

};


const unselectAll=()=>{

setSelected([]);

};


const downloadSelected = async()=>{

await API.post("/download-selected/",{ids:selected});

alert("Download started");

};


const moveToTrash = async()=>{

await API.post("/move-to-trash/",{ids:selected});

alert("Moved to trash");

fetchFiles();

};


return(

<div className="files-page">

<Navbar/>

<div className="files-container">

<h2 className="page-title">Files</h2>


<div className="action-bar">

<button className="btn select" onClick={selectAll}>
Select All
</button>

<button className="btn select" onClick={unselectAll}>
Unselect
</button>

<button className="btn download" onClick={downloadSelected}>
Download
</button>

<button className="btn delete" onClick={moveToTrash}>
Move To Trash
</button>


{/* FILTERS */}

<div className="filters">

<select value={year} onChange={e=>setYear(e.target.value)}>
<option value="">Year</option>

{years.map(y=>(
<option key={y}>{y}</option>
))}

</select>


<select value={month} onChange={e=>setMonth(e.target.value)}>

<option value="">Month</option>

{months.map(m=>(
<option key={m}>{m}</option>
))}

</select>


<button className="btn filter" onClick={applyFilter}>
Filter
</button>

<button className="btn reset" onClick={resetFilter}>
Reset
</button>

</div>

</div>


<div className="table-container">

<table>

<thead>

<tr>
<th></th>
<th>File Name</th>
<th>Date</th>
<th>Year</th>
<th>Month</th>
</tr>

</thead>

<tbody>

{files.map(file=>(

<tr key={file.id}>

<td>
<input
type="checkbox"
checked={selected.includes(file.id)}
onChange={()=>toggleFile(file.id)}
/>
</td>

<td>{file.file_name}</td>
<td>{file.trade_date}</td>
<td>{file.year}</td>
<td>{file.month}</td>

</tr>

))}

</tbody>

</table>

</div>

</div>

</div>

);

}

export default Files;