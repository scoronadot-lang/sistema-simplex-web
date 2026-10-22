/** Cliente común. Guardar devuelve pending hasta solicitar resolver explícitamente. */
export async function api(path, method = 'GET', body, {historyKey = '', signal} = {}) {
  if (typeof path !== 'string' || !/^\/(?!\/)/.test(path)) {
    throw new Error('La ruta debe comenzar con una sola barra, relativa a /api.');
  }
  const response = await fetch('/api' + path, {
    method,
    headers: {'Content-Type': 'application/json', 'X-History-Key': historyKey},
    ...(body !== undefined ? {body: JSON.stringify(body)} : {}),
    ...(signal ? {signal} : {}),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({detail: 'Servidor no disponible.'}));
    const detail = data.detail;
    const error = new Error(Array.isArray(detail)
      ? detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join('; ')
      : typeof detail === 'string' ? detail : 'Error de API.');
    error.status = response.status;
    error.detail = detail; // La captura puede asociar errores 422 con sus campos.
    throw error;
  }
  return response.status === 204 ? null : response.json();
}
