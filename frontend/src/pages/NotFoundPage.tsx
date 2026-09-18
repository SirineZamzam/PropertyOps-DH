import {
  ArrowLeft,
  MapPinOff,
} from "lucide-react";

import {
  Link,
} from "react-router";


export default function NotFoundPage() {
  return (
    <div className="grid min-h-screen place-items-center bg-canvas px-6">
      <div className="text-center">
        <div className="mx-auto grid size-16 place-items-center rounded-3xl bg-mist/40 text-forest">
          <MapPinOff size={28} />
        </div>

        <p className="mt-6 text-xs font-bold uppercase tracking-[0.2em] text-moss">
          404
        </p>

        <h1 className="mt-3 text-4xl font-semibold tracking-[-0.05em] text-forest">
          This space doesn't exist.
        </h1>

        <Link
          to="/"
          className="mt-7 inline-flex items-center gap-2 rounded-2xl bg-forest px-5 py-3 text-sm font-semibold text-white"
        >
          <ArrowLeft size={16} />
          Back to PropertyOps
        </Link>
      </div>
    </div>
  );
}