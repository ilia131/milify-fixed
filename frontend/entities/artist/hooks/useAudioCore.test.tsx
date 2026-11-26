import { renderHook } from "@testing-library/react";

import type { Song } from "@/redux/features/playerSlice";
import { useGetSongSubscriptionAccessQuery } from "@/redux/services/artistApislice";
import { useAudioCore } from "./useAudioCore";

jest.mock("@/redux/services/artistApislice");

test("plays the current signed source and clears it when access is lost", () => {
  const audio = document.createElement("audio");
  jest.spyOn(audio, "load").mockImplementation(() => {});
  jest.spyOn(audio, "pause").mockImplementation(() => {});
  const play = jest.spyOn(audio, "play").mockResolvedValue(undefined);
  const song = {
    unique_id: "song-id", is_subscription_only: true, track_url: "https://storage.example/stale",
  } as Song;
  const audioRef = { current: audio };
  const mockAccess = jest.mocked(useGetSongSubscriptionAccessQuery);
  mockAccess.mockReturnValue({
    currentData: { can_play: true, track_url: "https://storage.example/signed" },
    isFetching: false,
  } as ReturnType<typeof useGetSongSubscriptionAccessQuery>);

  const { rerender } = renderHook(() => useAudioCore(audioRef, song, true, 0.5));
  expect(audio.src).toBe("https://storage.example/signed");
  expect(play).toHaveBeenCalledTimes(1);

  mockAccess.mockReturnValue({
    currentData: { can_play: false },
    isFetching: false,
  } as ReturnType<typeof useGetSongSubscriptionAccessQuery>);
  rerender();
  expect(audio.hasAttribute("src")).toBe(false);
  expect(play).toHaveBeenCalledTimes(1);
});
