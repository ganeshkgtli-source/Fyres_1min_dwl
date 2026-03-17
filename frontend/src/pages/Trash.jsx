import { useEffect, useState } from "react";
import API from "../api/api";
import Navbar from "../components/Navbar";
import "../styles/files.css";

function Trash({ fileType = "bhavcopy" }) {
  const [files, setFiles] = useState([]);
  const [years, setYears] = useState([]);
  const [months, setMonths] = useState([]);
  const [selected, setSelected] = useState([]);
  const [year, setYear] = useState("");
  const [month, setMonth] = useState("");

  useEffect(() => {
    fetchTrash();
  }, []);

  const fetchTrash = async () => {
    try {
      const res = await API.get(`/trash/?file_type=${fileType}`);
      setFiles(res.data.files || []);
      setYears(res.data.years || []);
      setMonths(res.data.months || []);
    } catch (err) {
      console.error(err);
    }
  };

  const applyFilter = async () => {
    try {
      const res = await API.get(
        `/trash/?file_type=${fileType}&year=${year}&month=${month}`
      );
      setFiles(res.data.files || []);
      setYears(res.data.years || []);
      setMonths(res.data.months || []);
    } catch (err) {
      console.error(err);
    }
  };

  const resetFilter = () => {
    setYear("");
    setMonth("");
    fetchTrash();
  };

  const toggle = (id) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const selectAll = () => setSelected(files.map((f) => f.id));
  const unselectAll = () => setSelected([]);

  const restoreFiles = async () => {
    try {
      await API.post("/restore/", { ids: selected, file_type: fileType });
      setFiles((prev) => prev.filter((f) => !selected.includes(f.id)));
      setSelected([]);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async () => {
    try {
      await API.post("/delete-permanent/", { ids: selected, file_type: fileType });
      setFiles((prev) => prev.filter((f) => !selected.includes(f.id)));
      setSelected([]);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="files-page">
      <Navbar />
      <div className="files-container">
        <div className="action-bar">
          <button className="btn select" onClick={selectAll}>Select All</button>
          <button className="btn select" onClick={unselectAll}>Unselect</button>
          <button className="btn filter" onClick={restoreFiles}>Restore</button>
          <button className="btn delete" onClick={handleDelete}>Delete Permanently</button>

          <div className="filters">
            <select value={year} onChange={(e) => setYear(e.target.value)}>
              <option value="">Year</option>
              {years.map((y) => <option key={y} value={y}>{y}</option>)}
            </select>

            <select value={month} onChange={(e) => setMonth(e.target.value)}>
              <option value="">Month</option>
              {months.map((m) => <option key={m} value={m}>{m}</option>)}
            </select>

            <button className="btn filter" onClick={applyFilter}>Filter</button>
            <button className="btn reset" onClick={resetFilter}>Reset</button>
          </div>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th></th>
                <th>File Name</th>
                <th>Date</th>
                <th>Year</th>
                <th>Month</th>
              </tr>
            </thead>
            <tbody>
              {files.length === 0 ? (
                <tr><td colSpan="5">No files in trash</td></tr>
              ) : (
                files.map((file) => (
                  <tr key={file.id}>
                    <td>
                      <input type="checkbox" checked={selected.includes(file.id)} onChange={() => toggle(file.id)} />
                    </td>
                    <td>{file.file_name}</td>
                    <td>{file.trade_date}</td>
                    <td>{file.year}</td>
                    <td>{file.month}</td>
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

export default Trash;