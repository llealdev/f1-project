import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { DriverHistoryRow, Prediction } from '../lib/api'
import { getDriverColor } from '../lib/utils'

type Props = {
  histories: { driverid: string; fullname: string; rows: DriverHistoryRow[] }[]
  predictions: Prediction[]
  year: number | null
}

type ChartRow = Record<string, string | number | null>

export default function HistoryChart({ histories, predictions, year }: Props) {
  if (histories.length === 0) {
    return (
      <div className="card p-8 text-center text-gray-500">
        Selecione pilotos e clique em <b>Prever</b> para ver o histórico de probabilidades.
      </div>
    )
  }

  const probByKey: Record<string, number> = {}
  for (const p of predictions) {
    probByKey[`${p.driverid}|${p.dt_ref}`] = p.prob_win
  }

  const allDates = new Set<string>()
  histories.forEach((h) => h.rows.forEach((r) => allDates.add(r.dt_ref)))
  const sortedDates = [...allDates].sort()
  const filteredDates = year
    ? sortedDates.filter((d) => d.startsWith(String(year)))
    : sortedDates

  const chartData: ChartRow[] = filteredDates.map((dt) => {
    const row: ChartRow = { dt_ref: dt }
    histories.forEach((h) => {
      const r = h.rows.find((x) => x.dt_ref === dt)
      const key = `${h.driverid}|${dt}`
      const predicted = probByKey[key]
      if (predicted !== undefined) {
        row[h.fullname] = +(predicted * 100).toFixed(2)
      } else {
        row[h.fullname] = null
      }
    })
    return row
  })

  return (
    <div className="card p-6 h-[460px] animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-display font-bold text-f1-dark">
            Evolução da Probabilidade
          </h3>
          <p className="text-sm text-gray-500">
            Probabilidade de ser campeão por snapshot da feature store.
          </p>
        </div>
        {year && <div className="badge bg-f1-red text-white">{year}</div>}
      </div>

      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={chartData} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis dataKey="dt_ref" stroke="#888" fontSize={11} angle={-30} dy={8} height={50} />
          <YAxis
            domain={[0, 100]}
            tickFormatter={(v) => `${v}%`}
            stroke="#888"
            fontSize={12}
          />
          <Tooltip
            formatter={(value: number) => [`${value}%`, 'Prob. Campeão']}
            labelFormatter={(label: string) => `Data: ${label}`}
          />
          <Legend />
          {histories.map((h) => (
            <Line
              key={h.driverid}
              type="monotone"
              dataKey={h.fullname}
              stroke={getDriverColor(h.driverid)}
              strokeWidth={2.5}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
