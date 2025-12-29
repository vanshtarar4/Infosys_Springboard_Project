'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'dark' | 'light'

interface ThemeContextType {
    theme: Theme
    toggleTheme: () => void
    setTheme: (theme: Theme) => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: React.ReactNode }) {
    const [theme, setThemeState] = useState<Theme>('dark')

    useEffect(() => {
        // Load theme from localStorage or default to dark
        const savedTheme = localStorage.getItem('secureguard-theme') as Theme | null
        const initialTheme = savedTheme || 'dark'
        setThemeState(initialTheme)
        applyTheme(initialTheme)
    }, [])

    const applyTheme = (newTheme: Theme) => {
        const root = document.documentElement

        if (newTheme === 'light') {
            root.setAttribute('data-theme', 'light')
        } else {
            root.removeAttribute('data-theme')
        }
    }

    const setTheme = (newTheme: Theme) => {
        setThemeState(newTheme)
        applyTheme(newTheme)
        localStorage.setItem('secureguard-theme', newTheme)
    }

    const toggleTheme = () => {
        const newTheme = theme === 'dark' ? 'light' : 'dark'
        setTheme(newTheme)
    }

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
            {children}
        </ThemeContext.Provider>
    )
}

export function useTheme() {
    const context = useContext(ThemeContext)
    if (context === undefined) {
        throw new Error('useTheme must be used within a ThemeProvider')
    }
    return context
}
