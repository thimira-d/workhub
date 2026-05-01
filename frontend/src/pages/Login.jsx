import { useState } from 'react'
import axios from 'axios'

const API = 'http://127.0.0.1:8080'

function Login() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    setLoading(true)
    try {
      const res = await axios.post(`${API}/auth/login`, form)
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('role', res.data.role)
      setMessage('✅ Login successful! Redirecting...')
      setTimeout(() => window.location.href = '/dashboard', 1500)
    } catch (err) {
      setMessage('❌ ' + (err.response?.data?.detail || 'Login failed'))
    }
    setLoading(false)
  }

  return (
    <div style={pageStyle}>
      <div style={cardStyle}>
        <h2 style={{ marginBottom: '1.5rem' }}>Login to WorkHub</h2>
        <input
          style={inputStyle}
          placeholder="Email"
          value={form.email}
          onChange={e => setForm({...form, email: e.target.value})}
        />
        <input
          style={inputStyle}
          placeholder="Password"
          type="password"
          value={form.password}
          onChange={e => setForm({...form, password: e.target.value})}
        />
        <button style={btnStyle} onClick={handleSubmit} disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
        {message && (
          <p style={{ marginTop: '1rem', color: message.includes('✅') ? 'green' : 'red' }}>
            {message}
          </p>
        )}
        <p style={{ marginTop: '1rem', color: '#64748b' }}>
          Don't have an account? <a href="/register">Register</a>
        </p>
      </div>
    </div>
  )
}

const pageStyle = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  minHeight: '80vh',
  padding: '2rem'
}

const cardStyle = {
  background: '#fff',
  padding: '2rem',
  borderRadius: '12px',
  boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
  width: '100%',
  maxWidth: '400px'
}

const inputStyle = {
  width: '100%',
  padding: '0.75rem 1rem',
  marginBottom: '1rem',
  border: '1px solid #e2e8f0',
  borderRadius: '8px',
  fontSize: '0.95rem',
  display: 'block'
}

const btnStyle = {
  width: '100%',
  padding: '0.75rem',
  background: '#38bdf8',
  color: '#fff',
  border: 'none',
  borderRadius: '8px',
  fontSize: '1rem',
  fontWeight: '600'
}

export default Login