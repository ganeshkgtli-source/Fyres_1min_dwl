import { useState } from "react";
import API from "../api/api";

function Dashboard() {

const [date,setDate] = useState("");
const [year,setYear] = useState("");

const downloadDate = async () => {

await API.post("/api/download/",{date});

alert("Download started");

};

const downloadYear = () => {

window.location.href = `/logs/${year}`;

};

return (

<div>

<h2>Bhavcopy Downloader</h2>

<input
type="date"
value={date}
onChange={(e)=>setDate(e.target.value)}
/>

<button onClick={downloadDate}>
Download Date
</button>

<hr/>

<input
placeholder="Year"
value={year}
onChange={(e)=>setYear(e.target.value)}
/>

<button onClick={downloadYear}>
Download Year
</button>

</div>

);

}

export default Dashboard;