import { create } from 'zustand';

export const useTransitionStore = create((set) => ({
  warpSpeed: 0.0005,
  isTransitioning: false,
  startTransition: () => set({ warpSpeed: 0.008, isTransitioning: true }),
  completeTransition: () => set({ warpSpeed: 0.0005, isTransitioning: false }),
}));
