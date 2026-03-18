import { useState } from "react"
import Navbar from "../components/Navbar"
import "../styles/files.css"

function Matrix(){

  const [loaded, setLoaded] = useState(false)
  const [generating, setGenerating] = useState(false)

  // 🔥 Generate Matrix API
  const generateMatrix = async () => {
    try {
      setGenerating(true)

      await fetch("http://127.0.0.1:8000/api/generate-matrix/")

      alert("Matrix generated successfully")

      // reload iframe
      setLoaded(false)

    } catch (err) {
      alert("Error generating matrix")
    } finally {
      setGenerating(false)
    }
  }

  return(

    <div>

      <Navbar/>

      <div className="topbar">

        <h2>Security Presence Matrix</h2>

        {/* 🔥 GENERATE BUTTON */}
        <button onClick={generateMatrix} disabled={generating}>
          {generating ? "Generating..." : "Generate Matrix"}
        </button>

        {/* 🔥 DOWNLOAD BUTTON */}
        <button onClick={() => window.location = "http://127.0.0.1:8000/api/download-matrix/"}>
          Download CSV
        </button>

      </div>

      {!loaded &&
        <div id="loader">
          <div className="spinner"></div>
          <br/>
          Loading Matrix...
        </div>
      }

      <iframe
        src="http://127.0.0.1:8000/api/view-matrix/"
        style={{width:"100%", height:"88vh", border:"none"}}
        onLoad={() => setLoaded(true)}
      />

    </div>

  )

}

export default Matrix