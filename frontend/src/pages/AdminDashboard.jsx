import { useEffect, useState } from "react";
import API from "../api/api";
import { useNavigate } from "react-router-dom";
import "../styles/dashboard.css";

function AdminDashboard() {

  const navigate = useNavigate();
  const clientId = localStorage.getItem("client_id");

  const [users, setUsers] = useState([]);

  // ================= PROTECT =================
  useEffect(() => {

    const clientId = localStorage.getItem("client_id");
    const isAdmin = localStorage.getItem("is_admin") === "true";

    if (!clientId) {
      navigate("/login");
      return;
    }

    if (!isAdmin) {
      navigate("/");
      return;
    }

    fetchUsers();

  }, []);

  // ================= FETCH =================
  const fetchUsers = async () => {
    try {
      const res = await API.get(`/admin/?client_id=${clientId}`);
      setUsers(res.data);
    } catch {
      alert("Failed to load users");
    }
  };

  // ================= DELETE =================
  const deleteUser = async (id) => {
    if (!window.confirm("Delete user?")) return;

    try {
      await API.delete(`/admin/delete-user/${id}/?client_id=${clientId}`);
      fetchUsers();
    } catch {
      alert("Delete failed");
    }
  };

  // ================= LOGOUT =================
  const logout = () => {
    localStorage.clear();
    navigate("/login");
  };

  return (
    <div className="admin-layout">

      {/* SIDEBAR */}
      <div className="admin-sidebar">

        <h2 className="logo">TLI</h2>

        <ul>
          <li className="active">Users</li>
        </ul>

        {/* LOGOUT BOTTOM */}
        <div className="sidebar-bottom">
          <button onClick={logout} className="logout-btn">
            Logout
          </button>
        </div>

      </div>

      {/* MAIN CONTENT */}
      <div className="admin-main">

        <h2>Admin Dashboard</h2>

        <div className="dashboard-box">

          <table className="admin-table">

            <thead>
              <tr>
                <th>NAME</th>
                <th>EMAIL</th>
                <th>CLIENT ID</th>
                <th>ACTION</th>
              </tr>
            </thead>

            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.username}</td>
                  <td>{u.email}</td>
                  <td>{u.client_id}</td>
                  <td>
                    <button
                      className="delete-btn"
                      onClick={() => deleteUser(u.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>

          </table>

        </div>

      </div>

    </div>
  );
}

export default AdminDashboard;