import { useEffect, useState } from "react";
import API from "../api/api";
import Navbar from "../components/Navbar";
import "../styles/files.css";

function OneMinFiles() {
  const [files, setFiles] = useState([]);
  const [symbols, setSymbols] = useState([]);
  const [selected, setSelected] = useState([]);
  const [symbol, setSymbol] = useState("");

  useEffect(() => {
    fetchFiles();
  }, []);

  // -------------------------
  // FETCH 1MIN FILES
  // -------------------------
  const fetchFiles = async () => {
    try {
      const res = await API.get("/1min-files/");
      setFiles(res.data.files || []);
      setSymbols(res.data.symbols || []);
    } catch (err) {
      console.error("Error fetching 1min files:", err);
    }
  };

  // -------------------------
  // FILTER BY SYMBOL
  // -------------------------
  const applyFilter = async () => {
    try {
      const res = await API.get(`/1min-files/?symbol=${symbol}`);
      setFiles(res.data.files || []);
    } catch (err) {
      console.error("Error filtering 1min files:", err);
    }
  };

  // -------------------------
  // RESET FILTER
  // -------------------------
  const resetFilter = () => {
    setSymbol("");
    fetchFiles();
  };

  // -------------------------
  // TOGGLE SELECT FILE
  // -------------------------
  const toggleFile = (id) => {
    if (selected.includes(id)) {
      setSelected(selected.filter((x) => x !== id));
    } else {
      setSelected([...selected, id]);
    }
  };

  // -------------------------
  // SELECT ALL / UNSELECT ALL
  // -------------------------
  const selectAll = () => setSelected(files.map((f) => f.id));
  const unselectAll = () => setSelected([]);

  // -------------------------
  // DOWNLOAD SELECTED FILES
  // -------------------------
  const handleDownload = async () => {
    if (selected.length === 0) return;
    try {
      const res = await API.post(
        "/1min-download-selected/",
        { ids: selected },
        { responseType: "blob" }
      );

      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "OneMin_Files.zip");
      document.body.appendChild(link);
      link.click();
      link.remove();

      setSelected([]);
    } catch (err) {
      console.error("Error downloading files:", err);
    }
  };

  // -------------------------
  // MOVE SELECTED FILES TO TRASH
  // -------------------------
  const moveToTrash = async () => {
    if (selected.length === 0) return;
    try {
      await API.post("/move-to-trash/", {
        ids: selected,
        file_type: "1min",
      });

      setFiles((prev) => prev.filter((f) => !selected.includes(f.id)));
      setSelected([]);
    } catch (err) {
      console.error("Error moving files to trash:", err);
    }
  };

  return (
    <div className="files-page">
      <Navbar />

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
          {/* <button className="btn delete" onClick={moveToTrash}>
            Move To Trash
          </button> */}

          {/* FILTER */}
          <div className="filters">
            <select value={symbol} onChange={(e) => setSymbol(e.target.value)}>
              <option value="">Symbol</option>
              {symbols.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
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
                <th>Symbol</th>
                <th>File Name</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {files.length === 0 ? (
                <tr>
                  <td colSpan="4">No files found</td>
                </tr>
              ) : (
                files.map((file) => (
                  <tr key={file.id}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selected.includes(file.id)}
                        onChange={() => toggleFile(file.id)}
                      />
                    </td>
                    <td>{file.symbol}</td>
                    <td>{file.file_name}</td>
                    <td>{new Date(file.created_at).toLocaleString()}</td>
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

export default OneMinFiles;