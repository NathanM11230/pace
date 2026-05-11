import React from 'react'
import { Cpu, Trophy, Rocket, Heart, Bot } from 'lucide-react'

const CATEGORY_CONFIG = {
  tech: {
    color: '#0066FF',
    bg: '#EBF3FF',
    label: 'Tech',
    Icon: Cpu,
  },
  nba: {
    color: '#FF6B35',
    bg: '#FFF0EB',
    label: 'NBA',
    Icon: Trophy,
  },
  space: {
    color: '#7B61FF',
    bg: '#F0EEFF',
    label: 'Space',
    Icon: Rocket,
  },
  health: {
    color: '#00D9A3',
    bg: '#E6FAF5',
    label: 'Health',
    Icon: Heart,
  },
  ai: {
    color: '#FF61B6',
    bg: '#FFE8F5',
    label: 'AI',
    Icon: Bot,
  },
}

const DEFAULT_CONFIG = {
  color: '#6B7280',
  bg: '#F3F4F6',
  label: 'Other',
  Icon: Cpu,
}

export default function CategoryPill({ category, size = 'md', dark = false }) {
  const config = CATEGORY_CONFIG[category?.toLowerCase()] || DEFAULT_CONFIG
  const { color, bg, label, Icon } = config

  if (size === 'sm') {
    return (
      <span
        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold"
        style={{
          color: dark ? '#ffffff' : color,
          backgroundColor: dark ? `${color}33` : bg,
        }}
      >
        <Icon size={10} />
        {label}
      </span>
    )
  }

  return (
    <span
      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold"
      style={{
        color: dark ? '#ffffff' : color,
        backgroundColor: dark ? `${color}33` : bg,
      }}
    >
      <Icon size={13} />
      {label}
    </span>
  )
}

export { CATEGORY_CONFIG, DEFAULT_CONFIG }
