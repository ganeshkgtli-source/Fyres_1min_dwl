import { useEffect, useState } from "react"
import Navbar from "../components/Navbar"

function Logs(){

const [logs,setLogs] = useState([])

useEffect(()=>{

const source = new EventSource("http://127.0.0.1:8000/api/stream-logs")

source.onmessage = (event)=>{

setLogs(prev=>[...prev,event.data])

}

return ()=>source.close()

},[])


return(

<div>

<Navbar/>

<h2 className="title">Live Download Console</h2>

<div className="log-container">

<div id="logBox">

{logs.map((log,i)=>{

let color=""

if(log.includes("Downloading")) color="download"
else if(log.includes("Downloaded") || log.includes("Saved")) color="success"
else if(log.includes("Error")) color="error"

return <div key={i} className={color}>{log}</div>

})}

</div>

</div>

</div>

)

}

export default Logs