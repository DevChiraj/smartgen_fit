const HOW_IT_WORKS = [
  {
    title: '1. Upload a photo',
    description: 'Share a full-body photo so we can analyze your body type.',
  },
  {
    title: '2. AI classifies your body type',
    description: 'A CNN model classifies you as Thin, Normal, or Overweight — nothing more.',
  },
  {
    title: '3. Get your personalized plan',
    description:
      'We look up a meal and workout plan matched to your body type, BMI, age group, and gender from our curated database.',
  },
]

export default function About() {
  return (
    <div>
      <h1>About SmartGen Fit</h1>
      <p className="lead text-muted">
        SmartGen Fit is a final year project exploring how computer vision and a curated
        nutrition database can work together to give people a starting point for healthier
        habits — without ever letting an algorithm invent health advice.
      </p>

      <h2 className="mt-5 mb-3">How it works</h2>
      <div className="row g-4">
        {HOW_IT_WORKS.map((step) => (
          <div className="col-md-4" key={step.title}>
            <div className="card h-100">
              <div className="card-body">
                <h3 className="h5">{step.title}</h3>
                <p className="card-text text-muted">{step.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <h2 className="mt-5 mb-3">Our AI boundary</h2>
      <p className="text-muted">
        Our AI model performs one task only: classifying your body type from a photo. It never
        generates meal plans, workouts, calories, or health advice. Every recommendation you
        receive comes from a predefined, rule-based lookup in our nutrition and fitness
        database, keyed on your body type, BMI category, age group, and gender — reviewed
        and managed by administrators, not invented by an algorithm.
      </p>
    </div>
  )
}
