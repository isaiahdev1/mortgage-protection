"use client";

import { useState, useEffect, useRef } from "react";

const SERIF = "var(--font-serif), Georgia, serif";
const SANS = "var(--font-inter), sans-serif";

function useInView(threshold = 0.15) {
  const ref = useRef<HTMLDivElement>(null);
  const [inView, setInView] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setInView(true); }, { threshold });
    obs.observe(el);
    return () => obs.disconnect();
  }, [threshold]);
  return { ref, inView };
}

function RevealSection({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  const { ref, inView } = useInView();
  return (
    <div ref={ref} className={`transition-all duration-[900ms] ease-[cubic-bezier(0.16,1,0.3,1)] ${inView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"} ${className}`}>
      {children}
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  background: "rgba(255,255,255,0.05)",
  border: "1px solid rgba(255,255,255,0.1)",
  color: "#f5f0e8",
  borderRadius: 10,
  padding: "14px 18px",
  fontSize: 15,
  width: "100%",
  outline: "none",
  fontFamily: SANS,
};

const labelStyle: React.CSSProperties = {
  fontSize: 12,
  color: "rgba(245,240,232,0.4)",
  letterSpacing: "0.05em",
  textTransform: "uppercase",
  display: "block",
  marginBottom: 8,
};

export default function Home() {
  const [form, setForm] = useState({ name: "", email: "", phone: "", message: "" });
  const [sent, setSent] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const subject = encodeURIComponent(`Mortgage Protection Inquiry — ${form.name}`);
    const body = encodeURIComponent(
      `Name: ${form.name}\nEmail: ${form.email}\nPhone: ${form.phone}\n\nMessage:\n${form.message}`
    );
    window.location.href = `mailto:Isaackapadia@gmail.com?subject=${subject}&body=${body}`;
    setSent(true);
  };

  return (
    <main style={{ background: "#0a0a0a", color: "#f5f0e8", fontFamily: SANS }}>

      {/* NAV */}
      <nav style={{
        position: "fixed", top: 0, left: 0, right: 0, zIndex: 100,
        padding: "20px 48px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: "rgba(10,10,10,0.8)",
        backdropFilter: "blur(20px)",
        borderBottom: "1px solid rgba(255,255,255,0.06)"
      }}>
        <span style={{ fontFamily: SERIF, fontSize: 20, letterSpacing: "-0.02em", color: "#f5f0e8" }}>
          Mortgage Protection
        </span>
        <a href="#contact" style={{
          background: "linear-gradient(135deg, #c9a84c, #e8c46a)",
          color: "#0a0a0a",
          fontWeight: 600,
          fontSize: 13,
          padding: "10px 22px",
          borderRadius: 100,
          textDecoration: "none",
          letterSpacing: "0.02em"
        }}>
          Get a Quote
        </a>
      </nav>

      {/* HERO */}
      <section style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        padding: "120px 24px 80px",
        background: "radial-gradient(ellipse 90% 70% at 50% -5%, rgba(180,130,50,0.18) 0%, transparent 65%), #0a0a0a",
        position: "relative",
        overflow: "hidden"
      }}>
        <div style={{
          position: "absolute", inset: 0,
          backgroundImage: "radial-gradient(rgba(255,255,255,0.03) 1px, transparent 1px)",
          backgroundSize: "40px 40px"
        }} />

        <div style={{ position: "relative", zIndex: 1, maxWidth: 780 }}>
          <p className="fade-up delay-1" style={{
            fontSize: 12, letterSpacing: "0.2em", textTransform: "uppercase",
            color: "#c9a84c", marginBottom: 24, fontWeight: 500
          }}>
            Mortgage Protection Insurance · Gilroy, CA
          </p>

          <h1 className="fade-up delay-2" style={{
            fontFamily: SERIF,
            fontSize: "clamp(44px, 7vw, 88px)",
            lineHeight: 1.05,
            letterSpacing: "-0.03em",
            color: "#f5f0e8",
            marginBottom: 28
          }}>
            Your home stays yours.<br />
            <span className="gradient-text">No matter what.</span>
          </h1>

          <p className="fade-up delay-3" style={{
            fontSize: "clamp(16px, 2vw, 19px)",
            color: "rgba(245,240,232,0.55)",
            lineHeight: 1.7,
            maxWidth: 560,
            margin: "0 auto 44px",
            fontWeight: 300
          }}>
            Mortgage protection is term life insurance built specifically for homeowners.
            If something happens to you, the policy pays off your loan — your family keeps the house.
          </p>

          <div className="fade-up delay-4" style={{ display: "flex", gap: 16, justifyContent: "center", flexWrap: "wrap" }}>
            <a href="#contact" style={{
              background: "linear-gradient(135deg, #c9a84c, #b8933b)",
              color: "#0a0a0a",
              fontWeight: 600,
              fontSize: 15,
              padding: "16px 36px",
              borderRadius: 100,
              textDecoration: "none",
              letterSpacing: "0.01em",
              display: "inline-block"
            }}>
              Get Protected Today
            </a>
            <a href="#how-it-works" style={{
              background: "rgba(255,255,255,0.06)",
              color: "#f5f0e8",
              fontWeight: 500,
              fontSize: 15,
              padding: "16px 36px",
              borderRadius: 100,
              textDecoration: "none",
              border: "1px solid rgba(255,255,255,0.1)",
              display: "inline-block"
            }}>
              Learn More
            </a>
          </div>
        </div>

        <div className="fade-up delay-4" style={{
          position: "absolute", bottom: 48, left: "50%", transform: "translateX(-50%)",
          display: "flex", gap: 48, flexWrap: "wrap", justifyContent: "center"
        }}>
          {[
            { val: "~$50/mo", label: "Average premium" },
            { val: "$300K+", label: "Coverage available" },
            { val: "20–30 yr", label: "Term lengths" },
          ].map((s) => (
            <div key={s.label} style={{ textAlign: "center" }}>
              <div style={{ fontFamily: SERIF, fontSize: 26, color: "#c9a84c", letterSpacing: "-0.02em" }}>{s.val}</div>
              <div style={{ fontSize: 12, color: "rgba(245,240,232,0.4)", letterSpacing: "0.05em", textTransform: "uppercase", marginTop: 4 }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      <div style={{ height: 1, background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.07), transparent)" }} />

      {/* HOW IT WORKS */}
      <section id="how-it-works" style={{ padding: "120px 24px", maxWidth: 1100, margin: "0 auto" }}>
        <RevealSection>
          <p style={{ fontSize: 11, letterSpacing: "0.2em", textTransform: "uppercase", color: "#c9a84c", marginBottom: 16, fontWeight: 500 }}>
            How It Works
          </p>
          <h2 style={{ fontFamily: SERIF, fontSize: "clamp(32px, 4vw, 56px)", letterSpacing: "-0.02em", marginBottom: 64, lineHeight: 1.1 }}>
            Simple coverage.<br />Real peace of mind.
          </h2>
        </RevealSection>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 24 }}>
          {[
            { num: "01", title: "You get a policy", desc: "We match you to a term life policy that covers your exact loan amount — typically $100K–$500K — for the life of your mortgage." },
            { num: "02", title: "You pay a small monthly premium", desc: "Most homeowners pay $40–$70/month. That's it. No medical exam required for most applicants." },
            { num: "03", title: "If something happens to you", desc: "The full coverage amount is paid out immediately to cover your remaining mortgage balance. Your family never has to worry about losing the home." },
          ].map((step) => (
            <RevealSection key={step.num}>
              <div style={{
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.07)",
                borderRadius: 16,
                padding: 36,
                height: "100%"
              }}>
                <div style={{ fontFamily: SERIF, fontSize: 48, color: "rgba(201,168,76,0.2)", lineHeight: 1, marginBottom: 24 }}>{step.num}</div>
                <h3 style={{ fontFamily: SERIF, fontSize: 22, marginBottom: 14, color: "#f5f0e8" }}>{step.title}</h3>
                <p style={{ fontSize: 15, color: "rgba(245,240,232,0.5)", lineHeight: 1.75, fontWeight: 300 }}>{step.desc}</p>
              </div>
            </RevealSection>
          ))}
        </div>
      </section>

      <div style={{ height: 1, background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.07), transparent)" }} />

      {/* WHY NOW */}
      <section style={{ padding: "120px 24px", maxWidth: 900, margin: "0 auto", textAlign: "center" }}>
        <RevealSection>
          <p style={{ fontSize: 11, letterSpacing: "0.2em", textTransform: "uppercase", color: "#c9a84c", marginBottom: 16, fontWeight: 500 }}>
            Why This Matters
          </p>
          <h2 style={{ fontFamily: SERIF, fontSize: "clamp(32px, 4vw, 56px)", letterSpacing: "-0.02em", marginBottom: 28, lineHeight: 1.1 }}>
            Most families are one tragedy<br />away from losing their home.
          </h2>
          <p style={{ fontSize: 17, color: "rgba(245,240,232,0.5)", lineHeight: 1.8, fontWeight: 300, maxWidth: 680, margin: "0 auto" }}>
            When you bought your home, you took on one of the biggest financial commitments of your life.
            Mortgage protection ensures that commitment never becomes a burden for the people you love.
            At $50/month, it&apos;s the most affordable safety net a homeowner can have.
          </p>
        </RevealSection>

        <RevealSection>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 24, marginTop: 72 }}>
            {[
              { icon: "🏠", label: "Your family keeps the home" },
              { icon: "💰", label: "Loan fully paid off" },
              { icon: "📋", label: "No medical exam required" },
              { icon: "🔒", label: "Locked-in monthly rate" },
            ].map((item) => (
              <div key={item.label} style={{
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.07)",
                borderRadius: 12,
                padding: "28px 20px",
                textAlign: "center"
              }}>
                <div style={{ fontSize: 28, marginBottom: 12 }}>{item.icon}</div>
                <div style={{ fontSize: 14, color: "rgba(245,240,232,0.7)", fontWeight: 500 }}>{item.label}</div>
              </div>
            ))}
          </div>
        </RevealSection>
      </section>

      <div style={{ height: 1, background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.07), transparent)" }} />

      {/* CONTACT */}
      <section id="contact" style={{ padding: "120px 24px", maxWidth: 640, margin: "0 auto" }}>
        <RevealSection>
          <p style={{ fontSize: 11, letterSpacing: "0.2em", textTransform: "uppercase", color: "#c9a84c", marginBottom: 16, fontWeight: 500 }}>
            Get a Free Quote
          </p>
          <h2 style={{ fontFamily: SERIF, fontSize: "clamp(32px, 4vw, 52px)", letterSpacing: "-0.02em", marginBottom: 14, lineHeight: 1.1 }}>
            Let&apos;s find the right coverage for you.
          </h2>
          <p style={{ fontSize: 16, color: "rgba(245,240,232,0.45)", lineHeight: 1.7, marginBottom: 48, fontWeight: 300 }}>
            Fill out the form and Isaac will reach out within 24 hours with a personalized quote — no pressure, no obligation.
          </p>
        </RevealSection>

        <RevealSection>
          {sent ? (
            <div style={{
              background: "rgba(201,168,76,0.08)",
              border: "1px solid rgba(201,168,76,0.2)",
              borderRadius: 16,
              padding: "48px 32px",
              textAlign: "center"
            }}>
              <div style={{ fontFamily: SERIF, fontSize: 32, marginBottom: 12 }}>You&apos;re all set.</div>
              <p style={{ color: "rgba(245,240,232,0.55)", fontSize: 16 }}>Isaac will be in touch within 24 hours.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                <div>
                  <label style={labelStyle}>Full Name</label>
                  <input type="text" placeholder="John Smith" required value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })} style={inputStyle} />
                </div>
                <div>
                  <label style={labelStyle}>Phone</label>
                  <input type="tel" placeholder="(408) 555-0100" value={form.phone}
                    onChange={(e) => setForm({ ...form, phone: e.target.value })} style={inputStyle} />
                </div>
              </div>

              <div>
                <label style={labelStyle}>Email</label>
                <input type="email" placeholder="john@example.com" required value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })} style={inputStyle} />
              </div>

              <div>
                <label style={labelStyle}>Message (optional)</label>
                <textarea placeholder="Tell us about your home or any questions..." rows={4} value={form.message}
                  onChange={(e) => setForm({ ...form, message: e.target.value })}
                  style={{ ...inputStyle, resize: "vertical" }} />
              </div>

              <button type="submit" style={{
                background: "linear-gradient(135deg, #c9a84c, #b8933b)",
                color: "#0a0a0a",
                fontWeight: 600,
                fontSize: 15,
                padding: "18px 32px",
                borderRadius: 10,
                border: "none",
                cursor: "pointer",
                fontFamily: SANS,
                letterSpacing: "0.01em",
                marginTop: 8
              }}>
                Request My Free Quote
              </button>

              <p style={{ fontSize: 12, color: "rgba(245,240,232,0.25)", textAlign: "center", lineHeight: 1.6 }}>
                By submitting, you agree to be contacted by Isaac Kapadia regarding mortgage protection insurance.
                No spam. Unsubscribe any time.
              </p>
            </form>
          )}
        </RevealSection>
      </section>

      {/* FOOTER */}
      <footer style={{
        borderTop: "1px solid rgba(255,255,255,0.06)",
        padding: "40px 48px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: 16
      }}>
        <span style={{ fontFamily: SERIF, fontSize: 18, color: "rgba(245,240,232,0.5)" }}>Mortgage Protection</span>
        <div style={{ display: "flex", gap: 32, alignItems: "center" }}>
          <a href="mailto:Isaackapadia@gmail.com" style={{ fontSize: 13, color: "rgba(245,240,232,0.35)", textDecoration: "none" }}>
            Isaackapadia@gmail.com
          </a>
          <span style={{ fontSize: 13, color: "rgba(245,240,232,0.2)" }}>Gilroy, CA</span>
        </div>
      </footer>

    </main>
  );
}
