import { useEffect, useState } from 'react'
import { API_ORIGIN } from '../services/apiClient'
import { analyzeImage, getAnalysisHistory } from '../services/imageAnalysisService'
import { formatApiError } from '../utils/formatApiError'

const BODY_TYPE_VARIANT = {
  Thin: 'info',
  Normal: 'success',
  Overweight: 'warning',
}

export default function ImageAnalysis() {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isLoadingHistory, setIsLoadingHistory] = useState(true)

  const fetchHistory = () => {
    return getAnalysisHistory()
      .then((data) => setHistory(data.history))
      .catch(() => setHistory([]))
  }

  useEffect(() => {
    fetchHistory().finally(() => setIsLoadingHistory(false))
  }, [])

  const handleFileChange = (event) => {
    const selected = event.target.files[0]
    setFile(selected || null)
    setResult(null)
    setError('')
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(selected ? URL.createObjectURL(selected) : null)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!file) return

    setError('')
    setResult(null)
    setIsSubmitting(true)
    try {
      const data = await analyzeImage(file)
      setResult(data.analysis)
      fetchHistory()
    } catch (err) {
      setError(formatApiError(err, 'Could not analyze the photo.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div>
      <h1>Body Type Analysis</h1>

      <div className="alert alert-warning">
        <strong>Demo classifier.</strong> This model was trained on a small proof-of-concept
        dataset to prove the upload-to-prediction pipeline works end to end. Results here are for
        demonstration only and should not be treated as an accurate body-type assessment.
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <form onSubmit={handleSubmit} className="mb-4">
        <div className="mb-3">
          <label className="form-label" htmlFor="image">
            Upload a full-body photo
          </label>
          <input
            id="image"
            type="file"
            accept="image/png, image/jpeg, image/webp"
            className="form-control"
            onChange={handleFileChange}
          />
        </div>

        {previewUrl && (
          <img
            src={previewUrl}
            alt="Selected preview"
            style={{ maxWidth: 200, maxHeight: 260, objectFit: 'cover' }}
            className="mb-3 rounded border d-block"
          />
        )}

        <button type="submit" className="btn btn-primary" disabled={!file || isSubmitting}>
          {isSubmitting ? 'Analyzing...' : 'Analyze photo'}
        </button>
      </form>

      {result && (
        <div className="p-3 border rounded mb-4 text-center">
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
              <div className="card h-100">
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
