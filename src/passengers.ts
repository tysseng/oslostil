// Zombie passengers (assets/sprites/passengers.png, tools/sprites/people.py): ordinary travellers with red
// glowing eyes. They replace the ticket bot for the labelled kinds (ADULT, CHILD, SENIOR, STUDENT);
// the label is still drawn above them. Facing left, 40 × 32 cells, feet on the bottom row.
import passengersJson from '../assets/sprites/passengers.json';

export const PASSENGERS = passengersJson;
export type PassengerKind = keyof typeof passengersJson.kinds;
export const PASSENGER_CELL_W = passengersJson.cell[0], PASSENGER_CELL_H = passengersJson.cell[1];
export const isPassenger = (kind: string): kind is PassengerKind => Object.hasOwn(PASSENGERS.kinds, kind);

/** Sheet column at song time t (u = t − arr): a shambling walk, and a lunge (the senior swats) as they reach the girls. */
export function passengerColumn(u: number, t: number, seed: number): number {
  const a = PASSENGERS.anims;
  if (u > -0.3 && u < 0.3) return a.attack[Math.min(1, Math.floor((u + 0.3) / 0.3))];
  return a.walk[Math.floor(t * PASSENGERS.fps.walk + seed * 5) % a.walk.length];
}
