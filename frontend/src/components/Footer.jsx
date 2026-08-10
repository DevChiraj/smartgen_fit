import { Link } from 'react-router-dom'
import { Mail, MapPin, Phone, Globe } from 'lucide-react'
import { FaFacebookF, FaXTwitter, FaInstagram, FaPinterestP, FaLinkedinIn } from 'react-icons/fa6'
import workoutPlansImg from '../assets/feature-workout-plans.jpg'
import sriLankanMealPlansImg from '../assets/feature-sri-lankan-meal-plans.jpg'

const SOCIAL_LINKS = [
  { label: 'Facebook', href: 'https://facebook.com', Icon: FaFacebookF },
  { label: 'Twitter', href: 'https://twitter.com', Icon: FaXTwitter },
  { label: 'Instagram', href: 'https://instagram.com', Icon: FaInstagram },
  { label: 'Pinterest', href: 'https://pinterest.com', Icon: FaPinterestP },
  { label: 'LinkedIn', href: 'https://linkedin.com', Icon: FaLinkedinIn },
]

const GALLERY_HIGHLIGHTS = [
  { image: workoutPlansImg, title: 'Full-Body Strength Circuit', subtitle: 'Workout Library' },
  { image: sriLankanMealPlansImg, title: 'Sri Lankan Meal Prep', subtitle: 'Meal Plans' },
]

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container">
        <div className="footer-grid">
          <div className="footer-col footer-col-brand">
            <Link to="/" className="footer-logo">
              Smart<span className="text-accent">Gen</span> Fit
            </Link>
            <p className="footer-tagline">
              Empowering your fitness journey with AI-driven insights and personalized Sri Lankan
              meal plans.
            </p>
            <div className="footer-socials">
              {SOCIAL_LINKS.map(({ label, href, Icon }) => (
                <a
                  key={label}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="footer-social-icon"
                  aria-label={label}
                >
                  <Icon size={15} />
                </a>
              ))}
            </div>
          </div>

          <div className="footer-col">
            <h3 className="footer-heading">Quick Contacts</h3>
            <ul className="footer-contact-list">
              <li>
                <MapPin size={16} className="footer-contact-icon" />
                <span>Colombo, Sri Lanka</span>
              </li>
              <li>
                <Mail size={16} className="footer-contact-icon" />
                <a href="mailto:hello@smartgenfit.app">hello@smartgenfit.app</a>
              </li>
              <li>
                <Phone size={16} className="footer-contact-icon" />
                <a href="tel:+94185236982">0185236982</a>
              </li>
              <li>
                <Globe size={16} className="footer-contact-icon" />
                <span>www.smartgenfit.app</span>
              </li>
            </ul>
          </div>

          <div className="footer-col">
            <h3 className="footer-heading">Gallery</h3>
            <ul className="footer-gallery-list">
              {GALLERY_HIGHLIGHTS.map((item) => (
                <li key={item.title}>
                  <img src={item.image} alt="" className="footer-gallery-thumb" />
                  <div>
                    <p className="footer-gallery-title">{item.title}</p>
                    <span className="footer-gallery-subtitle">{item.subtitle}</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="footer-subbar">
          <span>&copy; Copyright {new Date().getFullYear()} by SmartGen Fit</span>
          <div className="footer-sublinks">
            <span className="footer-sublink-static">Terms &amp; Conditions</span>
            <span className="footer-sublink-divider">/</span>
            <span className="footer-sublink-static">Privacy Policy</span>
            <span className="footer-sublink-divider">/</span>
            <Link to="/contact">Support</Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
