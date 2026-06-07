type Driver = { driverid: string; fullname: string }

type Props = {
  drivers: Driver[]
  selected: string[]
  onToggle: (driverid: string) => void
  onSelectAll: () => void
  onClear: () => void
  year: number | null
  onYearChange: (year: number | null) => void
  years: number[]
  onPredict: () => void
  loading: boolean
  topK: number
  onTopKChange: (n: number) => void
}

export default function ControlPanel({
  drivers,
  selected,
  onToggle,
  onSelectAll,
  onClear,
  year,
  onYearChange,
  years,
  onPredict,
  loading,
  topK,
  onTopKChange,
}: Props) {
  return (
    <div className="card p-6 sticky top-6 animate-fade-in">
      <h3 className="text-lg font-display font-bold text-f1-dark flex items-center gap-2">
        <span className="w-2 h-6 bg-f1-red rounded-sm inline-block" />
        Painel de Controle
      </h3>
      <p className="text-sm text-gray-500 mt-1">
        Selecione pilotos e o ano-alvo da predição.
      </p>

      <div className="mt-5">
        <label className="block text-xs uppercase tracking-widest font-semibold text-gray-600 mb-1">
          Temporada alvo
        </label>
        <div className="flex flex-wrap gap-2">
          {years.map((y) => (
            <button
              key={y}
              onClick={() => onYearChange(y === year ? null : y)}
              className={`px-3 py-1.5 rounded-lg text-sm font-semibold border transition-all ${
                y === year
                  ? 'bg-f1-red text-white border-f1-red shadow-md shadow-red-500/20'
                  : 'bg-white text-f1-dark border-gray-200 hover:border-f1-red hover:text-f1-red'
              }`}
            >
              {y}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-5">
        <label className="block text-xs uppercase tracking-widest font-semibold text-gray-600 mb-1">
          Top K pilotos
        </label>
        <div className="flex gap-2">
          {[5, 10, 15, 20].map((k) => (
            <button
              key={k}
              onClick={() => onTopKChange(k)}
              className={`flex-1 px-2 py-1.5 rounded-lg text-sm font-semibold border transition-all ${
                topK === k
                  ? 'bg-f1-dark text-white border-f1-dark'
                  : 'bg-white text-f1-dark border-gray-200 hover:border-f1-dark'
              }`}
            >
              {k}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-5">
        <div className="flex items-center justify-between mb-1">
          <label className="block text-xs uppercase tracking-widest font-semibold text-gray-600">
            Pilotos ({selected.length}/{drivers.length})
          </label>
          <div className="flex gap-2">
            <button
              onClick={onSelectAll}
              className="text-[11px] uppercase tracking-wider text-f1-red font-bold hover:underline"
            >
              Todos
            </button>
            <span className="text-gray-300">|</span>
            <button
              onClick={onClear}
              className="text-[11px] uppercase tracking-wider text-gray-500 font-bold hover:underline"
            >
              Limpar
            </button>
          </div>
        </div>

        <input
          type="text"
          placeholder="Buscar piloto..."
          onChange={(e) => {
            const target = e.target
            const driverEls = document.querySelectorAll<HTMLElement>('[data-driver-name]')
            const q = target.value.toLowerCase()
            driverEls.forEach((el) => {
              const name = (el.dataset.driverName || '').toLowerCase()
              el.style.display = name.includes(q) ? '' : 'none'
            })
          }}
          className="w-full px-3 py-2 rounded-lg border border-gray-200 focus:border-f1-red focus:ring-2 focus:ring-f1-red/20 outline-none text-sm mb-2 transition-all"
        />

        <div className="max-h-72 overflow-y-auto pr-1 space-y-1">
          {drivers.length === 0 && (
            <div className="text-sm text-gray-400 text-center py-6">
              Nenhum piloto disponível para o filtro.
            </div>
          )}
          {drivers.map((d) => {
            const isSel = selected.includes(d.driverid)
            return (
              <button
                key={d.driverid}
                onClick={() => onToggle(d.driverid)}
                data-driver-name={`${d.fullname} ${d.driverid}`}
                className={`w-full text-left px-3 py-2 rounded-lg flex items-center gap-3 transition-all border ${
                  isSel
                    ? 'bg-f1-red/10 border-f1-red text-f1-dark font-semibold'
                    : 'bg-white border-gray-100 hover:border-gray-300 text-f1-dark'
                }`}
              >
                <div
                  className={`w-4 h-4 rounded border-2 flex-shrink-0 flex items-center justify-center transition-all ${
                    isSel ? 'bg-f1-red border-f1-red' : 'border-gray-300'
                  }`}
                >
                  {isSel && (
                    <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="truncate text-sm">{d.fullname}</div>
                  <div className="text-[10px] uppercase tracking-wider text-gray-400 font-mono truncate">
                    {d.driverid}
                  </div>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      <button
        onClick={onPredict}
        disabled={loading}
        className="btn-primary w-full mt-6"
      >
        {loading ? (
          <>
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" opacity="0.25" />
              <path
                d="M4 12a8 8 0 018-8"
                stroke="currentColor"
                strokeWidth="3"
                strokeLinecap="round"
              />
            </svg>
            Calculando...
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Prever Campeão
          </>
        )}
      </button>
    </div>
  )
}
