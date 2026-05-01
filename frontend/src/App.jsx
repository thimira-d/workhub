import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'

function App() {
  return (
    <BrowserRouter>
      <nav style={{
        background: '#1e293b',
        padding: '1rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Link to="/" style={{
          color: '#38bdf8',
          fontWeight: '700',
          fontSize: '1.4rem',
          textDecoration: 'none'
        }}>
          WorkHub 🚀
        </Link>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <Link to="/login" style={navLink}>Login</Link>
          <Link to="/register" style={navLink}>Register</Link>
          <Link to="/dashboard" style={navLink}>Dashboard</Link>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  )
}

const navLink = {
  color: '#94a3b8',
  textDecoration: 'none',
  fontSize: '0.95rem'
}

export default App