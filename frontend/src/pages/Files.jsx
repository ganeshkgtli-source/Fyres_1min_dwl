import { useEffect, useState } from "react"
import API from "../api/api"
import Navbar from "../components/Navbar"

function Files(){

const [files,setFiles] = useState([])
const [selected,setSelected] = useState([])

const [year,setYear] = useState("")
const [month,setMonth] = useState("")


// LOAD FILES

useEffect(()=>{

fetchFiles()

},[])


const fetchFiles = async()=>{

const res = await API.get("/files/")

setFiles(res.data)

}


// TOGGLE FILE

const toggleFile=(id)=>{

if(selected.includes(id))
setSelected(selected.filter(x=>x!==id))

else
setSelected([...selected,id])

}


// SELECT ALL

const selectAll=()=>{

setSelected(files.map(f=>f.id))

}


// UNSELECT ALL

const unselectAll=()=>{

setSelected([])

}


// DOWNLOAD SELECTED

const downloadSelected = async()=>{

if(selected.length===0){
alert("Select files first")
return
}

await API.post("/download-selected/",{ids:selected})

alert("Download started")

}


// MOVE TO TRASH

const moveToTrash = async()=>{

if(selected.length===0){
alert("Select files first")
return
}

await API.post("/move-to-trash/",{ids:selected})

alert("Moved to trash")

fetchFiles()

}


// FILTER

const filteredFiles = files.filter(f=>{

return (
(!year || f.year==year) &&
(!month || f.month==month)
)

})



return(

<div>

<Navbar/>


{/* TOP ACTION BAR */}

<div style={{margin:"20px"}}>

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

<select
value={year}
onChange={e=>setYear(e.target.value)}
style={{marginLeft:"20px"}}
>

<option value="">All Years</option>

{[2025,2024,2023,2022].map(y=>(

<option key={y}>{y}</option>

))}

</select>


<select
value={month}
onChange={e=>setMonth(e.target.value)}
>

<option value="">All Months</option>

<option value="01">Jan</option>
<option value="02">Feb</option>
<option value="03">Mar</option>
<option value="04">Apr</option>
<option value="05">May</option>
<option value="06">Jun</option>
<option value="07">Jul</option>
<option value="08">Aug</option>
<option value="09">Sep</option>
<option value="10">Oct</option>
<option value="11">Nov</option>
<option value="12">Dec</option>

</select>

</div>



{/* FILE TABLE */}

<div className="table-container">

<table>

<thead>

<tr>

<th></th>
<th>File Name</th>
<th>Trade Date</th>
<th>Year</th>
<th>Month</th>

</tr>

</thead>

<tbody>

{filteredFiles.map(file=>(

<tr key={file.id}>

<td>

<input
type="checkbox"
className="fileCheckbox"
checked={selected.includes(file.id)}
onChange={()=>toggleFile(file.id)}
/>

</td>

<td>{file.name}</td>

<td>{file.date}</td>

<td>{file.year}</td>

<td>{file.month}</td>

</tr>

))}

</tbody>

</table>

</div>

</div>

)

}

export default Files