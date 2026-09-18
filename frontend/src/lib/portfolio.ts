import { apiRequest } from "./api";

import type {
  Building,
  Lease,
  LeaseWithContext,
  Property,
  PropertyNode,
  Unit,
} from "../types/domain";


export async function loadPortfolioStructure(): Promise<
  PropertyNode[]
> {
  const properties =
    await apiRequest<Property[]>(
      "/properties/",
    );

  return Promise.all(
    properties.map(
      async (property) => {
        const buildings =
          await apiRequest<
            Building[]
          >(
            `/properties/${property.id}/buildings`,
          );

        const buildingNodes =
          await Promise.all(
            buildings.map(
              async (
                building,
              ) => {
                const units =
                  await apiRequest<
                    Unit[]
                  >(
                    `/buildings/${building.id}/units`,
                  );

                return {
                  ...building,
                  units,
                };
              },
            ),
          );

        return {
          ...property,
          buildings:
            buildingNodes,
        };
      },
    ),
  );
}


export function flattenUnits(
  structure: PropertyNode[],
) {
  return structure.flatMap(
    (property) =>
      property.buildings.flatMap(
        (building) =>
          building.units.map(
            (unit) => ({
              ...unit,
              property_id:
                property.id,
              property_name:
                property.name,
              building_name:
                building.name,
            }),
          ),
      ),
  );
}


export async function loadOwnerLeases(
  structure: PropertyNode[],
): Promise<
  LeaseWithContext[]
> {
  const units =
    flattenUnits(structure);

  const grouped =
    await Promise.all(
      units.map(
        async (unit) => {
          const leases =
            await apiRequest<
              Lease[]
            >(
              `/units/${unit.id}/leases`,
            );

          return leases.map(
            (lease) => ({
              ...lease,
              property_name:
                unit.property_name,
              building_name:
                unit.building_name,
              unit_number:
                unit.unit_number,
            }),
          );
        },
      ),
    );

  return grouped.flat();
}