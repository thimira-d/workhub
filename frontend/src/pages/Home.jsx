function Home() {
  return (
    <div style={{ padding: '4rem 2rem', textAlign: 'center' }}>
      <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
        Find skilled freelancers 🚀
      </h1>
      <p style={{ color: '#64748b', fontSize: '1.1rem', marginBottom: '2rem' }}>
        WorkHub connects clients with talented freelancers around the world.
      </p>
      <a href="/register" style={{
        background: '#38bdf8',
        color: '#fff',
        padding: '0.8rem 2rem',
        borderRadius: '8px',
        textDecoration: 'none',
        fontWeight: '600'
      }}>
        Get Started
      </a>
    </div>
  )
}

export default Home