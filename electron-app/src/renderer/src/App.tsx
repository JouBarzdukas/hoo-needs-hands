"use client"
import { useState, useEffect, useRef } from "react"
import "./assets/main.css"
import "./assets/fluid-orb.css"

interface LogEntry {
  id: number
  type: "input" | "response"
  text: string
  timestamp: Date
}

function App(): JSX.Element {
  const [isListening, setIsListening] = useState(false)
  const [audioLevel, setAudioLevel] = useState(0)
  const [logEntries, setLogEntries] = useState<LogEntry[]>([])
  const [isExpanded, setIsExpanded] = useState(false)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const mediaStreamRef = useRef<MediaStream | null>(null)
  const animationFrameRef = useRef<number | null>(null)
  const logContainerRef = useRef<HTMLDivElement | null>(null)
  const blobRef = useRef<HTMLDivElement | null>(null)
  const blobCoreRef = useRef<HTMLDivElement | null>(null)
  const blobEdgeRef = useRef<HTMLDivElement | null>(null)
  const blobHighlightRef = useRef<HTMLDivElement | null>(null)
  const blobContainerRef = useRef<HTMLDivElement | null>(null)
  // Add a ref to track if we're currently processing a toggle
  const isTogglingRef = useRef(false)

  const ipcHandle = (): void => window.electron.ipcRenderer.send("ping")

  // Add a sample log entry when the app starts
  useEffect(() => {
    addLogEntry("response", "Hello! I'm listening for your commands.")
  }, [])

  // Handle window resizing when expanded state changes
  useEffect(() => {
    const height = isExpanded ? 400 : 180
    window.electron.ipcRenderer.send("resize-window", height)
  }, [isExpanded])

  // Add effect for dynamic color changes based on audio level - balanced between v26 and v27
  useEffect(() => {
    if (!blobCoreRef.current) return

    if (isListening) {
      // Calculate color values based on audio level - balanced
      const brightness = 1.1 + Math.min(0.45, audioLevel * 0.006) // Increased effect
      const contrast = 1.2 + Math.min(0.45, audioLevel * 0.006) // Increased effect

      // Apply dynamic color filter - balanced
      blobCoreRef.current.style.filter = `brightness(${brightness}) contrast(${contrast})`

      // Adjust box shadow intensity based on audio level - balanced
      const blueIntensity = 0.4 + Math.min(0.45, audioLevel * 0.006) // Increased effect
      const purpleIntensity = 0.3 + Math.min(0.45, audioLevel * 0.006) // Increased effect
      const cyanIntensity = 0.4 + Math.min(0.45, audioLevel * 0.006) // Increased effect

      blobCoreRef.current.style.boxShadow = `
        0 0 10px rgba(0, 132, 255, ${blueIntensity}), 
        0 0 20px rgba(110, 47, 235, ${purpleIntensity}), 
        inset 0 0 15px rgba(0, 226, 226, ${cyanIntensity})
      `

      // Make the edge more responsive to audio - balanced
      if (blobEdgeRef.current) {
        const edgeOpacity = 0.2 + Math.min(0.35, audioLevel * 0.005) // Increased effect
        blobEdgeRef.current.style.opacity = edgeOpacity.toString()

        // Adjust rotation speed based on audio level - more subtle
        const rotationDuration = Math.max(12, 20 - audioLevel * 0.05) // Reduced from 0.1 to 0.05 and increased base duration
        blobEdgeRef.current.style.animationDuration = `${rotationDuration}s`
      }

      // Make the highlight more responsive - balanced
      if (blobHighlightRef.current) {
        const highlightOpacity = 0.6 + Math.min(0.4, audioLevel * 0.005) // Increased effect
        blobHighlightRef.current.style.opacity = highlightOpacity.toString()
      }

      // NEW: Adjust the outer glow based on audio level
      if (blobContainerRef.current) {
        // Create a dynamic style for the ::before pseudo-element
        const glowOpacity = 0.3 + Math.min(0.6, audioLevel * 0.01)
        const glowScale = 0.95 + Math.min(0.15, audioLevel * 0.003)

        // Apply custom property to control the glow animation
        blobContainerRef.current.style.setProperty("--glow-opacity", glowOpacity.toString())
        blobContainerRef.current.style.setProperty("--glow-scale", glowScale.toString())
      }
    } else {
      blobCoreRef.current.style.filter = "brightness(1.1) contrast(1.2)"
      blobCoreRef.current.style.boxShadow =
        "0 0 10px rgba(0, 132, 255, 0.4), 0 0 20px rgba(110, 47, 235, 0.3), inset 0 0 15px rgba(0, 226, 226, 0.4)"

      if (blobEdgeRef.current) {
        blobEdgeRef.current.style.opacity = "0.2"
        blobEdgeRef.current.style.animationDuration = "20s" // Increased from 15s to 20s
      }

      if (blobHighlightRef.current) {
        blobHighlightRef.current.style.opacity = "0.6"
      }

      // Reset glow properties when not listening
      if (blobContainerRef.current) {
        blobContainerRef.current.style.removeProperty("--glow-opacity")
        blobContainerRef.current.style.removeProperty("--glow-scale")
      }
    }
  }, [isListening, audioLevel])

  // Update blob scaling based on audio level - MORE DRAMATIC
  useEffect(() => {
    if (!blobRef.current) return

    if (isListening) {
      // Apply more dramatic scaling based on audio level
      const scale = 1 + Math.min(0.25, audioLevel * 0.005) // Increased from 0.12 to 0.25 and from 0.003 to 0.005
      blobRef.current.style.transform = `scale(${scale})`
    } else {
      blobRef.current.style.transform = "scale(1)"
    }
  }, [isListening, audioLevel])

  const toggleMicrophone = async () => {
    if (isListening) {
      stopListening()
      addLogEntry("response", "Listening stopped")
    } else {
      try {
        await startListening()
        addLogEntry("response", "Listening for your voice...")
      } catch (error) {
        console.error("Error accessing microphone:", error)
        addLogEntry("response", "Error accessing microphone. Please check permissions.")
      }
    }
  }

  const addLogEntry = (type: "input" | "response", text: string) => {
    const newEntry = {
      id: Date.now(),
      type,
      text,
      timestamp: new Date(),
    }

    setLogEntries((prev) => [...prev, newEntry])

    // Scroll to bottom of log container when expanded
    // This ensures the most recent messages are visible
    setTimeout(() => {
      if (logContainerRef.current && isExpanded) {
        logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
      }
    }, 100)
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
      analyser.fftSize = 1024
      analyserRef.current = analyser

      // Connect the microphone to the analyser
      const source = audioContext.createMediaStreamSource(stream)
      source.connect(analyser)

      // Start analyzing audio
      setIsListening(true)
      analyzeAudio()
    } catch (error) {
      console.error("Error starting microphone:", error)
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

  // Update the analyzeAudio function with HIGHER THRESHOLD:
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

      // Normalize to 0-100 range with balanced amplification
      const normalizedLevel = Math.min(100, Math.max(0, avg * 3.5)) // Keep the same amplification

      // Apply balanced transitions
      setAudioLevel((prevLevel) => {
        // If current level is lower, return to calm state at balanced pace
        if (normalizedLevel < prevLevel) {
          return prevLevel * 0.75 + normalizedLevel * 0.25
        } else {
          return prevLevel * 0.5 + normalizedLevel * 0.5
        }
      })

      // Detect significant audio for log entries - HIGHER THRESHOLD
      if (normalizedLevel > 75 && Math.random() > 0.996) {
        // Increased from 55 to 75
        const phrases = [
          "Opening your calendar",
          "Checking the weather",
          "Setting a reminder",
          "Searching for that",
          "Playing your music",
        ]
        addLogEntry("input", phrases[Math.floor(Math.random() * phrases.length)])

        // Simulate a response after a short delay
        setTimeout(() => {
          const responses = [
            "I've opened your calendar",
            "It's currently 72°F and sunny",
            "Reminder set for tomorrow",
            "Here are your search results",
            "Playing your favorite playlist",
          ]
          addLogEntry("response", responses[Math.floor(Math.random() * responses.length)])
        }, 800)
      }

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

  // Modified toggle function with debounce to prevent rapid toggling
  const toggleExpand = () => {
    // If we're already processing a toggle, ignore this request
    if (isTogglingRef.current) return

    // Set the flag to indicate we're processing a toggle
    isTogglingRef.current = true

    // Toggle the expanded state
    setIsExpanded(!isExpanded)

    // When expanding, scroll to the bottom to show most recent messages
    if (!isExpanded) {
      setTimeout(() => {
        if (logContainerRef.current) {
          logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
        }
      }, 100)
    }

    // Reset the flag after a short delay to prevent rapid toggling
    setTimeout(() => {
      isTogglingRef.current = false
    }, 300)
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  }

  return (
    <div className={`app-container ${isExpanded ? "expanded" : ""}`}>
      <div className="app-header">
        {/* Removed the app title */}
        <div className="app-title-placeholder"></div>
        <div className="app-controls">
          <button className="control-button expand-button" onClick={toggleExpand}>
            {isExpanded ? (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polyline points="18 15 12 9 6 15"></polyline>
              </svg>
            ) : (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            )}
          </button>
        </div>
      </div>

      <div className="mic-container">
        {/* Fluid Blob Orb with oily effect */}
        <div
          className={`fluid-blob-container ${isListening ? "active" : "inactive"}`}
          onClick={toggleMicrophone}
          ref={blobContainerRef}
        >
          <div className="fluid-blob" ref={blobRef}>
            <div className="blob-core" ref={blobCoreRef}></div>
            <div className="blob-highlight" ref={blobHighlightRef}></div>
            <div className="blob-surface"></div>
            <div className="blob-edge" ref={blobEdgeRef}></div>
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="log-container" ref={logContainerRef}>
          <div className="log-entries-wrapper">
            {logEntries.map((entry) => (
              <div key={entry.id} className={`log-entry ${entry.type}`}>
                <div className="log-entry-content">
                  <div className="log-entry-icon">
                    {entry.type === "input" ? (
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
                    ) : (
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <circle cx="12" cy="12" r="10"></circle>
                        <path d="M12 16v-4"></path>
                        <path d="M12 8h.01"></path>
                      </svg>
                    )}
                  </div>
                  <div className="log-entry-text">{entry.text}</div>
                  <div className="log-entry-time">{formatTime(entry.timestamp)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Removed status indicator */}
    </div>
  )
}

export default App

