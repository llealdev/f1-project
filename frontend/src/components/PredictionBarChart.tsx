import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { Prediction } from '../lib/api'
import { getDriverColor } from '../lib/utils'

type Props = {
  predictions: Prediction[]
}

export default function PredictionBarChart({ predictions }: Props) {
  const data = predictions.map((p) => ({
    name: p.fullname,
    prob: +(p.prob_win * 100).toFixed(2),
    driverid: p.driverid,
  }))

  return (
    <div className="card p-6 h-[480px] animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-display font-bold text-f1-dark">
            Probabilidade de Ser Campeão
          </h3>
          <p className="text-sm text-gray-500">
            Snapshot mais recente da feature store para o ano selecionado.
          </p>
        </div>
        <div className="badge bg-f1-dark text-white">Random Forest</div>
      </div>

      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data} layout="vertical" margin={{ left: 12, right: 24, top: 8, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis
            type="number"
            domain={[0, 100]}
            tickFormatter={(v) => `${v}%`}
            stroke="#888"
            fontSize={12}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={150}
            stroke="#888"
            fontSize={12}
          />
          <Tooltip
            formatter={(value: number) => [`${value}%`, 'Prob. Campeão']}
            cursor={{ fill: 'rgba(225,6,0,0.08)' }}
          />
          <Bar dataKey="prob" radius={[0, 8, 8, 0]}>
            {data.map((entry) => (
              <Cell key={entry.driverid} fill={getDriverColor(entry.driverid)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
