
import './Reportes.css'

function ReporteTabla({
  titulo,
  descripcion,
  columnas,
  datos,
  cargando,
  error,
  mensajeVacio
}) {
  return (
    <section className="dashboard-panel reporte-panel">
      <div className="panel-heading">
        <div>
          <h3>{titulo}</h3>
          <p>{descripcion}</p>
        </div>
      </div>

      <div className="panel-divider" />

      {cargando ? (
        <p className="matches-message">Cargando información...</p>
      ) : error ? (
        <p className="matches-message matches-error">
          No se pudo cargar la información: {error}
        </p>
      ) : datos.length === 0 ? (
        <p className="matches-message">{mensajeVacio}</p>
      ) : (
        <div className="reporte-table-container">
          <table className="reporte-table">
            <thead>
              <tr>
                {columnas.map((columna) => (
                  <th key={columna.key}>{columna.titulo}</th>
                ))}
              </tr>
            </thead>

            <tbody>
              {datos.map((fila, indice) => (
                <tr key={fila.id ?? fila.ci ?? indice}>
                  {columnas.map((columna) => (
                    <td key={columna.key}>
                      {columna.render
                        ? columna.render(fila)
                        : (fila[columna.key] ?? '-')}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

export default ReporteTabla
