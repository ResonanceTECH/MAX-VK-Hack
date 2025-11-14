import React from 'react'
import './LoadingSpinner.css'

interface LoadingSpinnerProps {
  text?: string
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ text = 'Загрузка...' }) => {
  return (
    <div className="loading-spinner-container">
      <p className="loading-text">{text}</p>
    </div>
  )
}

export default LoadingSpinner

