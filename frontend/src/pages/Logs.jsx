import { useEffect, useRef, useState } from "react"
import { useLocation } from "react-router-dom"
import Navbar from "../components/Navbar"
import "../styles/files.css"

function Logs(){

const [logs,setLogs] = useState([])
const logEndRef = useRef(null)
const location = useLocation()

useEffect(()=>{

const params = new URLSearchParams(location.search)

const year = params.get("year")
const isAll = params.get("all")

let url = ""

// ✅ FIXED URL LOGIC
if(year){
  url = `http://127.0.0.1:8000/api/stream-logs/${year}/`
}
else if(isAll){
  url = `http://127.0.0.1:8000/api/stream-all-logs/`
}
else{
  console.error("No params provided")
  return
}

console.log("Connecting to:", url)

const source = new EventSource(url)

source.onmessage = (event)=>{

const message = event.data || "Empty log"

// ⏱ timestamp
const time = new Date().toLocaleTimeString("en-GB", {
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit"
})

setLogs(prev => [
  ...prev,
  { text: message, time }
])

}

source.onerror = (err)=>{
  console.error("SSE Error:", err)
  source.close()
}

return ()=>source.close()

},[location.search])


// 🔽 AUTO SCROLL
useEffect(()=>{
  logEndRef.current?.scrollIntoView({ behavior: "smooth" })
},[logs])


// 🎯 STATUS COLOR (SAFE)
const getClass = (log) => {

if (!log || !log.text) return "log-normal"

const text = log.text.toLowerCase()

if (text.includes("downloading")) return "log-downloading"

if (
  text.includes("downloaded") ||
  text.includes("saved") ||
  text.includes("already exists")
) return "log-success"

if (
  text.includes("not available") ||
  text.includes("not found") ||
  text.includes("error") ||
  text.includes("failed")
) return "log-failed"

return "log-normal"
}


return(

<div className="files-page">

<Navbar/>

<div className="files-container">

<h2 className="page-title">Live Download Console</h2>

<div className="console-box">

{logs.length === 0 && (
<div className="log-empty">Waiting for logs...</div>
)}

{logs.map((log,i)=>(
<div key={i} className={`log-line ${getClass(log)}`}>

<span className="log-time">
[{log.time}]
</span>

<span className="log-text">
{log.text}
</span>

</div>
))}

<div ref={logEndRef}></div>

</div>

</div>

</div>

)

}

export default Logs