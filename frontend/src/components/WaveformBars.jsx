import React from 'react'

const NUM_BARS = 32

// Pre-defined heights and durations for visual variety
const BAR_CONFIGS = [
  { height: 60, duration: 0.8 }, { height: 80, duration: 0.6 },
  { height: 40, duration: 1.0 }, { height: 90, duration: 0.7 },
  { height: 55, duration: 0.9 }, { height: 75, duration: 0.5 },
  { height: 35, duration: 1.1 }, { height: 85, duration: 0.8 },
  { height: 65, duration: 0.6 }, { height: 50, duration: 1.2 },
  { height: 95, duration: 0.7 }, { height: 45, duration: 0.9 },
  { height: 70, duration: 0.5 }, { height: 30, duration: 1.0 },
  { height: 88, duration: 0.8 }, { height: 60, duration: 0.7 },
  { height: 72, duration: 1.1 }, { height: 42, duration: 0.6 },
  { height: 83, duration: 0.9 }, { height: 58, duration: 0.8 },
  { height: 67, duration: 0.5 }, { height: 38, duration: 1.2 },
  { height: 92, duration: 0.7 }, { height: 53, duration: 1.0 },
  { height: 78, duration: 0.6 }, { height: 44, duration: 0.9 },
  { height: 86, duration: 0.8 }, { height: 62, duration: 0.7 },
  { height: 48, duration: 1.1 }, { height: 74, duration: 0.5 },
  { height: 33, duration: 0.9 }, { height: 80, duration: 0.8 },
]

export default function WaveformBars({ isPlaying, color = '#ffffff', height = 40 }) {
  return (
    <div
      className="flex items-end gap-[2px]"
      style={{ height: `${height}px` }}
      aria-label={isPlaying ? 'Playing' : 'Paused'}
    >
      {BAR_CONFIGS.map((config, index) => {
        const barHeight = (config.height / 100) * height
        const delay = (index * 0.04) % config.duration

        if (isPlaying) {
          return (
            <div
              key={index}
              style={{
                width: '3px',
                height: `${barHeight}px`,
                backgroundColor: color,
                borderRadius: '1.5px',
                transformOrigin: 'bottom',
                animation: `waveform-pulse ${config.duration}s ease-in-out infinite`,
                animationDelay: `${delay}s`,
                opacity: 0.85 + (index % 4) * 0.04,
              }}
            />
          )
        }

        return (
          <div
            key={index}
            style={{
              width: '3px',
              height: `${(height * 0.35).toFixed(0)}px`,
              backgroundColor: color,
              borderRadius: '1.5px',
              opacity: 0.4,
            }}
          />
        )
      })}
    </div>
  )
}
