import { useEffect, useMemo, useState } from 'react'
import Hero from './components/Hero'
import ControlPanel from './components/ControlPanel'
import PredictionRow from './components/PredictionRow'
import PredictionBarChart from './components/PredictionBarChart'
import HistoryChart from './components/HistoryChart'
import StatCard from './components/StatCard'
import {
  getDrivers,
  getHealth,
  getTopPredictions,
  getYears,
  getDriverHistory,
  type Prediction,
  type Driver,
  type DriverHistoryRow,
} from './lib/api'

type HealthState = { ok: boolean; model_loaded: boolean; message?: string }

export default function App() {
  const [health, setHealth] = useState<HealthState>({ ok: false, model_loaded: false })
  const [years, setYears] = useState<number[]>([])
  const [year, setYear] = useState<number | null>(null)
  const [drivers, setDrivers] = useState<Driver[]>([])
  const [selected, setSelected] = useState<string[]>([])
  const [topK, setTopK] = useState(10)
  const [predictions, setPredictions] = useState<Prediction[]>([])
  const [histories, setHistories] = useState<
    { driverid: string; fullname: string; rows: DriverHistoryRow[] }[]
  >([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [tab, setTab] = useState<'rank' | 'chart' | 'history'>('rank')

  useEffect(() => {
    getHealth()
      .then((d) => setHealth({ ok: d.status === 'ok', model_loaded: d.model_loaded }))
      .catch(() => setHealth({ ok: false, model_loaded: false }))

    getYears()
      .then((ys) => {
        setYears(ys)
        if (ys.length > 0) setYear(ys[0])
      })
      .catch((e) => setError(`Falha ao carregar anos: ${e.message}`))
  }, [])

  useEffect(() => {
    getDrivers(year ?? undefined)
      .then(setDrivers)
      .catch((e) => setError(`Falha ao carregar pilotos: ${e.message}`))
  }, [year])

  const topProb = useMemo(() => {
    if (predictions.length === 0) return 0
    return Math.max(...predictions.map((p) => p.prob_win))
  }, [predictions])

  const handleToggle = (id: string) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    )
  }

  const handlePredict = async () => {
    setLoading(true)
    setError(null)
    try {
      const top = await getTopPredictions(year ?? undefined, topK)
      setPredictions(top)

      const idsToFetch = selected.length > 0 ? selected : top.map((t) => t.driverid)
      const histResponses = await Promise.all(
        idsToFetch.map((id) => getDriverHistory(id).catch(() => null)),
      )
      const valid = histResponses
        .filter((r): r is NonNullable<typeof r> => r !== null && r.count > 0)
        .map((r) => ({
          driverid: r.driverid,
          fullname: r.fullname,
          rows: r.rows,
        }))
      setHistories(valid)
    } catch (e) {
      const err = e as Error
      setError(err.message || 'Erro ao rodar predição')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Hero>
        <h1 className="font-display font-black text-5xl md:text-6xl lg:text-7xl tracking-tight max-w-4xl animate-slide-up">
          Preveja o <span className="text-f1-red">Campeão</span> da temporada.
          <br />
          <span className="text-white/70 text-3xl md:text-4xl lg:text-5xl">
            Com Machine Learning e dados históricos.
          </span>
        </h1>
        <p className="mt-6 text-white/70 text-lg max-w-2xl animate-slide-up">
          Modelo <b>Random Forest</b> treinado sobre uma base de 12.936 snapshots
          de pilotos, comparando 128+ features de performance (poles, vitórias, grid,
          voltas, etc.) para classificar a probabilidade de cada piloto ser campeão
          da temporada.
        </p>

        <div className="mt-10 grid grid-cols-2 md:grid-cols-4 gap-3 max-w-3xl animate-slide-up">
          <div className="rounded-xl bg-white/5 border border-white/10 backdrop-blur px-4 py-3">
            <div className="text-[10px] uppercase tracking-widest text-white/50 font-semibold">API</div>
            <div className={`text-sm font-bold mt-1 flex items-center gap-2 ${health.ok ? 'text-green-400' : 'text-red-400'}`}>
              <span className={`w-2 h-2 rounded-full ${health.ok ? 'bg-green-400' : 'bg-red-400'} ${health.ok ? 'animate-pulse' : ''}`} />
              {health.ok ? 'Online' : 'Offline'}
            </div>
          </div>
          <div className="rounded-xl bg-white/5 border border-white/10 backdrop-blur px-4 py-3">
            <div className="text-[10px] uppercase tracking-widest text-white/50 font-semibold">Modelo</div>
            <div className={`text-sm font-bold mt-1 flex items-center gap-2 ${health.model_loaded ? 'text-green-400' : 'text-yellow-400'}`}>
              <span className={`w-2 h-2 rounded-full ${health.model_loaded ? 'bg-green-400' : 'bg-yellow-400'}`} />
              {health.model_loaded ? 'Carregado' : 'Indisponível'}
            </div>
          </div>
          <div className="rounded-xl bg-white/5 border border-white/10 backdrop-blur px-4 py-3">
            <div className="text-[10px] uppercase tracking-widest text-white/50 font-semibold">Anos</div>
            <div className="text-sm font-bold mt-1 text-white">{years.length}</div>
          </div>
          <div className="rounded-xl bg-white/5 border border-white/10 backdrop-blur px-4 py-3">
            <div className="text-[10px] uppercase tracking-widest text-white/50 font-semibold">Pilotos</div>
            <div className="text-sm font-bold mt-1 text-white">{drivers.length}</div>
          </div>
        </div>
      </Hero>

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-10">
        {error && (
          <div className="mb-6 p-4 rounded-xl border border-red-200 bg-red-50 text-red-700 text-sm">
            <b>Erro:</b> {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-6">
          <ControlPanel
            drivers={drivers}
            selected={selected}
            onToggle={handleToggle}
            onSelectAll={() => setSelected(drivers.map((d) => d.driverid))}
            onClear={() => setSelected([])}
            year={year}
            onYearChange={setYear}
            years={years}
            onPredict={handlePredict}
            loading={loading}
            topK={topK}
            onTopKChange={setTopK}
          />

          <section>
            {predictions.length === 0 && !loading && (
              <div className="card p-12 text-center">
                <div className="w-20 h-20 mx-auto rounded-full bg-f1-red/10 flex items-center justify-center mb-4">
                  <svg className="w-10 h-10 text-f1-red" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="font-display font-bold text-2xl text-f1-dark">Pronto para a Previsão</h3>
                <p className="text-gray-500 mt-2 max-w-md mx-auto">
                  Escolha pilotos e o ano no painel ao lado, e clique em
                  <b className="text-f1-red"> Prever Campeão</b> para ver as probabilidades calculadas pelo modelo.
                </p>
              </div>
            )}

            {loading && (
              <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="card p-4 h-20 skeleton" />
                ))}
              </div>
            )}

            {predictions.length > 0 && !loading && (
              <>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
                  <StatCard
                    label="Top Piloto"
                    value={predictions[0]?.fullname ?? '—'}
                    hint={`${(topProb * 100).toFixed(1)}% de chance`}
                    tone="red"
                  />
                  <StatCard
                    label="Predições"
                    value={predictions.length}
                    hint={`Ano ${year ?? '—'}`}
                    tone="dark"
                  />
                  <StatCard
                    label="Histórico carregado"
                    value={histories.length}
                    hint="pilotos"
                    tone="light"
                  />
                  <StatCard
                    label="Modelo"
                    value="RF"
                    hint="Champion Predictor"
                    tone="light"
                  />
                </div>

                <div className="flex gap-2 mb-4 border-b border-gray-200">
                  {[
                    { id: 'rank', label: 'Ranking' },
                    { id: 'chart', label: 'Gráfico' },
                    { id: 'history', label: 'Histórico' },
                  ].map((t) => (
                    <button
                      key={t.id}
                      onClick={() => setTab(t.id as 'rank' | 'chart' | 'history')}
                      className={`px-4 py-2 -mb-px text-sm font-semibold border-b-2 transition-colors ${
                        tab === t.id
                          ? 'border-f1-red text-f1-red'
                          : 'border-transparent text-gray-500 hover:text-f1-dark'
                      }`}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>

                {tab === 'rank' && (
                  <div className="space-y-3">
                    {predictions.map((p, i) => (
                      <PredictionRow
                        key={p.driverid + p.dt_ref}
                        rank={i + 1}
                        driverid={p.driverid}
                        fullname={p.fullname}
                        prob_win={p.prob_win}
                        dt_ref={p.dt_ref}
                      />
                    ))}
                  </div>
                )}

                {tab === 'chart' && <PredictionBarChart predictions={predictions} />}

                {tab === 'history' && (
                  <HistoryChart
                    histories={histories}
                    predictions={predictions}
                    year={year}
                  />
                )}
              </>
            )}
          </section>
        </div>
      </main>

      <footer className="border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-6 py-6 flex flex-col md:flex-row items-center justify-between gap-2 text-sm text-gray-500">
          <div className="font-display font-bold text-f1-dark">
            F1 <span className="text-f1-red">Smart</span> Predict
          </div>
          <div>
            Powered by <b className="text-f1-dark">FastAPI</b> · <b className="text-f1-dark">MLflow</b> ·{' '}
            <b className="text-f1-dark">Postgres</b> · <b className="text-f1-dark">React</b>
          </div>
        </div>
      </footer>
    </div>
  )
}
