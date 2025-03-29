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

      // Calculate average volume level
      let sum = 0
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i]
      }
      const avg = sum / dataArray.length

      // Normalize to 0-100 range and apply some amplification
      const normalizedLevel = Math.min(100, Math.max(0, avg * 2))
      setAudioLevel(normalizedLevel)

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
      >
        <div className="mic-icon">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
            <line x1="12" y1="19" x2="12" y2="23"></line>
            <line x1="8" y1="23" x2="16" y2="23"></line>
          </svg>
        </div>
      </div>

      {isListening && (
        <>
          <div
            className="audio-ring ring-1"
            style={{ transform: `scale(${1 + audioLevel * 0.005})` }}
          ></div>
          <div
            className="audio-ring ring-2"
            style={{ transform: `scale(${1 + audioLevel * 0.01})` }}
          ></div>
          <div
            className="audio-ring ring-3"
            style={{ transform: `scale(${1 + audioLevel * 0.015})` }}
          ></div>
        </>
      )}
    </div>
  )
}

export default App
