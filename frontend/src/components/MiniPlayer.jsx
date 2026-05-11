import React, { useEffect, useRef } from 'react'
import { Play, Pause, SkipForward, SkipBack } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import useAppStore from '../store/appStore'
import { CATEGORY_CONFIG, DEFAULT_CONFIG } from './CategoryPill'

function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

export default function MiniPlayer({
  isPlaying,
  currentTime,
  duration,
  progress,
  onPlayPause,
  onNext,
  onPrev,
}) {
  const navigate = useNavigate()
  const { getCurrentSnippet } = useAppStore()
  const snippet = getCurrentSnippet()

  if (!snippet) return null

  const catConfig =
    CATEGORY_CONFIG[snippet.category?.toLowerCase()] || DEFAULT_CONFIG

  const handleBarClick = (e) => {
    e.stopPropagation()
  }

  return (
    <div
      className="fixed bottom-16 left-1/2 -translate-x-1/2 w-full max-w-[480px] px-3 z-40"
      style={{ paddingBottom: '0' }}
    >
      <div
        className="bg-navy rounded-2xl shadow-xl shadow-navy/30 overflow-hidden cursor-pointer"
        onClick={() => navigate('/player')}
      >
        {/* Progress bar at top */}
        <div className="h-1 w-full bg-white/10">
          <div
            className="h-full bg-blue transition-all duration-300"
            style={{ width: `${(progress * 100).toFixed(1)}%` }}
          />
        </div>

        <div className="flex items-center gap-3 px-4 py-3">
          {/* Category icon badge */}
          <div
            className="flex items-center justify-center w-10 h-10 rounded-xl shrink-0"
            style={{ backgroundColor: `${catConfig.color}22` }}
          >
            <catConfig.Icon
              size={20}
              style={{ color: catConfig.color }}
            />
          </div>

          {/* Title + source */}
          <div className="flex-1 min-w-0">
            <p
              className="text-white text-sm font-semibold leading-snug truncate"
            >
              {snippet.title || 'Now Playing'}
            </p>
            <p className="text-white/50 text-xs mt-0.5">
              {formatTime(currentTime)} / {formatTime(duration)}
            </p>
          </div>

          {/* Controls */}
          <div
            className="flex items-center gap-1"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className="w-8 h-8 flex items-center justify-center text-white/60 hover:text-white transition-colors rounded-full hover:bg-white/10"
              onClick={(e) => { e.stopPropagation(); onPrev() }}
              aria-label="Previous"
            >
              <SkipBack size={16} />
            </button>

            <button
              className="w-9 h-9 flex items-center justify-center bg-blue rounded-full text-white shadow-md hover:bg-blue-600 transition-colors"
              onClick={(e) => { e.stopPropagation(); onPlayPause() }}
              aria-label={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? (
                <Pause size={16} fill="currentColor" />
              ) : (
                <Play size={16} fill="currentColor" />
              )}
            </button>

            <button
              className="w-8 h-8 flex items-center justify-center text-white/60 hover:text-white transition-colors rounded-full hover:bg-white/10"
              onClick={(e) => { e.stopPropagation(); onNext() }}
              aria-label="Next"
            >
              <SkipForward size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
