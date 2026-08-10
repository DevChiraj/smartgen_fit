import FloatingIcons from '../components/FloatingIcons'

export default function Privacy() {
  return (
    <div className="position-relative">
      <FloatingIcons />
      <div className="col-lg-9 mx-auto">
        <h1>Privacy Policy</h1>
        <p className="lead text-muted">
          This page explains what data SmartGen Fit collects, why, and how it&apos;s handled.
        </p>

        <h2 className="h4 mt-5 mb-3">1. What we collect</h2>
        <p className="text-muted">
          When you register, we store your name, email, date of birth, gender, and a bcrypt hash
          of your password &mdash; never the password itself. If you use the body analysis
          feature, we store the photo you upload and the resulting classification. If you use the
          workout tracker, meal diary, or BMI calculator, we store the entries you log. We never
          collect more than a feature needs to work.
        </p>

        <h2 className="h4 mt-5 mb-3">2. How your photo is used</h2>
        <p className="text-muted">
          An uploaded body photo is used only to produce a body type classification (Thin,
          Normal, or Overweight) via our CNN model, and to look up a matching meal and workout
          recommendation. It is not used for any other purpose, and it is not shared with anyone
          outside the platform.
        </p>

        <h2 className="h4 mt-5 mb-3">3. How we use your data</h2>
        <p className="text-muted">
          Your data is used to run the features you interact with: showing your dashboard,
          matching you with a meal/workout recommendation, tracking your BMI and workout history
          over time, and letting administrators keep the underlying reference data accurate. We
          don&apos;t sell your data, and we don&apos;t share it with third parties for advertising
          or marketing.
        </p>

        <h2 className="h4 mt-5 mb-3">4. Cookies &amp; local storage</h2>
        <p className="text-muted">
          We use browser local storage to keep you signed in (your session token) and to remember
          your light/dark theme preference. We don&apos;t use third-party tracking or advertising
          cookies.
        </p>

        <h2 className="h4 mt-5 mb-3">5. Data security</h2>
        <p className="text-muted">
          Passwords are hashed with bcrypt and are never logged in plain text. Access to
          administrator features is role-gated on the server, not just hidden in the interface.
        </p>

        <h2 className="h4 mt-5 mb-3">6. Your choices</h2>
        <p className="text-muted">
          You can update your profile details at any time from your account settings. To request
          that your account and associated data be deleted, contact us at the email below.
        </p>

        <h2 className="h4 mt-5 mb-3">7. Academic project scope</h2>
        <p className="text-muted">
          SmartGen Fit is a final year academic project, not a commercial product. Data is used
          solely to operate the platform&apos;s features for evaluation and demonstration
          purposes.
        </p>

        <h2 className="h4 mt-5 mb-3">8. Contact</h2>
        <p className="text-muted">
          Questions about this policy or your data? Reach out at{' '}
          <a href="mailto:hello@smartgenfit.app">hello@smartgenfit.app</a>.
        </p>
      </div>
    </div>
  )
}
