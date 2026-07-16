export default function Footer() {
  return (
    <footer className="bg-white border-top py-3 mt-auto">
      <div className="container d-flex justify-content-between flex-wrap small text-muted">
        <span>&copy; {new Date().getFullYear()} SmartGen Fit</span>
        <span>AI-powered nutrition &amp; fitness recommendations &mdash; Final Year Project</span>
      </div>
    </footer>
  )
}
