import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";

import Files from "./pages/Files";
import Trash from "./pages/Trash";
import Logs from "./pages/Logs";
import LogsAll from "./pages/LogsAll";
import LogDashboard from "./pages/LogDashboard";
import Matrix from "./pages/Matrix";

function App(){

return(

<BrowserRouter>

<Routes>

<Route path="/login" element={<Login/>}/>
<Route path="/register" element={<Register/>}/>

<Route path="/" element={<Home/>}/>
<Route path="/files" element={<Files/>}/>
<Route path="/trash" element={<Trash/>}/>

<Route path="/logs" element={<Logs/>}/>
<Route path="/logs-all" element={<LogsAll/>}/>
<Route path="/log-dashboard" element={<LogDashboard/>}/>

<Route path="/matrix" element={<Matrix/>}/>

</Routes>

</BrowserRouter>

)

}

export default App