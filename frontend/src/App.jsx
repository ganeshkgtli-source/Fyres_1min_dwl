import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";

import Files from "./pages/Files";
import Trash from "./pages/Trash";
import Logs from "./pages/Logs";
 
import LogDashboard from "./pages/LogDashboard";
import Matrix from "./pages/Matrix";
import OneMinData from "./pages/OneMinData";
import UserDashboard from "./pages/UserDashboard";
import AdminDashboard from "./pages/AdminDashboard";

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
 <Route path="/admin" element={<AdminDashboard />} />
<Route path="/log-dashboard" element={<LogDashboard/>}/>
<Route path="/user-dashboard" element={<UserDashboard/>}/>
<Route path="/matrix" element={<Matrix/>}/>
<Route path="/1min-data" element={<OneMinData />} /> 
</Routes>

</BrowserRouter>

)

}

export default App