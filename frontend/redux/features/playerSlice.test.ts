import reducer, { setQueue, setVolume, stopPlayback, toggleRepeatOne, toggleShuffle } from "./playerSlice";
import type { Song } from "./playerSlice";

test("player options are preserved when the queue changes", () => {
  let state = reducer(undefined, toggleShuffle());
  state = reducer(state, toggleRepeatOne());
  state = reducer(state, setVolume(0.25));
  state = reducer(state, setQueue({ songs: [{ id: 1, unique_id: "fixture" } as Song] }));
  expect(state).toMatchObject({ volume: 0.25, shuffle: true, repeatOne: true, isPlaying: true });
  expect(reducer(state, stopPlayback()).isPlaying).toBe(false);
});
