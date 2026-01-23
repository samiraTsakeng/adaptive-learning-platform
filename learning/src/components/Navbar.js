import { Link } from "react-router-dom";
import "../styles/navbar.css";

const Navbar = () => {
  return (
    <nav className="navbar" style={styles.nav}>
      <h2>Adaptive Learning</h2>
      <div>
      
        <Link to="/login" style={styles.link}>Login</Link>
        <Link to="/register" style={styles.link}>Register</Link>
      </div>
    </nav>
  );
};

const styles = {
  nav: {
    display: "flex",
    justifyContent: "space-between",
    padding: "16px 32px",
    background: "#111827",
    color: "white",
  },
  link: {
    marginLeft: "20px",
    color: "white",
  },
};

export default Navbar;
