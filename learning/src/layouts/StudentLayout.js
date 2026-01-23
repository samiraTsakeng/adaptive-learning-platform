import { Outlet } from "react-router-dom";
import StudentSidebar from "../components/StudentSidebar";

const StudentLayout = () => {
  return (
    <div className="dashboard-layout">
      <StudentSidebar />
      <div className="dashboard-content">
        <Outlet />
      </div>
    </div>
  );
};

export default StudentLayout;
