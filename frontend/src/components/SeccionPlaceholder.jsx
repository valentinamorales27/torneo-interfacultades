function SeccionPlaceholder({ titulo, descripcion }) {
  return (
    <>
      <div className="dashboard-title-row">
        <div>
          <h2>{titulo}</h2>
          <p>{descripcion}</p>
        </div>
      </div>

      <section className="dashboard-panel section-placeholder">
        <div className="section-placeholder-content">
          <h3>{titulo}</h3>

          <p>
            Esta sección estará disponible próximamente.
          </p>
        </div>
      </section>
    </>
  )
}

export default SeccionPlaceholder