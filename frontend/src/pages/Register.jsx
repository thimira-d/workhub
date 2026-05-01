import { useState } from 'react'
import axios from 'axios'

const API = 'https://workhub-api-production.up.railway.app'

function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'client' })
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    setLoading(true)
    try {
      const res = await axios.post(`${API}/auth/register`, form)
      setMessage('✅ ' + res.data.message)
      setTimeout(() => window.location.href = '/login', 1500)
    } catch (err) {
      setMessage('❌ ' + (err.response?.data?.detail || 'Registration failed'))
    }
    setLoading(false)
  }

  return (
    <div style={pageStyle}>
      <div style={cardStyle}>
        <h2 style={{ marginBottom: '1.5rem' }}>Join WorkHub</h2>
        <input
          style={inputStyle}
          placeholder="Full Name"
          value={form.name}
          onChange={e => setForm({...form, name: e.target.value})}
        />
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
        <select
          style={inputStyle}
          value={form.role}
          onChange={e => setForm({...form, role: e.target.value})}
        >
          <option value="client">I want to hire (Client)</option>
          <option value="freelancer">I want to work (Freelancer)</option>
        </select>
        <button style={btnStyle} onClick={handleSubmit} disabled={loading}>
          {loading ? 'Registering...' : 'Create Account'}
        </button>
        {message && (
          <p style={{ marginTop: '1rem', color: message.includes('✅') ? 'green' : 'red' }}>
            {message}
          </p>
        )}
        <p style={{ marginTop: '1rem', color: '#64748b' }}>
          Already have an account? <a href="/login">Login</a>
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

export default Register