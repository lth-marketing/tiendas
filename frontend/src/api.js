// Cliente ligero de la API. Frontend y backend comparten origen, así que
// usamos rutas relativas.

export async function fetchConfig() {
  const res = await fetch("/api/config/");
  if (!res.ok) {
    throw new Error("No se pudo cargar la configuración.");
  }
  return res.json();
}

export async function submitRequest(payload) {
  const res = await fetch("/api/material-requests/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }
  // 409: algún material ya se pidió recientemente para esta tienda.
  if (res.status === 409 && data && data.duplicates) {
    return { status: "duplicate", duplicates: data.duplicates };
  }
  if (!res.ok) {
    const message =
      (data && (data.detail || JSON.stringify(data))) ||
      "Se produjo un error al enviar la solicitud.";
    throw new Error(message);
  }
  return { status: "ok", data };
}
