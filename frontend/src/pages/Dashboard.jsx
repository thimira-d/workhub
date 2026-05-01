import { useState, useEffect } from 'react'
import axios from 'axios'

const API = 'https://workhub-api-production.up.railway.app'

function Dashboard() {
  const [services, setServices] = useState([])
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  useEffect(() => {
    axios.get(`${API}/services`).then(res => setServices(res.data.services))
  }, [])

  if (!token) {
    return (
      <div style={pageStyle}>
        <div style={cardStyle}>
          <h2 style={{ marginBottom: '1rem' }}>Please login first</h2>
          <a href="/login" style={{ color: '#38bdf8' }}>Go to Login</a>
        </div>
      </div>
    )
  }

  return (
    <div style={{ padding: '2rem' }}>
      <h2 style={{ marginBottom: '1.5rem' }}>
        Welcome to WorkHub! You are logged in as a <strong>{role}</strong> 👋
      </h2>

      <h3 style={{ marginBottom: '1rem' }}>Available Services</h3>

      {services.length === 0 ? (
        <p style={{ color: '#64748b' }}>No services yet.</p>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: '1rem'
        }}>
          {services.map((s, i) => (
            <div key={i} style={serviceCard}>
              <h4 style={{ marginBottom: '0.5rem' }}>{s.title}</h4>
              <p style={{ color: '#64748b', marginBottom: '0.5rem' }}>{s.description}</p>
              <p style={{ color: '#38bdf8', fontWeight: '600', marginBottom: '0.25rem' }}>
                ${s.price}
              </p>
              <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>By {s.freelancer_name}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

const pageStyle = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  minHeight: '80vh'
}

const cardStyle = {
  background: '#fff',
  padding: '2rem',
  borderRadius: '12px',
  boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
  textAlign: 'center'
}

const serviceCard = {
  background: '#fff',
  padding: '1.25rem',
  borderRadius: '12px',
  boxShadow: '0 2px 10px rgba(0,0,0,0.06)',
  border: '1px solid #e2e8f0'
}

export default Dashboard