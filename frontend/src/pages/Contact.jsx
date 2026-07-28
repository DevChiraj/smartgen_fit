import FloatingIcons from '../components/FloatingIcons'

export default function Contact() {
  return (
    <div className="position-relative">
      <FloatingIcons />
      <div className="col-lg-8 mx-auto">
        <h1>Contact</h1>
        <p className="text-muted">
          SmartGen Fit is a final year project. Questions, feedback, or bug reports are welcome.
        </p>
        <p>
          Email: <a href="mailto:hello@smartgenfit.app">hello@smartgenfit.app</a>
        </p>
      </div>
    </div>
  )
}
