import { useEffect,useState } from "react"
import API from "../api/api"
import Navbar from "../components/Navbar"

function Trash(){

const [files,setFiles] = useState([])
const [selected,setSelected] = useState([])

useEffect(()=>{

API.get("/trash-files/")
.then(res=>setFiles(res.data))

},[])

const toggle=(id)=>{

if(selected.includes(id))
setSelected(selected.filter(x=>x!==id))
else
setSelected([...selected,id])

}

const selectAll=()=>{

setSelected(files.map(f=>f.id))

}

const unselectAll=()=>{

setSelected([])

}

const deleteFiles=async()=>{

await API.post("/delete-selected/",{ids:selected})

alert("Deleted")

window.location.reload()

}

return(

<div>

<Navbar/>

<button onClick={selectAll}>Select All</button>

<button onClick={unselectAll}>Unselect</button>

<button onClick={deleteFiles}>Delete</button>

<table>

<thead>

<tr>
<th></th>
<th>File</th>
<th>Date</th>
</tr>

</thead>

<tbody>

{files.map(file=>(

<tr key={file.id}>

<td>

<input
type="checkbox"
checked={selected.includes(file.id)}
onChange={()=>toggle(file.id)}
/>

</td>

<td>{file.name}</td>
<td>{file.date}</td>

</tr>

))}

</tbody>

</table>

</div>

)

}

export default Trash