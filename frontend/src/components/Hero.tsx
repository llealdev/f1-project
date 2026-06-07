import type { ReactNode } from 'react'

type Props = {
  children: ReactNode
}

export default function Hero({ children }: Props) {
  return (
    <section className="relative overflow-hidden bg-carbon text-white">
      <div className="absolute inset-0 opacity-30 pointer-events-none"
           style={{
             backgroundImage:
               'repeating-linear-gradient(45deg, rgba(225,6,0,0.08) 0 2px, transparent 2px 18px)',
           }}
      />
      <div className="absolute -top-32 -right-32 w-96 h-96 bg-f1-red/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-32 -left-32 w-96 h-96 bg-f1-red/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-6 py-16 lg:py-24">
        <div className="flex items-center gap-3 mb-6 animate-fade-in">
          <div className="w-10 h-10 rounded-lg bg-f1-red flex items-center justify-center font-display font-black text-white">
            F1
          </div>
          <span className="text-sm font-semibold tracking-[0.3em] uppercase text-white/60">
            Smart Predict
          </span>
        </div>
        {children}
      </div>
    </section>
  )
}
