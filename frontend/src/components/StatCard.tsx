type Props = {
  label: string
  value: string | number
  hint?: string
  tone?: 'red' | 'dark' | 'light'
}

export default function StatCard({ label, value, hint, tone = 'dark' }: Props) {
  const tones: Record<string, string> = {
    red: 'bg-f1-red text-white',
    dark: 'bg-f1-dark text-white',
    light: 'bg-white text-f1-dark border border-gray-200',
  }
  return (
    <div className={`rounded-2xl p-5 shadow-sm ${tones[tone]} transition-transform hover:scale-[1.02]`}>
      <div className="text-xs uppercase tracking-widest opacity-70 font-semibold">{label}</div>
      <div className="text-3xl font-display font-black mt-2">{value}</div>
      {hint && <div className="text-xs mt-1 opacity-70">{hint}</div>}
    </div>
  )
}
