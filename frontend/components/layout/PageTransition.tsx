'use client'

import { motion } from 'framer-motion'
import { pageTransition } from '@/utils/animations'

interface PageTransitionProps {
    children: React.ReactNode
}

export default function PageTransition({ children }: PageTransitionProps) {
    return (
        <motion.div
            initial="initial"
            animate="animate"
            exit="exit"
            variants={pageTransition}
            className="w-full"
        >
            {children}
        </motion.div>
    )
}
