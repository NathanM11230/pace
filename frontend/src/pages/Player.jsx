import React, { useCallback, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ChevronLeft,
  SkipBack,
  SkipForward,
  Play,
  Pause,
  ArrowRight,
  Loader2,
  AlertCircle,
} from 'lucide-react'
import useAppStore from '../store/appStore'
import { api } from '../api/client'
import { useAudioPlayer } from '../hooks/useAudioPlayer'
import CategoryPill, { CATEGORY_CONFIG, DEFAULT_CONFIG } from '../components/CategoryPill'
import WaveformBars from '../components/WaveformBars'
import { BottomNav } from './Feed'

function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

export default function Player() {
  const navigate = useNavigate()
  const {
    user,
    feed,
    currentIndex,
    isPlaying,
    setIsPlaying,
    nextSnippet,
    prevSnippet,
    getCurrentSnippet,
  } = useAppStore()

  const currentSnippet = getCurrentSnippet()
  const audioUrl = currentSnippet ? api.getAudioUrl(currentSnippet.id) : null
  const interactedRef = useRef(new Set())

  const handleEnded = useCallback(async () => {
    if (currentSnippet && user && !interactedRef.current.has(`${currentSnippet.id}-completed`)) {
      interactedRef.current.add(`${currentSnippet.id}-completed`)
      try {
        await api.recordInteraction(user.id, currentSnippet.id, 'completed')
      } catch {}
    }
    nextSnippet()
  }, [currentSnippet, user, nextSnippet])

  const handlePlay = useCallback(async () => {
    if (currentSnippet && user && !interactedRef.current.has(`${currentSnippet.id}-played`)) {
      interactedRef.current.add(`${currentSnippet.id}-played`)
      try {
        await api.recordInteraction(user.id, currentSnippet.id, 'played')
      } catch {}
    }
  }, [currentSnippet, user])

  const {
    isPlaying: audioIsPlaying,
    currentTime,
    duration,
    progress,
    isLoading,
    error: audioError,
    toggle,
    seekTo,
    skipForward,
    skipBackward,
    play,
  } = useAudioPlayer(audioUrl, {
    onEnded: handleEnded,
    onPlay: handlePlay,
  })

  // Sync playing state to store
  useEffect(() => {
    setIsPlaying(audioIsPlaying)
  }, [audioIsPlaying, setIsPlaying])

  // Auto-play when snippet changes
  useEffect(() => {
    if (currentSnippet && audioUrl) {
      const timer = setTimeout(() => {
        play()
      }, 200)
      return () => clearTimeout(timer)
    }
  }, [currentSnippet?.id])

  const handleSkipSnippet = async () => {
    if (currentSnippet && user) {
      try {
        await api.recordInteraction(user.id, currentSnippet.id, 'skipped')
      } catch {}
    }
    nextSnippet()
  }

  const handleSeek = (e) => {
    const val = parseFloat(e.target.value)
    seekTo(val * duration)
  }

  if (!currentSnippet) {
    return (
      <div className="min-h-screen bg-navy flex flex-col items-center justify-center text-white max-w-[480px] mx-auto">
        <AlertCircle size={40} className="text-white/40 mb-4" />
        <p className="text-white/70 mb-6">No snippet selected</p>
        <button
          onClick={() => navigate('/feed')}
          className="bg-blue text-white px-6 py-3 rounded-xl font-semibold"
        >
          Go to Feed
        </button>
        <BottomNav active="player" />
      </div>
    )
  }

  const catConfig =
    CATEGORY_CONFIG[currentSnippet.category?.toLowerCase()] || DEFAULT_CONFIG

  const prevSnippetData = feed.length > 1
    ? feed[(currentIndex - 1 + feed.length) % feed.length]
    : null

  const nextSnippetData = feed.length > 1
    ? feed[(currentIndex + 1) % feed.length]
    : null

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{ background: 'linear-gradient(160deg, #1A1F36 0%, #0D1124 100%)' }}
    >
      <div className="w-full max-w-[480px] mx-auto flex flex-col min-h-screen pb-16">

        {/* Top bar */}
        <div className="flex items-center justify-between px-4 pt-12 pb-4">
          <button
            onClick={() => navigate(-1)}
            className="w-9 h-9 rounded-full bg-white/10 flex items-center justify-center text-white hover:bg-white/20 transition-colors"
            aria-label="Go back"
          >
            <ChevronLeft size={20} />
          </button>

          <div className="flex flex-col items-center gap-1">
            <p className="text-white/50 text-[10px] font-bold tracking-[0.15em] uppercase">
              Now Playing
            </p>
          </div>

          <div>
            <CategoryPill category={currentSnippet.category} size="sm" dark />
          </div>
        </div>

        {/* Previous snippet ghost */}
        {prevSnippetData && (
          <div className="px-6 mb-3">
            <p
              className="text-white/25 text-xs text-center truncate cursor-pointer hover:text-white/40 transition-colors"
              onClick={prevSnippet}
            >
              ↑ {prevSnippetData.title}
            </p>
          </div>
        )}

        {/* Main content */}
        <div className="flex-1 flex flex-col items-center justify-center px-6 py-4">
          {/* Large category icon */}
          <div
            className="w-24 h-24 rounded-3xl flex items-center justify-center mb-6 shadow-2xl"
            style={{
              background: `linear-gradient(135deg, ${catConfig.color}33, ${catConfig.color}66)`,
              border: `1px solid ${catConfig.color}44`,
            }}
          >
            <catConfig.Icon
              size={48}
              style={{ color: catConfig.color }}
            />
          </div>

          {/* Title */}
          <h2
            className="text-white font-black text-xl text-center leading-snug mb-2 max-w-[320px]"
            style={{
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
            }}
          >
            {currentSnippet.title || 'Untitled'}
          </h2>

          {/* Source */}
          {currentSnippet.source && (
            <p className="text-white/50 text-sm mb-6">
              {currentSnippet.source}
            </p>
          )}

          {/* Waveform */}
          <div className="mb-6">
            {audioError ? (
              <div className="text-center">
                <p className="text-orange text-sm font-medium mb-2">Audio not available</p>
                {currentSnippet.script && (
                  <div className="bg-white/5 rounded-xl p-4 max-w-[300px] max-h-32 overflow-y-auto">
                    <p className="text-white/70 text-xs leading-relaxed">
                      {currentSnippet.script}
                    </p>
                  </div>
                )}
              </div>
            ) : isLoading ? (
              <div className="flex items-center gap-2 text-white/50">
                <Loader2 size={16} className="animate-spin" />
                <span className="text-sm">Loading audio...</span>
              </div>
            ) : (
              <WaveformBars isPlaying={audioIsPlaying} color={catConfig.color} height={48} />
            )}
          </div>
        </div>

        {/* Progress section */}
        {!audioError && (
          <div className="px-6 mb-6">
            <input
              type="range"
              min="0"
              max="1"
              step="0.001"
              value={progress}
              onChange={handleSeek}
              className="progress-bar w-full mb-2"
              aria-label="Seek"
            />
            <div className="flex justify-between text-white/40 text-xs font-medium">
              <span>{formatTime(currentTime)}</span>
              <span>{formatTime(duration)}</span>
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="px-6 mb-6">
          <div className="flex items-center justify-center gap-6 mb-5">
            {/* Skip back 10s */}
            <button
              onClick={skipBackward}
              className="w-12 h-12 flex flex-col items-center justify-center text-white/70 hover:text-white transition-colors group"
              aria-label="Skip back 10 seconds"
              disabled={!!audioError}
            >
              <SkipBack size={28} />
              <span className="text-[9px] font-bold opacity-60 group-hover:opacity-100 -mt-1">10s</span>
            </button>

            {/* Play/Pause */}
            <button
              onClick={toggle}
              disabled={!!audioError || isLoading}
              className={`w-16 h-16 rounded-full flex items-center justify-center text-white shadow-xl transition-all duration-200 active:scale-95 ${
                audioError || isLoading
                  ? 'bg-white/20 cursor-not-allowed'
                  : 'bg-blue hover:bg-blue-600 shadow-blue/40'
              }`}
              aria-label={audioIsPlaying ? 'Pause' : 'Play'}
            >
              {isLoading ? (
                <Loader2 size={28} className="animate-spin" />
              ) : audioIsPlaying ? (
                <Pause size={28} fill="currentColor" />
              ) : (
                <Play size={28} fill="currentColor" />
              )}
            </button>

            {/* Skip forward 10s */}
            <button
              onClick={skipForward}
              className="w-12 h-12 flex flex-col items-center justify-center text-white/70 hover:text-white transition-colors group"
              aria-label="Skip forward 10 seconds"
              disabled={!!audioError}
            >
              <SkipForward size={28} />
              <span className="text-[9px] font-bold opacity-60 group-hover:opacity-100 -mt-1">10s</span>
            </button>
          </div>

          {/* Skip snippet */}
          <div className="flex justify-center">
            <button
              onClick={handleSkipSnippet}
              className="flex items-center gap-1.5 text-white/40 hover:text-white/70 text-sm font-medium transition-colors py-2 px-4"
            >
              Skip snippet
              <ArrowRight size={14} />
            </button>
          </div>
        </div>

        {/* Next snippet ghost */}
        {nextSnippetData && (
          <div className="px-6 mb-4">
            <p
              className="text-white/25 text-xs text-center truncate cursor-pointer hover:text-white/40 transition-colors"
              onClick={nextSnippet}
            >
              ↓ {nextSnippetData.title}
            </p>
          </div>
        )}

        {/* Bottom nav */}
        <BottomNav active="player" />
      </div>
    </div>
  )
}
