const API = 'https://matriculas-rib.yakoribiza.workers.dev/capture';

const origLog = console.log;
console.log = function(...args) {
  if (typeof args[0] === 'string' && args[0].includes('SkritPlus') && args[1] && args[1].matricula) {
    ribCapturar(args[1]);
  }
  return origLog.apply(console, args);
};

async function ribCapturar(data) {
  const v = data.retVehiculo  || {};
  const m = data.retMatricula || {};

  const payload = {
    matricula:           data.matricula,
    vin:                 m.Bastidor            || null,
    marca:               m.Marca               || v.Fabricante  || null,
    modelo:              v.Modelo              || null,
    modelo_corto:        m.Modelo              || null,
    carburante:          m.Carburante          || v.Combustible || null,
    fecha_matriculacion: m.FechaMatricula      || null,
    cc:                  v.CC                  || null,
    kw:                  v.Kw                  || null,
    motor:               v.Motor               || null,
    motores:             v.Motores             || null,
    f_desde:             v.FDesde              || null,
    f_hasta:             v.FHasta              || null,
    descripcion:         v.Descripcion         || null,
    id_tecdoc:           m.idTecdoc            || v.Id || null,
    capturado_por:       'docnet',
  };

  origLog('[RIB] Capturando:', payload.matricula, payload.marca, payload.modelo, payload.carburante);

  try {
    const res = await fetch(API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const json = await res.json();
    origLog('[RIB] Guardado OK:', json);
  } catch (err) {
    console.warn('[RIB] Error al guardar:', err.message);
  }
}

origLog('[RIB] Extensión matriculas activa');
