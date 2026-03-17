import { useEffect, useState } from "react";
import API from "../api/api";
import Navbar from "../components/Navbar";
import "../styles/files.css";

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


// FETCH FILES
const fetchFiles = async()=>{
try{
const res = await API.get("/files/");

setFiles(res.data.files || []);
setYears(res.data.years || []);
setMonths(res.data.months || []);

}catch(err){
console.error(err);
}
};


// APPLY FILTER
const applyFilter = async()=>{
try{
const res = await API.get(`/files/?year=${year}&month=${month}`);

setFiles(res.data.files || []);
setYears(res.data.years || []);
setMonths(res.data.months || []);

}catch(err){
console.error(err);
}
};


// RESET FILTER
const resetFilter = ()=>{
setYear("");
setMonth("");
fetchFiles();
};


// TOGGLE FILE
const toggleFile=(id)=>{
if(selected.includes(id)){
setSelected(selected.filter(x=>x!==id));
}else{
setSelected([...selected,id]);
}
};


// SELECT ALL
const selectAll=()=>{
setSelected(files.map(f=>f.id));
};


// UNSELECT
const unselectAll=()=>{
setSelected([]);
};


// DOWNLOAD ZIP
const handleDownload = async () => {
  try {
    const res = await API.post(
      "/download-selected/",
      { ids: selected },
      { responseType: "blob" }
    );

    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");

    link.href = url;
    link.setAttribute("download", "Bhavcopy_Files.zip");

    document.body.appendChild(link);
    link.click();
    link.remove();

    setSelected([]);

  } catch (err) {
    console.error(err);
  }
};


// MOVE TO TRASH
const moveToTrash = async()=>{
try{
await API.post("/move-to-trash/",{ids:selected});

// instant UI update
setFiles(prev => prev.filter(f => !selected.includes(f.id)));
setSelected([]);

}catch(err){
console.error(err);
}
};


return(

<div className="files-page">

<Navbar/>

<div className="files-container">



{/* ACTION BAR */}
<div className="action-bar">

<button className="btn select" onClick={selectAll}>
Select All
</button>

<button className="btn select" onClick={unselectAll}>
Unselect
</button>

<button className="btn download" onClick={handleDownload}>
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
<option key={y} value={y}>{y}</option>
))}

</select>


<select value={month} onChange={e=>setMonth(e.target.value)}>
<option value="">Month</option>

{months.map(m=>(
<option key={m} value={m}>{m}</option>
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


{/* TABLE */}
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

{files.length === 0 ? (
<tr>
<td colSpan="5">No files found</td>
</tr>
) : (
files.map(file=>(
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
))
)}

</tbody>

</table>

</div>

</div>

</div>

);

}

export default Files;