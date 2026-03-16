import { useEffect } from "react";
import { useParams } from "react-router-dom";
import API from "../api/api";

function FyersLogin(){

const { client_id } = useParams();

useEffect(()=>{

const redirectToFyers = async ()=>{

try{

const res = await API.get(`/fyers-login/${client_id}/`);

window.location.href = res.data.auth_url;

}catch{

alert("Unable to connect to Fyers");

}

};

redirectToFyers();

},[]);

return(

<div style={{textAlign:"center",marginTop:"100px"}}>

<h2>Redirecting to Fyers...</h2>

</div>

);

}

export default FyersLogin;