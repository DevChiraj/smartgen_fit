import FloatingIcons from '../components/FloatingIcons'

export default function Terms() {
  return (
    <div className="position-relative">
      <FloatingIcons />
      <div className="col-lg-9 mx-auto">
        <h1>Terms &amp; Conditions</h1>
        <p className="lead text-muted">
          SmartGen Fit is a final year academic project. These terms explain what you can expect
          from the platform and what we expect from you as a user.
        </p>

        <h2 className="h4 mt-5 mb-3">1. Eligibility</h2>
        <p className="text-muted">
          You must be at least 15 years old to register an account. Age is verified at
          registration and enforced on our servers, not just in the browser.
        </p>

        <h2 className="h4 mt-5 mb-3">2. What the platform does</h2>
        <p className="text-muted">
          SmartGen Fit lets you upload a full-body photo, which a trained CNN model classifies
          into one of three body types (Thin, Normal, or Overweight). That classification, along
          with your age and gender, is matched against a curated database of real meal and
          workout records to show you a recommendation. The AI model never generates meal plans,
          workouts, calories, or medical advice — every recommendation you see is an existing,
          human-curated record from our database, not text authored by an algorithm at request
          time.
        </p>

        <h2 className="h4 mt-5 mb-3">3. Not medical advice</h2>
        <p className="text-muted">
          Nothing on this platform is medical, dietary, or clinical advice. Body type
          classification and BMI category are simplified, general-purpose indicators. Always
          consult a qualified healthcare professional before making significant changes to your
          diet or exercise routine, especially if you have an existing health condition.
        </p>

        <h2 className="h4 mt-5 mb-3">4. Your account</h2>
        <p className="text-muted">
          You&apos;re responsible for keeping your login credentials confidential and for the
          accuracy of the information you provide. Passwords are hashed with bcrypt before
          storage and are never logged or stored in plain text.
        </p>

        <h2 className="h4 mt-5 mb-3">5. Acceptable use</h2>
        <p className="text-muted">
          Please don&apos;t upload photos of anyone other than yourself without their consent,
          attempt to interfere with the platform&apos;s normal operation, or try to access data
          that isn&apos;t yours. Administrator accounts and admin-only tools exist to keep the
          platform&apos;s reference data (foods, exercises, body types, BMI categories) accurate
          and are not available to standard accounts.
        </p>

        <h2 className="h4 mt-5 mb-3">6. Academic project disclaimer</h2>
        <p className="text-muted">
          This project is built for educational purposes as part of a final year undergraduate
          project. It is provided as-is, without warranty of any kind, and is not intended for
          commercial use in its current form.
        </p>

        <h2 className="h4 mt-5 mb-3">7. Changes to these terms</h2>
        <p className="text-muted">
          These terms may be updated as the project evolves. Continued use of the platform after
          a change means you accept the updated terms.
        </p>

        <h2 className="h4 mt-5 mb-3">8. Contact</h2>
        <p className="text-muted">
          Questions about these terms? Reach out at{' '}
          <a href="mailto:hello@smartgenfit.app">hello@smartgenfit.app</a>.
        </p>
      </div>
    </div>
  )
}
