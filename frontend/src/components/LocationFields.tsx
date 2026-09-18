import {
  FormField,
  controlClass,
} from "./FormField";

import type {
  PropertyNode,
} from "../types/domain";


interface Props {
  structure:
    PropertyNode[];

  propertyId: string;
  buildingId: string;
  unitId: string;

  onPropertyChange: (
    value: string,
  ) => void;

  onBuildingChange: (
    value: string,
  ) => void;

  onUnitChange: (
    value: string,
  ) => void;

  propertyError?: string;
  buildingError?: string;
  unitError?: string;

  vacantOnly?: boolean;
  occupiedOnly?: boolean;

  allowAll?: boolean;
  unitOptional?: boolean;
}


export function LocationFields({
  structure,
  propertyId,
  buildingId,
  unitId,
  onPropertyChange,
  onBuildingChange,
  onUnitChange,
  propertyError,
  buildingError,
  unitError,
  vacantOnly = false,
  occupiedOnly = false,
  allowAll = false,
  unitOptional = false,
}: Props) {
  const property =
    structure.find(
      (item) =>
        String(item.id) ===
        propertyId,
    );

  const buildings =
    property?.buildings ??
    [];

  const building =
    buildings.find(
      (item) =>
        String(item.id) ===
        buildingId,
    );

  let units =
    building?.units ?? [];

  if (vacantOnly) {
    units =
      units.filter(
        (unit) =>
          unit.status ===
          "VACANT",
      );
  }

  if (occupiedOnly) {
    units =
      units.filter(
        (unit) =>
          unit.status ===
          "OCCUPIED",
      );
  }


  function changeProperty(
    value: string,
  ) {
    onPropertyChange(
      value,
    );

    onBuildingChange("");
    onUnitChange("");
  }


  function changeBuilding(
    value: string,
  ) {
    onBuildingChange(
      value,
    );

    onUnitChange("");
  }


  return (
    <>
      <FormField
        label="Property"
        error={propertyError}
      >
        <select
          value={propertyId}
          onChange={(event) =>
            changeProperty(
              event.target.value,
            )
          }
          className={controlClass}
        >
          <option value="">
            {allowAll
              ? "All properties"
              : "Select property"}
          </option>

          {structure.map(
            (item) => (
              <option
                key={item.id}
                value={item.id}
              >
                {item.name}
              </option>
            ),
          )}
        </select>
      </FormField>

      <FormField
        label="Building"
        error={buildingError}
      >
        <select
          value={buildingId}
          disabled={!propertyId}
          onChange={(event) =>
            changeBuilding(
              event.target.value,
            )
          }
          className={controlClass}
        >
          <option value="">
            {allowAll
              ? "All buildings"
              : "Select building"}
          </option>

          {buildings.map(
            (item) => (
              <option
                key={item.id}
                value={item.id}
              >
                {item.name}
              </option>
            ),
          )}
        </select>
      </FormField>

      <FormField
        label="Unit"
        error={unitError}
      >
        <select
          value={unitId}
          disabled={!buildingId}
          onChange={(event) =>
            onUnitChange(
              event.target.value,
            )
          }
          className={controlClass}
        >
          <option value="">
            {unitOptional
              ? "Property level / No unit"
              : allowAll
                ? "All units"
                : "Select unit"}
          </option>

          {units.map(
            (item) => (
              <option
                key={item.id}
                value={item.id}
              >
                Unit{" "}
                {
                  item.unit_number
                }{" "}
                ·{" "}
                {item.status}
              </option>
            ),
          )}
        </select>
      </FormField>
    </>
  );
}