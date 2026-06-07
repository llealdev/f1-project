import { getDriverColor } from '../lib/utils'

type Props = {
  rank: number
  driverid: string
  fullname: string
  prob_win: number
  dt_ref: string
}

export default function PredictionRow({ rank, driverid, fullname, prob_win, dt_ref }: Props) {
  const color = getDriverColor(driverid)
  const podium = rank <= 3
  const medalEmoji = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : null

  return (
    <div
      className="card p-4 flex items-center gap-4 animate-slide-up"
      style={{ borderLeft: `6px solid ${color}` }}
    >
      <div className="w-12 h-12 rounded-xl flex items-center justify-center font-display font-black text-2xl"
           style={{ backgroundColor: `${color}20`, color }}>
        {medalEmoji ?? `#${rank}`}
      </div>

      <div className="flex-1 min-w-0">
        <div className="font-bold text-lg text-f1-dark truncate">
          {fullname}
        </div>
        <div className="text-xs text-gray-500 uppercase tracking-wider font-mono">
          {driverid} · {dt_ref}
        </div>
      </div>

      <div className="hidden sm:block w-1/3 max-w-[220px]">
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full transition-all duration-700 ease-out rounded-full"
            style={{ width: `${Math.max(2, prob_win * 100)}%`, backgroundColor: color }}
          />
        </div>
      </div>

      <div className="text-right min-w-[80px]">
        <div className="font-display font-black text-2xl" style={{ color }}>
          {(prob_win * 100).toFixed(1)}%
        </div>
        <div className="text-[10px] uppercase tracking-widest text-gray-500 font-semibold">
          Champion
        </div>
      </div>

      {podium && (
        <div className="badge bg-f1-red text-white">P{rank}</div>
      )}
    </div>
  )
}
