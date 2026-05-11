import React from 'react'
import { Play, Pause } from 'lucide-react'
import CategoryPill from './CategoryPill'

function timeAgo(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return ''
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

function estimateDuration(wordCount) {
  if (!wordCount) return null
  // Average speaking pace ~130 words per minute
  const seconds = Math.round((wordCount / 130) * 60)
  if (seconds < 60) return `~${seconds}s`
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return secs > 0 ? `~${mins}m ${secs}s` : `~${mins}m`
}

export default function SnippetCard({ snippet, isActive, onPlay, isPlaying }) {
  if (!snippet) return null

  const {
    title,
    category,
    source,
    published_at,
    word_count,
    script,
  } = snippet

  const durationLabel = estimateDuration(word_count)
  const timeLabel = timeAgo(published_at)

  return (
    <div
      className={`relative bg-white rounded-2xl p-4 shadow-sm border transition-all duration-200 cursor-pointer active:scale-[0.98] ${
        isActive
          ? 'border-blue shadow-md shadow-blue/10'
          : 'border-gray-mid hover:border-gray-dark/30 hover:shadow-md'
      }`}
      onClick={onPlay}
    >
      {/* Top row */}
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2 flex-wrap">
          <CategoryPill category={category} size="sm" />
          {durationLabel && (
            <span className="text-xs text-gray-dark bg-gray-light px-2 py-0.5 rounded-full font-medium">
              {durationLabel}
            </span>
          )}
        </div>

        {isActive && (
          <div className="flex items-center gap-1.5 shrink-0">
            <span
              className="w-2 h-2 rounded-full bg-blue dot-pulse"
            />
            <span className="text-xs font-semibold text-blue">
              Now Playing
            </span>
          </div>
        )}
      </div>

      {/* Title */}
      <h3
        className="font-semibold text-navy text-sm leading-snug mb-2"
        style={{
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }}
      >
        {title || 'Untitled Snippet'}
      </h3>

      {/* Meta + Play row */}
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-1.5 text-xs text-gray-dark min-w-0">
          {source && (
            <span className="font-medium truncate max-w-[120px]">{source}</span>
          )}
          {source && timeLabel && (
            <span className="text-gray-mid/80">·</span>
          )}
          {timeLabel && <span>{timeLabel}</span>}
        </div>

        {/* Play button */}
        <button
          className={`flex items-center justify-center w-9 h-9 rounded-full shrink-0 transition-all duration-200 ${
            isActive
              ? 'bg-blue text-white shadow-md shadow-blue/30 scale-105'
              : 'bg-gray-light text-navy hover:bg-blue hover:text-white'
          }`}
          onClick={(e) => {
            e.stopPropagation()
            onPlay()
          }}
          aria-label={isActive && isPlaying ? 'Pause' : 'Play'}
        >
          {isActive && isPlaying ? (
            <Pause size={16} fill="currentColor" />
          ) : (
            <Play size={16} fill="currentColor" />
          )}
        </button>
      </div>
    </div>
  )
}
