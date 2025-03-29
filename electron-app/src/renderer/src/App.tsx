// function App(): JSX.Element {
//   const ipcHandle = (): void => window.electron.ipcRenderer.send('ping')

//   return <>{/* add html */}</>
// }

import { useState, useEffect, useRef } from 'react'

function App(): JSX.Element {
  const [isListening, setIsListening] = useState(false)
  const [audioLevel, setAudioLevel] = useState(0)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const animationFrameRef = useRef<number | null>(null)

  const ipcHandle = (): void => window.electron.ipcRenderer.send('ping')

  const toggleMicrophone = async () => {
    if (isListening) {
      stopListening()
    } else {
      try {
        await startListening()
      } catch (error) {
        console.error('Error accessing microphone:', error)
      }
    }
  }

  const startListening = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaStreamRef.current = stream

      // Create audio context
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      audioContextRef.current = audioContext

      // Create analyser
      const analyser = audioContext.createAnalyser()
      analyser.fftSize = 256
      analyserRef.current = analyser

      // Connect the microphone to the analyser
      const source = audioContext.createMediaStreamSource(stream)
      source.connect(analyser)

      // Start analyzing audio
      setIsListening(true)
      analyzeAudio()
    } catch (error) {
      console.error('Error starting microphone:', error)
      throw error
    }
  }

  const stopListening = () => {
    // Stop the animation frame
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
      animationFrameRef.current = null
    }

    // Stop all microphone tracks
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop())
      mediaStreamRef.current = null
    }

    // Close audio context
    if (audioContextRef.current) {
      audioContextRef.current.close()
      audioContextRef.current = null
    }

    analyserRef.current = null
    setIsListening(false)
    setAudioLevel(0)
  }

  const analyzeAudio = () => {
    if (!analyserRef.current) return

    const analyser = analyserRef.current
    const dataArray = new Uint8Array(analyser.frequencyBinCount)

    const updateAudioLevel = () => {
      analyser.getByteFrequencyData(dataArray)

      // Calculate average volume level with more weight to higher frequencies
      let sum = 0
      let weightedSum = 0
      for (let i = 0; i < dataArray.length; i++) {
        const weight = 1 + i / dataArray.length // Higher frequencies get more weight
        weightedSum += dataArray[i] * weight
        sum += weight
      }
      const avg = weightedSum / sum

      // Normalize to 0-100 range with more amplification
      const normalizedLevel = Math.min(100, Math.max(0, avg * 2.5))

      // Apply smoothing to avoid jumpy animations
      setAudioLevel((prevLevel) => prevLevel * 0.7 + normalizedLevel * 0.3)

      // Continue analyzing
      animationFrameRef.current = requestAnimationFrame(updateAudioLevel)
    }

    updateAudioLevel()
  }

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop())
      }
      if (audioContextRef.current) {
        audioContextRef.current.close()
      }
    }
  }, [])

  return (
    <div className="app-container">
      <div
        className={`mic-button ${isListening ? 'active' : 'inactive'}`}
        onClick={toggleMicrophone}
        style={{ transform: isListening ? `scale(${1 + audioLevel * 0.003})` : 'scale(1)' }}
      >
        {isListening ? (
          <div className="siri-waves">
            {Array.from({ length: 5 }).map((_, index) => (
              <div
                key={index}
                className="wave"
                style={{
                  animationDuration: `${1.5 - index * 0.1}s`,
                  height: `${10 + index * 5 + audioLevel * 0.2}px`,
                  opacity: 0.7 - index * 0.1
                }}
              ></div>
            ))}
          </div>
        ) : (
          <div className="mic-off-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="1" y1="1" x2="23" y2="23"></line>
              <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"></path>
              <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"></path>
              <line x1="12" y1="19" x2="12" y2="23"></line>
              <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
