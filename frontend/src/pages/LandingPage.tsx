import {
  Building2,
  CreditCard,
  DoorOpen,
  Home,
  Volume2,
  VolumeX,
  Wrench,
} from "lucide-react";

import { useRef, useState } from "react";

import { Link, useNavigate } from "react-router";

import { Brand } from "../components/Brand";

export default function LandingPage() {
  const navigate = useNavigate();

  const videoRef = useRef<HTMLVideoElement>(null);

  const [muted, setMuted] = useState(true);

  async function toggleSound() {
    const video = videoRef.current;

    if (!video) {
      return;
    }

    const nextMuted = !muted;

    video.muted = nextMuted;
    setMuted(nextMuted);

    if (!nextMuted) {
      try {
        await video.play();
      } catch {
        // Browser may block playback until
        // another direct interaction.
      }
    }
  }

  return (
    <div className="min-h-screen overflow-hidden bg-canvas text-ink">
      {/* NAV */}
      <header className="fixed inset-x-0 top-0 z-50 border-b border-phthalo/6 bg-canvas/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 md:px-8">
          <Link to="/">
            <Brand />
          </Link>

          <nav className="hidden items-center gap-8 text-sm font-medium text-phthalo/65 md:flex">
            <a href="#how-it-works" className="transition hover:text-celestial">
              How it works
            </a>

            <a href="#owners" className="transition hover:text-celestial">
              For owners
            </a>

            <a href="#tenants" className="transition hover:text-celestial">
              For tenants
            </a>
          </nav>

          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate("/auth?mode=login")}
              className="rounded-xl px-4 py-2.5 text-sm font-semibold text-phthalo transition hover:bg-phthalo/5"
            >
              Sign in
            </button>

            <button
              onClick={() => navigate("/auth?mode=register")}
              className="hidden rounded-xl bg-phthalo px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-moss sm:block"
            >
              Create workspace
            </button>
          </div>
        </div>
      </header>

      <main>
        {/* HERO */}
        <section className="relative min-h-[860px] overflow-hidden pt-24 lg:min-h-screen">
          {/* organic background shapes */}
          <div className="hero-blob absolute -left-40 top-28 h-[420px] w-[520px] rounded-[45%_55%_60%_40%] bg-cyan/18" />

          <div className="hero-blob absolute -right-52 top-10 h-[520px] w-[600px] rounded-[60%_40%_44%_56%] bg-ash/24" />

          <div className="hero-blob absolute bottom-[-260px] right-[15%] h-[520px] w-[520px] rounded-full bg-celestial/10" />

          <div className="relative mx-auto max-w-7xl px-5 pb-20 pt-10 md:px-8 lg:pt-14">
            <div className="relative min-h-[720px]">
              {/* vertical video */}
              <div className="page-enter relative z-20 mx-auto w-[230px] sm:w-[270px] lg:absolute lg:left-[4%] lg:top-6 lg:w-[350px] xl:left-[7%] xl:w-[335px]">
                <div className="relative overflow-hidden rounded-[2.8rem] border-[8px] border-phthalo bg-black shadow-[0_40px_100px_rgba(26,54,31,0.24)]">
                  <video
                    ref={videoRef}
                    autoPlay
                    loop
                    muted={muted}
                    playsInline
                    className="aspect-[9/16] w-full object-cover"
                  >
                    <source
                      src="/media/propertyops-hero.mp4"
                      type="video/mp4"
                    />
                  </video>

                  <button
                    type="button"
                    onClick={toggleSound}
                    aria-label={muted ? "Unmute video" : "Mute video"}
                    className="absolute bottom-4 right-4 grid size-11 place-items-center rounded-full bg-black/45 text-white backdrop-blur-md transition hover:scale-105 hover:bg-black/65"
                  >
                    {muted ? <VolumeX size={18} /> : <Volume2 size={18} />}
                  </button>
                </div>

                <div className="absolute -bottom-8 left-1/2 h-12 w-[75%] -translate-x-1/2 rounded-full bg-phthalo/16 blur-2xl" />
              </div>

              {/* headline */}
              <div className="page-enter relative z-10 mx-auto mt-14 max-w-2xl text-center lg:absolute lg:left-[46%] lg:top-[12%] lg:mt-0 lg:text-left">
                <p className="text-xs font-bold uppercase tracking-[0.22em] text-celestial">
                  Built around real properties
                </p>

                <h1 className="mt-5 text-5xl font-semibold leading-[0.94] tracking-[-0.065em] text-phthalo sm:text-6xl lg:text-[5rem]">
                  Every door
                  <br />
                  has a story.
                </h1>

                <p className="mt-6 max-w-xl text-base leading-7 text-phthalo/60 sm:text-lg">
                  Keep properties, tenants, leases, maintenance and rent
                  connected from one workspace.
                </p>

                <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row lg:justify-start">
                  <button
                    onClick={() => navigate("/auth?mode=register")}
                    className="rounded-2xl bg-phthalo px-6 py-3.5 text-sm font-semibold text-white shadow-xl shadow-phthalo/12 transition hover:-translate-y-1 hover:bg-moss"
                  >
                    Start as an owner
                  </button>

                  <button
                    onClick={() => navigate("/auth?mode=login")}
                    className="rounded-2xl border border-phthalo/10 bg-white px-6 py-3.5 text-sm font-semibold text-phthalo shadow-sm transition hover:border-celestial/35 hover:bg-skywash"
                  >
                    Sign in
                  </button>
                </div>
              </div>

              {/* floating door / operation cards */}
              <div className="door-float absolute right-[5%] top-[48%] hidden w-52 rounded-[1.7rem] border border-phthalo/7 bg-white p-4 shadow-xl shadow-phthalo/8 lg:block">
                <div className="flex items-center gap-3">
                  <div className="grid size-11 place-items-center rounded-2xl bg-cyan/35 text-phthalo">
                    <DoorOpen size={19} />
                  </div>

                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-celestial">
                      Unit 101
                    </p>
                    <p className="mt-1 text-sm font-semibold text-phthalo">
                      Occupied
                    </p>
                  </div>
                </div>
              </div>

              <div className="door-float-delay absolute right-[26%] top-[69%] hidden w-56 rounded-[1.7rem] bg-celestial p-4 text-white shadow-xl shadow-celestial/20 lg:block">
                <div className="flex items-center gap-3">
                  <div className="grid size-11 place-items-center rounded-2xl bg-white/16">
                    <Wrench size={18} />
                  </div>

                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-white/65">
                      Maintenance
                    </p>
                    <p className="mt-1 text-sm font-semibold">Issue assigned</p>
                  </div>
                </div>
              </div>

              <div className="door-float-slow absolute right-[3%] top-[77%] hidden w-52 rounded-[1.7rem] border border-phthalo/6 bg-ash/75 p-4 shadow-lg lg:block">
                <div className="flex items-center gap-3">
                  <div className="grid size-11 place-items-center rounded-2xl bg-white/55 text-phthalo">
                    <CreditCard size={18} />
                  </div>

                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-phthalo/45">
                      Rent
                    </p>
                    <p className="mt-1 text-sm font-semibold text-phthalo">
                      Obligation tracked
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* HOW IT WORKS */}
        <section id="how-it-works" className="bg-white py-24">
          <div className="mx-auto max-w-7xl px-5 md:px-8">
            <div className="max-w-2xl">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-celestial">
                How it works
              </p>

              <h2 className="mt-4 text-4xl font-semibold tracking-[-0.05em] text-phthalo sm:text-5xl">
                A property isn't a spreadsheet.
              </h2>

              <p className="mt-4 max-w-xl text-sm leading-7 text-phthalo/55">
                Every unit, tenant and maintenance request belongs to something
                larger. PropertyOps keeps those relationships visible.
              </p>
            </div>

            <div className="mt-12 grid auto-rows-[230px] gap-4 md:grid-cols-2 lg:grid-cols-12">
              {/* LARGE PHOTO */}
              <article className="group relative overflow-hidden rounded-[2.2rem] bg-phthalo md:row-span-2 lg:col-span-7">
                <img
                  src="/images/how-building.jpg"
                  alt=""
                  className="absolute inset-0 h-full w-full object-cover transition duration-700 group-hover:scale-105"
                  onError={(e) => {
                    e.currentTarget.style.display = "none";
                  }}
                />

                <div className="absolute inset-0 bg-gradient-to-t from-phthalo via-phthalo/35 to-transparent" />

                <div className="absolute bottom-0 left-0 p-7 text-white">
                  <p className="text-xs font-bold uppercase tracking-[0.18em] text-cyan">
                    01 · Property
                  </p>

                  <h3 className="mt-3 max-w-md text-3xl font-semibold tracking-[-0.04em]">
                    Start with the real structure.
                  </h3>

                  <p className="mt-3 max-w-md text-sm leading-6 text-white/65">
                    Property → building → unit. Nothing floats around without
                    context.
                  </p>
                </div>
              </article>

              {/* CYAN */}
              <article className="relative overflow-hidden rounded-[2.2rem] bg-cyan p-6 text-deep-blue lg:col-span-5">
                <DoorOpen size={26} />

                <p className="mt-10 text-xs font-bold uppercase tracking-[0.16em] opacity-50">
                  02 · Unit
                </p>

                <h3 className="mt-2 text-2xl font-semibold tracking-[-0.04em]">
                  Every door has a history.
                </h3>

                <div className="absolute -bottom-12 -right-10 size-40 rounded-full border-[22px] border-deep-blue/8" />
              </article>

              {/* MOSS */}
              <article className="relative overflow-hidden rounded-[2.2rem] bg-moss p-6 text-lime-soft lg:col-span-3">
                <Wrench size={24} />

                <p className="mt-10 text-xs font-bold uppercase tracking-[0.16em] opacity-55">
                  03
                </p>

                <h3 className="mt-2 text-xl font-semibold">
                  Issues move, not disappear.
                </h3>
              </article>

              {/* ASH */}
              <article className="relative overflow-hidden rounded-[2.2rem] bg-ash p-6 text-slate-green lg:col-span-2">
                <CreditCard size={24} />

                <p className="mt-10 text-xs font-bold uppercase tracking-[0.16em] opacity-50">
                  04
                </p>

                <h3 className="mt-2 text-lg font-semibold">
                  Rent stays attached.
                </h3>
              </article>
            </div>
          </div>
        </section>

        {/* OWNERS */}
        <section
  id="owners"
  className="overflow-hidden bg-[#f3f9fc] py-24"
>
  <div className="mx-auto grid max-w-7xl gap-12 px-5 md:px-8 lg:grid-cols-2 lg:items-center">
    <div>
      <p className="text-xs font-bold uppercase tracking-[0.2em] text-celestial">
        For owners
      </p>

      <h2 className="mt-4 max-w-xl text-4xl font-semibold tracking-[-0.05em] text-phthalo sm:text-5xl">
        See the building
        before the problem.
      </h2>

      <p className="mt-5 max-w-xl text-sm leading-7 text-phthalo/55">
        Move between properties,
        units, tenants, maintenance
        and costs without losing
        context.
      </p>

      <button
        onClick={() =>
          navigate(
            "/auth?mode=register",
          )
        }
        className="mt-7 rounded-2xl bg-celestial px-6 py-3.5 text-sm font-semibold text-light-slate transition hover:bg-cyan hover:text-deep-blue"
      >
        Create owner workspace
      </button>
    </div>

    <div className="relative min-h-[480px]">
      <div className="absolute inset-x-10 top-8 rounded-[2.4rem] bg-celestial p-7 text-light-slate shadow-2xl shadow-celestial/15">
        <Building2 size={26} />

        <p className="mt-16 text-xs font-bold uppercase tracking-[0.18em] opacity-60">
          Cedar House
        </p>

        <p className="mt-2 text-3xl font-semibold">
          5 units
        </p>
      </div>

      <div className="float-soft absolute bottom-20 left-0 w-56 rounded-[1.8rem] bg-cyan p-5 text-deep-blue shadow-xl">
        <Wrench size={20} />

        <p className="mt-5 text-xs font-bold uppercase tracking-[0.15em] opacity-50">
          Maintenance
        </p>

        <p className="mt-1 font-semibold">
          Plumbing assigned
        </p>
      </div>

      <div className="float-soft-delay absolute bottom-0 right-0 w-56 rounded-[1.8rem] bg-ash p-5 text-slate-green shadow-xl">
        <CreditCard size={20} />

        <p className="mt-5 text-xs font-bold uppercase tracking-[0.15em] opacity-50">
          Rent
        </p>

        <p className="mt-1 font-semibold">
          October tracked
        </p>
      </div>
    </div>
  </div>
</section>

        {/* TENANTS */}
        <section
  id="tenants"
  className="bg-moss py-24 text-lime-soft"
>
  <div className="mx-auto grid max-w-7xl gap-12 px-5 md:px-8 lg:grid-cols-[0.85fr_1.15fr] lg:items-center">
    <div className="relative mx-auto w-full max-w-sm">
      <div className="rounded-[2.3rem] bg-ash p-5 text-slate-green shadow-2xl">
        <Home size={25} />

        <p className="mt-14 text-xs font-bold uppercase tracking-[0.16em] opacity-55">
          My home
        </p>

        <h3 className="mt-2 text-3xl font-semibold">
          Unit 101
        </h3>

        <div className="mt-6 space-y-3">
          <div className="rounded-2xl bg-white/35 p-4">
            Maintenance
          </div>

          <div className="rounded-2xl bg-cyan p-4 text-deep-blue">
            Rent & payments
          </div>
        </div>
      </div>
    </div>

    <div>
      <p className="text-xs font-bold uppercase tracking-[0.2em] opacity-60">
        For tenants
      </p>

      <h2 className="mt-4 max-w-xl text-4xl font-semibold tracking-[-0.05em] sm:text-5xl">
        Less chasing.
        More knowing.
      </h2>

      <p className="mt-5 max-w-xl text-sm leading-7 opacity-65">
        Report a problem,
        track its status and
        stay connected to the
        lease that actually
        belongs to you.
      </p>

      <div className="mt-8 flex flex-wrap gap-3">
        {[
          "Report issues",
          "Track progress",
          "See rent",
        ].map(
          (item) => (
            <div
              key={item}
              className="rounded-full border border-lime-soft/20 px-4 py-2 text-sm font-semibold"
            >
              {item}
            </div>
          ),
        )}
      </div>
    </div>
  </div>
</section>
      </main>

      <footer className="bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 px-5 py-9 sm:flex-row sm:items-center sm:justify-between md:px-8">
          <Brand />

          <p className="text-xs text-phthalo/40">
            PropertyOps — property operations, connected.
          </p>
        </div>
      </footer>
    </div>
  );
}