import { Variants } from 'framer-motion'

/**
 * Page transition animations
 */
export const pageTransition: Variants = {
    initial: {
        opacity: 0,
        x: -20,
    },
    animate: {
        opacity: 1,
        x: 0,
        transition: {
            duration: 0.3,
            ease: 'easeInOut',
        },
    },
    exit: {
        opacity: 0,
        x: 20,
        transition: {
            duration: 0.2,
            ease: 'easeInOut',
        },
    },
}

/**
 * Fade in animation
 */
export const fadeIn: Variants = {
    initial: {
        opacity: 0,
    },
    animate: {
        opacity: 1,
        transition: {
            duration: 0.4,
            ease: 'easeOut',
        },
    },
    exit: {
        opacity: 0,
        transition: {
            duration: 0.2,
        },
    },
}

/**
 * Slide up animation
 */
export const slideUp: Variants = {
    initial: {
        opacity: 0,
        y: 20,
    },
    animate: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.4,
            ease: 'easeOut',
        },
    },
    exit: {
        opacity: 0,
        y: -20,
        transition: {
            duration: 0.2,
        },
    },
}

/**
 * Scale animation for modals
 */
export const scaleIn: Variants = {
    initial: {
        opacity: 0,
        scale: 0.95,
    },
    animate: {
        opacity: 1,
        scale: 1,
        transition: {
            duration: 0.2,
            ease: 'easeOut',
        },
    },
    exit: {
        opacity: 0,
        scale: 0.95,
        transition: {
            duration: 0.15,
        },
    },
}

/**
 * Stagger children animation
 */
export const staggerContainer: Variants = {
    initial: {},
    animate: {
        transition: {
            staggerChildren: 0.1,
            delayChildren: 0.1,
        },
    },
}

/**
 * Stagger item animation
 */
export const staggerItem: Variants = {
    initial: {
        opacity: 0,
        y: 20,
    },
    animate: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.4,
            ease: 'easeOut',
        },
    },
}

/**
 * Card hover animation
 */
export const cardHover: Variants = {
    rest: {
        scale: 1,
        y: 0,
    },
    hover: {
        scale: 1.02,
        y: -4,
        transition: {
            duration: 0.2,
            ease: 'easeOut',
        },
    },
    tap: {
        scale: 0.98,
    },
}

/**
 * Button press animation
 */
export const buttonPress: Variants = {
    rest: {
        scale: 1,
    },
    hover: {
        scale: 1.05,
        transition: {
            duration: 0.2,
            ease: 'easeOut',
        },
    },
    tap: {
        scale: 0.95,
    },
}

/**
 * Sidebar collapse animation
 */
export const sidebarVariants: Variants = {
    expanded: {
        width: '240px',
        transition: {
            duration: 0.3,
            ease: 'easeInOut',
        },
    },
    collapsed: {
        width: '80px',
        transition: {
            duration: 0.3,
            ease: 'easeInOut',
        },
    },
}

/**
 * Dropdown menu animation
 */
export const dropdownVariants: Variants = {
    closed: {
        opacity: 0,
        y: -10,
        scale: 0.95,
        transition: {
            duration: 0.15,
        },
    },
    open: {
        opacity: 1,
        y: 0,
        scale: 1,
        transition: {
            duration: 0.2,
            ease: 'easeOut',
        },
    },
}

/**
 * Number counter spring config
 */
export const counterSpring = {
    type: 'spring',
    stiffness: 100,
    damping: 15,
    mass: 0.8,
}

/**
 * Tooltip animation
 */
export const tooltipVariants: Variants = {
    hidden: {
        opacity: 0,
        scale: 0.9,
        y: 5,
    },
    visible: {
        opacity: 1,
        scale: 1,
        y: 0,
        transition: {
            duration: 0.15,
            ease: 'easeOut',
        },
    },
}

/**
 * Alert pulse animation
 */
export const alertPulse: Variants = {
    initial: {
        scale: 1,
        opacity: 1,
    },
    animate: {
        scale: [1, 1.05, 1],
        opacity: [1, 0.8, 1],
        transition: {
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
        },
    },
}

/**
 * Loading spinner rotation
 */
export const spinnerRotation = {
    animate: {
        rotate: 360,
        transition: {
            duration: 1,
            repeat: Infinity,
            ease: 'linear',
        },
    },
}

/**
 * Progress bar fill animation
 */
export const progressFill = (value: number) => ({
    initial: {
        width: '0%',
    },
    animate: {
        width: `${value}%`,
        transition: {
            duration: 1,
            ease: 'easeOut',
        },
    },
})

/**
 * Chart draw animation
 */
export const chartDraw: Variants = {
    hidden: {
        pathLength: 0,
        opacity: 0,
    },
    visible: {
        pathLength: 1,
        opacity: 1,
        transition: {
            pathLength: {
                duration: 1.5,
                ease: 'easeInOut',
            },
            opacity: {
                duration: 0.5,
            },
        },
    },
}

/**
 * Table row hover
 */
export const tableRowHover: Variants = {
    rest: {
        backgroundColor: 'transparent',
    },
    hover: {
        backgroundColor: 'hsl(var(--card-hover))',
        transition: {
            duration: 0.15,
        },
    },
}

/**
 * Badge pulse animation
 */
export const badgePulse = (color: string = 'red') => ({
    scale: [1, 1.1, 1],
    boxShadow: [
        `0 0 0 0 rgba(239, 68, 68, 0)`,
        `0 0 0 8px rgba(239, 68, 68, 0.4)`,
        `0 0 0 0 rgba(239, 68, 68, 0)`,
    ],
    transition: {
        duration: 2,
        repeat: Infinity,
        ease: 'easeInOut',
    },
})

/**
 * Slide in from side
 */
export const slideInFromRight: Variants = {
    initial: {
        x: '100%',
        opacity: 0,
    },
    animate: {
        x: 0,
        opacity: 1,
        transition: {
            duration: 0.3,
            ease: 'easeOut',
        },
    },
    exit: {
        x: '100%',
        opacity: 0,
        transition: {
            duration: 0.2,
        },
    },
}

/**
 * Slide in from side
 */
export const slideInFromLeft: Variants = {
    initial: {
        x: '-100%',
        opacity: 0,
    },
    animate: {
        x: 0,
        opacity: 1,
        transition: {
            duration: 0.3,
            ease: 'easeOut',
        },
    },
    exit: {
        x: '-100%',
        opacity: 0,
        transition: {
            duration: 0.2,
        },
    },
}
