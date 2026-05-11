import { useRef, useState, useEffect, useCallback } from 'react'

export function useAudioPlayer(audioUrl, { onEnded, onPlay, onTimeUpdate } = {}) {
  const audioRef = useRef(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  // Create or recreate audio element when URL changes
  useEffect(() => {
    if (!audioUrl) return

    // Cleanup previous audio
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.removeAttribute('src')
      audioRef.current.load()
    }

    const audio = new Audio()
    audio.preload = 'metadata'
    audioRef.current = audio

    setIsPlaying(false)
    setCurrentTime(0)
    setDuration(0)
    setError(null)
    setIsLoading(true)

    const handleLoadedMetadata = () => {
      setDuration(audio.duration || 0)
      setIsLoading(false)
    }

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime)
      if (onTimeUpdate) {
        onTimeUpdate(audio.currentTime)
      }
    }

    const handleEnded = () => {
      setIsPlaying(false)
      setCurrentTime(0)
      if (onEnded) onEnded()
    }

    const handlePlay = () => {
      setIsPlaying(true)
      if (onPlay) onPlay()
    }

    const handlePause = () => {
      setIsPlaying(false)
    }

    const handleError = () => {
      setIsLoading(false)
      setError('Audio not available')
      setIsPlaying(false)
    }

    const handleCanPlay = () => {
      setIsLoading(false)
    }

    audio.addEventListener('loadedmetadata', handleLoadedMetadata)
    audio.addEventListener('timeupdate', handleTimeUpdate)
    audio.addEventListener('ended', handleEnded)
    audio.addEventListener('play', handlePlay)
    audio.addEventListener('pause', handlePause)
    audio.addEventListener('error', handleError)
    audio.addEventListener('canplay', handleCanPlay)

    audio.src = audioUrl

    return () => {
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata)
      audio.removeEventListener('timeupdate', handleTimeUpdate)
      audio.removeEventListener('ended', handleEnded)
      audio.removeEventListener('play', handlePlay)
      audio.removeEventListener('pause', handlePause)
      audio.removeEventListener('error', handleError)
      audio.removeEventListener('canplay', handleCanPlay)
      audio.pause()
      audio.removeAttribute('src')
      audio.load()
    }
  }, [audioUrl])

  const play = useCallback(async () => {
    if (!audioRef.current) return
    try {
      await audioRef.current.play()
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError('Could not play audio')
      }
    }
  }, [])

  const pause = useCallback(() => {
    if (!audioRef.current) return
    audioRef.current.pause()
  }, [])

  const toggle = useCallback(async () => {
    if (!audioRef.current) return
    if (audioRef.current.paused) {
      await play()
    } else {
      pause()
    }
  }, [play, pause])

  const seekTo = useCallback((seconds) => {
    if (!audioRef.current) return
    const clamped = Math.max(0, Math.min(seconds, audioRef.current.duration || 0))
    audioRef.current.currentTime = clamped
    setCurrentTime(clamped)
  }, [])

  const skipForward = useCallback(() => {
    if (!audioRef.current) return
    seekTo(audioRef.current.currentTime + 10)
  }, [seekTo])

  const skipBackward = useCallback(() => {
    if (!audioRef.current) return
    seekTo(audioRef.current.currentTime - 10)
  }, [seekTo])

  const progress = duration > 0 ? currentTime / duration : 0

  return {
    audioRef,
    isPlaying,
    currentTime,
    duration,
    progress,
    isLoading,
    error,
    play,
    pause,
    toggle,
    seekTo,
    skipForward,
    skipBackward,
  }
}
