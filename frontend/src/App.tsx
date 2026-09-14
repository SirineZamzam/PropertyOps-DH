import { useEffect, useState } from "react";

import { getProperties } from "./lib/api";
import type { Property } from "./types/property";


function App() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadProperties() {
      try {
        const data = await getProperties();
        setProperties(data);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Something went wrong."
        );
      } finally {
        setLoading(false);
      }
    }

    loadProperties();
  }, []);

  return (
    <main className="min-h-screen bg-[#fffaf4] px-6 py-12">
      <div className="mx-auto max-w-5xl">
        <div className="mb-10">
          <p className="mb-2 font-semibold uppercase tracking-[0.2em] text-[#933D1C]">
            PropertyOps
          </p>

          <h1 className="text-4xl font-bold text-[#322119] md:text-5xl">
            Property operations,
            <span className="text-[#F48A28]"> connected.</span>
          </h1>

          <p className="mt-4 max-w-2xl text-lg text-[#74452D]">
            Day 1 vertical slice: React is reading real property data
            from FastAPI and PostgreSQL.
          </p>
        </div>

        {loading && (
          <p className="text-[#74452D]">
            Loading properties...
          </p>
        )}

        {error && (
          <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-red-700">
            {error}
          </div>
        )}

        {!loading && !error && properties.length === 0 && (
          <div className="rounded-3xl border border-dashed border-[#F48A28] p-8">
            No properties yet.
          </div>
        )}

        <div className="grid gap-5 md:grid-cols-2">
          {properties.map((property) => (
            <article
              key={property.id}
              className="rounded-3xl border border-[#FECB4E]/50 bg-white p-6 shadow-sm transition duration-200 hover:-translate-y-1 hover:shadow-lg"
            >
              <div className="mb-6 h-2 w-16 rounded-full bg-[#FECB4E]" />

              <h2 className="text-2xl font-semibold text-[#322119]">
                {property.name}
              </h2>

              <p className="mt-2 text-[#74452D]">
                {property.address}
              </p>

              <p className="mt-1 text-sm text-[#933D1C]">
                {[property.city, property.country]
                  .filter(Boolean)
                  .join(", ")}
              </p>
            </article>
          ))}
        </div>
      </div>
    </main>
  );
}

export default App;