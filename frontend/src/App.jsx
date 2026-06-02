import { useEffect, useState } from "react";
import { fetchConfig, submitRequest } from "./api";

const LOGO_URL =
  "https://latiendahome-cms.s3.eu-west-1.amazonaws.com/Logotipo_68d4113877.svg";

function emptyItem() {
  return { material: "", units: 1 };
}

export default function App() {
  const [config, setConfig] = useState({ stores: [], materials: [] });
  const [loadingConfig, setLoadingConfig] = useState(true);
  const [configError, setConfigError] = useState("");

  const [step, setStep] = useState(1);
  const [store, setStore] = useState("");
  const [requester, setRequester] = useState("");
  const [reason, setReason] = useState("");
  const [items, setItems] = useState([emptyItem()]);

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [done, setDone] = useState(false);

  useEffect(() => {
    fetchConfig()
      .then((data) => setConfig(data))
      .catch(() => setConfigError("No se pudo cargar la configuración."))
      .finally(() => setLoadingConfig(false));
  }, []);

  function updateItem(index, field, value) {
    setItems((prev) =>
      prev.map((it, i) => (i === index ? { ...it, [field]: value } : it))
    );
  }

  function addItem() {
    setItems((prev) => [...prev, emptyItem()]);
  }

  function removeItem(index) {
    setItems((prev) => prev.filter((_, i) => i !== index));
  }

  const itemsValid =
    items.length > 0 &&
    items.every((it) => it.material && Number(it.units) >= 1);
  const canSubmit = store && reason.trim() && itemsValid && !submitting;

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitError("");
    setSubmitting(true);
    try {
      await submitRequest({
        store,
        requester: requester.trim(),
        reason: reason.trim(),
        items: items.map((it) => ({
          material: it.material,
          units: Number(it.units),
        })),
      });
      setDone(true);
    } catch (err) {
      setSubmitError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  function resetForm() {
    setStep(1);
    setStore("");
    setRequester("");
    setReason("");
    setItems([emptyItem()]);
    setSubmitError("");
    setDone(false);
  }

  return (
    <div className="page">
      <header className="header">
        <img src={LOGO_URL} alt="La Tienda Home" className="logo" />
        <h1>Solicitud de material</h1>
        <p className="subtitle">
          Pide al equipo de marketing el material que necesitas en tu tienda.
        </p>
      </header>

      <main className="card">
        {loadingConfig && <p className="muted">Cargando…</p>}
        {configError && <p className="error">{configError}</p>}

        {!loadingConfig && !configError && done && (
          <div className="success">
            <div className="success-icon">✓</div>
            <h2>¡Solicitud enviada!</h2>
            <p>El equipo de marketing ha recibido tu solicitud.</p>
            <button className="btn" onClick={resetForm}>
              Hacer otra solicitud
            </button>
          </div>
        )}

        {!loadingConfig && !configError && !done && (
          <form onSubmit={handleSubmit}>
            {step === 1 && (
              <section>
                <h2 className="step-title">1. ¿De qué tienda eres?</h2>
                <label className="field">
                  <span>Tienda</span>
                  <select
                    value={store}
                    onChange={(e) => setStore(e.target.value)}
                    required
                  >
                    <option value="" disabled>
                      Selecciona tu tienda
                    </option>
                    {config.stores.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </label>
                <div className="actions">
                  <button
                    type="button"
                    className="btn"
                    disabled={!store}
                    onClick={() => setStep(2)}
                  >
                    Continuar
                  </button>
                </div>
              </section>
            )}

            {step === 2 && (
              <section>
                <h2 className="step-title">2. ¿Qué material necesitas?</h2>
                <p className="muted store-badge">Tienda: {store}</p>

                {items.map((item, index) => (
                  <div className="item-row" key={index}>
                    <label className="field grow">
                      <span>Material</span>
                      <select
                        value={item.material}
                        onChange={(e) =>
                          updateItem(index, "material", e.target.value)
                        }
                        required
                      >
                        <option value="" disabled>
                          Selecciona un material
                        </option>
                        {config.materials.map((m) => (
                          <option key={m.id} value={m.id}>
                            {m.name}
                          </option>
                        ))}
                      </select>
                    </label>
                    <label className="field units">
                      <span>Unidades</span>
                      <input
                        type="number"
                        min="1"
                        value={item.units}
                        onChange={(e) =>
                          updateItem(index, "units", e.target.value)
                        }
                        required
                      />
                    </label>
                    {items.length > 1 && (
                      <button
                        type="button"
                        className="btn-icon"
                        aria-label="Eliminar material"
                        onClick={() => removeItem(index)}
                      >
                        ✕
                      </button>
                    )}
                  </div>
                ))}

                <button type="button" className="btn-link" onClick={addItem}>
                  + Añadir otro material
                </button>

                <label className="field">
                  <span>Motivo (¿por qué lo necesitas?)</span>
                  <textarea
                    rows="3"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    placeholder="Explica brevemente para qué necesitas el material…"
                    required
                  />
                </label>

                <label className="field">
                  <span>Tu nombre (opcional)</span>
                  <input
                    type="text"
                    value={requester}
                    onChange={(e) => setRequester(e.target.value)}
                    placeholder="Nombre del comercial"
                  />
                </label>

                {submitError && <p className="error">{submitError}</p>}

                <div className="actions">
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setStep(1)}
                  >
                    Atrás
                  </button>
                  <button type="submit" className="btn" disabled={!canSubmit}>
                    {submitting ? "Enviando…" : "Enviar solicitud"}
                  </button>
                </div>
              </section>
            )}
          </form>
        )}
      </main>

      <footer className="footer">La Tienda Home · Marketing</footer>
    </div>
  );
}
