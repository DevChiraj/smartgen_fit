import { useEffect, useState } from 'react'
import { getBodyTypes, updateBodyType } from '../../services/adminService'
import { formatApiError } from '../../utils/formatApiError'

export default function AdminBodyTypes() {
  const [bodyTypes, setBodyTypes] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [drafts, setDrafts] = useState({})
  const [savingId, setSavingId] = useState(null)

  useEffect(() => {
    getBodyTypes()
      .then((data) => {
        setBodyTypes(data.body_types)
        const initialDrafts = {}
        data.body_types.forEach((bt) => {
          initialDrafts[bt.body_type_id] = bt.description
        })
        setDrafts(initialDrafts)
      })
      .catch((err) => setError(formatApiError(err, 'Could not load body types.')))
      .finally(() => setIsLoading(false))
  }, [])

  const handleSave = async (bodyTypeId) => {
    setSavingId(bodyTypeId)
    setError('')
    try {
      const { body_type: updated } = await updateBodyType(bodyTypeId, {
        description: drafts[bodyTypeId],
      })
      setBodyTypes((prev) => prev.map((bt) => (bt.body_type_id === bodyTypeId ? updated : bt)))
    } catch (err) {
      setError(formatApiError(err, 'Could not update body type.'))
    } finally {
      setSavingId(null)
    }
  }

  if (isLoading) return <p className="text-muted">Loading...</p>

  return (
    <div>
      <p className="text-muted">
        Names (Thin/Normal/Overweight) are fixed - they map directly to the CNN&apos;s
        classification labels. Only descriptions are editable here.
      </p>
      {error && <div className="alert alert-danger">{error}</div>}

      {bodyTypes.map((bodyType) => (
        <div className="card mb-3" key={bodyType.body_type_id}>
          <div className="card-body">
            <h2 className="h5">{bodyType.name}</h2>
            <textarea
              className="form-control mb-2"
              rows={2}
              value={drafts[bodyType.body_type_id] ?? ''}
              onChange={(event) =>
                setDrafts({ ...drafts, [bodyType.body_type_id]: event.target.value })
              }
            />
            <button
              type="button"
              className="btn btn-primary btn-sm"
              disabled={savingId === bodyType.body_type_id}
              onClick={() => handleSave(bodyType.body_type_id)}
            >
              Save
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
