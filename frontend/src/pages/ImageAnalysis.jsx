import { useEffect, useRef, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { API_ORIGIN } from '../services/apiClient'
import { useNotifications } from '../context/NotificationContext'
import { analyzeImage, getAnalysisHistory } from '../services/imageAnalysisService'
import { formatApiError } from '../utils/formatApiError'

const BODY_TYPE_VARIANT = {
  Thin: 'info',
  Normal: 'success',
  Overweight: 'warning',
}

export default function ImageAnalysis() {
  const { user } = useAuth()
  const { showToast } = useNotifications()

  const [previewUrl, setPreviewUrl] = useState(null)
  const [isScanning, setIsScanning] = useState(false)
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isLoadingHistory, setIsLoadingHistory] = useState(true)

  // Display-only "pre-scan" fields. Camera height / distance have no real
  // counterpart in SmartGen Fit (single-photo upload, no camera/3D sensing),
  // so they're decorative to match the scanner aesthetic. Gender/age start
  // from the user's real profile since those already mean something in this
  // app (the KNN recommender matches on them) - editable here for display
  // only though, since the analyze endpoint only accepts the photo itself.
  const [cameraHeight, setCameraHeight] = useState(120)
  const [distance, setDistance] = useState(175)
  const [gender, setGender] = useState(user?.gender || 'male')
  const [age, setAge] = useState(user?.age || 25)

  const fileInputRef = useRef(null)
  const requestTokenRef = useRef(0)

  const fetchHistory = () => {
    return getAnalysisHistory()
      .then((data) => setHistory(data.history))
      .catch(() => setHistory([]))
  }

  useEffect(() => {
    fetchHistory().finally(() => setIsLoadingHistory(false))
  }, [])

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const runAnalysis = async (selectedFile, token) => {
    setError('')
    setResult(null)
    setIsSubmitting(true)
    try {
      const data = await analyzeImage(selectedFile)
      if (requestTokenRef.current !== token) return // stopped/reset before this resolved
      setResult(data.analysis)
      showToast(
        `Body type analyzed: ${data.analysis.predicted_body_type?.name} (${(
          Number(data.analysis.confidence_score) * 100
        ).toFixed(0)}% confidence)`,
        'success',
      )
      fetchHistory()
    } catch (err) {
      if (requestTokenRef.current !== token) return
      setError(formatApiError(err, 'Could not analyze the photo.'))
    } finally {
      if (requestTokenRef.current === token) {
        setIsSubmitting(false)
        setIsScanning(false)
      }
    }
  }

  const handleFileChange = (event) => {
    const selected = event.target.files[0]
    if (!selected) return

    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(URL.createObjectURL(selected))
    setResult(null)
    setError('')
    setIsScanning(true)

    const token = ++requestTokenRef.current
    runAnalysis(selected, token)
  }

  const handleStartScan = () => {
    fileInputRef.current?.click()
  }

  const handleStop = () => {
    requestTokenRef.current++ // invalidate any in-flight response
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(null)
    setIsScanning(false)
    setIsSubmitting(false)
    setResult(null)
    setError('')
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div>
      <h1 className="mb-1">Body Type Analysis</h1>
      <p className="text-secondary small mb-4" style={{ fontFamily: 'var(--sgf-mono-font)' }}>
        Keep full body in the guide box.
      </p>

      <input
        ref={fileInputRef}
        id="image"
        type="file"
        accept="image/png, image/jpeg, image/webp"
        onChange={handleFileChange}
        className="visually-hidden"
        aria-label="Upload a full-body photo"
      />

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="scanner-grid mb-4">
        <div className="scanner-viewfinder">
          <span className="scanner-crosshair scanner-crosshair-tl" />
          <span className="scanner-crosshair scanner-crosshair-tr" />
          <span className="scanner-crosshair scanner-crosshair-bl" />
          <span className="scanner-crosshair scanner-crosshair-br" />

          {previewUrl ? (
            <img src={previewUrl} alt="Selected preview" className="scanner-preview-img" />
          ) : (
            <>
              <div className="scanner-guide-box" />
              <span className="scanner-guide-text">Step into the guide box</span>
            </>
          )}

          {isScanning && <div className="scanner-laser" />}

          <div className="scanner-viewfinder-footer">
            <span className="scanner-rec-dot" aria-hidden="true" />
            {previewUrl
              ? isSubmitting
                ? 'SCANNING...'
                : result
                  ? 'SCAN COMPLETE'
                  : 'SCAN STOPPED'
              : "CLICK 'START SCAN' TO BEGIN"}
          </div>
        </div>

        <div className="d-flex flex-column gap-3">
          <div className="card scanner-card">
            <div className="card-body">
              <h2 className="scanner-card-title">Camera setup</h2>

              <label className="scanner-field-label" htmlFor="cameraHeight">
                <span>Camera height</span>
                <span className="scanner-field-value">{cameraHeight}cm</span>
              </label>
              <input
                id="cameraHeight"
                type="range"
                min="100"
                max="220"
                value={cameraHeight}
                onChange={(e) => setCameraHeight(Number(e.target.value))}
                className="form-range scanner-slider"
              />

              <label className="scanner-field-label mt-3" htmlFor="distance">
                <span>Distance to camera</span>
                <span className="scanner-field-value">{distance}cm</span>
              </label>
              <input
                id="distance"
                type="range"
                min="50"
                max="300"
                value={distance}
                onChange={(e) => setDistance(Number(e.target.value))}
                className="form-range scanner-slider"
              />

              <label className="scanner-field-label mt-3" htmlFor="scanGender">
                <span>Gender</span>
              </label>
              <select
                id="scanGender"
                className="form-select scanner-select"
                value={gender}
                onChange={(e) => setGender(e.target.value)}
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>

              <label className="scanner-field-label mt-3" htmlFor="scanAge">
                <span>Age</span>
                <span className="scanner-field-value">{age}yr</span>
              </label>
              <input
                id="scanAge"
                type="range"
                min="15"
                max="90"
                value={age}
                onChange={(e) => setAge(Number(e.target.value))}
                className="form-range scanner-slider"
              />
            </div>
          </div>

          <div className="card scanner-card">
            <div className="card-body">
              <h2 className="scanner-card-title">Scan controls</h2>
              <p className="text-secondary small">
                Once your photo loads, analysis starts automatically.
              </p>
              <div className="d-flex gap-2">
                <button
                  type="button"
                  className="btn scanner-btn-start flex-grow-1"
                  onClick={handleStartScan}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Scanning…' : 'Start scan'}
                </button>
                <button
                  type="button"
                  className="btn scanner-btn-stop"
                  onClick={handleStop}
                  disabled={!previewUrl}
                >
                  Stop
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {result && (
        <div className="p-3 border rounded mb-4 text-center animate-in">
          <div className="mb-2">Predicted body type:</div>
          <span
            className={`badge fs-5 text-bg-${BODY_TYPE_VARIANT[result.predicted_body_type?.name] || 'secondary'}`}
          >
            {result.predicted_body_type?.name}
          </span>
          <p className="text-muted small mt-2 mb-0">
            Confidence: {(Number(result.confidence_score) * 100).toFixed(1)}%
          </p>
        </div>
      )}

      <h2 className="h5">Past analyses</h2>
      {isLoadingHistory ? (
        <p className="text-muted">Loading...</p>
      ) : history.length === 0 ? (
        <p className="text-muted">No analyses yet.</p>
      ) : (
        <div className="row g-3">
          {history.map((item) => (
            <div className="col-sm-6 col-md-4 col-lg-3" key={item.analysis_id}>
              <div className="card card-interactive h-100">
                <img
                  src={`${API_ORIGIN}${item.image_path}`}
                  alt="Analyzed"
                  className="card-img-top"
                  style={{ height: 160, objectFit: 'cover' }}
                />
                <div className="card-body text-center">
                  <span
                    className={`badge text-bg-${BODY_TYPE_VARIANT[item.predicted_body_type?.name] || 'secondary'}`}
                  >
                    {item.predicted_body_type?.name}
                  </span>
                  <p className="text-muted small mt-2 mb-0">
                    {(Number(item.confidence_score) * 100).toFixed(1)}% &middot;{' '}
                    {new Date(item.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
